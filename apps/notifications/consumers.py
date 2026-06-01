from channels.generic.websocket import AsyncJsonWebsocketConsumer


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        return

    async def receive_json(self, content, **kwargs):
        await self.send_json({"status": "received", "payload": content})