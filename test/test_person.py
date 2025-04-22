import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from person_package import Person


class TestPerson(unittest.TestCase):

    @patch('utils.bbox_utils.get_center', return_value=(100, 150))
    @patch('utils.pixel_utils.get_axes_x_y_intersection_ratio', return_value=(0.5, 0.5))
    def test_person_initialization(self, mock_ratio, mock_center):
        # Fake input values
        id = 1
        bbox = (50, 100, 150, 200)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # Mocking a mini_map object
        mini_map = MagicMock()
        mini_map.map_start_x = 10
        mini_map.map_start_y = 20
        mini_map.draw_rect_width = 200
        mini_map.draw_rect_height = 100
        mini_map.padding_map = 5

        # Mock keypoints
        keypoints = [149, 187, 374, 191, 469, 313, 39, 301]

        # Create the Person object
        p = Person(id, bbox, frame, mini_map, keypoints)

        # Test ID and color
        self.assertEqual(p.get_id(), id)
        self.assertIsInstance(p.get_color(), tuple)
        self.assertEqual(len(p.get_color()), 3)

        # Test converted coordinates
        expected_x = 10 + 0.5 * (200 - 2 * 5)
        expected_y = 20 + 0.5 * (100 - 2 * 5)
        self.assertEqual(p.get_converted_coord(), (int(expected_x), int(expected_y)))

    def test_str_method(self):
        keypoints = [149, 187, 374, 191, 469, 313, 39, 301]

        p = Person(2, (10, 20, 30, 40), np.zeros((1, 1, 3)), MagicMock(), keypoints)
        str_repr = str(p)
        self.assertIn("Pers", str_repr)
        self.assertIn("at", str_repr)
        self.assertIn("with color", str_repr)


if __name__ == '__main__':
    unittest.main()