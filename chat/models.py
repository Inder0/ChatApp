from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=255,unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.group_name
    
class Message(models.Model):
    group = models.ForeignKey(ChatGroup,on_delete=models.CASCADE,related_name='messages')
    author=models.ForeignKey(User,on_delete=models.CASCADE,related_name='messages')
    body=models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} : {self.body}'
    
    class Meta:
        ordering = ('-created_at',)
                           
    
