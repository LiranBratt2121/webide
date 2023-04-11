import json
import subprocess

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'test'

        async_to_sync(self.channel_layer.group_add)(
        self.room_group_name,
        self.channel_name
        )        
        
        self.accept()
        
        
    def receive(self, text_data):

        text_data_json = json.loads(text_data)
            
        if 'message' in text_data_json:
            message = text_data_json['message']
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type':'chat_message',
                    'message': message
                }
            )
        elif 'content' in text_data_json:
            input_string = text_data_json['content']
            process = subprocess.Popen(['python', '-c', input_string], stdout=subprocess.PIPE)
            output, error = process.communicate()
            output = output.decode()
            self.send(text_data=json.dumps({
                'type': 'input_response',
                'message': output
            }))

            
    
    def chat_message(self, event):
        message = event['message']
        
        self.send(text_data=json.dumps({
            'type': 'chat',
            'message': message            
        }))

