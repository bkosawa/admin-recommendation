import csv
import sys
from datetime import datetime

import requests
from crawler.models import App, AppDescription, Category, CategoryDescription, Developer, AppCategory
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from lxml import html

DETAILS_URL = 'http://play.google.com/store/apps/details?id={}&hl={}'
DATE_MASK = {'en': '%B %d, %Y', 'pt_BR': '%d de %B de %Y'}


def populate_category_description(content, category, loc):
    category_desc = CategoryDescription()
    category_desc.name = extract_category_desc(content)
    category_desc.locale = loc
    category_desc.category = category
    return category_desc


def populate_category(content):
    category = Category()
    category.key = extract_category_key(content)
    return category


def populate_app_description(content, app, loc):
    app_description = AppDescription()
    app_description.name = extract_name(content)
    app_description.description = extract_description(content)
    app_description.locale = loc
    app_description.app = app
    return app_description


def populate_app(content, app_package, developer, loc):
    app = App()
    app.package_name = app_package
    app.icon_url = extract_icon_url(content)
    app.size = extract_file_size(content)
    app.publication_date = extract_update_date(content, loc)
    app.version = extract_version(content)
    app.rating = extract_rating(content)
    app.content_rating = extract_content_rating(content)
    app.developer = developer
    return app


def populate_developer(content):
    developer = Developer()
    developer.name = extract_developer(content)
    return developer


def populate_app_category(app, category):
    app_category = AppCategory()
    app_category.app = app
    app_category.category = category
    return app_category


def extract_name(content):
    # return content.xpath('//div[@class="id-app-title"]')[0].text_content()
    name = ''
    names = content.xpath('//div[@class="id-app-title"]')
    if names:
        name = names[0].text_content().strip()
    return name.encode('utf-8')


def extract_description(content):
    # return content.xpath('//div[@itemprop="description"]')[0].text_content().strip()
    description = ''
    descriptions = content.xpath('//div[@itemprop="description"]')
    if descriptions:
        description = descriptions[0].text_content().strip()
    return description.encode('utf-8')


def extract_icon_url(content):
    return "http:{}".format(content.xpath('//img[@class="cover-image"]/@src')[0]).encode('utf-8')


def extract_update_date(content, loc):
    # return datetime.strptime(content.xpath('//div[@itemprop="datePublished"]')[0].text_content(), DATE_MASK[loc])
    update_date = ''
    update_dates = content.xpath('//div[@itemprop="datePublished"]')
    if update_dates:
        update_date_str = update_dates[0].text_content().strip()
        update_date = datetime.strptime(update_date_str, DATE_MASK[loc])
    return update_date


def extract_content_rating(content):
    # return content.xpath('//div[@itemprop="contentRating"]')[0].text_content()
    content_rating = ''
    content_ratings = content.xpath('//div[@itemprop="contentRating"]')
    if content_ratings:
        content_rating = content_ratings[0].text_content().strip()
    return content_rating


def extract_file_size(content):
    # return content.xpath('//div[@itemprop="fileSize"]')[0].text_content().strip()
    size = 0
    sizes = content.xpath('//div[@itemprop="fileSize"]')
    if sizes:
        size = sizes[0].text_content().strip()
    return size


def extract_version(content):
    # return content.xpath('//div[@itemprop="softwareVersion"]')[0].text_content().strip()
    version = 0
    versions = content.xpath('//div[@itemprop="softwareVersion"]')
    if versions:
        version = versions[0].text_content().strip()
    return version


def extract_rating(content):
    # return content.xpath('//div[@class="score"]')[0].text_content()
    rating = ''
    ratings = content.xpath('//div[@class="score"]')
    if ratings:
        rating = ratings[0].text_content().strip()
    return rating


def extract_developer(content):
    # return content.xpath('//a[@class="document-subtitle primary"]/span[@itemprop="name"]')[0].text_content()
    developer = ''
    developers = content.xpath('//a[@class="document-subtitle primary"]/span[@itemprop="name"]')
    if developers:
        developer = developers[0].text_content().strip()
    return developer.encode('utf-8')


