# Generated by Django 5.0.2 on 2025-03-18 16:18

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_signaturetype_document_is_signed_documentsignature'),
    ]

    operations = [
        migrations.CreateModel(
            name='SignaturePlacement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_number', models.IntegerField()),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('width', models.FloatField()),
                ('height', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_signed', models.BooleanField(default=False)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signature_placements', to='web.document')),
            ],
        ),
        migrations.CreateModel(
            name='Signer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signing_order', models.PositiveSmallIntegerField(default=0, help_text='Position in the list of signers.', verbose_name='signing order')),
                ('signature_backend_id', models.CharField(blank=True, db_index=True, default='', max_length=100, verbose_name='ID in signature backend')),
                ('anysign_internal_id', models.UUIDField(default=uuid.uuid4, verbose_name='ID in internal database')),
                ('signature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signers', to='web.documentsignature')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
