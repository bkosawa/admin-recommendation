import numpy as np
from django.test.testcases import SimpleTestCase
from scipy.sparse import dok_matrix

from crawler.models import convert_from_sparse_array


class UtilityMatrixTest(SimpleTestCase):
    def test_utility_matrix_serialization_return_not_none(self):
        sparse_array = dok_matrix((10, 100), dtype=np.int8)
        serialized_array = convert_from_sparse_array(sparse_array)
        self.assertIsNotNone(serialized_array)
