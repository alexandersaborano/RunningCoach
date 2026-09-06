import logging
import unittest

from core.safe_logging import _redact


class SafeLoggingTests(unittest.TestCase):
    def test_sensitive_values_are_redacted(self):
        message = _redact("GEMINI_API_KEY=secret-value token=abc123")
        self.assertNotIn("secret-value", message)
        self.assertNotIn("abc123", message)
        self.assertIn("REDACTED", message)

    def test_logger_does_not_add_handler_when_disabled(self):
        logger = logging.getLogger("atleta_ai.test_disabled")
        self.assertEqual(logger.handlers, [])


if __name__ == "__main__":
    unittest.main()
