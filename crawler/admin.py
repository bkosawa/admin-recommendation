# Register your models here.
from django.contrib import admin
from crawler import models


@admin.register(models.App)
class AppAdmin(admin.ModelAdmin):
    pass
    # actions = ['run_crawler']

    # def run_crawler(self):
    #     crawler.craw_for_app()
