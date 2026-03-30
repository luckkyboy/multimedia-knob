import unittest

from pico.boot_logic import should_enable_write_mode, write_mode_indicator_colors


class BootLogicTests(unittest.TestCase):
    def test_button_held_enables_write_mode(self):
        self.assertTrue(should_enable_write_mode(button_value=False))

    def test_button_not_held_disables_write_mode(self):
        self.assertFalse(should_enable_write_mode(button_value=True))

    def test_write_mode_indicator_is_solid_red(self):
        self.assertEqual([0xFF0000], write_mode_indicator_colors())


if __name__ == "__main__":
    unittest.main()
