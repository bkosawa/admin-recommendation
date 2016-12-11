from django.core.management.base import BaseCommand

from crawler.models import App
from crawler.tasks import AppClassifier


class Command(BaseCommand):
    help = 'Process similar csv'

    def handle(self, *args, **options):
        classifier = AppClassifier()
        apps = App.objects.all()[:100]
        classifier.create_utility_matrix(apps)
