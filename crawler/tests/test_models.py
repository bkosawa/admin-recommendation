import numpy as np
from django.test.testcases import SimpleTestCase
from scipy.sparse import dok_matrix

from crawler.models import convert_from_sparse_array, convert_from_dict_string


class UtilityMatrixTest(SimpleTestCase):
    def test_utility_matrix_serialization_return_not_none(self):
        sparse_array = dok_matrix((10, 100), dtype=np.int8)
        serialized_array = convert_from_sparse_array(sparse_array)
        self.assertIsNotNone(serialized_array)

    def test_utility_matrix_empty_array_return_an_empty_string(self):
        expected_serialized_array = '{}'
        sparse_array = dok_matrix((1, 100), dtype=np.int8)
        serialized_array = convert_from_sparse_array(sparse_array)
        self.assertEqual(serialized_array, expected_serialized_array)

    def test_utility_matrix_one_element_array_return_an_dict_as_string(self):
        expected_serialized_array = '{(0, 40): 1}'
        sparse_array = dok_matrix((1, 100), dtype=np.int8)
        sparse_array[0, 40] = 1
        serialized_array = convert_from_sparse_array(sparse_array)
        self.assertEqual(serialized_array, expected_serialized_array)

    def test_utility_matrix_two_elements_array_return_an_dict_as_string(self):
        expected_serialized_array = '{(0, 40): 1, (0, 80): 1}'
        sparse_array = dok_matrix((1, 100), dtype=np.int8)
        sparse_array[0, 40] = 1
        sparse_array[0, 80] = 1
        serialized_array = convert_from_sparse_array(sparse_array)
        self.assertEqual(serialized_array, expected_serialized_array)

    def test_utility_matrix_two_elements_matrix_two_by_one_hundred_return_an_dict_as_string(self):
        expected_serialized_array = '{(1, 80): 1, (0, 40): 1}'
        sparse_array = dok_matrix((2, 100), dtype=np.int8)
        sparse_array[0, 40] = 1
        sparse_array[1, 80] = 1
        serialized_array = convert_from_sparse_array(sparse_array)
        self.assertEqual(serialized_array, expected_serialized_array)

    def test_utility_matrix_empty_string_to_sparse_matrix(self):
        serialized_dict = ''
        matrix = convert_from_dict_string(serialized_dict)
        self.assertTrue(matrix.nnz == 0)

    def test_utility_matrix_empty_dict_to_sparse_matrix(self):
        serialized_dict = '{}'
        matrix = convert_from_dict_string(serialized_dict)
        self.assertTrue(matrix.nnz == 0)
