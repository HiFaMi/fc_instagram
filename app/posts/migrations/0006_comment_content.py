# Generated by Django 2.0.6 on 2018-07-02 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='content',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
