# utils.py
from django.conf import settings
from django.template.loader import render_to_string
import logging
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)

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

# Email Utilities
# ===============

def send_signature_request_email(document, signer_email):
    """
    Sends an email to request a signature on a document.
    """
    subject = f'Signature Request for {document.title}'
    
    # Create the signature URL
    signature_url = f"{settings.SITE_URL}{reverse('sign_document', args=[document.id, document.signatures.first().id])}"
    
    # Render the email template
    html_message = render_to_string('email/signature_request.html', {
        'document': document,
        'signature_url': signature_url,
        'signer_email': signer_email
    })
    
    try:
        # Send the email
        send_mail(
            subject=subject,
            message='',  # Plain text version (empty as we're using HTML)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[signer_email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Signature request email sent to {signer_email}")
    except Exception as e:
        logger.error(f"Failed to send signature request email: {str(e)}")
        raise

def send_signature_completion_email(document, signer_email):
    """
    Sends an email to notify that a document has been signed.
    """
    subject = f'Document Signed: {document.title}'
    
    # Render the email template
    html_message = render_to_string('email/signature_completion.html', {
        'document': document,
        'signer_email': signer_email
    })
    
    try:
        # Send the email
        send_mail(
            subject=subject,
            message='',  # Plain text version (empty as we're using HTML)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[document.user.email],  # Notify the document owner
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Signature completion email sent to {document.user.email}")
    except Exception as e:
        logger.error(f"Failed to send signature completion email: {str(e)}")
        raise