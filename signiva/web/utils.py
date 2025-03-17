# utils.py
import resend
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from celery import shared_task  # Optional for async
import logging
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)

# Email Configuration
# ====================

def send_email(to, subject, html_content, from_email=None):
    """
    Send email using Resend API.
    
    Args:
        to (str/list): Recipient email address(es)
        subject (str): Email subject
        html_content (str): HTML email content
        from_email (str): Sender email (default: settings.DEFAULT_FROM_EMAIL)
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Validate configuration
    if not settings.RESEND_API_KEY:
        raise ImproperlyConfigured("RESEND_API_KEY is missing in settings")
    
    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL
    
    # Configure Resend
    resend.api_key = settings.RESEND_API_KEY
    
    try:
        resend.Emails.send({
            "from": from_email,
            "to": to,
            "subject": subject,
            "html": html_content
        })
        logger.info(f"Email sent to {to} with subject: {subject}")
        return True
    except Exception as e:
        logger.error(f"Email failed to {to}: {str(e)}")
        return False

def send_template_email(to, subject, template_name, context=None, from_email=None):
    """
    Send email using a Django template.
    
    Args:
        to (str/list): Recipient email address(es)
        subject (str): Email subject
        template_name (str): Path to template file
        context (dict): Context variables for template
        from_email (str): Sender email
    
    Returns:
        bool: True if successful, False otherwise
    """
    html_content = render_to_string(template_name, context or {})
    return send_email(to, subject, html_content, from_email)

@shared_task
def async_send_email(to, subject, html_content, from_email=None):
    """Celery task wrapper for sending emails asynchronously"""
    return send_email(to, subject, html_content, from_email)

# PDF Utilities
# ==============

def generate_pdf_thumbnail(pdf_path, output_path, size=(200, 200)):
    """
    Generate thumbnail from PDF file.
    Requires `pdf2image` package.
    """
    from pdf2image import convert_from_path
    
    try:
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        if images:
            thumbnail = images[0].resize(size)
            thumbnail.save(output_path)
            return True
    except Exception as e:
        logger.error(f"Thumbnail generation failed: {str(e)}")
    return False

# Signature Utilities
# ====================

def validate_signature(signature_data):
    """
    Validate signature data structure.
    Returns (is_valid, error_message)
    """
    required_fields = ['name', 'email', 'signature_image']
    for field in required_fields:
        if field not in signature_data:
            return False, f"Missing required field: {field}"
    
    if not isinstance(signature_data['signature_image'], bytes):
        return False, "Invalid signature image format"
    
    return True, ""

# File Handling
# =============

def sanitize_filename(filename):
    """Clean filename to prevent directory traversal"""
    import os
    from django.utils.text import get_valid_filename
    name, ext = os.path.splitext(filename)
    return f"{get_valid_filename(name)}{ext}"

# Model Utilities
# ===============

def model_to_dict(instance, fields=None, exclude=None):
    """Convert model instance to dictionary with field control"""
    from django.forms.models import model_to_dict
    data = model_to_dict(instance, fields=fields, exclude=exclude)
    # Add custom transformations if needed
    return data

# Security Utilities
# ==================

def validate_email_domain(email):
    """Validate email domain against allowed list"""
    allowed_domains = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', [])
    if not allowed_domains:
        return True
    
    domain = email.split('@')[-1]
    return domain.lower() in [d.lower() for d in allowed_domains]

def send_signature_request_email(signature, document):
    """Send signature request email using HTML template"""
    subject = f'Signature Request for {document.title}'
    
    # Generate the signature URL
    signature_url = f"{settings.SITE_URL}{reverse('sign_document', kwargs={'signature_id': signature.id})}"
    
    # Prepare context for the template
    context = {
        'document': document,
        'signature_url': signature_url,
    }
    
    # Render HTML content
    html_message = render_to_string('emails/signature_request.html', context)
    
    try:
        send_mail(
            subject=subject,
            message='',  # Plain text version (empty as we're using HTML)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[signature.signer_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Signature request email sent to {signature.signer_email}")
    except Exception as e:
        logger.error(f"Failed to send signature request email: {str(e)}")
        raise

def send_signature_completion_email(signature, document):
    """Send signature completion email using HTML template"""
    subject = f'Document "{document.title}" has been signed'
    
    # Generate the document URL
    document_url = f"{settings.SITE_URL}{reverse('view_document', kwargs={'document_id': document.id})}"
    
    # Prepare context for the template
    context = {
        'document': document,
        'signature': signature,
        'document_url': document_url,
    }
    
    # Render HTML content
    html_message = render_to_string('emails/signature_completion.html', context)
    
    try:
        send_mail(
            subject=subject,
            message='',  # Plain text version (empty as we're using HTML)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[document.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Signature completion email sent to {document.user.email}")
    except Exception as e:
        logger.error(f"Failed to send signature completion email: {str(e)}")
        raise