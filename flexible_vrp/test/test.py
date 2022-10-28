from unittest import TestCase, main
from .. import FlexibleVRP
from ..tools import from_json


class TestModel(TestCase):
    test_data_path = "./flexible_vrp/test/test_data/"

    def test_empty_data(self):
        """
        Test for error if the data is empty.
        """
        data = {}
        config = {"solver": "basic_mip"}
        app = FlexibleVRP()
        self.assertRaises(ValueError, app.solve, data, config)

    def test_small_instance(self):
        """
        Test the model with a small instance.
        """
        # todo replace the small instance with a real small instance
        data = from_json(self.test_data_path + "small_instance.json")
        config = {"solver": "basic_mip"}
        # todo: replace that with the expected solution
        expected_solution = {"data": "This solver is not implemented yet"}
        app = FlexibleVRP()
        solution, checks, instance_checks, log_txt, log = app.solve(data, config)
        self.assertEqual(solution, expected_solution)


if __name__ == "__main__":
    main()
