from django.core.management.base import BaseCommand

from crawler.models import App, Category, Developer, SimilarApp
from crawler.tasks import AppClassifier


def get_category_dict(category_list, start=0):
    category_keys = dict()
    for category in category_list:
        category_keys[category.key] = start
        start += 1

    category_keys['GAME'] = start
    start += 1
    return category_keys


def get_developer_dict(devs, start=0):
    developer_list = dict()
    for dev in devs:
        developer_list[dev.name] = start
        start += 1
    return developer_list


def get_features():
    features = dict()
    features['category'] = get_category_dict(Category.get_all_categories())
    features['developer'] = get_developer_dict(Developer.get_developer_list(), len(features['category']))
    return features


class Command(BaseCommand):
    help = 'Process similar csv'

    def add_arguments(self, parser):
        parser.add_argument('--apps_count', type=int, default=-1,
                            help='Number of apps to be classified. Default value is all')
        parser.add_argument('--boundary', type=float, default=0.5,
                            help='Minimum value to be considered similar. Default value is 0.5')

    def handle(self, *args, **options):
        apps_count = options['apps_count']
        boundary = options['boundary']

        if apps_count < 0:
            apps = App.objects.all()
        else:
            apps = App.objects.all()[:apps_count]

        classifier = AppClassifier(apps, features=get_features(), boundary=boundary)
        similar_apps = classifier.find_similar_apps()

        for app_tuple in similar_apps:
            similar_apps = SimilarApp()
            similar_apps.source_package = app_tuple[0].package_name
            similar_apps.similar_package = app_tuple[1].package_name
            similar_apps.distance = app_tuple[2]
            similar_apps.save()