def extract_category_desc(content):
    # return content.xpath('//span[@itemprop="genre"]')[0].text_content()
    category = ''
    categories = content.xpath('//span[@itemprop="genre"]')
    if categories:
        category = categories[0].text_content().strip()
    return category.encode('utf-8')


def extract_category_key(content):
    # return content.xpath('//a[@class="document-subtitle category"]/@href')[0].split('/')[-1]
    category_key = ''
    category_urls = content.xpath('//a[@class="document-subtitle category"]/@href')
    if category_urls:
        category_url = category_urls[0]
        category_key = category_url.split('/')[-1].strip()
    return category_key.encode('utf-8')


def get_details(app_package, loc):
    url = DETAILS_URL.format(app_package, loc)

    try:
        response = requests.get(url, timeout=1.0)
        if response.status_code != 200:
            return
    except requests.exceptions.Timeout as e:
        print('Timeout Error\n' + str(e))
        return
    except requests.exceptions.ConnectionError as e:
        print ('Connection Err\n' + str(e))
        return

    content = html.fromstring(response.text)

    developer = populate_developer(content)

    developer, developer_created = Developer.objects.get_or_create(
        name=developer.name,
    )

    app = populate_app(content, app_package, developer, loc)

    app, app_created = App.objects.get_or_create(
        package_name=app.package_name,
        defaults={
            'icon_url': app.icon_url,
            'size': app.size,
            'publication_date': app.publication_date,
            'rating': app.rating,
            'version': app.version,
            'content_rating': app.content_rating,
            'developer': app.developer
        },
    )

    app_description = populate_app_description(content, app, loc)

    app_description = AppDescription.objects.get_or_create(
        app=app_description.app,
        locale=app_description.locale,
        defaults={
            'name': app_description.name,
            'description': app_description.description
        },
    )

    category = populate_category(content)

    category, category_created = Category.objects.get_or_create(
        key=category.key,
    )

    category_description = populate_category_description(content, category, loc)

    category_description, category_description_created = CategoryDescription.objects.get_or_create(
        category=category_description.category,
        locale=category_description.locale,
        defaults={
            'name': category_description.name
        }
    )

    app_category = populate_app_category(app, category)

    app_description, app_category = AppCategory.objects.get_or_create(
        app=app_category.app,
        category=app_category.category,
    )

    similars = extract_similars(content)

    return {'developer': developer,
            'app': app,
            'app_description': app_description,
            'category': category,
            'category_description': category_description,
            'similars': similars,
            }


def extract_similars(content):
    similars = content.xpath(
        '//div[@class="rec-cluster"]//div[@class="card no-rationale square-cover apps small"]/@data-docid')
    return similars


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
        with open('error-apps-id-list-{}.txt'.format(now), 'w') as error_file, \
                open('similar-apps-{}.csv'.format(now), 'wb') as similar_file:
            crawled_count = 0
            total_count = 0
            for app_package in app_packages:
                package = app_package.rstrip()
                try:
                    total_count += 1
                    app_details_map = get_details(package, 'en')
                    if not app_details_map:
                        error_file.write(package + '\n')
                        print '{} Not Found'.format(package)
                        continue
                    # print app_details_map
                    if app_details_map.get('similars'):
                        for similar in app_details_map.get('similars'):
                            csv_writer = csv.writer(similar_file, delimiter=';', quotechar='"',
                                                    quoting=csv.QUOTE_MINIMAL)
                            csv_writer.writerow([package, similar])
                    crawled_count += 1
                except IOError as e:
                    print('Error on parsing')
                    error_file.write(package + '\n')
                    pass
                except ValidationError as ve:
                    error_file.write(package + '\n')
                    print('Error on validation')
                    pass

            self.stdout.write(self.style.SUCCESS("{} app data collected from {}".format(crawled_count, total_count)))