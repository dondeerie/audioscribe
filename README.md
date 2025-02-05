# AudioScribe

AudioScribe is a Python tool that transcribes audio interviews with speaker detection and generates structured summaries. It processes audio files using OpenAI's Whisper model and creates formatted transcripts with accurate timestamps and speaker attribution.

## Features
- Audio transcription with speaker detection
- Timestamp synchronization
- Automated summary generation
- Organized output structure
- Markdown formatting for summaries

## Project Structure
```
audioscribe/
├── src/              # Source code
├── audio/            # Audio files directory
├── output/           # Generated outputs
│   ├── transcripts/  # Formatted transcripts
│   └── summaries/    # Generated summaries
├── tests/            # Test files
└── requirements.txt  # Project dependencies
```

## Setup
1. Clone the repository
2. Create a virtual environment (recommended)
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with your API keys:
   OPENAI_API_KEY=your_key_here

## Usage
python src/transcribe.py

## Requirements
- Python 3.8+
- OpenAI API key
- pydub

## Installation
1. Clone this repository:
   git clone https://github.com/yourusername/audioscribe.git
   cd audioscribe

2. Create and activate virtual environment:
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Create .env file in project root and add your API key:
   OPENAI_API_KEY=your_key_here

## Dependencies
openai
python-dotenv
pydub
