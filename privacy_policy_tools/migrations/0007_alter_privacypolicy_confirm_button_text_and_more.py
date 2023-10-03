# Generated by Django 4.2.3 on 2023-09-19 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('privacy_policy_tools', '0006_auto_20230202_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privacypolicy',
            name='confirm_button_text',
            field=models.CharField(max_length=128, verbose_name='Confirm button text'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='confirm_button_text_de',
            field=models.CharField(max_length=128, null=True, verbose_name='Confirm button text'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='confirm_button_text_en',
            field=models.CharField(max_length=128, null=True, verbose_name='Confirm button text'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='confirm_checkbox_text',
            field=models.CharField(max_length=128, verbose_name='Confirm checkbox text'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='confirm_checkbox_text_de',
            field=models.CharField(max_length=128, null=True, verbose_name='Confirm checkbox text'),
        ),
        migrations.AlterField(
            model_name='privacypolicy',
            name='confirm_checkbox_text_en',
            field=models.CharField(max_length=128, null=True, verbose_name='Confirm checkbox text'),
        ),
    ]
