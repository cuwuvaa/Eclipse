from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from EclipseServers import models
from EclipseUser.serializer import EclipseUserSerializer
from collections import defaultdict
import json


connected_users = dict()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.server_id = self.scope['url_route']['kwargs']['server_id']
        self.user = EclipseUserSerializer(self.scope['user']).data
        self.group_name = f'server_{self.server_id}'

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        print(connected_users)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'channel_name': self.channel_name
        }))

    async def disconnect(self,close_code):
        if self.channel_name in connected_users.keys():
            del connected_users[self.user["id"]]
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if (data['action'] == "start_voice"):
            connected_users[self.user["id"]] = self.channel_name
            print(f"user {connected_users[self.user["id"]]} started voice call")
            await self.channel_layer.group_send(self.group_name,{
                "type":"send_background",
                "userid":self.user["id"]
            })

        if (data['action'] == "offer"):
            connected_users[int(self.user["id"])] = str(self.channel_name)
            print("connected users: ", connected_users)
            print(f"user {self.user["id"]} connected voice call")
            destination = int(data["message"]["to"])
            print(f"sending offer to user ID:{destination} CHANNEL:{connected_users.get(destination)}")
            destination_channel = connected_users.get(destination)
            if destination_channel:
                await self.channel_layer.send(destination_channel,{
                    "type":"send_sdp",
                    "type_action":"new_offer",
                    "sdp":data['message']['sdp'],
                    "userid":self.user["id"]
                })
            else:
                print(f"Error: Destination user {destination} not found.")
            
            await self.channel_layer.group_send(self.group_name,{
                "type":"send_background",
                "userid":self.user["id"]
            })
        if (data['action'] == "answer"):
            destination = data["message"]["to"]
            print("sending answer to ", destination)
            await self.channel_layer.send(connected_users.get(destination),{
                "type":"send_sdp",
                "type_action":"new_answer",
                "sdp":data['message']['sdp'],
                "userid":self.user["id"]
            })
        if (data['action'] == "ice"):
            try:
                destination = int(data["message"]["to"])
                print(f"sending ICE to user ID:{destination} CHANNEL:{connected_users.get(destination)}")
                destination_channel = connected_users.get(destination)
                await self.channel_layer.send(destination_channel,{
                    "type":"send_ice",
                    "ice":data["message"]["candidate"],
                    "userid":self.user["id"]
                })
            except:
                print("skip sending...")
        if (data['action'] == "render"):
            await self.send(text_data=json.dumps({"action":"listusers", "users":connected_users}))
        
        if (data['action'] == "disconnect_voice"):
            print(f"user {self.user["id"]} disconnecting")
            connected_users.pop(int(self.user["id"]))
            print(connected_users)

            print("-----sending data to group-------")
            await self.channel_layer.group_send(self.group_name,{
                "type":"user_disconnect",
                "type_action":"user_disconnect",
                "userid":self.user["id"]
            })

    async def user_disconnect(self,event):
        if self.channel_name in connected_users.values():
            await self.send(json.dumps({
                "action":event["type_action"],
                "userid":event["userid"]
            }))
        elif not(self.channel_name in connected_users.values()) and self.channel_name != connected_users.get(event["userid"]):
            await self.send(json.dumps({
                "action":"background",
                "task":"disconnection",
                "userid":event["userid"]
            }))    

    async def send_sdp(self,event):
        if self.channel_name != connected_users.get(event["userid"]) and self.channel_name in connected_users.values():
            await self.send(json.dumps({
                "action":event["type_action"],
                "sdp":event["sdp"],
                "userid":event["userid"]
            }))


    async def send_background(self,event):
        await self.send(json.dumps({
                "action":"background",
                "task":"connection",
                "userid":event["userid"]
            }))   

    async def send_ice(self,event):
        if self.channel_name != connected_users.get(event["userid"]) and self.channel_name in connected_users.values():
            await self.send(json.dumps({
                "action":"ice",
                "ice":event["ice"],
                "userid":event["userid"]
            }))

