# Generated by Django 4.1.5 on 2023-12-21 10:27

from django.db import migrations, models
import django.db.models.deletion
import reviews.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_id', models.CharField(max_length=100, unique=True)),
                ('name', models.CharField(blank=True, max_length=300, null=True)),
                ('url', models.URLField(blank=True, max_length=500, null=True)),
                ('feed_url', models.URLField(blank=True, max_length=500, null=True)),
                ('address', models.CharField(blank=True, max_length=300, null=True)),
                ('rating', models.PositiveIntegerField(default=0)),
                ('latitude', models.CharField(blank=True, max_length=400, null=True)),
                ('longitude', models.CharField(blank=True, max_length=400, null=True)),
                ('number_of_reviews', models.PositiveIntegerField(default=0)),
                ('additional_information', models.JSONField(blank=True, help_text='Additional information the company', null=True)),
                ('telephone', models.CharField(blank=True, max_length=300, null=True)),
                ('website', models.URLField(blank=True, null=True)),
                ('reviews_file', models.FileField(blank=True, help_text='Optionally save the file containing the reviews', upload_to=reviews.utils.file_upload_helper)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name_plural': 'companies',
                'ordering': ['-created_on', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_id', models.CharField(max_length=100, unique=True)),
                ('reviewer_name', models.CharField(blank=True, max_length=100, null=True)),
                ('reviewer_number_of_reviews', models.PositiveIntegerField(default=0)),
                ('google_review_id', models.CharField(help_text='The comment ID as referenced by Google', max_length=400)),
                ('period', models.CharField(blank=True, max_length=100, null=True)),
                ('rating', models.CharField(blank=True, max_length=100, null=True)),
                ('text', models.TextField(blank=True, max_length=10000, null=True)),
                ('machine_learning_text', models.TextField(blank=True, max_length=10000, null=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reviews.company')),
            ],
            options={
                'ordering': ['created_on'],
            },
        ),
        migrations.AddIndex(
            model_name='company',
            index=models.Index(fields=['company_id'], name='reviews_com_company_d03054_idx'),
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['review_id'], name='reviews_rev_review__ebdfb1_idx'),
        ),
    ]
