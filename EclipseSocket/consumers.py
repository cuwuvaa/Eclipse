from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from EclipseServers import models
from collections import defaultdict
import json


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.server_id = self.scope['url_route']['kwargs']['server_id']
        self.group_name = f'chat_{self.server_id}'

        # Вступаем в группу канала
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()


    async def disconnect(self, close_code):
        # Покидаем группу
        await self.send(json.dumps({'message':f'Successfully disconnected from group: {self.group_name}'}))
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        action = text_data_json['action']
        if (action == "send_chatmsg"):
            await self.handle_chat_message(text_data_json["message"])

        if ((action == 'new-offer') or (action == 'new-answer')):
            receiver_channel_name = text_data_json['message']['receiver_channel_name']
            text_data_json['message']['receiver_channel_name'] == self.channel_name
            await self.channel_layer.send(receiver_channel_name,{
                'type':'send.sdp',
                'peer_data':text_data_json
            })

        if (action == "new-peer"):
            text_data_json['message']['receiver_channel_name'] = self.channel_name
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type':'send.sdp',
                    'peer_data':text_data_json
                }
            )

    async def send_sdp(self, event):
        await self.send(text_data=json.dumps(event['peer_data']))

    @database_sync_to_async
    def serialize_user(self, user, server_id):
        server = models.Server.objects.get(id=server_id)
        connected_user = models.ServerMember.objects.select_related('user').get(user=user, server=server)
        return connected_user.user

    @database_sync_to_async
    def create_message_async(self, content):
        server = models.Server.objects.get(id=self.server_id)
        server_member = models.ServerMember.objects.select_related('user').get(user=self.scope['user'], server=server)
        message = models.ServerMessage.objects.create(
            server=server,
            sender=server_member,
            content=content
        )
        return message, server_member.user.username, server_member.user.id, server_member.user
    
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'id': event['id'],
            'content': event['content'],
            'sender': event['sender'],
            'avatar_url': event['avatar_url'],
            'sender_id': event['sender_id'],
            'timestamp': event['timestamp']
        }))

    async def handle_chat_message(self, message_content):
        message, sender_username, sender_id, sender = await self.create_message_async(message_content)
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'action': 'chat_message',
                'id': message.id,
                'content': message.content,
                'sender': sender_username,
                'avatar_url': sender.avatar.url,
                'sender_id': sender_id,
                'timestamp': message.timestamp.isoformat()
            }
        )

class VoiceChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = f'chat_test'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        action = text_data_json['action']
        if ((action == 'new-offer') or (action == 'new-answer')):
            receiver_channel_name = text_data_json['message']['receiver_channel_name']
            text_data_json['message']['receiver_channel_name'] == self.channel_name
            await self.channel_layer.send(receiver_channel_name,{
                'type':'send.sdp',
                'peer_data':text_data_json
            })


        text_data_json['message']['receiver_channel_name'] = self.channel_name
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type':'send.sdp',
                'peer_data':text_data_json
            }
        )
    async def send_sdp(self, event):
        await self.send(text_data=json.dumps(event['peer_data']))