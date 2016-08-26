from datetime import datetime

from django.core.management.base import BaseCommand

from crawler.tasks import Crawler


class Command(BaseCommand):
    help = 'Run crawler for apps'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=file)

    def handle(self, *args, **options):

        app_packages = options['file']
        if not app_packages:
            print 'File attribute is mandatory!!'
            exit(1)
        now = datetime.now()
        crawler = Crawler()
        crawled_count, total_count = crawler.crawl(app_packages, now)
        self.stdout.write(self.style.SUCCESS("{} app data collected from {}".format(crawled_count, total_count)))

