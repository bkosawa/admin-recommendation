import numpy as np
from django.test import SimpleTestCase
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


class AppClassifierTest(SimpleTestCase):
    def setUp(self):
        self.categories = get_categories()
        self.developers = get_developers()
        self.apps = get_mocked_apps()
        self.classifier = AppClassifier(self.apps, self.categories, self.developers)

    def test_create_matrix(self):
        rows = len(self.apps)
        cols = len(self.categories.keys()) + len(self.developers.keys())
        expected_matrix = get_expected_matrix(rows, cols)

        matrix = self.classifier.create_utility_matrix()

        self.assertTrue((matrix - expected_matrix).nnz == 0)

    def test_is_similar_with_two_non_zeros_and_the_same_array(self):
        u = dok_matrix((1, 10), dtype=np.int)
        v = dok_matrix((1, 10), dtype=np.int)

        u[0, 7] = 1
        u[0, 9] = 1

        v[0, 7] = 1
        v[0, 9] = 1

        self.assertTrue(self.classifier.is_similar(u, v, 0.6))

    def test_is_similar_with_two_non_zeros_and_one_equals(self):
        u = dok_matrix((1, 10), dtype=np.int)
        v = dok_matrix((1, 10), dtype=np.int)

        u[0, 7] = 1
        u[0, 9] = 1

        v[0, 2] = 1
        v[0, 9] = 1

        self.assertTrue(self.classifier.is_similar(u, v, 0.6))

    def test_is_similar_with_two_non_zeros_and_none_equals(self):
        u = dok_matrix((1, 10), dtype=np.int)
        v = dok_matrix((1, 10), dtype=np.int)

        u[0, 7] = 1
        u[0, 9] = 1

        v[0, 2] = 1
        v[0, 6] = 1

        self.assertFalse(self.classifier.is_similar(u, v, 0.6))
