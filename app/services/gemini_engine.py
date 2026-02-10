
import google.generativeai as genai
import os
import re
import json
from app.core.config import settings

# Configure Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)

def transcribe_with_gemini(audio_path: str, language: str = "en"):
    """
    Uploads audio to Gemini and requests a structured transcription.
    Uses the exact prompt engineering patterns from Task_4.ipynb.
    """
    
    print(f"Uploading to Gemini: {audio_path}")
    uploaded_file = genai.upload_file(audio_path)
    
    # Use Gemini 1.5 Pro or Flash (Flash is faster/cheaper, Pro is smarter)
    # Task doc suggests evaluating models. 1.5 Flash is excellent for this.
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt_text = f"""
You are a professional multilingual speech transcription system for Vikaspedia.

TASK:
Transcribe the provided audio in {language} EXACTLY as spoken.

STRICT INSTRUCTIONS (DO NOT VIOLATE):
1. Verbatim transcription only (no paraphrasing).
2. Preserve Hindi, English, and Hinglish accurately.
3. Include automatic punctuation and capitalization.
4. Add timestamps in [MM:SS] format at least every 7–10 words or at natural pauses.
5. Label speakers strictly as Speaker 1, Speaker 2, etc.
6. Segment paragraphs based on natural speech patterns.
7. Use correct technical terms for Agriculture, Health, and Education contexts.
8. Output MUST follow the format below EXACTLY.

OUTPUT FORMAT (MANDATORY):

### Interactive Transcript
[00:00] Speaker 1: Start of the sentence...
[00:05] Speaker 1: ...continuation or new sentence.
[00:12] Speaker 2: Response from second speaker.

### Summary
Write a concise 3–5 sentence summary of the content.
"""

    try:
        print("Sending prompt to Gemini...")
        response = model.generate_content(
            [prompt_text, uploaded_file],
            request_options={"timeout": 600}
        )
        
        full_text = response.text.strip()
        
        # --- PARSING LOGIC (Adapted from Task_4.ipynb) ---
        
        # 1. Extract Summary
        summary_split = re.split(r"\n### Summary\n", full_text, flags=re.IGNORECASE)
        if len(summary_split) >= 2:
            interactive_part = summary_split[0].strip()
            summary_part = "\n".join(summary_split[1:]).strip()
        else:
            interactive_part = full_text
            summary_part = "Summary not found."

        # 2. Parse Segments (Timestamp, Speaker, Text)
        segments = []
        # Regex to capture [MM:SS] Speaker X: Text
        pattern = re.compile(r'^\[(\d{2}):(\d{2})\](?:\s+(Speaker\s+\d+):)?\s*(.*)$', re.MULTILINE)
        
        lines = interactive_part.split('\n')
        current_speaker = "Speaker 1"
        
        for line in lines:
            line = line.strip()
            # Skip header or empty lines
            if not line or "Interactive Transcript" in line:
                continue
                
            match = pattern.match(line)
            if match:
                mins = int(match.group(1))
                secs = int(match.group(2))
                start_seconds = mins * 60 + secs
                
                explicit_speaker = match.group(3)
                if explicit_speaker:
                    current_speaker = explicit_speaker
                
                text = match.group(4).strip()
                
                segments.append({
                    "start": start_seconds,
                    "speaker": current_speaker,
                    "text": text
                })
        
        # 3. Calculate end times
        for i in range(len(segments)):
            if i < len(segments) - 1:
                segments[i]["end"] = segments[i+1]["start"]
            else:
                segments[i]["end"] = segments[i]["start"] + 3.0  # Estimate last segment length

        return {
            "segments": segments,
            "summary": summary_part,
            "raw_text": interactive_part
        }

    except Exception as e:
        print(f"Gemini Error: {e}")
        raise e
    finally:
        # Cleanup remote file
        try:
            genai.delete_file(uploaded_file.name)
        except:
            pass
