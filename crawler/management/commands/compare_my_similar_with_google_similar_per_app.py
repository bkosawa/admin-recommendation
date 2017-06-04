import logging.config
from operator import or_

from django.core.management.base import BaseCommand

from crawler.models import *

logger = logging.getLogger('crawler.command')


class Command(BaseCommand):
    help = 'Generate comparison between google similar app and ours per app'

    def handle(self, *args, **options):
        apps = self.get_my_similar()
        result_dict = dict()
        for app in apps:
            count = 0
            similar_apps = SimilarApp.objects.filter(source_package=app).all()
            total = len(similar_apps)
            for similar_app in similar_apps:
                if self.is_compatible_with_google(similar_app):
                    count = count + 1

            similar_apps = SimilarApp.objects.filter(similar_package=app).all()
            total = total + len(similar_apps)
            for similar_app in similar_apps:
                if self.is_compatible_with_google(similar_app):
                    count = count + 1

            percentage = count / total
            if percentage not in result_dict:
                result_count = 0
            else:
                result_count = result_dict[percentage]

            result_dict[percentage] = result_count + 1

        admin_file = open('comparison_per_app.csv', 'w')
        admin_file.write('{};{}\n'.format('Percentage of Compatibility', 'Apps in this situation'))
        for key in result_dict:
            admin_file.write('{};{}\n'.format(key, result_dict[key]))
        admin_file.close()
        self.stdout.write(self.style.SUCCESS('Finished'.format()))

    @staticmethod
    def is_compatible_with_google(similar_app):
        count = GoogleSimilarApp.objects.filter(
            source_package=similar_app.source_package,
            similar_package=similar_app.similar_package
        ).count()

        if count > 0:
            return True

        count = GoogleSimilarApp.objects.filter(
            source_package=similar_app.similar_package,
            similar_package=similar_app.source_package
        ).count()

        if count > 0:
            return True

        return False

    @staticmethod
    def get_my_similar():
        apps = SimilarApp.objects.order_by().values_list('source_package', flat=True).distinct()
        similar_apps = SimilarApp.objects.order_by().values_list('similar_package', flat=True).distinct()
        app_set = set(apps)
        similar_set = set(similar_apps)
        merged_set = reduce(or_, [app_set, similar_set])
        return merged_set
