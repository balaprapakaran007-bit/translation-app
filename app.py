"""
Language Translation Application
A college mini-project demonstrating Google Cloud Translation API (v3) integration with Streamlit.
"""

import os
import logging
from typing import Optional, Tuple

import streamlit as st
from dotenv import load_dotenv

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("language_translator")

# Load environment variables from .env file
load_dotenv()

# ==============================================================================
# Supported Languages Configuration
# ==============================================================================
# Human-readable name to official ISO 639-1 / BCP-47 language code mapping
SUPPORTED_LANGUAGES = {
    "English": "en",
    "Tamil": "ta",
    "Hindi": "hi",
    "Telugu": "te",
    "Malayalam": "ml",
    "Kannada": "kn",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Japanese": "ja",
    "Chinese (Simplified)": "zh-CN",
    "Arabic": "ar",
    "Korean": "ko",
    "Portuguese": "pt",
    "Italian": "it",
}

# Reverse mapping for displaying detected language names
CODE_TO_LANGUAGE = {code: name for name, code in SUPPORTED_LANGUAGES.items()}
# Additional common aliases for detected code fallback
CODE_TO_LANGUAGE.update({
    "zh": "Chinese (Simplified)",
    "zh-Hans": "Chinese (Simplified)",
})

SOURCE_OPTIONS = ["Auto Detect"] + list(SUPPORTED_LANGUAGES.keys())
TARGET_OPTIONS = list(SUPPORTED_LANGUAGES.keys())
MAX_CHARACTERS = 5000


