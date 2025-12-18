# seed_health_tips.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from content.models import HealthTip

print("=== Adding Health Tips ===")

tips = [
    {
        'tip': 'Kunywa angalau lita 2 za maji kila siku kwa afya njema',
        'category': 'general',
        'language': 'sw',
        'is_active': True
    },
    {
        'tip': 'Lala saa 8 usiku kupata usingizi wa kutosha',
        'category': 'general',
        'language': 'sw',
        'is_active': True
    },
    {
        'tip': 'Wash your hands regularly with soap and water to prevent diseases',
        'category': 'disease',
        'language': 'en',
        'is_active': True
    },
    {
        'tip': 'Kula mboga za majani na matunda mengi kila siku',
        'category': 'nutrition',
        'language': 'sw',
        'is_active': True
    },
    {
        'tip': 'Fanya mazoezi angalau dakika 30 kila siku',
        'category': 'general',
        'language': 'sw',
        'is_active': True
    },
    {
        'tip': 'Pima shinikizo la damu mara kwa mara ukiwa na umri wa miaka 40 na kuendelea',
        'category': 'disease',
        'language': 'sw',
        'is_active': True
    },
    {
        'tip': 'Breastfeed your baby exclusively for the first 6 months',
        'category': 'maternal',
        'language': 'en',
        'is_active': True
    },
    {
        'tip': 'Take your child for immunization as per the scheduled dates',
        'category': 'child',
        'language': 'en',
        'is_active': True
    },
    {
        'tip': 'Tembelea daktari mara kwa mara kwa ukaguzi wa afya',
        'category': 'general',
        'language': 'sw',
        'is_active': True
    },
    {
        'tip': 'Use mosquito nets to prevent malaria',
        'category': 'disease',
        'language': 'en',
        'is_active': True
    },
]

for tip_data in tips:
    tip, created = HealthTip.objects.get_or_create(
        tip=tip_data['tip'],
        defaults=tip_data
    )
    if created:
        print(f"✅ Added: {tip.tip[:50]}...")
    else:
        print(f"⚠️ Already exists: {tip.tip[:50]}...")

print(f"\n=== Total Health Tips: {HealthTip.objects.count()} ===")
print("\nTest with:")
print("curl http://127.0.0.1:8000/api/articles/")