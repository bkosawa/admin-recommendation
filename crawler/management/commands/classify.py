from django.core.management.base import BaseCommand

from crawler.models import App, Category, Developer
from crawler.tasks import AppClassifier


class Command(BaseCommand):
    help = 'Process similar csv'

    def handle(self, *args, **options):
        category_keys = Category.get_category_list(0)
        developer_list = Developer.get_developer_list(len(category_keys))
        apps = App.objects.all()[:100]
        classifier = AppClassifier(apps, category_keys, developer_list)
        classifier.create_utility_matrix()
