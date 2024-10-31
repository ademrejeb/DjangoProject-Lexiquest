from django.shortcuts import render, redirect
from chat.models import Room, Message
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

def home2(request):
    # Récupérer tous les salons existants
    rooms = Room.objects.all()
    return render(request, 'chat/home.html', {'rooms': rooms})


def home(request):
    # Récupérer tous les salons existants
    rooms = Room.objects.all()
    return render(request, 'chat/home.html', {'rooms': rooms})

def room(request, room):
    username = request.GET.get('username')
    room_details = Room.objects.get(name=room)
    return render(request, 'chat/room.html', {
        'username': username,
        'room': room,
        'room_details': room_details
    })

def checkview(request):
    room = request.POST['room_name']
    
    username = request.user.username
    if Room.objects.filter(name=room).exists():
        return redirect('/chat/'+room+'/?username='+username)
    else:
        new_room = Room.objects.create(name=room)
        new_room.save()
        return redirect('/chat/'+room+'/?username='+username)

def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']

    new_message = Message.objects.create(value=message, user=username, room=room_id)
    new_message.save()
    return HttpResponse('Message sent successfully')

def getMessages(request, room):
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages":list(messages.values())})

@csrf_exempt
def delete_message(request, message_id):
    username = request.POST.get('username')
    try:
        message = Message.objects.get(id=message_id, user=username)
        message.delete()
        return JsonResponse({'status': 'success'})
    except Message.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Message not found or you do not have permission to delete this message'})

@csrf_exempt
def update_message(request, message_id):
    if request.method == 'POST':
        new_value = request.POST.get('new_value')
        username = request.POST.get('username')
        try:
            message = Message.objects.get(id=message_id, user=username)
            message.value = new_value
            message.save()
            return JsonResponse({'status': 'success'})
        except Message.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Message not found or you do not have permission to edit this message'})