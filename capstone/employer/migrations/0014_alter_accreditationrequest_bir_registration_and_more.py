# Generated by Django 5.1 on 2024-09-08 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employer', '0013_accreditationrequest_latest_job_order_with_qualifications_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accreditationrequest',
            name='bir_registration',
            field=models.FileField(null=True, upload_to='accreditation_documents/bir_registration/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='business_permit',
            field=models.FileField(null=True, upload_to='accreditation_documents/business_permit/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='dole_permit',
            field=models.FileField(null=True, upload_to='accreditation_documents/dole_permit/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='dti_permit',
            field=models.FileField(null=True, upload_to='accreditation_documents/dti_permit/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='latest_job_order_with_qualifications',
            field=models.FileField(null=True, upload_to='accreditation_documents/latest_job_order_with_qualifications/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='latest_job_posting',
            field=models.FileField(null=True, upload_to='accreditation_documents/latest_job_posting/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='latest_payment_receipt',
            field=models.FileField(null=True, upload_to='accreditation_documents/latest_payment_receipt/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='no_pending_case_certificate',
            field=models.FileField(null=True, upload_to='accreditation_documents/no_pending_case_certificate/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='phil_job_net_registration',
            field=models.FileField(null=True, upload_to='accreditation_documents/phil_job_net_registration/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='poea_permit',
            field=models.FileField(null=True, upload_to='accreditation_documents/poea_permit/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='sec_registration',
            field=models.FileField(null=True, upload_to='accreditation_documents/sec_registration/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='sss_membership_registration',
            field=models.FileField(null=True, upload_to='accreditation_documents/sss_membership_registration/'),
        ),
        migrations.AlterField(
            model_name='accreditationrequest',
            name='tied_companies_list',
            field=models.FileField(null=True, upload_to='accreditation_documents/tied_companies_list/'),
        ),
    ]
