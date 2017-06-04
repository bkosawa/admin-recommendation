import logging.config
from operator import or_

from django.core.management.base import BaseCommand

from crawler.models import *

logger = logging.getLogger('crawler.command')


class Command(BaseCommand):
    help = 'Generate comparison between google similar app and ours'

    def handle(self, *args, **options):
        apps, similar_apps, similar_apps_count \
            = self.my_similar_report('my_distribution.csv')
        google_apps, google_similar_apps, google_similar_apps_count \
            = self.google_similar_report('google_distribution.csv')

        self.stdout.write(self.style.SUCCESS(
            'Mine: {} apps and {} similar_apps from {}'.format(
                len(apps), len(similar_apps), similar_apps_count)))
        self.stdout.write(self.style.SUCCESS(
            'Google: {} apps and {} similar_apps from {}'.format(
                len(google_apps), len(google_similar_apps), google_similar_apps_count)))

    @staticmethod
    def my_similar_report(filename):
        result_dict = dict()
        similar_apps_count = SimilarApp.objects.count()
        apps = SimilarApp.objects.order_by().values_list('source_package', flat=True).distinct()
        similar_apps = SimilarApp.objects.order_by().values_list('similar_package', flat=True).distinct()
        app_set = set(apps)
        similar_set = set(similar_apps)
        merged_set = reduce(or_, [app_set, similar_set])
        for app in merged_set:
            logger.debug('App: {}'.format(app))
            my_similar_source = SimilarApp.objects.filter(source_package=app).all()
            my_similar_similar = SimilarApp.objects.filter(similar_package=app).all()

            my_similar = list(my_similar_source) + list(my_similar_similar)

            if not my_similar:
                continue

            if not len(my_similar) in result_dict:
                count = 0
            else:
                count = result_dict[len(my_similar)]

            result_dict[len(my_similar)] = count + 1
            logger.debug('Updated: {} with {}'.format(len(my_similar), count + 1))

        admin_file = open(filename, 'w')
        for key in result_dict:
            admin_file.write('{};{}\n'.format(key, result_dict[key]))
        admin_file.close()
        return apps, similar_apps, similar_apps_count

    @staticmethod
    def google_similar_report(filename):
        result_dict = dict()
        similar_apps_count = GoogleSimilarApp.objects.count()
        apps = GoogleSimilarApp.objects.order_by().values_list('source_package', flat=True).distinct()
        similar_apps = GoogleSimilarApp.objects.order_by().values_list('similar_package', flat=True).distinct()
        app_set = set(apps)
        similar_set = set(similar_apps)
        merged_set = reduce(or_, [app_set, similar_set])
        for app in merged_set:
            google_similar = GoogleSimilarApp.objects.filter(source_package=app).all()

            if not google_similar:
                continue

            if not len(google_similar) in result_dict:
                count = 0
            else:
                count = result_dict[len(google_similar)]

            result_dict[len(google_similar)] = count + 1
            logger.debug('Updated: {} with {}'.format(len(google_similar), count + 1))

        admin_file = open(filename, 'w')
        for key in result_dict:
            admin_file.write('{};{}\n'.format(key, result_dict[key]))
        admin_file.close()
        return apps, similar_apps, similar_apps_count
