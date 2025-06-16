
from openai import OpenAI
from LLM.prompts import SYSTEM_PROMPT_CHAT, SYSTEM_PROMPT_SUGGESTIONS, USER_PROMPT_TEMPLATE_CHAT, USER_PROMPT_TEMPLATE_SUGGESTIONS
from LLM.structured_output import StoryGenerated, SuggestionsGenerated
from typing import Literal


def call_openai(
    user_input: str,
    client: OpenAI,
    functionality: Literal['chat', 'suggestions']
) -> dict:
    if functionality == 'chat':
        SYSTEM_PROMPT = SYSTEM_PROMPT_CHAT
        USER_PROMPT_TEMPLATE = USER_PROMPT_TEMPLATE_CHAT
        text_format_standrd = StoryGenerated
    elif functionality == 'suggestions':
        SYSTEM_PROMPT = SYSTEM_PROMPT_SUGGESTIONS
        USER_PROMPT_TEMPLATE = USER_PROMPT_TEMPLATE_SUGGESTIONS
        text_format_standrd = SuggestionsGenerated
    else:
        raise ValueError("Invalid functionality specified. Use 'chat' or 'suggestions'.")
    response = client.responses.parse(
        model="o4-mini-2025-04-16",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(user_input=user_input),
            },
        ],
    text_format=text_format_standrd,

    )
    return response.output_parsed

