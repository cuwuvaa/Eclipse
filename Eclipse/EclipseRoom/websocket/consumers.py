from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from api.serializers import UserAPISerializer
from collections import defaultdict
import json
from EclipseRoom.models.roommessage import RoomMessage
from EclipseRoom.serializers.roommessage import RoomMessageSerializer
from EclipseRoom.models.roomuser import RoomUser

# This dictionary will store all connected users in this instance of the server.
# Key: room_id, Value: {user_id: channel_name}
# This is a simplified approach; for production, a shared cache like Redis is recommended.
room_connections = defaultdict(dict)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'room_{self.room_id}'
        self.user = UserAPISerializer(self.scope['user']).data
        auth = self.scope['user'].is_authenticated

        if not auth:
            await self.close()
            return

        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Remove user from the room's connection list
        if self.user["id"] in room_connections.get(self.room_id, {}):
            del room_connections[self.room_id][self.user["id"]]

            # Announce that the user has left to all other users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_disconnect',
                    'user': self.user,
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
            room_connections[self.room_id][self.user["id"]] = self.channel_name

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_connect',
                    'action': "new_connect",
                    'user': self.user
                }
            )
        
        # Route signaling messages
        elif action in ["offer", "answer", "ice_candidate"]:
            target_user_id = message.get("to")
            target_channel = room_connections.get(self.room_id, {}).get(target_user_id)

            if target_channel:
                await self.channel_layer.send(target_channel, {
                    "type": "send_sdp",
                    "action": action,
                    "pkg": message["sdp"],
                    "from_user_id": self.user["id"],
                })
        elif action == "user_camera":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_camera',
                    'status':message["enabled"],
                    'user': self.user,
                }
            )

        elif action == "user_message":
            # Handle text messages as before
            usermsg = await self.create_message(message, self.user["id"])
            serialized_data = await sync_to_async(lambda: RoomMessageSerializer(usermsg).data)()
            await self.channel_layer.group_send(self.room_group_name, {
                "type": "new_message",
                "message": serialized_data
            })

        elif action == "user_disconnect":
            if self.user["id"] in room_connections.get(self.room_id, {}):
                del room_connections[self.room_id][self.user["id"]]

            # Announce that the user has left to all other users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_disconnect',
                    'user': self.user,
                }
            )

    # Handler to forward SDP (offer, answer, candidate) to the client
    async def send_sdp(self, event):
        if event['from_user_id'] != self.user["id"]:
            await self.send(text_data=json.dumps({
                "action": event["action"],
                "pkg": event["pkg"],
                "from_user_id": event["from_user_id"],
            }))

    # Handler to broadcast new user connection
    async def user_connect(self, event):
            if event['user']['id'] != self.user["id"]:
                await self.send(text_data=json.dumps({
                    'action': 'new_connect',
                    'user': event['user']
                }))
    
    async def user_camera(self,event):
            if event['user']['id'] != self.user["id"]:
                await self.send(text_data=json.dumps({
                    'action':'user_camera',
                    'status':event['status'],
                    'user':event['user'],
                }))

    # Handler to broadcast user disconnection
    async def user_disconnect(self, event):
        if event['user']['id'] != self.user["id"]:
            await self.send(text_data=json.dumps({
                'action': 'user_disconnect',
                'user': event['user'],
            }))

    # Handler for new text messages
    async def new_message(self, event):
        await self.send(text_data=json.dumps({
            'action': 'new_message',
            'message': event['message']
        }))

    @database_sync_to_async
    def create_message(self, content, user_id):
        usermsg = RoomMessage(room_id=self.room_id, room_user_id=user_id, text=content)
        usermsg.save()
        return usermsg
