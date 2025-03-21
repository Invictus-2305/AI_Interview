# from kokoro import KPipeline
# import soundfile as sf


pipeline = KPipeline(lang_code='a')

def generate_audio_for_questions(questions):
    """Generate audio files for each question using Kokoro."""
    for i, question in enumerate(questions):
        audio_file = f'static/audios/question_{i + 1}.wav'
        pipeline = KPipeline(lang_code='a')
        generator = pipeline(
            question["question"], voice='af_heart', speed=1
        )
        for gs, ps, audio in generator:
            sf.write(audio_file, audio, 24000)

if __name__ == '__main__':
    generate_audio_for_questions([
  {
    "question": "What is a list in Python?",
    "skill_set": ["Python"]
  }])