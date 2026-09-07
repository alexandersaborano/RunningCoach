import unittest

from core.heart_rate_zones import calcular_zonas_hrr


class HeartRateZonesTests(unittest.TestCase):
    def test_calculates_karvonen_upper_limits(self):
        self.assertEqual(calcular_zonas_hrr(190, 50), [134, 148, 162, 176, 190])

    def test_supports_custom_upper_boundaries(self):
        self.assertEqual(calcular_zonas_hrr(190, 50, (0.5, 0.8, 1.0)), [120, 162, 190])

    def test_rejects_invalid_range(self):
        with self.assertRaises(ValueError):
            calcular_zonas_hrr(50, 60)


if __name__ == "__main__":
    unittest.main()
