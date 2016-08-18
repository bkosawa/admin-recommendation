import sys
from datetime import datetime

import requests
from lxml import html

from crawler.models import App, AppDescription, Category, CategoryDescription, Developer

DETAILS_URL = 'https://play.google.com/store/apps/details?id={}&hl={}'
DATE_MASK = {'en': '%B %d, %Y', 'pt_BR': '%d de %B de %Y'}


def get_details(app_package, loc):
    url = DETAILS_URL.format(app_package, loc)

    try:
        response = requests.get(url, timeout=1.0)
    except requests.exceptions.Timeout as e:
        print('Timeout Error\n' + str(e))
        return
    except requests.exceptions.ConnectionError as e:
        print ('Connection Err\n' + str(e))
        sys.exit(-1)

    content = html.fromstring(response.text)

    name = extract_name(content)

    description = extract_description(content)

    icon_url = extract_icon_url(content)

    category_key = extract_category_key(content)

    category = extract_category_desc(content)

    developer = extract_developer(content)

    file_size = extract_file_size(content)

    update_date = extract_update_date(content, loc)

    version = extract_version(content)

    rating = extract_rating(content)

    content_rating = extract_content_rating(content)

    return App(app_package,
               [AppDescription(name, description, loc)],
               icon_url,
               [Category(category_key, [CategoryDescription(category, loc)])],
               Developer(developer),
               file_size,
               update_date,
               version,
               rating,
               content_rating)


def extract_name(content):
    return content.xpath('//div[@class="id-app-title"]')[0].text_content()
    # names = content.xpath('//div[@class="id-app-title"]')
    # if names:
    #     name = names[0].text_content()
    # return name


def extract_description(content):
    return content.xpath('//div[@itemprop="description"]')[0].text_content().strip()
    # descriptions = content.xpath('//div[@itemprop="description"]')
    # if descriptions:
    #     description = descriptions[0].text_content()
    # return description


def extract_icon_url(content):
    return "http:{}".format(content.xpath('//img[@class="cover-image"]/@src')[0])


def extract_update_date(content, loc):
    return datetime.strptime(content.xpath('//div[@itemprop="datePublished"]')[0].text_content(), DATE_MASK[loc])
    # update_dates = content.xpath('//div[@itemprop="datePublished"]')
    # if update_dates:
    #     update_date_str = update_dates[0].text_content()
    #     update_date = datetime.strptime(update_date_str, DATE_MASK[loc])
    # return update_date


def extract_content_rating(content):
    return content.xpath('//div[@itemprop="contentRating"]')[0].text_content()
    # content_rating = content.xpath('//div[@itemprop="contentRating"]')
    # if content_rating:
    #     content_rating = content_rating[0].text_content()
    # return content_rating


def extract_file_size(content):
    # return content.xpath('//div[@itemprop="fileSize"]')[0].text_content().strip()
    size = 0
    sizes = content.xpath('//div[@itemprop="fileSize"]')
    if sizes:
        size = sizes[0].text_content()
    return size


def extract_version(content):
    # return content.xpath('//div[@itemprop="softwareVersion"]')[0].text_content().strip()
    version = 0
    versions = content.xpath('//div[@itemprop="softwareVersion"]')
    if versions:
        version = versions[0].text_content()
    return version


def extract_rating(content):
    return content.xpath('//div[@class="score"]')[0].text_content()
    # ratings = content.xpath('//div[@class="score"]')
    # if ratings:
    #     rating = ratings[0].text_content()
    # return rating


def extract_developer(content):
    return content.xpath('//a[@class="document-subtitle primary"]/span[@itemprop="name"]')[0].text_content()
    # developers = content.xpath('//a[@class="document-subtitle primary"]/span[@itemprop="name"]')
    # if developers:
    #     developer = developers[0].text_content()
    # return developer


def extract_category_desc(content):
    return content.xpath('//span[@itemprop="genre"]')[0].text_content()
    # categories = content.xpath('//span[@itemprop="genre"]')
    # if categories:
    #     category = categories[0].text_content()
    # return category


def extract_category_key(content):
    return content.xpath('//a[@class="document-subtitle category"]/@href')[0].split('/')[-1]
    # category_urls = content.xpath('//a[@class="document-subtitle category"]/@href')
    # if category_urls:
    #     category_url = category_urls[0]
    #     category_key = category_url.split('/')[-1]
    # return category_key


# def validate_app(app):
#     a = db.query(App).filter_by(package_name=app.package_name).first()
#     if a:
#         found_app_desc = False
#         for index, app_desc in enumerate(a.descriptions):
#             if app_desc.loc == app.descriptions[0].loc:
#                 app.descriptions[index] = app.descriptions[0]
#                 found_app_desc = True
#                 break
#
#         if not found_app_desc:
#             a.descriptions.add(app.descriptions)
#     c = db.query(Category).filter_by(key=app.categories[0].key).first()
#     if c:
#         found_cat_desc = False
#         for index, cat_desc in enumerate(c.descriptions):
#             if cat_desc.loc == app.categories[0].descriptions[0].loc:
#                 c.descriptions[index] = app.categories[0].descriptions[0]
#                 found_cat_desc = True
#                 break
#
#         if not found_cat_desc:
#             c.add(app.categories[0].descriptions[0])
#
#         app.categories[0] = c
#     d = db.query(Developer).filter_by(name=app.developer.name).first()
#     if d:
#         app.developer_id = d.id
#         app.developer = d
#     if a:
#         app = a
#     return app


def craw_for_app():
    try:
        with open('apps-id-list', 'r') as aid:
            app_packages = [i for i in aid.read().split('\n')]

        try:
            for app_package in app_packages:
                app = get_details(app_package, 'en')
                app.save()
                # try:
                #     with DbManager() as db:
                #         validate_app(app).save(db)
                #
                # except Exception as exception:
                #     print("Error inserting on database.", exception)

        except IOError as e:
            print('Error on parsing')
            pass

        print "{} app data collected".format(len(app_packages))
    except IOError:
        print('Error')
