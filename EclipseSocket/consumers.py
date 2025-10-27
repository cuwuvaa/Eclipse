from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from EclipseServers import models
from EclipseUser.serializer import EclipseUserSerializer
from EclipseServers.serializer import ServerMessageSerializer
from collections import defaultdict
import json
# from .redis import redis_service
# import logging


connected_users = defaultdict()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.server_id = self.scope['url_route']['kwargs']['server_id']
        self.user = EclipseUserSerializer(self.scope['user']).data
        self.group_name = f'server_{self.server_id}'
        print(f"{self.user['username']} connected")
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'channel_name': self.channel_name
        }))

    async def disconnect(self, close_code):
        if self.user["id"] in connected_users:
            del connected_users[self.user["id"]]
            await self.channel_layer.group_send(self.group_name, {
                "type": "user_disconnect",
                "type_action": "user_disconnect",
                "userid": self.user["id"]
            })

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        message = data.get('message', {})
        user_id = str(self.user["id"])

        try:
            server_users = connected_users
            print("server_users: ", server_users)
            print("connected_users: ", connected_users)
        except:
            print("no one connected, server_users array is empty")

        if action == "start_voice":
            connected_users[user_id] = self.channel_name
            print(connected_users)
            await self.channel_layer.group_send(self.group_name, {
                "type": "send_background",
                "userid": user_id,
                "sender_channel": self.channel_name
            })

        elif action == "offer":
            connected_users[user_id] = self.channel_name
            print(connected_users)
            destination_id = message.get("to")
            destination_channel = connected_users[str(destination_id)]

            if destination_channel:
                await self.channel_layer.send(destination_channel, {
                    "type": "send_sdp",
                    "type_action": "new_offer",
                    "sdp": message.get('sdp'),
                    "userid": user_id
                })
            
            await self.channel_layer.group_send(self.group_name, {
                "type": "send_background",
                "userid": user_id,
                "sender_channel": self.channel_name
            })

        elif action == "answer":
            destination_id = message.get("to")
            destination_channel = connected_users[str(destination_id)]
            if destination_channel:
                await self.channel_layer.send(destination_channel, {
                    "type": "send_sdp",
                    "type_action": "new_answer",
                    "sdp": message.get('sdp'),
                    "userid": user_id
                })

        elif action == "ice":
            destination_id = message.get("to")
            destination_channel = connected_users[str(destination_id)]
            if destination_channel:
                await self.channel_layer.send(destination_channel, {
                    "type": "send_ice",
                    "ice": message.get("candidate"),
                    "userid": user_id
                })

        elif action == "render":
            try: #если голосовой канал пуст
                users = {uid: chan for uid, chan in connected_users.items() if uid != user_id}
            except:
                users = {}
            await self.send(text_data=json.dumps({
                "action": "listusers",
                "users": users,
            }))

        elif action == "disconnect_voice":
            if user_id in connected_users:
                del connected_users[user_id]
            
            await self.channel_layer.group_send(self.group_name, {
                "type": "user_disconnect",
                "type_action": "user_disconnect",
                "userid": user_id,
                "sender_channel": self.channel_name
            })
        elif action == "user_message":
            print("new msg")
            usermsg = await self.create_message(message, user_id)
            await self.channel_layer.group_send(self.group_name, {
                "type": "user_message",
                "action":"new_message",
                "message":ServerMessageSerializer(usermsg).data
            })


    @database_sync_to_async
    def create_message(self, content, user_id):
        server = models.Server.objects.get(id=self.server_id)
        sender = models.ServerMember.objects.get(user__id=user_id, server__id=self.server_id)
        usermsg = models.ServerMessage.objects.create(server=server, sender=sender, content=content)
        usermsg.save()
        print(usermsg)
        print(sender.user.avatar)
        return usermsg

    async def user_message(self,event):
        await self.send(json.dumps({
            "action": event["action"],
            "usermsg":event["message"]
        }))

    async def user_disconnect(self, event):
        # Send disconnect message to clients in the group
        if self.channel_name != event.get("sender_channel"):
             await self.send(json.dumps({
                "action": event["type_action"],
                "userid": event["userid"]
            }))

    async def send_sdp(self, event):
        await self.send(json.dumps({
            "action": event["type_action"],
            "sdp": event["sdp"],
            "userid": event["userid"]
        }))

    async def send_background(self, event):
        # уведомить всех о новом юзере
        if self.channel_name != event.get("sender_channel"):
            await self.send(json.dumps({
                "action": "background",
                "task": "connection",
                "userid": event["userid"]
            }))

    async def send_ice(self, event):
        await self.send(json.dumps({
            "action": "ice",
            "ice": event["ice"],
            "userid": event["userid"]
        }))