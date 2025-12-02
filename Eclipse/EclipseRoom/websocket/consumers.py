from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from api.serializers import UserAPISerializer
from collections import defaultdict
import json
from EclipseRoom.models.roommessage import RoomMessage
from EclipseRoom.serializers.roommessage import RoomMessageSerializer
from EclipseRoom.serializers.roomuser import RoomUserProfileSerializer
from EclipseRoom.models.roomuser import RoomUser


import asyncio
import logging

# YES, I HAD TO REALLY CODE THIS LOGGER
# Logger setup (optional, but more convenient than print)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s'))
    logger.addHandler(handler)

# Global variable (you already have this)
room_connections = defaultdict(dict)
streaming = defaultdict()

# Flag to avoid starting the task multiple times
_print_task_started = False

async def _print_room_connections_periodically():
    """Background task: prints room_connections every second."""
    while True:
        # Nice output: only non-empty rooms
        snapshot = {
            room_id: list(users.keys())  # only user IDs
            for room_id, users in room_connections.items()
            if users
        }
        if snapshot:
            logger.info(f"room_connections: {snapshot}")
        else:
            logger.info("room_connections: {} (empty)")
        await asyncio.sleep(1)

def start_monitoring():
    """Starts the background task if it's not already running."""
    global _print_task_started
    if not _print_task_started:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(_print_room_connections_periodically())
            _print_task_started = True
            logger.info("✅ Monitoring room_connections started (every 1s).")
        else:
            # If the loop is not yet running (rare in Channels), defer the start
            asyncio.ensure_future(_print_room_connections_periodically())
            _print_task_started = True


# add notifications. dynamic: user kick, user ban
room_connections = defaultdict(dict)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'
        self.user = UserAPISerializer(self.scope['user']).data
        auth = self.scope['user'].is_authenticated

        self.is_streaming = False

        self.profile = await self.user_profile()
        if (not auth) or not(self.profile):
            print("POSHEL NAHUI")
            await self.close()
            return

        self.profile = await sync_to_async(lambda: RoomUserProfileSerializer(self.profile).data)()
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
                "action":"handshake",
                "profile": self.profile,
                "connected":list(room_connections[self.room_id].keys())
            }))

    async def disconnect(self, close_code):
        if self.profile == False:
            return
        if self.profile["id"] in room_connections.get(self.room_id, {}):
            del room_connections[self.room_id][self.profile["id"]]


            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_disconnect',
                    'user': self.profile,
                }
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
            room_connections[self.room_id][self.profile["id"]] = self.channel_name

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_connect',
                    'action': "new_connect",
                    'user': self.profile
                }
            )
        

        elif action in ["offer", "answer", "ice_candidate"]:
            target_user_id = message.get("to")
            target_channel = room_connections.get(self.room_id, {}).get(target_user_id)

            if target_channel:
                await self.channel_layer.send(target_channel, {
                    "type": "send_sdp",
                    "action": action,
                    "pkg": message["sdp"],
                    "from_user_id": self.profile["id"],
                    "camera":self.is_streaming
                })
        elif action == "user_camera":
            self.is_streaming = message["enabled"]
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_camera',
                    'status':message["enabled"],
                    'user': self.profile,
                }
            )

        elif action == "user_message":
            usermsg = await self.create_message(message, self.profile["id"])
            serialized_data = await sync_to_async(lambda: RoomMessageSerializer(usermsg).data)()
            await self.channel_layer.group_send(self.room_group_name, {
                "type": "new_message",
                "message": serialized_data
            })

        elif action == "delete_message":
            await self.channel_layer.group_send(self.room_group_name, {
                "type": "delete_message",
                "message": message,
            })
        elif action == "kick_user":
            await self.channel_layer.group_send(self.room_group_name, {
                "type": "kick_user",
                "message": message,
            })

        elif action == "voice_kick":
            if (await self.has_permission()):
                await self.channel_layer.group_send(self.room_group_name, {
                "type": "voice_kick",
                "id": message["id"],
            })

        elif action == "user_disconnect":
            print(room_connections)
            if self.profile["id"] in room_connections.get(self.room_id, {}):
                del room_connections[self.room_id][self.profile["id"]]


            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_disconnect',
                    'user': self.profile,
                }
            )
            print(room_connections)


    async def send_sdp(self, event):
        if event['from_user_id'] != self.profile["id"]:
            await self.send(text_data=json.dumps({
                "action": event["action"],
                "pkg": event["pkg"],
                "from_user_id": event["from_user_id"],
                "camera":event["camera"]
            }))


    async def user_connect(self, event):
                await self.send(text_data=json.dumps({
                    'action': 'new_connect',
                    'user': event['user']
                }))
    
    async def user_camera(self,event):
            if event['user']['id'] != self.profile["id"]:
                await self.send(text_data=json.dumps({
                    'action':'user_camera',
                    'status':event['status'],
                    'user':event['user'],
                }))


    async def user_disconnect(self, event):
        if event['user']['id'] == self.profile["id"]:
            if self.profile["id"] in room_connections.get(self.room_id, {}):
                del room_connections[self.room_id][self.profile["id"]]
        if event['user']['id'] != self.profile["id"]:
            await self.send(text_data=json.dumps({
                'action': 'user_disconnect',
                'user': event['user'],
            }))
    
    async def voice_kick(self,event):
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
              "action":"delete_message",
              "message":event["message"],
         }))
    async def kick_user(self, event):
         await self.send(text_data=json.dumps({
              "action":"kick_user",
              "message":event["message"],
         }))

    @database_sync_to_async
    def create_message(self, content, user_id):
        usermsg = RoomMessage(room_id=self.room_id, room_user_id=user_id, text=content)
        usermsg.save()
        return usermsg

    @database_sync_to_async
    def user_profile(self):
        try:
            profile = RoomUser.objects.get(room_id=self.room_id, user_id=self.user["id"])
            return profile
        except:
            return False

    @database_sync_to_async
    def has_permission(self):
        user = RoomUser.objects.get(room_id=self.room_id, user_id=self.user["id"])
        if (user.role in RoomUser.ROLE_MODERATOR, RoomUser.ROLE_CREATOR):
            return True
        return False
