import asyncio
import json
import subprocess
from django.core.exceptions import ObjectDoesNotExist
from .models import Room
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = 'chat_%s' % self.slug
        self.process = None
        self.thread = None
        self.output = ''

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Update the textarea content when a user joins the room
        await self.update_textarea_content()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def update_textarea_content(self):
        room = await sync_to_async(Room.objects.get)(slug=self.slug)
        content = room.content
        
        await self.send(text_data=json.dumps({
            'type': 'update_textarea',
            'content': content
        }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if 'message' in text_data_json:
            message = text_data_json['message']
            await self.send_chat_message(message)
            
            try:            
                room = await sync_to_async(Room.objects.get)(slug=self.slug)
                room.content = message
                await sync_to_async(room.save)()
            except ObjectDoesNotExist:
                pass
            
        elif 'content' in text_data_json:
            print('In content')
            content = text_data_json['content']
            if len(content) > 100000:
                await self.group_send_input_response_message('Error: Message is too long.')
                return
            try:
                room = await sync_to_async(Room.objects.get)(slug=self.slug)
                room.content = content
                await sync_to_async(room.save)()
            except ObjectDoesNotExist:
                pass

            if self.process and self.process.poll() is None:
                await self.group_send_input_response_message('Code is already running. Please wait for it to finish before submitting new code.')
            else:
                try:
                    compile(content, '<string>', 'exec')
                except SyntaxError:
                    await self.group_send_input_response_message('Error: Invalid Python code.')
                    return
                self.output = ''  # clear the output before sending new input
                await self.run_code(content)
        elif 'input_response' in text_data_json:
            input_response = text_data_json['input_response']
            await self.group_send_input_response_message(input_response)
        elif 'clear' in text_data_json:
            self.output = ''
            await self.group_send_input_response_message('')
        elif 'stop' in text_data_json:
            if self.thread and self.thread.is_alive():
                self.process.terminate()
            await self.group_send_input_response_message('Process stopped by user.')

    async def _run_code_thread(self, content):
        print('In Run code Thread!')
        self.process = subprocess.Popen(['python', '-c', content], stdout=subprocess.PIPE)
        for line in iter(self.process.stdout.readline, b''):
            self.output += line.decode()
            if len(self.output) > 100000:
                self.group_send_input_response_message('Error: Output is too long.')
                self.process.terminate()
                self.process = None
                self.thread = None
                self.group_send_input_response_message('Process killed due to excessive output.')
                self.output = ''
                return
            await self.group_send_input_response_message(self.output)

        self.thread = None

        if self.process:
            self.process.stdout.close()
            self.process.wait()
            self.process = None

    async def run_code(self, content):
        print('Tried Running code')
        coro = self._run_code_thread(content)
        print('Started Thread')
        await asyncio.create_task(coro)

    # Update terminal functions
    async def input_response_message(self, event):
        input_response = event

        await self.send(text_data=json.dumps({
            'type': 'update_terminal',
            'message': input_response
        }))

    async def group_send_input_response_message(self, message):
        event = message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'input_response_message',
                'message': event
            }
        )

    # Update text-area functions
    async def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    async def send_chat_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
