# Register your models here.
from django.contrib import admin
from crawler import models, forms


class AppDescriptionAdminInline(admin.TabularInline):
    extra = 0
    model = models.AppDescription


class CategoryDescriptionAdminInline(admin.TabularInline):
    extra = 0
    model = models.CategoryDescription


class CategoryAdminInline(admin.TabularInline):
    extra = 0
    model = models.AppCategory


@admin.register(models.App)
class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_name', 'version', 'developer')
    form = forms.AppForm
    inlines = [AppDescriptionAdminInline, CategoryAdminInline]

    # actions = ['run_crawler']

    # def run_crawler(self):
    #     crawler.craw_for_app()


@admin.register(models.GoogleSimilarApp)
class GoogleSimilarAppAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Developer)
class DeveloperAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [CategoryDescriptionAdminInline]