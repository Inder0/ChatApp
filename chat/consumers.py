from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from .models import ChatGroup,Message
from django.template.loader import render_to_string
import json

class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.user=self.scope['user']
        self.room_name=self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom=get_object_or_404(ChatGroup,group_name=self.room_name)
        self.accept()
        
    def receive(self,text_data):
        message=json.loads(text_data)['body']
        message=Message.objects.create(
            group=self.chatroom,
            author=self.user,
            body=message
        )
        html=render_to_string('chat/partials/message.html',{'chat_message':message,'user':self.user},)
        self.send(text_data=f"""
                <ul id="chat_messages" hx-swap-oob="beforeend">
                    {html}
                </ul>
                """)