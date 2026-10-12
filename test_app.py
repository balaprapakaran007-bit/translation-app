"""
Unit and integration tests for the Language Translation Application.
Verifies validation logic, environment handling, and translation workflows
using a mocked TranslationServiceClient without requiring live cloud credentials.
"""

import unittest
from unittest.mock import MagicMock, patch
import os
import sys

# Ensure application module is accessible
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import (
    SUPPORTED_LANGUAGES,
    CODE_TO_LANGUAGE,
    SOURCE_OPTIONS,
    TARGET_OPTIONS,
    get_configured_project_id,
    translate_text_v3,
)


class TestLanguageConfiguration(unittest.TestCase):
    """Test language mappings and option configurations."""

    def test_language_mappings_exist(self):
        """Ensure all required college project languages are configured."""
        required = [
            "English", "Tamil", "Hindi", "Telugu", "Malayalam", "Kannada",
            "French", "German", "Spanish", "Japanese", "Chinese (Simplified)",
            "Arabic", "Korean", "Portuguese", "Italian"
        ]
        for lang in required:
            self.assertIn(lang, SUPPORTED_LANGUAGES)
            self.assertTrue(len(SUPPORTED_LANGUAGES[lang]) >= 2)

    def test_defaults_and_options(self):
        """Ensure Auto Detect is in source options but NOT in target options."""
        self.assertIn("Auto Detect", SOURCE_OPTIONS)
        self.assertNotIn("Auto Detect", TARGET_OPTIONS)
        self.assertEqual(SUPPORTED_LANGUAGES["English"], "en")
        self.assertEqual(SUPPORTED_LANGUAGES["Tamil"], "ta")

    def test_reverse_mapping(self):
        """Ensure detected language code maps back to human-readable names."""
        self.assertEqual(CODE_TO_LANGUAGE.get("ta"), "Tamil")
        self.assertEqual(CODE_TO_LANGUAGE.get("en"), "English")


class TestProjectConfiguration(unittest.TestCase):
    """Test retrieval of Google Cloud Project ID."""

    @patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "demo-college-project-123"}, clear=True)
    def test_configured_project_id_present(self):
        self.assertEqual(get_configured_project_id(), "demo-college-project-123")

    @patch.dict(os.environ, {"GOOGLE_CLOUD_PROJECT": "your-google-cloud-project-id"}, clear=True)
    def test_placeholder_project_id_ignored(self):
        self.assertIsNone(get_configured_project_id())

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_project_id(self):
        self.assertIsNone(get_configured_project_id())


class TestTranslationLogic(unittest.TestCase):
    """Test translate_text_v3 with validation and mocked Google Cloud client."""

    def test_missing_project_id_raises_value_error(self):
        with self.assertRaises(ValueError) as context:
            translate_text_v3("Hello", target_language_code="ta", project_id=None)
        self.assertIn("Google Cloud Project ID is missing", str(context.exception))

    @patch("google.cloud.translate_v3.TranslationServiceClient")
    def test_successful_translation_with_explicit_source(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_translation = MagicMock()
        mock_translation.translated_text = "வணக்கம், எப்படி இருக்கிறீர்கள்?"
        mock_translation.detected_language_code = ""

        mock_response = MagicMock()
        mock_response.translations = [mock_translation]
        mock_client.translate_text.return_value = mock_response

        result_text, detected_code = translate_text_v3(
            text="Hello, how are you?",
            target_language_code="ta",
            source_language_code="en",
            project_id="test-proj-456",
        )

        self.assertEqual(result_text, "வணக்கம், எப்படி இருக்கிறீர்கள்?")
        self.assertIsNone(detected_code)

        # Verify correct parent resource path format and parameters
        mock_client.translate_text.assert_called_once()
        _, kwargs = mock_client.translate_text.call_args
        request = kwargs.get("request", {})
        self.assertEqual(request["parent"], "projects/test-proj-456/locations/global")
        self.assertEqual(request["contents"], ["Hello, how are you?"])
        self.assertEqual(request["target_language_code"], "ta")
        self.assertEqual(request["source_language_code"], "en")

    @patch("google.cloud.translate_v3.TranslationServiceClient")
    def test_successful_translation_with_auto_detect(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_translation = MagicMock()
        mock_translation.translated_text = "Hola, ¿cómo estás?"
        mock_translation.detected_language_code = "en"

        mock_response = MagicMock()
        mock_response.translations = [mock_translation]
        mock_client.translate_text.return_value = mock_response

        result_text, detected_code = translate_text_v3(
            text="Hello, how are you?",
            target_language_code="es",
            source_language_code=None,  # Auto detect
            project_id="test-proj-456",
        )

        self.assertEqual(result_text, "Hola, ¿cómo estás?")
        self.assertEqual(detected_code, "en")

        # Verify source_language_code was NOT passed in request
        _, kwargs = mock_client.translate_text.call_args
        request = kwargs.get("request", {})
        self.assertNotIn("source_language_code", request)

    @patch("google.cloud.translate_v3.TranslationServiceClient")
    def test_empty_translations_response(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        mock_response = MagicMock()
        mock_response.translations = []
        mock_client.translate_text.return_value = mock_response

        with self.assertRaises(RuntimeError) as context:
            translate_text_v3(
                text="Hello",
                target_language_code="ta",
                project_id="test-proj-456",
            )
        self.assertIn("empty translation list", str(context.exception))


if __name__ == "__main__":
    unittest.main()
