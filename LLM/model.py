
from openai import OpenAI
from LLM.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
from LLM.structured_output import StoryGenerated



def call_openai(user_input: str, client: OpenAI) -> dict:
    response = client.responses.parse(
        model="gpt-4o-2024-08-06",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT_TEMPLATE.format(user_input=user_input),
            },
        ],
    text_format=StoryGenerated,

    )
    return response.output_parsed

