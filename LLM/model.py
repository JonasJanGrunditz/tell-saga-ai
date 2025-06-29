import time
import asyncio
from openai import AsyncOpenAI
from LLM.prompts import SYSTEM_PROMPT_CHAT, SYSTEM_PROMPT_SUGGESTIONS, USER_PROMPT_TEMPLATE_CHAT, USER_PROMPT_TEMPLATE_SUGGESTIONS
from LLM.structured_output import StoryGenerated, SuggestionsGenerated
from typing import Literal


async def call_openai(
    user_input: str,
    client: AsyncOpenAI,
    functionality: Literal['chat', 'suggestions']
) -> dict:
    if functionality == 'chat':
        SYSTEM_PROMPT = SYSTEM_PROMPT_CHAT
        USER_PROMPT_TEMPLATE = USER_PROMPT_TEMPLATE_CHAT
        text_format_standard = StoryGenerated
    elif functionality == 'suggestions':
        SYSTEM_PROMPT = SYSTEM_PROMPT_SUGGESTIONS
        USER_PROMPT_TEMPLATE = USER_PROMPT_TEMPLATE_SUGGESTIONS
        text_format_standard = SuggestionsGenerated
    else:
        raise ValueError("Invalid functionality specified. Use 'chat' or 'suggestions'.")
    start_time = time.time()
    response = await client.responses.parse(
        model="gpt-4o-mini",  # Much faster than o4-mini
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(user_input=user_input),
            },
        ],
        text_format=text_format_standard,
        timeout=30.0  # Add timeout to prevent hanging
    )
    end_time = time.time()
    duration = end_time - start_time
    print(f"API response time: {duration:.2f} seconds")
    return response.output_parsed

