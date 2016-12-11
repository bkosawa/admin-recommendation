# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class App(models.Model):
    package_name = models.CharField(unique=True, max_length=255)
    icon_url = models.CharField(max_length=200, blank=True, null=True)
    size = models.CharField(max_length=25, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    version = models.CharField(max_length=25, blank=True, null=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    content_rating = models.CharField(max_length=25, blank=True, null=True)
    developer = models.ForeignKey('Developer', models.CASCADE)

    class Meta:
        managed = False
        db_table = 'app'

    def __unicode__(self):
        return self.package_name

    def name(self):
        description = self.appdescription_set.filter(locale='en').all()
        if description:
            return u'{}'.format(description[0].name)
        return u''

    def category_key(self):
        category = self.appcategory_set.first().category
        if category:
            return u'{}'.format(category.key)
        return u''

    def developer_name(self):
        return self.developer.name

    # def __str__(self):
    #     return u'(id=' + str(self.id) + \
    #            ',\n package_name:' + str(self.package_name) + \
    #            ',\n icon_url:' + str(self.icon_url) + \
    #            ',\n developer:' + str(self.developer) + \
    #            ',\n size:' + str(self.size) + \
    #            ',\n publication date:' + str(self.publication_date) + \
    #            ',\n version:' + str(self.version) + \
    #            ',\n rating:' + str(self.rating) + \
    #            ',\n content_rating:' + str(self.content_rating) + \
    #            ')'


class AppCategory(models.Model):
    app = models.ForeignKey(App, models.CASCADE)
    category = models.ForeignKey('Category', models.CASCADE)

    class Meta:
        managed = False
        db_table = 'app_category'
        unique_together = (('app', 'category'),)


class AppDescription(models.Model):
    app = models.ForeignKey(App, models.CASCADE)
    locale = models.CharField(max_length=5)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_description'
        unique_together = (('app', 'locale'),)

    def __unicode__(self):
        return self.name

    # def __str__(self):
    #     return u'(locale:' + str(self.locale) + ', name:' + str(self.name) + ', description:' + str(
    #         self.description) + ')'


class Category(models.Model):
    key = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'category'

    def __unicode__(self):
        return self.key

    @staticmethod
    def get_category_list(start):
        category_keys = dict()
        categories = Category.objects.all().order_by('key')
        for category in categories:
            category_keys[category.key] = start
            start += 1
        return category_keys

    # def __str__(self):
    #     return u'(id:' + str(self.id) + ', key:' + str(self.key) + ')'


class CategoryDescription(models.Model):
    category = models.ForeignKey(Category, models.CASCADE)
    locale = models.CharField(max_length=5)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'category_description'
        unique_together = (('category', 'locale'),)

    def __unicode__(self):
        return self.name

    # def __str__(self):
    #     return u'(name:' + str(self.name) + ', locale:' + str(self.locale) + ')'


class Developer(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'developer'

    def __unicode__(self):
        return self.name

    # def __str__(self):
    #     return u'(id:' + str(self.id) + ', name:' + str(self.name) + ')'


class GoogleSimilarApp(models.Model):
    source_package = models.CharField(max_length=255)
    similar_package = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'google_similar_app'
        unique_together = (('source_package', 'similar_package'),)

    def __unicode__(self):
        return '{}, {}'.format(self.source_package, self.similar_package)
