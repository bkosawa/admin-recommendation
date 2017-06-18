from django.core.management import BaseCommand

from crawler.models import *


class Command(BaseCommand):
    help = 'Calculate recommendation accuracy per user'

    def handle(self, *args, **options):
        result_dict = dict()
        result_by_user_dict = dict()
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
            result_by_user_dict[user.id] = (count, recommended_apps_count, percentage)

        admin_file = open('recommendation_accuracy', 'w')
        admin_file.write('Percentage of Recommended Installed;Instances Count\n')
        for key in result_dict:
            admin_file.write('{};{}\n'.format(key, result_dict[key]))
        admin_file.close()

        admin_file = open('recommendation_accuracy_by_user', 'w')
        admin_file.write('User id;recommended_installed;recommended;ratio\n')
        for key in result_by_user_dict:
            data = result_by_user_dict[key]
            admin_file.write('{};{};{};{}\n'.format(key, data[0], data[1], data[2]))
        admin_file.close()
