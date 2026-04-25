from django.core.management.base import BaseCommand

from api.models import KBEntry


class Command(BaseCommand):
    help = 'Seed the knowledge base with baseline entries.'

    def handle(self, *args, **options):
        entries = [
            {
                'question': 'What is select_related in Django ORM?',
                'answer': 'select_related performs a SQL JOIN and fetches related foreign key objects in one query.',
                'category': KBEntry.Category.DATABASE,
            },
            {
                'question': 'How does prefetch_related differ from select_related?',
                'answer': 'prefetch_related runs separate queries and joins in Python, useful for many-to-many and reverse relations.',
                'category': KBEntry.Category.DATABASE,
            },
            {
                'question': 'How does transaction.atomic() work in Django?',
                'answer': 'transaction.atomic wraps code in a transaction and rolls back all changes if an exception occurs.',
                'category': KBEntry.Category.FRAMEWORK,
            },
            {
                'question': 'What is a JWT token?',
                'answer': 'A JWT token is a signed JSON payload used for stateless authentication and authorization.',
                'category': KBEntry.Category.API,
            },
            {
                'question': 'When should I use Q objects?',
                'answer': 'Use Q objects when composing OR logic or complex filter conditions in a queryset.',
                'category': KBEntry.Category.FRAMEWORK,
            },
            {
                'question': 'Why use database indexes?',
                'answer': 'Indexes improve read performance for frequent lookup fields at the cost of additional write overhead.',
                'category': KBEntry.Category.DATABASE,
            },
            {
                'question': 'What is autoscaling in cloud infrastructure?',
                'answer': 'Autoscaling adjusts compute instances based on load metrics to maintain performance and control costs.',
                'category': KBEntry.Category.CLOUD,
            },
            {
                'question': 'How do API rate limits protect systems?',
                'answer': 'Rate limits prevent abuse and traffic spikes by restricting request volume over time windows.',
                'category': KBEntry.Category.API,
            },
            {
                'question': 'How do Django signals work?',
                'answer': 'Signals let decoupled receivers respond to events like post_save for model lifecycle actions.',
                'category': KBEntry.Category.FRAMEWORK,
            },
            {
                'question': 'What is caching in backend systems?',
                'answer': 'Caching stores frequently used data for faster responses and reduced database load.',
                'category': KBEntry.Category.GENERAL,
            },
        ]

        created = 0
        for entry in entries:
            _, was_created = KBEntry.objects.get_or_create(
                question=entry['question'],
                defaults={
                    'answer': entry['answer'],
                    'category': entry['category'],
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'Seed complete. Created {created} entries.'))
