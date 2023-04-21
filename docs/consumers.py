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
            if len(content) > 10000:
                self.send_input_response_message('Error: Message is too long.')
                return
            if self.process and self.process.poll() is None:
                self.send_input_response_message('Code is already running. Please wait for it to finish before submitting new code.')
            else:
                try:
                    compile(content, '<string>', 'exec')
                except SyntaxError:
                    self.send_input_response_message('Error: Invalid Python code.')
                    return
                self.output = ''  # clear the output before sending new input
                self.run_code(content)
        elif 'input_response' in text_data_json:
            input_response = text_data_json['input_response']
            self.send_input_response_message(input_response)
        elif 'clear' in text_data_json:
            self.output = ''
            self.send_input_response_message('')
        elif 'stop' in text_data_json:
            if self.process and self.process.poll() is None:
                self.process.kill()
                self.process = None
                self.send_input_response_message('Process stopped by user.')
                self.thread.join()  
                self.thread = None
                self.output = ''


    def run_code(self, content):
        self.process = subprocess.Popen(['python', '-c', content], stdout=subprocess.PIPE)
        self.thread = threading.Thread(target=self._output_reader)
        self.thread.start()

    def _output_reader(self):
        for line in iter(self.process.stdout.readline, b''):
            self.output += line.decode()
            if len(self.output) > 10000:
                self.send_input_response_message('Error: Output is too long.')
                self.process.kill()
                self.process = None
                self.send_input_response_message('Process killed due to excessive output.')
                self.thread.join()  # Join the thread from a different thread
                self.thread = None
                self.output = ''
                return
            self.send_input_response_message(self.output)
            
        self.thread = None

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

    def send_input_response_message(self, message):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'input_response',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
        }))

    def input_response(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'type': 'input_response',
            'message': message
        }))
        
    def send_input_response_message(self, input_response):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'input_response_message',
                'message': input_response
            }
        )

    def input_response_message(self, event):
        input_response = event['message'] 
        self.send(text_data=json.dumps({
            'type': 'input_response',
            'message': input_response 
        }))

