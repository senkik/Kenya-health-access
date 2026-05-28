"""
Migration to add database indexes for new filter fields and
add description field to Service model.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0008_facility_mfl_code_facility_ward'),
    ]

    operations = [
        # Add description field to Service
        migrations.AddField(
            model_name='service',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        # Alter Service.category to accept new expanded choices
        migrations.AlterField(
            model_name='service',
            name='category',
            field=models.CharField(
                max_length=50,
                choices=[
                    ('emergency', 'Emergency Services'),
                    ('maternity', 'Maternity & Child Health'),
                    ('pharmacy', 'Pharmacy'),
                    ('laboratory', 'Laboratory Services'),
                    ('surgery', 'Surgery'),
                    ('dental', 'Dental Care'),
                    ('eye_care', 'Eye Care/Optical'),
                    ('vaccination', 'Vaccination'),
                    ('radiology', 'Radiology/X-Ray'),
                    ('inpatient', 'Inpatient Services'),
                    ('outpatient', 'Outpatient Services'),
                    ('general', 'General Medicine'),
                    ('specialist', 'Specialist Care'),
                    ('diagnostic', 'Diagnostic Services'),
                    ('maternal', 'Maternal & Child Health'),
                    ('pharmacy_services', 'Pharmacy Services'),
                ],
            ),
        ),
        # Performance indexes for the new filter fields
        migrations.AddIndex(
            model_name='facility',
            index=models.Index(fields=['constituency'], name='facility_constituency_idx'),
        ),
        migrations.AddIndex(
            model_name='facility',
            index=models.Index(fields=['town'], name='facility_town_idx'),
        ),
        migrations.AddIndex(
            model_name='facility',
            index=models.Index(fields=['is_24_hours'], name='facility_24hr_idx'),
        ),
    ]
