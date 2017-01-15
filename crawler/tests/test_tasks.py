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
    matrix[1, 0] = 1
    matrix[1, 3] = 1
    matrix[2, 1] = 1
    matrix[2, 4] = 1
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
    developers['TOCA BOCA'] = 4
    return developers


def get_mocked_apps():
    app1 = App()
    app1.category_key = MagicMock(return_value='GAMES')
    app1.developer_name = MagicMock(return_value='EA')

    app2 = App()
    app2.category_key = MagicMock(return_value='GAMES')
    app2.developer_name = MagicMock(return_value='CAPCOM')

    app3 = App()
    app3.category_key = MagicMock(return_value='EDUCATIONAL')
    app3.developer_name = MagicMock(return_value='TOCA BOCA')

    apps = [app1, app2, app3]
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

    def test_find_similar_apps(self):
        expected_similar_apps = []
        similar_apps = self.classifier.find_similar_apps()

        self.assertEqual(similar_apps, expected_similar_apps)
