import time
from openai import AsyncOpenAI
from LLM.prompts import (
    SYSTEM_PROMPT_CHAT, 
    SYSTEM_PROMPT_CHAT_WITH_STYLE,
    SYSTEM_PROMPT_SUGGESTIONS, 
    USER_PROMPT_TEMPLATE_CHAT, 
    USER_PROMPT_TEMPLATE_CHAT_WITH_STYLE,
    USER_PROMPT_TEMPLATE_SUGGESTIONS
)
from LLM.structured_output import StoryGenerated, SuggestionsGenerated
from typing import Literal, Optional


async def call_openai(
    user_input: str,
    client: AsyncOpenAI,
    functionality: Literal['chat', 'suggestions'],
    style_context: Optional[str] = None
) -> dict:
    """
    Call OpenAI API with enhanced style context support.
    
    Args:
        user_input: The text to process
        client: AsyncOpenAI client
        functionality: 'chat' for text improvement or 'suggestions' for writing suggestions
        style_context: Optional string containing previous writing examples from the user
    """
    if functionality == 'chat':
        if style_context:
            SYSTEM_PROMPT = SYSTEM_PROMPT_CHAT_WITH_STYLE
            USER_PROMPT_TEMPLATE = USER_PROMPT_TEMPLATE_CHAT_WITH_STYLE
        else:
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
    
    # Format the user prompt with style context if available
    if functionality == 'chat' and style_context:
        formatted_prompt = USER_PROMPT_TEMPLATE.format(
            user_input=user_input, 
            style_context=style_context
        )
    else:
        formatted_prompt = USER_PROMPT_TEMPLATE.format(user_input=user_input)
    
    print(f"Formatted prompt: {formatted_prompt}") 
    response = await client.responses.parse(
        model="gpt-4o-mini",  # Much faster than o4-mini
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": formatted_prompt,
            },
        ],
        text_format=text_format_standard,
        timeout=30.0  # Add timeout to prevent hanging
    )
    end_time = time.time()
    duration = end_time - start_time
    print(f"API response time: {duration:.2f} seconds")
    return response.output_parsed


def create_style_context(previous_texts: list[str], max_length: int = 1500) -> str:
    """
    Create a style context string from previous user texts.
    
    Args:
        previous_texts: List of previous texts written by the user
        max_length: Maximum character length for the style context
        
    Returns:
        Formatted style context string
    """
    if not previous_texts:
        return ""
    
    # Take the most recent texts and combine them
    context_parts = []
    current_length = 0
    
    for text in reversed(previous_texts):  # Start with most recent
        # Clean and prepare the text
        cleaned_text = text.strip()
        if not cleaned_text:
            continue
            
        # Check if adding this text would exceed the limit
        text_with_separator = f"\n\n--- Tidigare text ---\n{cleaned_text}"
        if current_length + len(text_with_separator) > max_length:
            break
            
        context_parts.insert(0, text_with_separator)
        current_length += len(text_with_separator)
    
    if not context_parts:
        return ""
        
    return "".join(context_parts)

