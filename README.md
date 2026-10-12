# Language Translation Application using Google Cloud Translation API

A modern, beginner-friendly web application for real-time text translation across 15+ global and Indian languages, powered by **Python**, **Streamlit**, and **Google Cloud Translation API (v3)**.

Developed as a college mini-project demonstrating Cloud Computing and Cloud API Integration.

---

## 📌 Project Overview

In an increasingly interconnected world, language barriers hinder smooth communication and information access. Manual translation is slow and often inaccessible. 

This project demonstrates a production-grade cloud solution:
- Users enter or paste text into an intuitive web interface.
- Users select the source language (or choose **Auto Detect**) and the desired target language.
- The Python backend securely dispatches the request to the official **Google Cloud Translation API v3** using Application Default Credentials (ADC).
- The cloud translation engine translates the text and returns both the translated output and detected source language metadata, which is displayed in a copy-friendly interface.

---

## ✨ Features

- **Multi-Language Support:** Translates between English, Tamil, Hindi, Telugu, Malayalam, Kannada, French, German, Spanish, Japanese, Chinese (Simplified), Arabic, Korean, Portuguese, and Italian.
- **Smart Automatic Language Detection:** Detects the input language automatically when "Auto Detect" is chosen.
- **Official Google Cloud Translation API v3 Integration:** Uses the official `google-cloud-translate` Python SDK with standard parent resource paths (`projects/{project-id}/locations/global`).
- **Secure Cloud Authentication:** Connects seamlessly using Google Cloud Application Default Credentials (ADC) or optional service account key configurations. No hard-coded API keys or passwords.
- **Modern Responsive UI:** Built with Streamlit, featuring side-by-side dropdowns, live character counters, loading indicators, and clean blue-accent styling.
- **Real-Time Input Validation:** Rejects empty or whitespace-only inputs, prevents selecting identical explicit source and target languages, and enforces a 5,000-character safety limit.
- **Copy-Friendly Output:** Includes a dedicated text area and a 1-click code block for quick copying.
- **Comprehensive Error Handling:** Provides clear, user-friendly guidance for missing credentials, disabled APIs, billing restrictions, quota limits, or invalid project IDs without crashing the application.

---

## 🗂️ Project Structure

```
language-translator/
│
├── app.py              # Main Streamlit web application & translation logic
├── test_app.py         # Unit tests (validation, mocking, config tests)
├── requirements.txt    # Application dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules for secrets, virtual environments, and caches
├── README.md           # Documentation and setup guide
└── assets/             # Optional static assets
```

---

## ⚙️ Prerequisites

Before running the application, make sure you have:
1. **Python 3.10+** (Python 3.11 or 3.12 recommended) installed on your system.
2. A **Google Cloud Account** (Google Cloud free trial or standard tier).
3. A **Google Cloud Project** with billing enabled (Google Cloud Translation API requires an active billing account linked to the project, though Google offers free monthly tier quotas for translation).

---

## ☁️ Google Cloud Setup Guide

Follow these steps to set up Google Cloud for translation:

### 1. Create or Select a Project
1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Click the project dropdown at the top of the page and click **New Project**.
3. Name your project (e.g., `translation-demo-project`) and note down your **Project ID** (e.g., `translation-demo-project-123456`).

> [!NOTE]
> Creating a project does **not** automatically enable the Translation API or link billing. You must complete the steps below.

### 2. Enable Billing
1. Navigate to **Billing** in the Google Cloud Console.
2. Link an active billing account to your newly created project. Google Cloud provides a free tier covering up to 500,000 characters per month for Cloud Translation.

### 3. Enable Cloud Translation API
1. Navigate to **APIs & Services > Library**.
2. Search for **Cloud Translation API**.
3. Click **Cloud Translation API** and click **Enable**.

### 4. Install Google Cloud CLI (`gcloud`)
1. Download and install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install) if you have not already done so.
2. Open Windows PowerShell or your terminal and initialize `gcloud`:
   ```powershell
   gcloud init
   ```
3. Set your active project:
   ```powershell
   gcloud config set project YOUR_GOOGLE_CLOUD_PROJECT_ID
   ```

