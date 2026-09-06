import os
import unittest
from unittest.mock import patch

from config import settings


class SettingsTests(unittest.TestCase):
    def test_streamlit_secret_takes_precedence_over_environment(self):
        with patch.object(settings, "_streamlit_secret", return_value=" cloud-key "):
            with patch.dict(os.environ, {"GEMINI_API_KEY": "local-key"}):
                self.assertEqual(settings._config_value("GEMINI_API_KEY"), "cloud-key")

    def test_environment_is_used_when_streamlit_secret_is_missing(self):
        with patch.object(settings, "_streamlit_secret", return_value=None):
            with patch.dict(os.environ, {"GEMINI_API_KEY": " local-key "}):
                self.assertEqual(settings._config_value("GEMINI_API_KEY"), "local-key")


if __name__ == "__main__":
    unittest.main()
