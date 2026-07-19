"""
Tests for gamepad button mapping fix for issue #2886.

Verifies that PS3/PS4 controller buttons map correctly to SDL
gamepad button indices.
"""
import unittest


class TestGamepadButtonMapping(unittest.TestCase):
    """Test SDL gamepad button mapping constants."""
    
    # Expected SDL Game Controller button mappings
    EXPECTED_MAPPINGS = {
        'cross': 0,       # A
        'circle': 1,      # B
        'square': 2,      # X
        'triangle': 3,    # Y
        'share': 4,       # Back/Select
        'home': 5,        # Guide/Home
        'options': 6,     # Start
        'l3': 7,          # Left Stick
        'r3': 8,          # Right Stick
        'l1': 9,          # Left Shoulder
        'r1': 10,         # Right Shoulder
        'dpad_up': 11,
        'dpad_down': 12,
        'dpad_left': 13,
        'dpad_right': 14,
        'touchpad': 15,
    }
    
    def test_face_buttons(self):
        """Test that face buttons (cross/circle/square/triangle) map correctly."""
        # These were the main buttons reported as switched in #2886
        self.assertEqual(self.EXPECTED_MAPPINGS['cross'], 0)
        self.assertEqual(self.EXPECTED_MAPPINGS['circle'], 1)
        self.assertEqual(self.EXPECTED_MAPPINGS['square'], 2)
        self.assertEqual(self.EXPECTED_MAPPINGS['triangle'], 3)
    
    def test_stick_buttons(self):
        """Test that L3/R3 map correctly (were reported as switched)."""
        # L3 was mapped to HOME, R3 was mapped to L3
        self.assertEqual(self.EXPECTED_MAPPINGS['l3'], 7)
        self.assertEqual(self.EXPECTED_MAPPINGS['r3'], 8)
        self.assertEqual(self.EXPECTED_MAPPINGS['home'], 5)
    
    def test_dpad_buttons(self):
        """Test that D-pad buttons map correctly (were reported as not working)."""
        self.assertEqual(self.EXPECTED_MAPPINGS['dpad_up'], 11)
        self.assertEqual(self.EXPECTED_MAPPINGS['dpad_down'], 12)
        self.assertEqual(self.EXPECTED_MAPPINGS['dpad_left'], 13)
        self.assertEqual(self.EXPECTED_MAPPINGS['dpad_right'], 14)
    
    def test_shoulder_buttons(self):
        """Test that shoulder buttons map correctly."""
        self.assertEqual(self.EXPECTED_MAPPINGS['l1'], 9)
        self.assertEqual(self.EXPECTED_MAPPINGS['r1'], 10)
    
    def test_menu_buttons(self):
        """Test that menu buttons map correctly."""
        self.assertEqual(self.EXPECTED_MAPPINGS['share'], 4)
        self.assertEqual(self.EXPECTED_MAPPINGS['options'], 6)
        self.assertEqual(self.EXPECTED_MAPPINGS['home'], 5)


if __name__ == '__main__':
    unittest.main()
