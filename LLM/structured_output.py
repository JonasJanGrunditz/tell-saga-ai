from pydantic import BaseModel

class StoryGenerated(BaseModel):
    story: str