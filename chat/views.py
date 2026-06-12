from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatGroup,Message
from .forms import ChatMessageForm
# Create your views here.

@login_required
def chat_view(request):
    group=get_object_or_404(ChatGroup,group_name='public-chat')
    chat_messages=group.messages.all()[:30]
    form=ChatMessageForm()
    if request.htmx:
        form=ChatMessageForm(request.POST)
        if form.is_valid():
            message=form.save(commit=False)
            message.group=group
            message.author=request.user
            message.save()
            context={
                'message':message,
                'user':request.user
            }
            return render(request,'chat/partials/message.html',{'chat_message':message})

    return render(request, 'chat/chat.html',{'chat_messages':chat_messages,'form':form,'group':group})

