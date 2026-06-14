from django.shortcuts import render,redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatGroup,Message
from .forms import ChatMessageForm,GroupChatForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from django.contrib.auth.hashers import make_password,check_password
from django.utils import timezone
from datetime import datetime

# Create your views here.

@login_required
def home(request):
    joined_groups=request.user.chat_groups.filter(is_private=False).exclude(group_name='public-chat').order_by('-updated_at')[:5]
    top_groups=ChatGroup.objects.filter(is_private=False).exclude(group_name='public-chat').order_by('-updated_at')[:5]
    return render(request,'chat/home.html',{'joined_groups':joined_groups,'top_groups':top_groups})



@login_required
def chat_view(request,chatroom_name='public-chat'):
    group=get_object_or_404(ChatGroup,group_name=chatroom_name)
    request.session[f'chat_{group.id}_last_seen'] = timezone.now().isoformat()
    if group.is_protected:
        has_access = request.session.get(f'group_access_{group.id}')
        if not has_access:
            return redirect('verify-group-password',chatroom_name=group.group_name)
    chat_messages=group.messages.all()[:30]
    has_more_messages=group.messages.count()>30
    form=ChatMessageForm()
    other_user=None
    group_members=None
    if group.is_private:
        if request.user not in group.members.all():
            raise Http404()
        other_user=group.members.exclude(id=request.user.id).first()
    else:
        if request.user not in group.members.all():
            group.members.add(request.user)
        group_members = group.members.all()

    if request.htmx:
        form=ChatMessageForm(request.POST)
        if form.is_valid():
            message=form.save(commit=False)
            message.group=group
            message.author=request.user
            message.save()
    
            return render(request,'chat/partials/message.html',{'chat_message':message,})

    return render(request, 'chat/chat.html',{'chat_messages':chat_messages,'form':form,'group':group,'other_user':other_user,'group_members':group_members,'has_more_messages':has_more_messages})

@login_required
def get_or_create_chatroom(request,username):
    if request.user.username==username:
        return redirect('home')
    user=get_object_or_404(User,username=username)
    private_chats=request.user.chat_groups.filter(is_private=True)
    for chat in private_chats:
        if user in chat.members.all():
            return redirect('chatroom',chatroom_name=chat.group_name)

    chat=ChatGroup.objects.create(is_private=True)
    chat.members.add(request.user,user)


    return redirect('chatroom',chatroom_name=chat.group_name)

@login_required
def private_chats_menu(request):
    chats=request.user.chat_groups.filter(is_private=True).prefetch_related('members','messages').order_by('-updated_at')
    chat_data=[]
    for chat in chats:
        latest_message=chat.messages.first()
        last_seen=request.session.get(f'chat_{chat.id}_last_seen')
        if last_seen:
            last_seen=datetime.fromisoformat(last_seen)
            has_new_messages=(chat.updated_at>last_seen) and latest_message and latest_message.author!=request.user
        else:
            has_new_messages=latest_message and latest_message.author!=request.user
        chat_data.append({
            'chat':chat,
            'has_new_messages':has_new_messages
        })
    return render(request, 'chat/partials/private_chat_menu.html', {'chat_data':chat_data})

@login_required
def search_private_chats(request):
    query=request.GET.get('q','').lower()
    users=[]
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
    return render(request,'chat/partials/chat_list_items.html',{'chats':chats,'users':users})

@login_required
def create_group_chat(request):
    form=GroupChatForm()
    if request.method=='POST':
        form=GroupChatForm(request.POST)
        if form.is_valid():
            group=form.save(commit=False)
            if group.is_protected:
                group.password=make_password(group.password)
            group.admin=request.user
            group.save()
            group.members.add(request.user)
            return redirect('chatroom',chatroom_name=group.group_name)
    return render(request,'chat/partials/create_group_chat.html',{'form':form})

@login_required
def search_group_chat(request):
    q=request.GET.get('q','').lower()
    groups=ChatGroup.objects.filter(is_private=False).exclude(group_name='public-chat').order_by('-updated_at')
    if q:
        groups=groups.filter(title__icontains=q)
    return render(request,'chat/partials/group_search_results.html',{'groups':groups})

@login_required
def leave_group(request,chatroom_name):
    group=get_object_or_404(ChatGroup,group_name=chatroom_name)
    if group.group_name == 'public-chat':
        return redirect('home')
    if group.is_private:
        return redirect('home')
    if request.user==group.admin:
        group.delete()
        return redirect('home')
    
    group.members.remove(request.user)
    return redirect('home')

@login_required
def verify_password(request,chatroom_name):
    group=get_object_or_404(ChatGroup,group_name=chatroom_name)
    if not group.is_protected:
        return redirect('chatroom',chatroom_name=group.group_name)
    if request.method=='POST':
        password=request.POST.get('password')
        if check_password(password,group.password):
            request.session[f'group_access_{group.id}']=True
            return redirect('chatroom',chatroom_name=group.group_name)
        else:
            messages.error(request,'Incorrect Password')
            return redirect('verify-group-password',chatroom_name=group.group_name)
    return render(request,'chat/partials/verify_password.html',{'group':group})

@login_required
def load_messages(request,chatroom_name):
    group=get_object_or_404(ChatGroup,group_name=chatroom_name)
    offset=int(request.GET.get('offset',30))
    messages=group.messages.all()[offset:offset+30]
    return render(request,'chat/partials/load_messages.html',{'messages':messages,'offset':offset,'next_offset':offset+30,'group':group})


