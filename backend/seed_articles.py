# seed_articles.py
import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from content.models import HealthArticle

print("=== Adding Health Articles ===")

articles = [
    {
        'title': 'Jinsi ya Kudumisha Afya Njema',
        'category': 'general',
        'content': '''Afya njema ni msingi wa maisha bora. Hapa kuna vidokezo:
1. Kunywa maji ya kutosha - angalau lita 2 kwa siku
2. Kula chakula chenye virutubishi
3. Fanya mazoezi mara kwa mara
4. Pumzika na kulala kwa wakati
5. Epuka sigara na pombe kupita kiasi''',
        'author': 'Daktari Jane Mwangi',
        'language': 'sw',
        'is_verified': True,
        'is_published': True
    },
    {
        'title': 'Malaria Prevention in Kenya',
        'category': 'disease',
        'content': '''Malaria is preventable. Here are key prevention methods:
1. Sleep under insecticide-treated mosquito nets
2. Use mosquito repellents
3. Wear long-sleeved clothing in the evening
4. Clear stagnant water around your home
5. Seek immediate treatment if symptoms appear''',
        'author': 'Dr. James Omondi',
        'language': 'en',
        'is_verified': True,
        'is_published': True
    },
    {
        'title': 'Uangalizi wa Mtoto Mdogo',
        'category': 'child',
        'content': '''Mambo muhimu ya kukumbucha:
1. Mpe mtoto chanjo kwa wakati
2. Mlishe mtoto kwa maziwa ya mama pekee kwa miezi 6
3. Ongeza vyakula vya ziada baada ya miezi 6
4. Angalia uzito na urefu wa mtoto mara kwa mara
5. Peleka mtoto hospitali ukiwa na wasiwasi''',
        'author': 'Daktari Mary Atieno',
        'language': 'sw',
        'is_verified': True,
        'is_published': True
    },
]

for article_data in articles:
    # Create slug from title
    article_data['slug'] = slugify(article_data['title'])
    
    article, created = HealthArticle.objects.get_or_create(
        slug=article_data['slug'],
        defaults=article_data
    )
    
    if created:
        print(f"✅ Added article: {article.title}")
    else:
        print(f"⚠️ Article exists: {article.title}")

print(f"\n=== Total Health Articles: {HealthArticle.objects.count()} ===")