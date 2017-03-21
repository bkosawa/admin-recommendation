import numpy as np
from django.test import SimpleTestCase
from mock import MagicMock
from scipy.sparse import dok_matrix

from crawler.models import App
from crawler.tasks import AppClassifier, get_features_total_count

TEST_SIMILARITY_BOUNDARY = 0.6


def get_expected_matrix(app_count, total_col):
    matrix = dok_matrix((app_count, total_col), dtype=np.int)
    matrix[0, 0] = 1
    matrix[0, 4] = 1
    matrix[0, 3] = 1

    matrix[1, 0] = 1
    matrix[1, 5] = 1
    matrix[1, 3] = 1

    matrix[2, 1] = 1
    matrix[2, 6] = 1

    matrix[3, 2] = 1
    matrix[3, 4] = 1
    matrix[3, 3] = 1
    return matrix


def get_categories():
    categories = dict()
    categories['GAME_ADVENTURE'] = 0
    categories['EDUCATIONAL'] = 1
    categories['GAME_EDUCATIONAL'] = 2
    categories['GAME'] = 3
    return categories


def get_developers():
    developers = dict()
    developers['EA'] = 4
    developers['CAPCOM'] = 5
    developers['TOCA BOCA'] = 6
    return developers


def get_features():
    features = dict()
    features['category'] = get_categories()
    features['developer'] = get_developers()
    return features


def get_mocked_apps():
    app1 = App()
    app1.category_key = MagicMock(return_value='GAME_ADVENTURE')
    app1.developer_name = MagicMock(return_value='EA')

    app2 = App()
    app2.category_key = MagicMock(return_value='GAME_ADVENTURE')
    app2.developer_name = MagicMock(return_value='CAPCOM')

    app3 = App()
    app3.category_key = MagicMock(return_value='EDUCATIONAL')
    app3.developer_name = MagicMock(return_value='TOCA BOCA')

    app4 = App()
    app4.category_key = MagicMock(return_value='GAME_EDUCATIONAL')
    app4.developer_name = MagicMock(return_value='EA')

    apps = [app1, app2, app3, app4]
    return apps


class AppClassifierTest(SimpleTestCase):
    def setUp(self):
        self.apps = get_mocked_apps()
        self.features = get_features()
        self.classifier = AppClassifier(self.apps, self.features)

    def test_create_matrix(self):
        rows = len(self.apps)
        cols = get_features_total_count(self.features)
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

        self.classifier.similarity_boundary = 0.6
        self.assertTrue(self.classifier.is_similar(u, v))

    def test_is_similar_with_two_non_zeros_and_one_equals(self):
        u = dok_matrix((1, 10), dtype=np.int)
        v = dok_matrix((1, 10), dtype=np.int)

        u[0, 7] = 1
        u[0, 9] = 1

        v[0, 2] = 1
        v[0, 9] = 1

        self.classifier.similarity_boundary = 0.6
        self.assertTrue(self.classifier.is_similar(u, v))

    def test_is_similar_with_two_non_zeros_and_none_equals(self):
        u = dok_matrix((1, 10), dtype=np.int)
        v = dok_matrix((1, 10), dtype=np.int)

        u[0, 7] = 1
        u[0, 9] = 1

        v[0, 2] = 1
        v[0, 6] = 1

        self.classifier.similarity_boundary = TEST_SIMILARITY_BOUNDARY
        self.assertFalse(self.classifier.is_similar(u, v))

    def test_find_similar_apps(self):
        expected_similar_apps = [(self.apps[0], self.apps[1], 0.33333333333333315),
                                 (self.apps[0], self.apps[3], 0.33333333333333315), ]
        similar_apps = self.classifier.find_similar_apps()

        self.assertEqual(similar_apps, expected_similar_apps)
