from django.core.management.base import BaseCommand

from crawler.models import App, Category, Developer
from crawler.tasks import AppClassifier


class Command(BaseCommand):
    help = 'Process similar csv'

    def handle(self, *args, **options):
        category_keys = self.get_category_dict(Category.get_all_categories())
        developer_list = self.get_developer_dict(Developer.get_developer_list(), len(category_keys))
        apps = App.objects.all()[:100]
        classifier = AppClassifier(apps, category_keys, developer_list)
        classifier.create_utility_matrix()

    @staticmethod
    def get_category_dict(category_list, start=0):
        category_keys = dict()
        for category in category_list:
            category_keys[category.key] = start
            start += 1
        return category_keys

    @staticmethod
    def get_developer_dict(devs, start=0):
        developer_list = dict()
        for dev in devs:
            developer_list[dev.name] = start
            start += 1
        return developer_list
