import logging.config

from django.core.management.base import BaseCommand

from crawler.models import *

logger = logging.getLogger('crawler.command')


class Command(BaseCommand):
    help = 'Generate comparison between google similar app and ours'

    def handle(self, *args, **options):
        compatibility_count = 0
        similar_apps = SimilarApp.objects.filter().all()
        for similar_app in similar_apps:
            if self.is_compatible_with_google(similar_app):
                compatibility_count = compatibility_count + 1

        admin_file = open('comparison.csv', 'w')
        admin_file.write('{};{}\n'.format('Percentage of Compatibility', 'Total Similarity'))
        admin_file.write('{};{}\n'.format(float(compatibility_count) / len(similar_apps), len(similar_apps)))
        admin_file.close()
        self.stdout.write(self.style.SUCCESS(
            'Compatible Count: {} - Similar Count: {}'.format(compatibility_count, len(similar_apps))))

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
