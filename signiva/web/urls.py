from django.contrib import admin
from django.urls import path, include

from web.views import *
urlpatterns = [
    path('', index, name="home"),
    path('login', login_view, name="login"),
    path('register', register_view, name="register"),
    path('logout', logout_view, name="logout"),
    path('profile/', profile, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    
    path('documents/upload/', upload_document, name='upload_document'),
    path('documents/', document_list, name='document_list'),
    path('documents/<uuid:document_id>/', view_document, name='view_document'),
    path('documents/<uuid:document_id>/doc', download_document, name='download_document'),
    path('documents/<uuid:document_id>/edit/', edit_document, name='edit_document'),
    path('documents/<uuid:document_id>/delete/', delete_document, name='delete_document'),
    path('documents/<uuid:document_id>/save', save_edited_pdf, name='save_edited_pdf'),
    path('documents/<uuid:document_id>/request_signature/', request_signature, name='request_signature'),
    path('documents/<uuid:document_id>/save_signature_placements/', save_signature_placements, name='save_signature_placements'),
    path('sign/<uuid:signature_id>/', sign_document, name='sign_document'),
]
