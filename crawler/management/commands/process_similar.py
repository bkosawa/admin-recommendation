import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from crawler.models import GoogleSimilarApp, App


class Command(BaseCommand):
    help = 'Process similar csv'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=file)

    def handle(self, *args, **options):
        app_similar_packages = options['file']
        if not app_similar_packages:
            print 'File attribute is mandatory!!'
            exit(1)

        now = datetime.now()
        with open('apps-id-{}.txt'.format(now.strftime("%Y-%m-%d-%H:%M:%S")), 'w') as apps_id_file:
            similar_csv = csv.reader(app_similar_packages, delimiter=';', quotechar='"')
            for row in similar_csv:
                if not App.objects.filter(package_name=row[1]):
                    apps_id_file.write('{}\n'.format(row[1]))

                similar, similar_created = GoogleSimilarApp.objects.get_or_create(
                    source_package=row[0],
                    similar_package=row[1],
                    defaults={}
                )
