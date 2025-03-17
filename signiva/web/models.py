from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
import django_anysign.api as anysign

class SignatureType(anysign.SignatureType):
    pass

class Document(models.Model):
    id = models.UUIDField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_signed = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username
    
class DocumentSignature(anysign.SignatureFactory(SignatureType)):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='signatures')
    signer_email = models.EmailField()
    signed_at = models.DateTimeField(null=True, blank=True)
    signature_image = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def __str__(self):
        return f"Signature for {self.document.title}"
    
class Signer(anysign.SignerFactory(DocumentSignature)):
    pass
    
