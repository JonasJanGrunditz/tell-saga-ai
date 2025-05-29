from openai import OpenAI
from pydantic import BaseModel
from prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE
client = OpenAI(api_key="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")

class CalendarEvent(BaseModel):
    RefinedText: str

user_input = "När jag var liten brukade jag alltid åka till mina föräldrar på öland där vi spelade my fotboll"



response = client.responses.parse(
    model="gpt-4o-2024-08-06",
    input=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": USER_PROMPT_TEMPLATE.format(user_input=user_input),
        },
    ],
    text_format=CalendarEvent,
)

event = response.output_parsed

print(f"Event Name: {event}")
