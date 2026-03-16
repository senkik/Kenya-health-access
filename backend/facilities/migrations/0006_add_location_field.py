from django.db import migrations
import django.contrib.gis.db.models.fields

class Migration(migrations.Migration):

    dependencies = [
        ('facilities', '0005_rename_accepts_nhif_facility_accepts_sha_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='facility',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]
