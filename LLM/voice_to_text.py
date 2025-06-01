from openai import OpenAI

def call_voice_to_text(
    client: OpenAI,
    temp_file_path: str,
) -> dict:
    with open(temp_file_path, "rb") as audio:
        transcription = client.audio.transcriptions.create(
            model="gpt-4o-transcribe", 
            file=audio,
            response_format="text",
            )

    return transcription


