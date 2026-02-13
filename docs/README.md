# 🎬 Vikaspedia Automated Video Transcription System

## 📋 Project Overview

This system automates the transcription of educational videos for Vikaspedia. It leverages the **Google Gemini API** (Gemini 2.5 Flash) for high-accuracy, multilingual speech-to-text conversion, handling English, Hindi, and technical terminology in Agriculture and Health domains.

---

## ✨ Features

- **🎥 Video Processing:** Extracts audio from YouTube URLs or local uploads
- **🤖 AI Transcription:** Uses Gemini to generate verbatim, timestamped transcripts with speaker labels
- **✏️ Interactive Editor:** Web interface to view video side-by-side with transcript, edit text, and seek via timestamps
- **📥 Export:** Download transcripts as SRT, VTT, or TXT formats

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10+
- FFmpeg installed and added to system PATH

### Installation

1. **Create Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   - Rename `.env.example` to `.env`
   - Add your `GOOGLE_API_KEY`

### Running the Application

```bash
python run.py
```

---

## 📊 Repository Information

| Metric | Details |
|--------|---------|
| **Repository** | saad-0012/Transcription-System |
| **Language** | Python (99.5%) |
| **Type** | Educational Video Transcription Platform |

---

## 📝 License & Contributing

For more information, please refer to the project documentation or open an issue for questions and contributions.