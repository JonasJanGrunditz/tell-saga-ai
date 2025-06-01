from pydantic import BaseModel

class StoryGenerated(BaseModel):
    story: str



class SuggestionsGenerated(BaseModel):
    suggestions: list[str]
