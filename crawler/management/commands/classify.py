from django.core.management.base import BaseCommand, CommandError

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
        parser.add_argument('--persist', type=bool, default=False,
                            help='Boolean that indicate if it should persist while iterating. Default value is False')
        parser.add_argument('--offset', type=int, default=0,
                            help='Indicate starting row to continue classification. Default value is 0')
        parser.add_argument('--starting_at', type=int, default=0,
                            help='Starting point of classification list. Default value is 0')
        parser.add_argument('--area', nargs="+", type=int, default=None,
                            help='Area of classification matrix. Default value is None')

    def handle(self, *args, **options):
        apps_count, area, boundary, offset, persist, starting_at = self.get_arguments(options)

        if apps_count < 0:
            apps = App.objects.all()[starting_at:]
        else:
            apps = App.objects.all()[starting_at:starting_at + apps_count]

        classifier = AppClassifier(apps, features=get_features(),
                                   boundary=boundary,
                                   should_persist=persist,
                                   offset=offset,
                                   target_area=area)
        similar_apps = classifier.find_similar_apps()

        if not persist:
            if similar_apps:
                for app_tuple in similar_apps:
                    similar_apps = SimilarApp()
                    similar_apps.source_package = app_tuple[0].package_name
                    similar_apps.similar_package = app_tuple[1].package_name
                    similar_apps.distance = app_tuple[2]
                    similar_apps.save()

    @staticmethod
    def get_arguments(options):
        apps_count = options['apps_count']
        boundary = options['boundary']
        persist = options['persist']
        offset = options['offset']
        starting_at = options['starting_at']
        area = options['area']
        area_tuple = None
        Command.validate_area(area)
        if area:
            apps_count = max(area[2], area[3])
            area_tuple = ((area[0], area[1]), (area[2], area[3]))

        return apps_count, area_tuple, boundary, offset, persist, starting_at

    @staticmethod
    def validate_area(area):
        if area:
            if len(area) != 4:
                raise CommandError("Option `--area ` must have 4 integer elements.")

            if area[0] > area[2] or area[1] > area[3]:
                raise CommandError("Option `--area ` ending point must be greater than starting point")
