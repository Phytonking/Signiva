from django.http import FileResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.contrib.auth.decorators import login_required
from .models import Document
from django.shortcuts import render, redirect
from .forms import DocumentForm
import uuid

# Index View
@login_required(login_url='/login')
def index(request):
    return render(request, 'index.html')

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Register View
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required(login_url='/login')
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.id = uuid.uuid4()
            document.user = request.user
            document.save()
            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'upload_document.html', {'form': form})

@login_required(login_url='/login')
def document_list(request):
    documents = Document.objects.filter(user=request.user)
    return render(request, 'document_list.html', {'documents': documents})

@login_required(login_url='/login')
def view_document(request, document_id):
    document = Document.objects.get(id=document_id, user=request.user)
    return render(request, 'view_document.html', {'document': document})

@login_required(login_url='/login')
def edit_document(request, document_id):
    document = Document.objects.get(id=document_id, user=request.user)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return redirect('document_list')
    else:
        form = DocumentForm(instance=document)
    return render(request, 'edit_document.html', {'form': form})

@login_required(login_url='/login')
def delete_document(request, document_id):
    document = Document.objects.get(id=document_id, user=request.user)
    if request.method == 'POST':
        document.delete()
        return redirect('document_list')
    return render(request, 'delete_document.html', {'document': document})


@login_required(login_url='/login')
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'profile.html', context)


@login_required(login_url='/login')
def dashboard(request):
    # Fetch the latest documents uploaded by the user
    documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
    
    # Fetch other relevant data
    # Count of documents uploaded by the user
    document_count = Document.objects.filter(user=request.user).count()

    context = {
        'documents': documents,
        'document_count': document_count,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='/login')
def download_document(request, document_id):
    document = Document.objects.get(id=document_id, user=request.user)
    return FileResponse(open(document.file.name, 'rb'))

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Document

@csrf_exempt
def save_edited_pdf(request, document_id):
    if request.method == 'POST':
        document = Document.objects.get(id=document_id, user=request.user)
        document.file.save('edited.pdf', request.FILES['file'])
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})