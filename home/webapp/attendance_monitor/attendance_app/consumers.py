import json
from channels.generic.websocket import AsyncWebsocketConsumer

class AttendanceConsumer(AsyncWebsocketConsumer):
    group_name = 'attendance_updates'

    async def connect(self):
        # Join group
        await self.channel_layer.group_add(
            'attendance_updates',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            'attendance_updates',
            self.channel_name
        )

    # Receive message from group
    async def attendance_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message']))
