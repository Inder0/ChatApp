from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatGroup,Message
from .forms import ChatMessageForm
from django.contrib.auth.models import User
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

# Create your views here.

@login_required
def chat_view(request,chatroom_name='public-chat'):
    group=get_object_or_404(ChatGroup,group_name=chatroom_name)
    chat_messages=group.messages.all()[:30]
    form=ChatMessageForm()
    other_user=None
    if group.is_private:
        if request.user not in group.members.all():
            raise Http404()
        other_user=group.members.exclude(id=request.user.id).first()

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

    return render(request, 'chat/chat.html',{'chat_messages':chat_messages,'form':form,'group':group,'other_user':other_user})

@login_required
def get_or_create_chatroom(request,username):
    if request.user.username==username:
        return redirect('home')
    user=User.objects.get(username=username)
    private_chats=request.user.chat_groups.filter(is_private=True)
    if private_chats.exists():
        for chat in private_chats:
            if user in chat.members.all():
                chat=chat
                break
            else:
                chat=ChatGroup.objects.create(is_private=True)
                chat.members.add(request.user,user)
    else:
        chat=ChatGroup.objects.create(is_private=True)
        chat.members.add(request.user,user)

    return redirect('chatroom',chatroom_name=chat.group_name)

@login_required
def private_chats_menu(request):
    chats=request.user.chat_groups.filter(is_private=True).prefetch_related('members').order_by('-updated_at')
    context = {'chats': chats}
    return render(request, 'chat/partials/private_chat_menu.html', context)

@login_required
def search_private_chats(request):
    query=request.GET.get('q','').lower()
    chats=request.user.chat_groups.filter(is_private=True,).prefetch_related('members').order_by('-updated_at')
    if query:
        filtered_chats=[]
        existing_users=[]
        for chat in chats:
            other_user=chat.members.exclude(id=request.user.id).first()
            if other_user and other_user.id not in existing_users:
                existing_users.append(other_user.id)
                if query in other_user.username.lower() or query in other_user.profile.displayname.lower():
                    filtered_chats.append(chat)
        users=User.objects.filter(username__icontains=query).exclude(id__in=existing_users).exclude(id=request.user.id)[:10]

        chats=filtered_chats
    return render(request,'chat/partials/chat_list_items.html',{'chats':chats,'users':users if users else []})

# @login_required
# def search_private_chats(request):
#     query = request.GET.get('q', '')

#     print("CURRENT USER:", request.user.username)

#     chats = request.user.chat_groups.filter(
#         is_private=True
#     )

#     print("ALL PRIVATE CHATS:", chats.count())

#     for chat in chats:
#         print("CHAT:", chat.group_name)

#         for member in chat.members.all():
#             print("MEMBER:", member.username)

#     return render(
#         request,
#         'chat/partials/chat_list_items.html',
#         {'chats': chats}
#     )