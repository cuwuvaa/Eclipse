import json
import asyncio
from channels.layers import get_channel_layer
from django.conf import settings
import redis.asyncio as redis

#todo: использовать редис для хранения сессий и звонков

class CallRedisService:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=0,
            decode_responses=True
        )
    

    async def create_room(self, room_id):
        room_key = f"room:{room_id}"
        room_data = {
            'id': room_id,
        }
        await self.redis.hset(room_key, mapping=room_data)
        await self.redis.expire(room_key, 3600*24)  #1 час * 24
        return room_data
    
    async def get_room(self, room_id):
        room_key = f"room:{room_id}"
        room_data = await self.redis.hgetall(room_key)
        return room_data if room_data else None
    
    async def delete_room(self, room_id):
        room_key = f"room:{room_id}"
        participants = await self.get_room_participants(room_id)
        await self.redis.delete(room_key)

        for participant in participants:
            await self.remove_participant(room_id, participant['user_id'])
        
        return participants
    

    async def add_participant(self, room_id, user_id, channel_name=None):
        room_key = f"room:{room_id}"
        participant_key = f"participant:{room_id}:{user_id}"
        
        if not await self.redis.exists(room_key):
            await self.create_room(room_id)
        
        participant_data = {
            'user_id': user_id,
            'channel_name': channel_name
        }
        
        # сохранение участника
        await self.redis.hset(participant_key, mapping=participant_data)
        await self.redis.expire(participant_key, 3600*24)
        
        # добавление в список участников комнаты
        await self.redis.sadd(f"room_participants:{room_id}", user_id)
        
        return participant_data
    
    async def remove_participant(self, room_id, user_id):
        participant_key = f"participant:{room_id}:{user_id}"
        
        # удаление из списка участников
        await self.redis.srem(f"room_participants:{room_id}", user_id)
        
        # удаление данных участника
        await self.redis.delete(participant_key)
        
        # пустая ли комната?
        participant_count = await self.get_room_participant_count(room_id)
        if participant_count == 0:
            await self.delete_room(room_id)
    
    async def get_room_participant_count(self, room_id):
        return await self.redis.scard(f"room_participants:{room_id}")

    async def get_room_participants(self, room_id):
        participant_ids = await self.redis.smembers(f"room_participants:{room_id}")
        participants = []
        
        for user_id in participant_ids:
            participant_key = f"participant:{room_id}:{user_id}"
            participant_data = await self.redis.hgetall(participant_key)
            if participant_data:
                participants.append(participant_data)
        
        return participants
    

redis_service = CallRedisService()