# coding=utf-8
from django.core.management.base import BaseCommand
from django.db.models import Q
from crawler.models import AppDescription, App


class Command(BaseCommand):
    help = 'Remove non latin1 char rows in db'

    def handle(self, *args, **options):
        apps_desc = AppDescription.objects.filter(
            Q(name__iregex=u'[^ -~]'),
            ~Q(name__contains=u'®'),
            ~Q(name__contains=u'™'),
            ~Q(name__contains=u'∞'),
        )

        print u'{} found. Deleting'.format(apps_desc.count())

        for ad in apps_desc:
            App.objects.get(id=ad.app_id).delete()

        print u'All entries found were delete successfully'
