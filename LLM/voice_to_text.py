from openai import AsyncOpenAI

async def call_voice_to_text(
    client: AsyncOpenAI,
    temp_file_path: str,
) -> str:
    with open(temp_file_path, "rb") as audio:
        transcription = await client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio,
            response_format="text",
            )

    return transcription


