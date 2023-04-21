import json
import subprocess
import threading

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'
        self.process = None
        self.thread = None
        self.output = ''
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        
        self.accept()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if 'message' in text_data_json:
            message = text_data_json['message']
            self.send_chat_message(message)
        elif 'content' in text_data_json:
            content = text_data_json['content']
            if self.process and self.process.poll() is None:
                self.send_input_response('Code is already running. Please wait for it to finish before submitting new code.')
            else:
                self.run_code(content)
        elif 'input_response' in text_data_json:
            input_response = text_data_json['input_response']
            self.send_input_response_message(input_response)

    def run_code(self, content):
        self.process = subprocess.Popen(['python', '-c', content], stdout=subprocess.PIPE)
        self.thread = threading.Thread(target=self._output_reader)
        self.thread.start()
        

    def _output_reader(self):
        for line in iter(self.process.stdout.readline, b''):
            self.output += line.decode()
            self.send_input_response_message(self.output)

        self.process.stdout.close()
        self.process.wait()
        self.process = None

    def send_chat_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message
        }))

    def send_input_response(self, message):
        self.send(text_data=json.dumps({
            'type': 'input_response',
            'message': message
        }))

    def send_input_response_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'input_response_message',
                'message': message
            }
        )

    def input_response_message(self, event):
        message = event['message']
        self.send_input_response(message)

    def disconnect(self, close_code):
        if self.process and self.process.poll() is None:
            self.process.kill()
        if self.thread and self.thread.is_alive():
            self.thread.join()
            
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
