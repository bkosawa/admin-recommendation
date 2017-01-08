import numpy as np
from django.test import TestCase
from mock import MagicMock
from scipy.sparse import dok_matrix

from crawler.models import App
from crawler.tasks import AppClassifier


def get_expected_matrix(app_count, total_col):
    matrix = dok_matrix((app_count, total_col), dtype=np.int)
    matrix[0, 0] = 1
    matrix[0, 2] = 1
    return matrix


def get_categories():
    categories = dict()
    categories['GAMES'] = 0
    categories['EDUCATIONAL'] = 1
    return categories


def get_developers():
    developers = dict()
    developers['EA'] = 2
    developers['CAPCOM'] = 3
    return developers


def get_mocked_apps():
    app = App()
    app.category_key = MagicMock(return_value='GAMES')
    app.developer_name = MagicMock(return_value='EA')
    apps = [app]
    return apps


class AppClassifierTest(TestCase):
    def test_create_matrix(self):
        categories = get_categories()
        developers = get_developers()
        apps = get_mocked_apps()
        rows = len(apps)
        cols = len(categories.keys()) + len(developers.keys())
        expected_matrix = get_expected_matrix(rows, cols)

        classifier = AppClassifier(apps, categories, developers)
        matrix = classifier.create_utility_matrix()

        self.assertTrue((matrix - expected_matrix).nnz == 0)
