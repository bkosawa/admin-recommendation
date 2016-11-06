from django import forms

from crawler import models


class AppForm(forms.ModelForm):
    class Meta:
        model = models.App
        fields = '__all__'


class AppDescriptionForm(forms.ModelForm):
    class Meta:
        model = models.AppDescription
        fields = '__all__'