### 5. Authenticate with Application Default Credentials (ADC)
Run the following command to allow your local Python code to authenticate automatically:
```powershell
gcloud auth application-default login
```
A browser window will open. Sign in with your Google account and grant the requested permissions.

### 6. Verify IAM Permissions
Ensure your Google account (or service account) has the **Cloud Translation API User** role:
- Role name: `roles/cloudtranslate.user`
- You can check this under **IAM & Admin > IAM** in the Google Cloud Console.

---

## 💻 Local Installation (Windows PowerShell)

### Step 1: Open Terminal in the Project Directory
```powershell
cd language-translator
```

### Step 2: Create a Virtual Environment
```powershell
py -m venv .venv
```

### Step 3: Activate the Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

> [!TIP]
> If PowerShell shows an `Execution_Policies` script restriction error, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```
> Or use Command Prompt:
> ```cmd
> .venv\Scripts\activate.bat
> ```

### Step 4: Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

---

## 🔑 Environment Configuration

1. Copy the example environment file:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` in any text editor and replace the placeholder with your actual Google Cloud Project ID:
   ```env
   GOOGLE_CLOUD_PROJECT=your-google-cloud-project-id
   ```

> [!SECURITY]
> Never commit `.env` or any `.json` private keys to GitHub. The `.gitignore` file already excludes these sensitive files.

---

## 🚀 Running the Application

Launch the Streamlit web server:

```powershell
streamlit run app.py
```

Or using the explicit virtual environment executable:
```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

The application will open automatically in your browser at:
`http://localhost:8501`

---

## 🧪 Running Automated Tests

A dedicated test suite `test_app.py` is included to verify input validations, language code mappings, error handlers, and Google Cloud client request formatting using mocks:

```powershell
.\.venv\Scripts\python.exe -m unittest test_app.py
```

---

## 📝 Demonstration Example for College Evaluation

| Field | Sample Input / Value |
|---|---|
| **Source Language** | `English` (or `Auto Detect`) |
| **Input Text** | `Hello, how are you? Welcome to our college project demonstration.` |
| **Target Language** | `Tamil` |
| **Expected Translation** | `வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? எங்கள் கல்லூரி திட்ட விளக்கக்காட்சிக்கு வருக.` |

*(Note: The exact translated phrasing is generated dynamically by Google Cloud Translation API's neural machine translation engine and may vary).*

---

## 🛠️ Troubleshooting

| Issue | Likely Cause | Solution |
|---|---|---|
| `Application Default Credentials were not found` | ADC credentials token not present locally. | Run `gcloud auth application-default login` in your terminal. |
| `PermissionDenied: Cloud Translation API has not been used...` | Cloud Translation API is disabled. | Open Google Cloud Console > APIs & Services > Enable `Cloud Translation API`. |
| `Billing account not linked` | Project does not have active billing. | Link an active billing account in Google Cloud Console. |
| `PermissionDenied: 403 Forbidden` | Missing IAM role. | Grant `roles/cloudtranslate.user` to your user/service account in IAM settings. |
| `Project Not Found / Invalid Argument` | Incorrect `GOOGLE_CLOUD_PROJECT` value in `.env`. | Verify that the Project ID matches the exact ID shown in Google Cloud Console. |
| `ImportError: google.cloud.translate` | Dependencies not installed. | Run `pip install -r requirements.txt` within the virtual environment. |

---

## 🎓 College Demonstration Workflow

During your presentation, you can explain the system flow in 4 simple steps:

1. **User Interaction (Frontend):** The user enters text in Streamlit and selects languages. Streamlit validates character counts and input sanity.
2. **Configuration & Credentials (Security Layer):** Python reads `GOOGLE_CLOUD_PROJECT` from `.env` and uses Google's Application Default Credentials (ADC) without exposing any API keys in source code.
3. **Cloud Processing (API Integration):** The official `TranslationServiceClient` packages the text into an API v3 request and calls Google's global endpoint (`projects/{id}/locations/global`).
4. **Result Rendering (UI/UX):** Streamlit unpacks the neural machine translation response, identifies the detected language, and displays the translated text with instant one-click copying.
