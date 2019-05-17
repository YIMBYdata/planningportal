# Generated by Django 2.2.1 on 2019-05-10 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ppts', '0002_delete_hearingdate'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='environmental_review',
            field=models.CharField(blank=True, help_text='Environmental Review type', max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='record',
            name='mcd_referral',
            field=models.CharField(blank=True, help_text='Medical Cannabis Dispensary referral', max_length=150, null=True),
        ),
        migrations.DeleteModel(
            name='EnvironmentalReview',
        ),
        migrations.DeleteModel(
            name='MCDReferral',
        ),
    ]