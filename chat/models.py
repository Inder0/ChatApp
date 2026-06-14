from django.db import models
from django.contrib.auth.models import User
import shortuuid

# Create your models here.

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=255,unique=True,default=shortuuid.uuid)
    created_at = models.DateTimeField(auto_now_add=True)
    users_online=models.ManyToManyField(User,related_name='online_in_groups',blank=True)
    members=models.ManyToManyField(User,related_name='chat_groups',blank=True)
    is_private=models.BooleanField(default=False)
    updated_at=models.DateTimeField(auto_now=True)
    title=models.CharField(max_length=100,blank=True,null=True)
    admin=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name='owned_groups')
    is_protected=models.BooleanField(default=False)
    password=models.CharField(max_length=255,blank=True)

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
                           
    
