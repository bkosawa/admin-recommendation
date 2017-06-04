from django.core.management import BaseCommand

from crawler.models import *


class Command(BaseCommand):
    help = 'Calculate recommendation accuracy per user'

    def handle(self, *args, **options):
        result_dict = dict()
        users = User.objects.all()

        for user in users:
            count = 0
            recommended_apps = user.recommended_apps.all()
            recommended_apps_count = len(recommended_apps)
            for app in recommended_apps:
                if user.userapps_set.filter(package_name=app.package_name).exists():
                    count = count + 1

            percentage = float(count) / recommended_apps_count
            if percentage not in result_dict:
                result_count = 0
            else:
                result_count = result_dict[percentage]

            result_dict[percentage] = result_count + 1

        admin_file = open('recommendation_accuracy', 'w')
        admin_file.write('Percentage of Recommended Installed;Instances Count\n')
        for key in result_dict:
            admin_file.write('{};{}\n'.format(key, result_dict[key]))
        admin_file.close()