# ==============================================================================
# Helper Functions
# ==============================================================================
def get_configured_project_id() -> Optional[str]:
    """Retrieve Google Cloud Project ID from environment variables."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
    if project_id and project_id.strip() and not project_id.startswith("your-google-cloud"):
        return project_id.strip()
    return None


def get_configured_api_key() -> Optional[str]:
    """Retrieve Google Cloud API Key from environment variables."""
    key = os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_CLOUD_API_KEY")
    if key and key.strip() and not key.startswith("your-api-key"):
        return key.strip()
    return None


def translate_text_v3(
    text: str,
    target_language_code: str,
    source_language_code: Optional[str] = None,
    project_id: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Tuple[str, Optional[str]]:
    """
    Translates text using Google Cloud Translation API v3.

    Args:
        text: The input text string to translate.
        target_language_code: Target BCP-47 language code (e.g., 'ta').
        source_language_code: Optional source BCP-47 language code (e.g., 'en').
                             If None, the API performs automatic language detection.
        project_id: The Google Cloud Project ID.
        api_key: Optional Google Cloud API Key.

    Returns:
        Tuple of (translated_text, detected_source_language_code)
    """
    if not project_id:
        raise ValueError(
            "Google Cloud Project ID is missing. Please set GOOGLE_CLOUD_PROJECT in your .env file or environment."
        )

    # Import google cloud translate client library
    from google.cloud import translate_v3 as translate
    from google.api_core.client_options import ClientOptions

    # Initialize client with optional API key via ClientOptions
    if api_key:
        client = translate.TranslationServiceClient(client_options=ClientOptions(api_key=api_key))
    else:
        client = translate.TranslationServiceClient()

    # API v3 parent resource path
    parent = f"projects/{project_id}/locations/global"

    logger.info(
        "Sending translation request: project=%s, target=%s, source=%s, char_len=%d, has_api_key=%s",
        project_id,
        target_language_code,
        source_language_code or "auto-detect",
        len(text),
        bool(api_key),
    )

    # Build request parameters according to API v3 specification
    request_params = {
        "parent": parent,
        "contents": [text],
        "mime_type": "text/plain",
        "target_language_code": target_language_code,
    }

    # Only pass source_language_code if explicitly provided (not Auto Detect)
    if source_language_code:
        request_params["source_language_code"] = source_language_code

    # Execute translation request
    response = client.translate_text(request=request_params)

    if not response.translations:
        raise RuntimeError("Google Cloud Translation API returned an empty translation list.")

    primary_translation = response.translations[0]
    translated_text = primary_translation.translated_text
    detected_language = primary_translation.detected_language_code or None

    logger.info(
        "Translation successful: detected_source=%s, result_len=%d",
        detected_language,
        len(translated_text),
    )

    return translated_text, detected_language



# ==============================================================================
# Streamlit User Interface
# ==============================================================================
def init_session_state():
    """Initialize Streamlit session state keys if not already present."""
    if "input_text" not in st.session_state:
        st.session_state["input_text"] = ""
    if "translation_result" not in st.session_state:
        st.session_state["translation_result"] = None
    if "detected_language" not in st.session_state:
        st.session_state["detected_language"] = None
    if "last_target_lang" not in st.session_state:
        st.session_state["last_target_lang"] = None


def clear_inputs():
    """Reset the input and translation state."""
    st.session_state["input_text"] = ""
    st.session_state["translation_result"] = None
    st.session_state["detected_language"] = None
    st.session_state["last_target_lang"] = None


def main():
    st.set_page_config(
        page_title="Language Translation Application",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_session_state()

    # Custom styling with clean blue accents and modern card containers
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 2.2rem;
            font-weight: 700;
            color: #1E3A8A;
            margin-bottom: 0.2rem;
        }
        .sub-header {
            font-size: 1.05rem;
            color: #4B5563;
            margin-bottom: 1.5rem;
        }
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
        }
        .status-badge-ok {
            background-color: #DEF7EC;
            color: #03543F;
        }
        .status-badge-warn {
            background-color: #FEF08A;
            color: #713F12;
        }
        .result-container {
            background-color: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
        }
        .char-counter {
            font-size: 0.85rem;
            color: #64748B;
            text-align: right;
            margin-top: -10px;
            margin-bottom: 15px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # Sidebar: Cloud Configuration & Demonstration Info
    # --------------------------------------------------------------------------
    project_id = get_configured_project_id()
    api_key = get_configured_api_key()

    with st.sidebar:
        st.title("⚙️ Cloud Setup")
        st.caption("College Mini-Project Demonstration")

        st.markdown("### Google Cloud Status")
        if project_id:
            st.success(f"**Project ID:** `{project_id}`")
        else:
            st.warning("⚠️ **Project ID:** Not configured")
            st.info(
                "Configure your project ID in the `.env` file:\n"
                "```bash\n"
                "GOOGLE_CLOUD_PROJECT=your-project-id\n"
                "```"
            )

        if api_key:
            masked_key = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "******"
            st.success(f"**API Key:** `{masked_key}`")
        else:
            st.caption("🔑 API Key: None (Using ADC credentials)")

        st.markdown("---")
        st.markdown("### 🔐 Authentication Guide")
        st.markdown(
            """
            This app uses **Google Cloud Application Default Credentials (ADC)**.

            **To log in locally:**
            ```powershell
            gcloud auth application-default login
            ```

            **To verify your project:**
            ```powershell
            gcloud config set project YOUR_PROJECT_ID
            ```
            """
        )

        st.markdown("---")
        st.markdown("### 📚 Project Architecture")
        st.markdown(
            """
            - **Frontend:** Streamlit
            - **Backend:** Python 3.12
            - **Cloud Service:** Google Cloud Translation API v3
            - **Library:** `google-cloud-translate`
            """
        )

    # --------------------------------------------------------------------------
    # Main Header
    # --------------------------------------------------------------------------
    st.markdown('<div class="main-header">🌐 Language Translation Application</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Translate text between languages using Google Cloud Translation API.</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # Language Selection (Side-by-Side Dropdowns)
    # --------------------------------------------------------------------------
    col_src, col_tgt = st.columns(2)

    with col_src:
        source_label = st.selectbox(
            "Source Language",
            options=SOURCE_OPTIONS,
            index=1,  # Default: English
            help="Choose the language of your input text or select Auto Detect.",
        )

    with col_tgt:
        # Default: Tamil (index 1 in SUPPORTED_LANGUAGES)
        default_target_idx = TARGET_OPTIONS.index("Tamil") if "Tamil" in TARGET_OPTIONS else 0
        target_label = st.selectbox(
            "Target Language",
            options=TARGET_OPTIONS,
            index=default_target_idx,
            help="Choose the language you want to translate the text into.",
        )

    # Validation: warn if user picks same explicit language
    if source_label != "Auto Detect" and source_label == target_label:
        st.warning(f"⚠️ Source and Target languages are both set to **{source_label}**. Please choose a different target language.")

    # --------------------------------------------------------------------------
    # Text Input Section
    # --------------------------------------------------------------------------
    user_input = st.text_area(
        label="Enter text to translate",
        value=st.session_state["input_text"],
        placeholder="Type or paste your text here...",
        height=180,
        max_chars=MAX_CHARACTERS,
        key="text_area_input",
    )

    # Keep session state updated with text area value
    st.session_state["input_text"] = user_input

    # Character count indicator
    current_char_count = len(user_input)
    st.markdown(
        f'<div class="char-counter">Character count: {current_char_count} / {MAX_CHARACTERS}</div>',
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------------------------
    # Action Buttons: Translate & Clear
    # --------------------------------------------------------------------------
    col_btn_trans, col_btn_clear, _ = st.columns([1.5, 1, 4])

    with col_btn_trans:
        translate_clicked = st.button("🚀 Translate Text", type="primary", use_container_width=True)

    with col_btn_clear:
        clear_clicked = st.button("🧹 Clear", on_click=clear_inputs, use_container_width=True)

    # --------------------------------------------------------------------------
    # Translation Processing
    # --------------------------------------------------------------------------
    if translate_clicked:
        # 1. Validate empty or whitespace input
        trimmed_input = user_input.strip()
        if not trimmed_input:
            st.error("❌ Please enter text to translate. Empty or whitespace-only input is not allowed.")
            return

        # 2. Validate identical explicit languages
        if source_label != "Auto Detect" and source_label == target_label:
            st.error("❌ Source and target languages cannot be identical. Please select different languages.")
            return

        # 3. Check Google Cloud Project ID
        if not project_id:
            st.error(
                "❌ **Google Cloud Project ID is not configured.**\n\n"
                "Please add your project ID to the `.env` file in the project folder:\n"
                "```bash\n"
                "GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id\n"
                "```\n"
                "Then refresh the application."
            )
            return

        # 4. Prepare language codes
        source_code = None if source_label == "Auto Detect" else SUPPORTED_LANGUAGES[source_label]
        target_code = SUPPORTED_LANGUAGES[target_label]

        # 5. Call Google Cloud Translation API with proper error handling
        with st.spinner("Translating text using Google Cloud Translation API..."):
            try:
                translated_text, detected_code = translate_text_v3(
                    text=trimmed_input,
                    target_language_code=target_code,
                    source_language_code=source_code,
                    project_id=project_id,
                    api_key=api_key,
                )

                # Store successful results in session state
                st.session_state["translation_result"] = translated_text
                st.session_state["detected_language"] = detected_code
                st.session_state["last_target_lang"] = target_label

            except ImportError as ie:
                logger.error("Missing dependency: %s", str(ie), exc_info=True)
                st.error("❌ Google Cloud client library is not installed. Run `pip install -r requirements.txt`.")

            except Exception as e:
                # Import exceptions safely for classification
                try:
                    from google.api_core import exceptions as g_exc
                    from google.auth import exceptions as a_exc
                except ImportError:
                    g_exc = None
                    a_exc = None

                logger.error("Translation API failure: %s", str(e), exc_info=True)

                if a_exc and isinstance(e, a_exc.DefaultCredentialsError):
                    st.error(
                        "❌ **Google Cloud Authentication Error:**\n\n"
                        "Application Default Credentials were not found. "
                        "Please authenticate using the Google Cloud CLI:\n\n"
                        "```powershell\n"
                        "gcloud auth application-default login\n"
                        "```\n"
                        "Or set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to a valid service account key."
                    )
                elif g_exc and isinstance(e, g_exc.PermissionDenied):
                    st.error(
                        "❌ **Permission Denied / API Not Enabled:**\n\n"
                        "1. Verify that **Cloud Translation API** is enabled in your Google Cloud project.\n"
                        "2. Ensure billing is enabled for your project.\n"
                        "3. Ensure your account/service account has the **Cloud Translation API User** (`roles/cloudtranslate.user`) role."
                    )
                elif g_exc and isinstance(e, g_exc.NotFound):
                    st.error(
                        f"❌ **Project Not Found:**\n\n"
                        f"The project ID `{project_id}` could not be found or parent location is invalid. Check `GOOGLE_CLOUD_PROJECT` in `.env`."
                    )
                elif g_exc and isinstance(e, g_exc.InvalidArgument):
                    st.error(
                        f"❌ **Invalid Argument:**\n\n"
                        f"Google Cloud Translation API rejected one of the parameters (e.g. invalid language code): {e.message}"
                    )
                elif g_exc and isinstance(e, g_exc.ResourceExhausted):
                    st.error(
                        "❌ **Quota Exceeded:**\n\n"
                        "You have exceeded your Google Cloud Translation API quota or billing limit."
                    )
                elif g_exc and isinstance(e, (g_exc.ServiceUnavailable, g_exc.DeadlineExceeded, g_exc.RetryError)):
                    st.error(
                        "❌ **Network / Timeout Error:**\n\n"
                        "Failed to communicate with Google Cloud servers. Please check your internet connection."
                    )
                else:
                    st.error(f"❌ **Translation Error:** {str(e)}")

    # --------------------------------------------------------------------------
    # Translation Result Display
    # --------------------------------------------------------------------------
    if st.session_state["translation_result"]:
        st.markdown("---")
        st.subheader("📋 Translation Result")

        detected = st.session_state["detected_language"]
        detected_display = ""
        if detected:
            friendly_name = CODE_TO_LANGUAGE.get(detected, detected)
            detected_display = f" | Detected Source: **{friendly_name} (`{detected}`)**"

        st.caption(
            f"Target: **{st.session_state.get('last_target_lang', target_label)} (`{SUPPORTED_LANGUAGES.get(st.session_state.get('last_target_lang', target_label), '')}`)**{detected_display}"
        )

        # Display result in clear copy-friendly container
        st.text_area(
            label="Translated Text",
            value=st.session_state["translation_result"],
            height=160,
            help="You can select and copy the translated text from this field.",
            disabled=False,
            key="result_display_area",
        )

        # Also provide a code-box display for single-click copy
        with st.expander("📄 Click here for one-click copy box", expanded=False):
            st.code(st.session_state["translation_result"], language=None)


if __name__ == "__main__":
    main()
