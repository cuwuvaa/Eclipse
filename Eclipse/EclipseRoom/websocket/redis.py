from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from api.serializers import UserAPISerializer
import json
import redis.asyncio as redis
import time

from EclipseRoom.models.roommessage import RoomMessage
from EclipseRoom.serializers.roommessage import RoomMessageSerializer
from EclipseRoom.serializers.roomuser import RoomUserProfileSerializer
from EclipseRoom.models.roomuser import RoomUser


# =============== REDIS MANAGER ===============
redis_conn = redis.Redis(host='redis', port=6379, decode_responses=True)
ROOM_USERS_KEY = "room:{}:users"

PRESENCE_KEY = "online:{}"

async def set_user_online(user_id: str):
    key = PRESENCE_KEY.format(user_id)
    await redis_conn.set(key, "1", ex=86400)

async def set_user_offline(user_id: str):
    key = PRESENCE_KEY.format(user_id)
    await redis_conn.delete(key)

async def is_user_online(user_id: str) -> bool:
    key = PRESENCE_KEY.format(user_id)
    return await redis_conn.exists(key)


async def add_user(room_id: str, user_id: str, channel_name: str):
    key = ROOM_USERS_KEY.format(room_id)
    await redis_conn.hset(key, user_id, channel_name)
    await redis_conn.expire(key, 7200)

async def remove_user(room_id: str, user_id: str):
    key = ROOM_USERS_KEY.format(room_id)
    await redis_conn.hdel(key, user_id)

async def get_channel(room_id: str, user_id: str) -> str | None:
    key = ROOM_USERS_KEY.format(room_id)
    return await redis_conn.hget(key, user_id)

async def get_user_ids(room_id: str) -> list[str]:
    key = ROOM_USERS_KEY.format(room_id)
    return await redis_conn.hkeys(key)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'
        self.user = UserAPISerializer(self.scope['user']).data
        auth = self.scope['user'].is_authenticated

        self.is_streaming = False

        self.profile = await self.user_profile()
        if not auth or not self.profile:
            await self.close()
            return

        self.profile = await sync_to_async(lambda: RoomUserProfileSerializer(self.profile).data)()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Получаем ID подключённых юзеров из Redis
        connected_user_ids = await get_user_ids(self.room_id)
        await set_user_online(str(self.user["id"]))
        await self.send(text_data=json.dumps({
            "action": "handshake",
            "profile": self.profile,
            "connected": connected_user_ids
        }))

    async def disconnect(self, close_code):
        if not self.profile or self.profile is False:
            return
        user_id = str(self.user["id"])
        await set_user_offline(user_id)

        user_id = str(self.profile["id"])
        await remove_user(self.room_id, user_id)
    

        await self.channel_layer.group_send(
            self.room_group_name,
            {'type': 'user_disconnect', 'user': self.profile}
        )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        message = data.get('message', {})

        if action == 'connect':
            await add_user(self.room_id, str(self.profile["id"]), self.channel_name)
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'user_connect', 'action': 'new_connect', 'user': self.profile}
            )
        elif action == 'status':
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'user_update', 'action': 'user_update', 'user': self.profile}
            )

        elif action in ["offer", "answer", "ice_candidate"]:
            target_user_id = str(message.get("to"))
            target_channel = await get_channel(self.room_id, target_user_id)
            if target_channel:
                await self.channel_layer.send(target_channel, {
                    "type": "send_sdp",
                    "action": action,
                    "pkg": message["sdp"],
                    "from_user_id": self.profile["id"],
                    "camera": self.is_streaming
                })

        elif action == "user_camera":
            self.is_streaming = message["enabled"]
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'user_camera', 'status': message["enabled"], 'user': self.profile}
            )

        elif action == "user_message":
            usermsg = await self.create_message(message, self.profile["id"])
            serialized_data = await sync_to_async(lambda: RoomMessageSerializer(usermsg).data)()
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "new_message", "message": serialized_data}
            )

        elif action == "delete_message":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "delete_message", "message": message}
            )

        elif action == "kick_user":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "kick_user", "message": message}
            )

        elif action == "voice_kick":
            if await self.has_permission():
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "voice_kick", "id": message["id"]}
                )

        elif action == "user_disconnect":
            await remove_user(self.room_id, str(self.profile["id"]))
            await self.channel_layer.group_send(
                self.room_group_name,
                {'type': 'user_disconnect', 'user': self.profile}
            )

    # === HANDLERS (точно как было) ===
    async def send_sdp(self, event):
        if event['from_user_id'] != self.profile["id"]:
            await self.send(text_data=json.dumps({
                "action": event["action"],
                "pkg": event["pkg"],
                "from_user_id": event["from_user_id"],
                "camera": event["camera"]
            }))

    async def user_connect(self, event):
        await self.send(text_data=json.dumps({
            'action': 'new_connect',
            'user': event['user']
        }))

    async def user_camera(self, event):
        if event['user']['id'] != self.profile["id"]:
            await self.send(text_data=json.dumps({
                'action': 'user_camera',
                'status': event['status'],
                'user': event['user'],
            }))

    async def user_disconnect(self, event):
        if event['user']['id'] != self.profile["id"]:
            await self.send(text_data=json.dumps({
                'action': 'user_disconnect',
                'user': event['user'],
            }))
    async def user_update(self, event):
        if event['user']['id'] != self.profile["id"]:
            await self.send(text_data=json.dumps({
                'action': 'user_update',
                'user': event['user'],
            }))

    async def voice_kick(self, event):
        await self.send(text_data=json.dumps({
            'action': 'voice_kick',
            'id': event['id'],
        }))

    async def new_message(self, event):
        await self.send(text_data=json.dumps({
            'action': 'new_message',
            'message': event['message']
        }))

    async def delete_message(self, event):
        await self.send(text_data=json.dumps({
            "action": "delete_message",
            "message": event["message"],
        }))

    async def kick_user(self, event):
        await self.send(text_data=json.dumps({
            "action": "kick_user",
            "message": event["message"],
        }))

    # === DB HELPERS ===
    @database_sync_to_async
    def create_message(self, content, user_id):
        usermsg = RoomMessage(room_id=self.room_id, room_user_id=user_id, text=content)
        usermsg.save()
        return usermsg

    @database_sync_to_async
    def user_profile(self):
        try:
            return RoomUser.objects.get(room_id=self.room_id, user_id=self.user["id"])
        except RoomUser.DoesNotExist:
            return False

    @database_sync_to_async
    def has_permission(self):
        try:
            user = RoomUser.objects.get(room_id=self.room_id, user_id=self.user["id"])
            return user.role in (RoomUser.ROLE_MODERATOR, RoomUser.ROLE_CREATOR)
        except:
            return False