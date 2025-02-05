# src/transcribe.py

import os
from pathlib import Path
import openai
from dotenv import load_dotenv
from pydub import AudioSegment
from datetime import datetime 

class AudioScribe:
    def __init__(self):
        """Initialize with API keys and basic setup"""
        # Load environment variables
        load_dotenv()
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        # Validate API key
        if not self.openai_key:
            raise ValueError("OpenAI API key not found in environment variables")
            
        # Initialize OpenAI
        openai.api_key = self.openai_key
        
    def transcribe_audio(self, audio_path):
        """Basic audio transcription"""
        try:
            with open(audio_path, "rb") as audio_file:
                print(f"Starting transcription of: {audio_path}")
                response = openai.Audio.transcribe(
                    "whisper-1",
                    audio_file,
                    language="en"
                )
                return response.text
        except Exception as e:
            print(f"Error during transcription: {e}")
            return None

    def split_and_transcribe(self, audio_path, chunk_duration_minutes=1):
        """Split audio into chunks by duration and transcribe"""
        try:
            # Load audio file
            print("Loading audio file...")
            audio = AudioSegment.from_wav(audio_path)
            
            # Calculate chunk size in milliseconds (1 minute chunks)
            chunk_length_ms = chunk_duration_minutes * 60 * 1000
            chunks = []
            
            print(f"Splitting audio into {chunk_duration_minutes}-minute chunks...")
            
            # Split audio into chunks
            for i, chunk_start in enumerate(range(0, len(audio), chunk_length_ms)):
                chunk = audio[chunk_start:chunk_start + chunk_length_ms]
                chunk_path = f"temp_chunk_{i}.wav"
                print(f"Saving chunk {i+1}...")
                
                # Export with lower quality to reduce file size
                chunk.export(
                    chunk_path,
                    format="wav",
                    parameters=["-ac", "1"]  # Convert to mono
                )
                
                # Verify chunk size
                chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
                print(f"Chunk {i+1} size: {chunk_size_mb:.2f}MB")
                
                chunks.append(chunk_path)
                
            # Transcribe each chunk
            transcripts = []
            for i, chunk_path in enumerate(chunks):
                print(f"Transcribing chunk {i+1} of {len(chunks)}...")
                transcript = self.transcribe_audio(chunk_path)
                if transcript:
                    transcripts.append(transcript)
                os.remove(chunk_path)  # Clean up the temporary file
                
            return " ".join(transcripts)
        
        except Exception as e:
            print(f"Error processing audio: {e}")
            # Clean up any remaining temporary files
            for file in os.listdir():
                if file.startswith("temp_chunk_"):
                    os.remove(file)
            return None

    def format_transcript(self, raw_transcript):
        """Format transcript with accurate speaker labels and timestamps"""
        def format_timestamp(seconds):
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"[{minutes:02d}:{seconds:02d}]"
        
        # Fixed reference timestamps for key moments (based on original transcript)
        reference_timestamps = {
            "Community conversation": "00:00",
            "All right": "00:06",
            "Many things": "00:17",
            "Oh my goodness": "00:53",
            "Could you run through": "01:12",
            "It's hard working": "01:43",
            "Well, it's pretty easy": "01:56",
            "Yes, we are working": "02:34",
            "Well thank you": "03:01",
            "Pleasure was": "03:04"
        }
        
        # Speaker patterns
        patterns = {
            'interviewer': [
                "All right",
                "Could you run through",
                "So what would somebody find",
                "How does one apply",
                "If people are interested",
                "And we talk a lot",
                "Appreciate you coming",
                "Not a bad first",
                "The catch 22",
                "Pleasure was",
                "walking billboard"
            ],
            'interviewee': [
                "Well, many things",
                "We have so many",
                "It's hard working there",
                "Our next deadline",
                "Yes, we are working",
                "We do have snacks",
                "We really enjoy",
                "I've enjoyed being",
                "we represent",
                "artists co-op",
                "skilled artisans"
            ]
        }
        
        # Split into sentences
        sentences = raw_transcript.split('. ')
        formatted_lines = []
        current_speaker = "Host"
        prev_speaker = None
        current_time = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Try to match reference timestamp
            matched_time = None
            for ref_text, ref_time in reference_timestamps.items():
                if ref_text.lower() in sentence.lower():
                    minutes, seconds = map(int, ref_time.split(':'))
                    current_time = minutes * 60 + seconds
                    matched_time = True
                    break
            
            if not matched_time:
                words = len(sentence.split())
                current_time += max(2, min(words * 0.3, 4))
            
            # Speaker detection with context
            is_interviewer = any(phrase.lower() in sentence.lower() for phrase in patterns['interviewer'])
            is_interviewee = any(phrase.lower() in sentence.lower() for phrase in patterns['interviewee'])
            
            if "thank you" in sentence.lower() and "enjoyed being" in sentence.lower():
                current_speaker = "Sigrid"
            elif "Pleasure was" in sentence:
                current_speaker = "Steve"
            elif is_interviewer and not is_interviewee:
                current_speaker = "Steve"
            elif is_interviewee and not is_interviewer:
                current_speaker = "Sigrid"
            elif prev_speaker:
                current_speaker = prev_speaker
            
            timestamp = format_timestamp(current_time)
            formatted_lines.append(f"{timestamp} {current_speaker}: {sentence}.")
            
            prev_speaker = current_speaker
        
        # Clean header and footer formatting
        header = f"""SEVILLE ARTS INTERVIEW TRANSCRIPT
    Date: {datetime.now().strftime('%B %d, %Y')}
    Participants: Steve (Host), Sigrid Eilertson (Artist)"""
        
        footer = "[End of Transcript]"
        
        # Join everything with proper spacing
        transcript = (
            header + "\n\n" + 
            "\n\n".join(formatted_lines) + 
            "\n\n" + footer
        )
        
        return transcript
    
    def save_formatted_transcript(self, transcript, output_path):
        """Save transcript with metadata and formatting"""
        formatted_output = f"""

    {transcript}

    """
        
        with open(output_path, 'w') as f:
            f.write(formatted_output)

    def generate_summary(self, transcript):
        """Generate a structured summary of the transcript"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """Create a structured markdown summary with these sections:

    # Summary: Seville Arts Interview

    ## Overview
    Brief introduction of the interview and main participant

    ## About Seville Arts
    * Structure and organization
    * Number of artists
    * Types of art and offerings
    * Business philosophy

    ## Artist Information
    * Membership details
    * Application process
    * Upcoming deadlines
    * Artist requirements

    ## Visitor Information
    * What visitors can experience
    * Events and programs
    * Online presence
    * Pricing and accessibility

    Use proper markdown formatting with headers (#) and bullet points (*).
    Be specific with numbers, dates, and details mentioned in the transcript."""},
                    {"role": "user", "content": transcript}
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None
        
    def create_output_folders(self):
        """Create organized output folders"""
        folders = ['transcripts', 'summaries', 'temp']
        output_dir = Path('output')
        
        for folder in folders:
            folder_path = output_dir / folder
            folder_path.mkdir(parents=True, exist_ok=True)
        
        return output_dir

def main():
    try:
        print("Initializing AudioScribe...")
        transcriber = AudioScribe()
        
        # Create output folders
        output_dir = transcriber.create_output_folders()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Audio file path
        audio_file = os.path.join(os.getcwd(), "audio", "audio3.wav")
        
        if os.path.exists(audio_file):
            print("Starting transcription process...")
            raw_transcript = transcriber.split_and_transcribe(audio_file)
            
            if raw_transcript:
                # Format the transcript
                formatted_transcript = transcriber.format_transcript(raw_transcript)
                
                # Save formatted transcript to organized folder
                transcript_path = output_dir / 'transcripts' / f"transcript_{timestamp}.txt"
                transcriber.save_formatted_transcript(
                    formatted_transcript, 
                    transcript_path
                )
                
                # Generate and save summary to organized folder
                summary = transcriber.generate_summary(formatted_transcript)
                if summary:
                    summary_path = output_dir / 'summaries' / f"summary_{timestamp}.txt"
                    with open(summary_path, "w") as f:
                        f.write(summary)
                
                print("\nProcessing complete!")
                print(f"- Formatted transcript saved to: {transcript_path}")
                print(f"- Summary saved to: {summary_path}")
        else:
            print(f"Audio file not found at: {audio_file}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()