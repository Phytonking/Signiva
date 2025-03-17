# Generated by Django 5.1.5 on 2025-03-10 20:35

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignatureType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature_backend_code', models.CharField(choices=[], db_index=True, max_length=50, verbose_name='signature backend')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='document',
            name='is_signed',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='DocumentSignature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signature_backend_id', models.CharField(blank=True, db_index=True, default='', max_length=100, verbose_name='ID for signature backend')),
                ('anysign_internal_id', models.UUIDField(default=uuid.uuid4, verbose_name='ID in internal database')),
                ('signer_email', models.EmailField(max_length=254)),
                ('signed_at', models.DateTimeField(blank=True, null=True)),
                ('signature_image', models.ImageField(blank=True, null=True, upload_to='signatures/')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signatures', to='web.document')),
                ('signature_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.signaturetype', verbose_name='signature type')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
