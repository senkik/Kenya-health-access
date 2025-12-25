from django.core.management.base import BaseCommand
from django.utils.text import slugify
from content.models import HealthArticle, HealthTip

class Command(BaseCommand):
    help = 'Seed health articles and tips'

    def handle(self, *args, **kwargs):
        self.stdout.write('=== Seeding Content ===')

        # Articles
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
            slug = slugify(article_data['title'])
            article, created = HealthArticle.objects.get_or_create(
                slug=slug,
                defaults=article_data
            )
            if created:
                self.stdout.write(f'✅ Added article: {article.title}')
            else:
                self.stdout.write(f'⚠️ Article exists: {article.title}')

        # Tips
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
                self.stdout.write(f'✅ Added tip: {tip.tip[:50]}...')
            else:
                self.stdout.write(f'⚠️ Tip exists: {tip.tip[:50]}...')

        self.stdout.write(self.style.SUCCESS('✓ Content seeding completed successfully!'))
