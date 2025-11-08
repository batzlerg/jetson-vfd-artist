#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
from vfd_agent import clean_code, validate_syntax, validate_runtime, KeyboardListener

class TestVFDAgent(unittest.TestCase):

    def test_clean_code(self):
        # Test case 1: Valid code with function
        raw_code_1 = "```python\ndef my_animation(animator, duration):\n    animator.write_frame('Hello', 'World')\n```"
        expected_code_1 = "from cd5220 import DiffAnimator\nimport random\nimport math\n\ndef my_animation(animator, duration):\n    animator.write_frame('Hello', 'World')"
        code, error = clean_code(raw_code_1, "my_animation")
        self.assertEqual(code, expected_code_1)
        self.assertEqual(error, "")

        # Test case 2: Code without function
        raw_code_2 = "animator.write_frame('No', 'Function')"
        code, error = clean_code(raw_code_2, "my_animation")
        self.assertIsNone(code)
        self.assertEqual(error, "No function found")

        # Test case 3: Code missing write_frame
        raw_code_3 = "def my_animation(animator, duration):\n    pass"
        code, error = clean_code(raw_code_3, "my_animation")
        self.assertIsNone(code)
        self.assertEqual(error, "Missing write_frame")

    def test_validate_syntax(self):
        # Test case 1: Valid syntax
        valid_code = "def my_func():\n    return True"
        is_valid, error = validate_syntax(valid_code)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Test case 2: Invalid syntax
        invalid_code = "def my_func()\n    return True"
        is_valid, error = validate_syntax(invalid_code)
        self.assertFalse(is_valid)
        self.assertIn("expected ':'", error)

    @patch('vfd_agent.CD5220')
    def test_validate_runtime(self, mock_cd5220):
        # Test case 1: Valid runtime
        def valid_func(animator, duration):
            animator.write_frame('Hello', 'World')

        is_valid, error, _ = validate_runtime(valid_func, "valid_func")
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

        # Test case 2: Runtime error
        def error_func(animator, duration):
            raise ValueError("Test Error")

        is_valid, error, _ = validate_runtime(error_func, "error_func")
        self.assertFalse(is_valid)
        self.assertIn("Runtime crash: ValueError: Test Error", error)

    @patch('vfd_agent.print')
    @patch('vfd_agent.sys.stdin')
    @patch('vfd_agent.termios')
    @patch('vfd_agent.tty')
    @patch('vfd_agent.select')
    def test_keyboard_listener(self, mock_select, mock_tty, mock_termios, mock_stdin, mock_print):
        mock_stdin.isatty.return_value = True

        # --- Test for 'b' ---
        # This simulates select finding input on stdin just once.
        select_side_effects = [
            ([mock_stdin], [], []),
        ]
        # After the first call, it will keep returning empty list.
        mock_select.select.side_effect = lambda *args, **kwargs: select_side_effects.pop(0) if select_side_effects else ([], [], [])
        mock_stdin.read.return_value = 'b'

        listener = KeyboardListener()
        listener.start()
        import time
        time.sleep(0.1) # allow thread to run

        self.assertTrue(listener.check_and_clear())
        self.assertFalse(listener.bookmark_pressed)
        listener.stop()

        # --- Test for 'd' ---
        select_side_effects_d = [
            ([mock_stdin], [], []),
        ]
        mock_select.select.side_effect = lambda *args, **kwargs: select_side_effects_d.pop(0) if select_side_effects_d else ([], [], [])
        mock_stdin.read.return_value = 'd'

        listener = KeyboardListener()
        listener.start()
        time.sleep(0.1)

        self.assertTrue(listener.check_and_clear_downvote())
        self.assertFalse(listener.downvote_pressed)
        listener.stop()

if __name__ == '__main__':
    unittest.main()
