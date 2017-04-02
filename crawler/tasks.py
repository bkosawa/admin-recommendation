import csv
import logging.config
from datetime import datetime

import numpy as np
import requests
from django.core.exceptions import ValidationError
from lxml import html
from scipy.sparse import dok_matrix
from sklearn.metrics import pairwise_distances

from admin_recommendation.celery import app
from crawler.models import App, AppDescription, Category, CategoryDescription, Developer, AppCategory, UserApps, \
    SimilarApp, User

logger = logging.getLogger(__name__)

DETAILS_URL = 'http://play.google.com/store/apps/details?id={}&hl={}'
DATE_MASK = {'en': '%B %d, %Y', 'pt_BR': '%d de %B de %Y'}


class Crawler:
    def __init__(self):
        pass

    def populate_category_description(self, content, category, loc):
        category_desc = CategoryDescription()
        category_desc.name = self.extract_category_desc(content)
        category_desc.locale = loc
        category_desc.category = category
        return category_desc

    def populate_category(self, content):
        category = Category()
        category.key = self.extract_category_key(content)
        return category

    def populate_app_description(self, content, app, loc):
        app_description = AppDescription()
        app_description.name = self.extract_name(content)
        app_description.description = self.extract_description(content)
        app_description.locale = loc
        app_description.app = app
        return app_description

    def populate_app(self, content, app_package, developer, loc):
        app = App()
        app.package_name = app_package
        app.icon_url = self.extract_icon_url(content)
        app.size = self.extract_file_size(content)
        app.publication_date = self.extract_update_date(content, loc)
        app.version = self.extract_version(content)
        app.rating = self.extract_rating(content)
        app.content_rating = self.extract_content_rating(content)
        app.developer = developer
        return app

    def populate_developer(self, content):
        developer = Developer()
        developer.name = self.extract_developer(content)
        return developer

    def populate_app_category(self, app, category):
        app_category = AppCategory()
        app_category.app = app
        app_category.category = category
        return app_category

    @staticmethod
    def extract_name(content):
        # return content.xpath('//div[@class="id-app-title"]')[0].text_content()
        name = ''
        names = content.xpath('//div[@class="id-app-title"]')
        if names:
            name = names[0].text_content().strip()
        return name.encode('utf-8')

    @staticmethod
    def extract_description(content):
        # return content.xpath('//div[@itemprop="description"]')[0].text_content().strip()
        description = ''
        descriptions = content.xpath('//div[@itemprop="description"]')
        if descriptions:
            description = descriptions[0].text_content().strip()
        return description.encode('utf-8')

    @staticmethod
    def extract_icon_url(content):
        return "http:{}".format(content.xpath('//img[@class="cover-image"]/@src')[0]).encode('utf-8')

    @staticmethod
    def extract_update_date(content, loc):
        # return datetime.strptime(content.xpath('//div[@itemprop="datePublished"]')[0].text_content(), DATE_MASK[loc])
        update_date = ''
        update_dates = content.xpath('//div[@itemprop="datePublished"]')
        if update_dates:
            update_date_str = update_dates[0].text_content().strip()
            update_date = datetime.strptime(update_date_str, DATE_MASK[loc])
        return update_date

    @staticmethod
    def extract_content_rating(content):
        # return content.xpath('//div[@itemprop="contentRating"]')[0].text_content()
        content_rating = ''
        content_ratings = content.xpath('//div[@itemprop="contentRating"]')
        if content_ratings:
            content_rating = content_ratings[0].text_content().strip()
        return content_rating

    @staticmethod
    def extract_file_size(content):
        # return content.xpath('//div[@itemprop="fileSize"]')[0].text_content().strip()
        size = 0
        sizes = content.xpath('//div[@itemprop="fileSize"]')
        if sizes:
            size = sizes[0].text_content().strip()
        return size

    @staticmethod
    def extract_version(content):
        # return content.xpath('//div[@itemprop="softwareVersion"]')[0].text_content().strip()
        version = 0
        versions = content.xpath('//div[@itemprop="softwareVersion"]')
        if versions:
            version = versions[0].text_content().strip()
        return version

    @staticmethod
    def extract_rating(content):
        # return content.xpath('//div[@class="score"]')[0].text_content()
        rating = ''
        ratings = content.xpath('//div[@class="score"]')
        if ratings:
            rating = ratings[0].text_content().strip()
        return rating

    @staticmethod
    def extract_developer(content):
        # return content.xpath('//a[@class="document-subtitle primary"]/span[@itemprop="name"]')[0].text_content()
        developer = ''
        developers = content.xpath('//a[@class="document-subtitle primary"]/span[@itemprop="name"]')
        if developers:
            developer = developers[0].text_content().strip()
        return developer.encode('utf-8')

    @staticmethod
    def extract_category_desc(content):
        # return content.xpath('//span[@itemprop="genre"]')[0].text_content()
        category = ''
        categories = content.xpath('//span[@itemprop="genre"]')
        if categories:
            category = categories[0].text_content().strip()
        return category.encode('utf-8')

    @staticmethod
    def extract_category_key(content):
        # return content.xpath('//a[@class="document-subtitle category"]/@href')[0].split('/')[-1]
        category_key = ''
        category_urls = content.xpath('//a[@class="document-subtitle category"]/@href')
        if category_urls:
            category_url = category_urls[0]
            category_key = category_url.split('/')[-1].strip()
        return category_key.encode('utf-8')

    @staticmethod
    def extract_similars(content):
        similars = content.xpath(
            '//div[@class="rec-cluster"]//div[@class="card no-rationale square-cover apps small"]/@data-docid')
        return similars

    def get_details(self, app_package, loc):
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

        developer = self.populate_developer(content)

        developer, developer_created = Developer.objects.get_or_create(
            name=developer.name,
        )

        app = self.populate_app(content, app_package, developer, loc)

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

        app_description = self.populate_app_description(content, app, loc)

        app_description = AppDescription.objects.get_or_create(
            app=app_description.app,
            locale=app_description.locale,
            defaults={
                'name': app_description.name,
                'description': app_description.description
            },
        )

        category = self.populate_category(content)

        category, category_created = Category.objects.get_or_create(
            key=category.key,
        )

        category_description = self.populate_category_description(content, category, loc)

        category_description, category_description_created = CategoryDescription.objects.get_or_create(
            category=category_description.category,
            locale=category_description.locale,
            defaults={
                'name': category_description.name
            }
        )

        app_category = self.populate_app_category(app, category)

        app_description, app_category = AppCategory.objects.get_or_create(
            app=app_category.app,
            category=app_category.category,
        )

        similars = self.extract_similars(content)

        return {'developer': developer,
                'app': app,
                'app_description': app_description,
                'category': category,
                'category_description': category_description,
                'similars': similars,
                }

    def crawl(self, app_packages, date):
        with open('error-apps-id-list-{}.txt'.format(date), 'w') as error_file, \
                open('similar-apps-{}.csv'.format(date), 'wb') as similar_file:
            crawled_count = 0
            total_count = 0
            for app_package in app_packages:
                package = app_package.rstrip()
                try:
                    total_count += 1
                    app_details_map = self.get_details(package, 'en')
                    if not app_details_map:
                        error_file.write(package + '\n')
                        print '{} Not Found'.format(package)
                        continue
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

            return crawled_count, total_count


