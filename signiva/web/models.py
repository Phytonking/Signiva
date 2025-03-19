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

    def __str__(self):
        return f'{self.user.username} Profile'
    
class DocumentSignature(anysign.SignatureFactory(SignatureType)):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='signatures')
    signer_email = models.EmailField()
    signed_at = models.DateTimeField(null=True, blank=True)
    signature_image = models.ImageField(upload_to='signatures/', null=True, blank=True)

    def __str__(self):
        return f"Signature for {self.document.title}"
    
class Signer(anysign.SignerFactory(DocumentSignature)):
    pass
    
class SignaturePlacement(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='signature_placements')
    page_number = models.IntegerField()
    x = models.FloatField()  # X coordinate as percentage of page width
    y = models.FloatField()  # Y coordinate as percentage of page height
    width = models.FloatField()  # Width as percentage of page width
    height = models.FloatField()  # Height as percentage of page height
    created_at = models.DateTimeField(auto_now_add=True)
    is_signed = models.BooleanField(default=False)

    def __str__(self):
        return f"Signature placement on page {self.page_number} for {self.document.title}"
    
