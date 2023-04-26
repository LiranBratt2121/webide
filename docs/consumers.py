import json
import subprocess
import threading

from channels.generic.websocket import AsyncWebsocketConsumer


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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if 'message' in text_data_json:
            message = text_data_json['message']
            await self.send_chat_message(message)
        elif 'content' in text_data_json:
            content = text_data_json['content']
            if len(content) > 100000:
                await self.send_input_response_message('Error: Message is too long.')
                return
            if self.process and self.process.poll() is None:
                await self.send_input_response_message('Code is already running. Please wait for it to finish before submitting new code.')
            else:
                try:
                    compile(content, '<string>', 'exec')
                except SyntaxError:
                    await self.send_input_response_message('Error: Invalid Python code.')
                    return
                self.output = ''  # clear the output before sending new input
                await self.run_code(content)
        elif 'input_response' in text_data_json:
            input_response = text_data_json['input_response']
            await self.send_input_response_message(input_response)
        elif 'clear' in text_data_json:
            self.output = ''
            await self.send_input_response_message('')
        elif 'stop' in text_data_json:
            if self.thread and self.thread.is_alive():
                self.process.terminate()
                self.process = None
                await self.send_input_response_message('Process stopped by user.')
                self.thread.join()
                self.thread = None
                self.output = ''

    async def run_code(self, content):
        self.send_input_response_message('bro code;')
        # self.thread = threading.Thread(target=self._run_code_thread, args=(content,))
        # self.thread.start()

    def _run_code_thread(self, content):
        self.process = subprocess.Popen(['python', '-c', content], stdout=subprocess.PIPE)
        for line in iter(self.process.stdout.readline, b''):
            self.output += line.decode()
            if len(self.output) > 100000:
                self.send_input_response_message('Error: Output is too long.')
                self.process.terminate()
                self.process = None
                self.thread = None
                self.send_input_response_message('Process killed due to excessive output.')
                self.output = ''
                return
            self.send_input_response_message(self.output)

        self.thread = None

        if (self.process):
            self.process.stdout.close()
            self.process.wait()
            self.process = None

    async def send_chat_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def send_input_response_message(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'input_response',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))


    async def send_input_response_message(self, input_response):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'input_response_message',
                'message': input_response
            }
        )
        
        
    async def input_response(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'type': 'input_response',
            'message': message
        }))


    async def input_response_message(self, event):
        input_response = event['message'] 
        await self.send(text_data=json.dumps({
            'type': 'input_response',
            'message': input_response 
        }))