def get_features_total_count(features):
    count = 0
    for feature_key in features.keys():
        count += len(features[feature_key])
    return count


class AppClassifier:
    apps_list = []
    features = dict()
    should_persist = False

    def __init__(self, apps, features=None, boundary=0.5, should_persist=False):
        if len(apps) < 2:
            raise ValueError("Invalid list of apps. It should have more than 1 element.")

        self.apps_list = apps
        if features:
            self.features = features
        self.similarity_boundary = boundary
        self.should_persist = should_persist

    def create_utility_matrix(self):
        app_count = len(self.apps_list)
        total_col = get_features_total_count(self.features)

        utility_matrix = dok_matrix((app_count, total_col), dtype=np.int)
        for mat_row, app in enumerate(self.apps_list):
            self.evaluate_category(app, mat_row, utility_matrix)

            self.evaluate_developer(app, mat_row, utility_matrix)

        return utility_matrix

    def evaluate_developer(self, app, mat_row, utility_matrix):
        dev_name = app.developer_name()
        mat_col2 = self.features['developer'][dev_name]
        utility_matrix[mat_row, mat_col2] = 1

    def evaluate_category(self, app, mat_row, utility_matrix):
        cat_key = app.category_key()

        if cat_key.startswith('GAME') and 'GAME' in self.features['category']:
            game_col = self.features['category']['GAME']
            utility_matrix[mat_row, game_col] = 1

        cat_col = self.features['category'][cat_key]
        utility_matrix[mat_row, cat_col] = 1

    def is_similar(self, u, v):
        cos_dist = self.cosine_distance(u, v)
        return cos_dist < self.similarity_boundary

    def is_close_enough(self, cos_dist):
        return cos_dist < self.similarity_boundary

    def find_similar_apps(self):
        logger.debug('Starting find_similar_apps_with_distance')
        similar_apps = []
        apps_count = len(self.apps_list)
        utility_matrix = self.create_utility_matrix()

        for i in range(0, apps_count - 1):
            for j in range(i + 1, apps_count):
                row = utility_matrix.getrow(i)
                other_row = utility_matrix.getrow(j)
                cos_dist = self.cosine_distance(other_row, row)
                if self.is_close_enough(cos_dist):
                    logger.debug('{} and {} - distance: {}'.format(self.apps_list[i], self.apps_list[j], cos_dist))
                    similar_apps.append((self.apps_list[i], self.apps_list[j], cos_dist))
                    if self.should_persist:
                        similar = SimilarApp()
                        similar.source_package = self.apps_list[i].package_name
                        similar.similar_package = self.apps_list[j].package_name
                        similar.distance = cos_dist

        logger.debug('Finished find_similar_apps_with_distance')
        return similar_apps

    @staticmethod
    def cosine_distance(other_row, row):
        return pairwise_distances(row, other_row, 'cosine')[0][0]


@app.task(name='recommend_to_user')
def recommend_to_user(user_id):
    # logger.info("finding user: {}".format(user_id))
    user = User.objects.get(id=user_id)
    user_apps = UserApps.objects.filter(user=user).all()
    apps = []
    for user_app in user_apps:
        package_name = user_app.package_name
        similar_apps = SimilarApp.objects.filter(source_package=package_name).all()
        for similar_app in similar_apps:
            similar_app_package = similar_app.similar_package
            if not UserApps.objects.filter(package_name=similar_app_package).exists():
                app_similar = App.objects.filter(package_name=similar_app_package).first()
                if app_similar:
                    apps.append(app_similar)
    if len(apps) > 0:
        user.recommended_apps = apps
        user.save()
