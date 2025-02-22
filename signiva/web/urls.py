from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', index, name="index"),
    path('login', login_view, name="login"),
    path('register', register_view, name="register"),
    path('logout', logout_view, name="logout"),
    
    path('document/<uuid:id>', document_view, name="document"),
    path('document/<uuid:id>/sign', sign_document, name="signdoc"),
    path('document/<uuid:id>/generate', generate_doc, name="generate_doc")
]
