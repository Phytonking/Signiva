"""
Views for handling all the web app functionality.
"""

from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm, DocumentForm, SignatureRequestForm
from .models import Profile, Document, DocumentSignature, SignatureType, SignaturePlacement
from django.contrib.auth.decorators import login_required
import uuid
from django.utils import timezone
from .utils import send_signature_request_email, send_signature_completion_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

def index(request):
    """Shows the home page. Redirects to dashboard if user is logged in."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')

def login_view(request):
    """Handles user login. Shows login form or redirects to dashboard on success."""
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

def register_view(request):
    """Creates new user accounts. Creates profile and logs in user on success."""
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

def logout_view(request):
    """Logs out the user and redirects to home page."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

@login_required(login_url='/login')
def upload_document(request):
    """Handles document uploads. Creates new document record and stores file."""
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
    """Shows all documents owned by the user."""
    documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'document_list.html', {'documents': documents})

@login_required(login_url='/login')
def view_document(request, document_id):
    """Shows document details and signature status."""
    document = Document.objects.get(id=document_id, user=request.user)
    return render(request, 'view_document.html', {'document': document})

@login_required(login_url='/login')
def edit_document(request, document_id):
    """Lets users edit document details and add signature boxes."""
    document = Document.objects.get(id=document_id, user=request.user)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return redirect('document_list')
    else:
        form = DocumentForm(instance=document)
    return render(request, 'edit_document.html', {'form': form, 'document':document})

@login_required(login_url='/login')
def delete_document(request, document_id):
    """Deletes a document and all its related data."""
    document = Document.objects.get(id=document_id, user=request.user)
    if request.method == 'POST':
        if document.file:
            document.file.delete(save=False)
        SignaturePlacement.objects.filter(document=document).delete()
        DocumentSignature.objects.filter(document=document).delete()
        document.delete()
        messages.success(request, 'Document deleted successfully!')
        return redirect('document_list')
    return render(request, 'delete_document.html', {'document': document})

@login_required(login_url='/login')
def profile(request):
    """Lets users update their profile info, settings, and password."""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        # Handle password change
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Password updated successfully!')
                return redirect('login')
        
        # Handle profile update
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('dashboard')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required(login_url='/login')
def dashboard(request):
    """Shows user's recent activity and document stats."""
    recent_documents = Document.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
    pending_signatures = Document.objects.filter(
        user=request.user,
        signatures__signed_at__isnull=True
    ).distinct().order_by('-uploaded_at')[:5]
    signed_documents = Document.objects.filter(
        user=request.user,
        is_signed=True
    ).order_by('-uploaded_at')[:5]
    
    document_count = Document.objects.filter(user=request.user).count()
    signed_count = Document.objects.filter(user=request.user, is_signed=True).count()
    pending_count = Document.objects.filter(
        user=request.user,
        signatures__signed_at__isnull=True
    ).distinct().count()

    context = {
        'recent_documents': recent_documents,
        'pending_signatures': pending_signatures,
        'signed_documents': signed_documents,
        'document_count': document_count,
        'signed_count': signed_count,
        'pending_count': pending_count,
    }
    return render(request, 'dashboard.html', context)

@login_required(login_url='/login')
def download_document(request, document_id):
    """Serves the document file for download."""
    document = Document.objects.get(id=document_id, user=request.user)
    return FileResponse(open(document.file.name, 'rb'))

@csrf_exempt
def save_edited_pdf(request, document_id):
    """Saves edited PDF document."""
    if request.method == 'POST':
        document = Document.objects.get(id=document_id, user=request.user)
        document.file.save('edited.pdf', request.FILES['file'])
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def request_signature(request, document_id):
    """Sends signature requests to specified email addresses."""
    document = get_object_or_404(Document, id=document_id, user=request.user)
    if request.method == 'POST':
        form = SignatureRequestForm(request.POST)
        if form.is_valid():
            signer_email = form.cleaned_data['signer_email']
            signature = DocumentSignature.objects.create(
                document=document,
                signer_email=signer_email,
                status='pending'
            )
            try:
                send_signature_request_email(document, signer_email)
                messages.success(request, 'Signature request sent successfully!')
            except Exception as e:
                logger.error(f"Failed to send signature request email: {str(e)}")
                messages.error(request, 'Failed to send signature request email.')
            return redirect('document_list')
    else:
        form = SignatureRequestForm()
    return render(request, 'request_signature.html', {
        'form': form,
        'document': document
    })

@login_required
def sign_document(request, document_id, signature_id):
    """Handles document signing process."""
    document = get_object_or_404(Document, id=document_id)
    signature = get_object_or_404(DocumentSignature, id=signature_id, document=document)
    
    if request.method == 'POST':
        signature_data = request.POST.get('signature')
        signature.signature_data = signature_data
        signature.status = 'completed'
        signature.signed_at = timezone.now()
        signature.save()
        
        try:
            send_signature_completion_email(document, signature.signer_email)
        except Exception as e:
            logger.error(f"Failed to send signature completion email: {str(e)}")
        
        return redirect('signature_success')
    
    return render(request, 'sign_document.html', {
        'document': document,
        'signature': signature
    })

@login_required
@require_POST
@csrf_exempt
def save_signature_placements(request, document_id):
    """Saves signature box positions on the document."""
    try:
        document = Document.objects.get(id=document_id, user=request.user)
        data = json.loads(request.body)
        signature_placements = data.get('signature_placements', [])
        
        SignaturePlacement.objects.filter(document=document).delete()
        
        for placement in signature_placements:
            SignaturePlacement.objects.create(
                document=document,
                page_number=placement['pageNumber'],
                x=placement['x'],
                y=placement['y'],
                width=placement['width'],
                height=placement['height']
            )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})