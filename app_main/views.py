import os

from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import models
from .models import TextToAudio


def index(request):
    if request.method == 'POST':

        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to upload an audio file.')
            return redirect('index')

        text_id = request.POST.get('id')
        audio = request.FILES.get('audio')
        duration = request.POST.get('duration')

        text = TextToAudio.objects.filter(id=text_id).first()
        if not text:
            return JsonResponse({'error': 'Text not found.'}, status=404)
        if not audio:
            return JsonResponse({'error': 'Audio file not found.'}, status=400)

        audio_extension = os.path.splitext(audio.name)[1]
        new_audio_name = f"audios/{text_id}{audio_extension}"
        new_audio_path = default_storage.save(new_audio_name, ContentFile(audio.read()))

        text.audio.name = new_audio_path
        text.duration = duration
        text.is_converted = True
        text.user = request.user
        text.save()

        messages.success(request, 'Audio file uploaded successfully.')
        return redirect('index')

    text = TextToAudio.objects.filter(is_converted=False, is_error=False).order_by('?').first()
    return render(request, 'index.html', {'text': text})


def upload_data(request):
    if request.method == "POST":
        if not request.user.is_superuser:
            messages.error(request, 'You are not authorized to access this page.')
            return redirect('index')
        uploaded_file = request.FILES.get('text_file')

        if not uploaded_file:
            messages.error(request, 'No file was uploaded.')
            return redirect('upload_data')

        try:
            lines = uploaded_file.read().decode('utf-8').splitlines()

            instances = []
            for line in lines:
                if line.strip():
                    instance = TextToAudio(
                        text=line.strip(),
                        char_count=len(line.strip()),
                    )
                    instances.append(instance)

            TextToAudio.objects.bulk_create(instances)
            messages.success(request, 'File uploaded successfully.')
            return redirect('upload_data')

        except UnicodeDecodeError:
            messages.error(request, 'File encoding not supported. Please upload a UTF-8 encoded file.')
            return redirect('upload_data')
        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {e}')
            return redirect('upload_data')
    if not request.user.is_superuser:
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('index')
    return render(request, 'upload_data.html')


def statistics(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You must be logged in to view statistics.')
        return redirect('index')

    total_texts = TextToAudio.objects.count()
    converted_texts = TextToAudio.objects.filter(is_converted=True).count()
    user_converted_texts = TextToAudio.objects.filter(is_converted=True, user=request.user).count()
    total_duration = \
        TextToAudio.objects.filter(is_converted=True, user=request.user).aggregate(total_duration=Sum('duration'))[
            'total_duration']
    total_duration = total_duration or 0

    user_rankings = (
        User.objects.annotate(
            total_converted_texts=Count('texttoaudio', filter=models.Q(texttoaudio__is_converted=True)),
            total_duration=Sum('texttoaudio__duration', filter=models.Q(texttoaudio__is_converted=True))
        )
        .filter(total_duration__isnull=False)
        .order_by('-total_duration')
    )

    rankings = [
        {
            'username': user.username,
            'total_converted_texts': user.total_converted_texts or 0,
            'total_duration': user.total_duration or 0,
        }
        for user in user_rankings
    ]

    return render(request, 'statictis.html', {
        'total_texts': total_texts,
        'converted_texts': converted_texts,
        'user_converted_texts': user_converted_texts,
        'total_duration': total_duration,
        'rankings': rankings,
    })


def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect("index")
        messages.info(request, 'Invalid Username/Password')
        return redirect('login')

    return render(request, 'login.html')


def logout(request):
    auth_logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('index')


def register(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')
        user = User.objects.create_user(username=username, password=password)
        auth_login(request, user)
        messages.success(request, 'You have successfully registered and logged in.')
        return redirect("index")
    return render(request, 'register.html')
