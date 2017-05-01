import csv
import logging

from django.core.management.base import BaseCommand, CommandError

from crawler.models import SimilarApp

logger = logging.getLogger('crawler.command')


class Command(BaseCommand):
    help = 'Process similar csv'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=file)

    def handle(self, *args, **options):
        app_similar_packages = options['file']
        if not app_similar_packages:
            logger.error('File attribute is mandatory!!')
            raise CommandError('--file attribute is mandatory!!')

        failed_csv = csv.reader(app_similar_packages, delimiter=';', quotechar='"')
        for row in failed_csv:
            logger.debug('Saving {} and {} are at distance of {}'.format(row[0], row[1], row[2]))
            SimilarApp.objects.get_or_create(
                source_package=row[0],
                similar_package=row[1],
                distance=row[2]
            )
