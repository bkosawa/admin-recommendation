import logging.config
from operator import or_

from django.core.management.base import BaseCommand

from crawler.models import *

logger = logging.getLogger('crawler.command')


class Command(BaseCommand):
    help = 'Generate comparison between google similar app and ours'

    def handle(self, *args, **options):
        result_dict = dict()
        similar_apps = self.get_my_similar()
        for similar_app in similar_apps:
            app = App.objects.filter(package_name=similar_app)
            category = app.category_name()
            if category not in result_dict:
                count = 0
            else:
                count = result_dict[category]

            result_dict[category] = count + 1

        admin_file = open('similar_apps_category.csv', 'w')
        admin_file.write('category;count')
        for key in result_dict:
            admin_file.write('{};{}\n'.format(key, result_dict[key]))
        admin_file.close()
        self.stdout.write(
            self.style.SUCCESS('Finished category counter')
        )

    @staticmethod
    def get_my_similar():
        apps = SimilarApp.objects.order_by().values_list('source_package', flat=True).distinct()
        similar_apps = SimilarApp.objects.order_by().values_list('similar_package', flat=True).distinct()
        app_set = set(apps)
        similar_set = set(similar_apps)
        merged_set = reduce(or_, [app_set, similar_set])
        return merged_set
