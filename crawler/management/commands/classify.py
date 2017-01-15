from django.core.management.base import BaseCommand

from crawler.models import App, Category, Developer
from crawler.tasks import AppClassifier


class Command(BaseCommand):
    help = 'Process similar csv'

    def add_arguments(self, parser):
        parser.add_argument('--apps_count', type=int, default=-1,
                            help='Number of apps to be classified. Default value is all')

    def handle(self, *args, **options):
        apps_count = options['apps_count']

        category_keys = self.get_category_dict(Category.get_all_categories())
        developer_list = self.get_developer_dict(Developer.get_developer_list(), len(category_keys))
        if apps_count < 0:
            apps = App.objects.all()
        else:
            apps = App.objects.all()[:apps_count]
        classifier = AppClassifier(apps, category_keys, developer_list)
        similar_apps = classifier.find_similar_apps()

        for app_tuple in similar_apps:
            print '{} and {} are similar'.format(app_tuple[0].name(), app_tuple[1].name())

    @staticmethod
    def get_category_dict(category_list, start=0):
        category_keys = dict()
        for category in category_list:
            category_keys[category.key] = start
            start += 1

        category_keys['GAME'] = start
        start += 1
        return category_keys

    @staticmethod
    def get_developer_dict(devs, start=0):
        developer_list = dict()
        for dev in devs:
            developer_list[dev.name] = start
            start += 1
        return developer_list
