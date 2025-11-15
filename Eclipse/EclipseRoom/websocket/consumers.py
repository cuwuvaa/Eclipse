from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from api.serializers import UserAPISerializer
from collections import defaultdict
import json
from EclipseRoom.models.roommessage import RoomMessage
from EclipseRoom.serializers.roommessage import RoomMessageSerializer
from EclipseRoom.models.roomuser import RoomUser

connected_users = defaultdict()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_name = f'room{self.room_id}'
        self.user = UserAPISerializer(self.scope['user']).data
        print(f"{self.user['username']} connected")
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )
        await self.accept()
    
        await self.send_voice_users()


    async def send_voice_users(self):
        try:
            await self.send(text_data=json.dumps({
                'action': 'voice_users',
                'users': connected_users,
                'me':self.user["id"],
            }))
        except:
            await self.send(text_data=json.dumps({
                'action': 'voice_users',
                'users': 'empty',
                'me':self.user["id"],
            }))

    async def disconnect(self, close_code):
        if self.user['id'] in connected_users:
            del connected_users[self.user['id']]
        await self.channel_layer.group_send(self.room_name, {
            "type": "user_left",
            "action":"user_left",
            "user_id": self.user["id"],
        })

        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        message = data.get('message', {})
        print(connected_users)
        print(f'USER: {self.user["username"]} || ACTION: {action}')
        if action == "user_message":
            usermsg = await self.create_message(message, self.user["id"])
            serialized_data = await sync_to_async(lambda: RoomMessageSerializer(usermsg).data)()
            await self.channel_layer.group_send(self.room_name, {
                "type": "user_message",
                "action":"new_message",
                "message": serialized_data
            })
        if action == "connect":
            connected_users[self.user["id"]] = self.channel_name
            await self.channel_layer.group_send(self.room_name, {
                "type": "user_connect",
                "action":"new_connect",
                "user": self.user,
            })
        if action == "disconnect":
            await self.channel_layer.group_send(self.room_name, {
                "type": "user_disconnect",
                "action":"user_disconnect",
                "user": self.user,
            })
        if action == "offer" or action == "answer" or action == "ice_candidate":
            await self.channel_layer.send(connected_users[message["to"]], {
                "type": "send_sdp",
                "action":action,
                "pkg":message["sdp"],
                "from_user_id":self.user["id"],
            })
    async def send_sdp(self, event):
        await self.send(json.dumps({
            "action":event["action"],
            "pkg":event["pkg"],
            "from_user_id":event["from_user_id"],
        }))

    async def user_connect(self, event):
        await self.send(json.dumps({
            "action": event["action"],
            "user":event["user"],
        }))

    async def user_disconnect(self, event):
        await self.send(json.dumps({
            "action": event["action"],
            "user":event["user"],
        }))

    async def user_message(self,event):
        await self.send(json.dumps({
            "action": event["action"],
            "message":event["message"]
        }))

    @database_sync_to_async
    def create_message(self, content, user_id):
        usermsg = RoomMessage(room_id=self.room_id, room_user_id = user_id, text=content)
        usermsg.save()
        return usermsg