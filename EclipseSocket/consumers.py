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

        voice_users = await self.get_online_users()
        await self.send(json.dumps({'type':'render','message':f'Successfully connected! Group: {self.group_name}', "users_connected_voice":voice_users}))

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.send(json.dumps({'message':f'Successfully disconnected from group: {self.group_name}'}))
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        action = text_data_json['action']
        if (action == "send_chatmsg"):
            await self.handle_chat_message(text_data_json["message"])
        elif (action == "voice_connect"):
            await self.handle_voice_connection(text_data_json["message"])
        elif (action == "voice_disconnect"):
            await self.handle_voice_disconnection(text_data_json["message"])
    
    async def handle_chat_message(self, message_content):
        message, sender_username, sender_id, sender = await self.create_message_async(message_content)
        
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'id': message.id,
                'content': message.content,
                'sender': sender_username,
                'avatar_url': sender.avatar.url,
                'sender_id': sender_id,
                'timestamp': message.timestamp.isoformat()
            }
        )

    @database_sync_to_async
    def serialize_user(self, user, server_id):
        server = models.Server.objects.get(id=server_id)
        connected_user = models.ServerMember.objects.select_related('user').get(user=user, server=server)
        return connected_user.user

    async def handle_voice_connection(self,event):
        connected_user = await self.serialize_user(self.scope['user'], server_id=self.server_id)
        print(f"{connected_user} connected to group: {self.group_name}")
        await self.channel_layer.group_send(self.group_name,
            {
            'type': 'voice_connection',
            'user': connected_user.username,
            'avatar_url': connected_user.avatar.url,
            'user_id': connected_user.id,
            })

    async def handle_voice_disconnection(self,event):
        disconnected_user = await self.serialize_user(self.scope['user'], server_id=self.server_id)
        print(f"{disconnected_user} disconnected from group: {self.group_name}")
        await self.channel_layer.group_send(self.group_name,
            {
            'type': 'voice_disconnection',
            'user': disconnected_user.username,
            'avatar_url': disconnected_user.avatar.url,
            'user_id': disconnected_user.id,
            })

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
    
    async def voice_connection(self,event):
        await self.send(text_data=json.dumps({
            'type': 'voice_connection',
            'user': event['user'],
            'avatar_url': event['avatar_url'],
            'user_id': event['user_id'],
        }))

    async def voice_disconnection(self,event):
        await self.send(text_data=json.dumps({
            'type': 'voice_disconnection',
            'user': event['user'],
            'avatar_url': event['avatar_url'],
            'user_id': event['user_id'],
        }))
    
    @database_sync_to_async
    def get_online_users(self):
        server = models.Server.objects.get(id=self.server_id)
        online_members = models.ServerMember.objects.filter(server=server, user__is_online=True).select_related('user')
        return [{"username": member.user.username, "id": member.user.id, "avatar_url": member.user.avatar.url} for member in online_members]

class VoiceChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.server_id = self.scope['url_route']['kwargs']['server_id']
        self.group_name = f'voicechat_{self.server_id}'

        # Вступаем в группу канала
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        await self.set_online_status(True)

        connected_user = await ChatConsumer.serialize_user(self.scope['user'], server_id=self.server_id)
        print(f"{connected_user} connected to voicegroup: {self.group_name}")

        await self.send(json.dumps({'message':f'Successfully connected to voicechat! Group: {self.group_name}'}))
        print(f"{self.scope['user']} status = {self.scope['user'].is_online}")

    async def disconnect(self, close_code):
        # Покидаем группу
        await self.send(json.dumps({'message':f'Successfully disconnected from voicechat! Group: {self.group_name}'}))
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        await self.set_online_status(False)
        print(f"{self.scope['user']} status = {self.scope['user'].is_online}")

    @database_sync_to_async
    def set_online_status(self, status):
        user = self.scope['user']
        user.is_online = status
        user.save()