import os
from typing import Optional
from supabase import Client
from LLM.model import create_style_context




async def get_user_style_context(book_id: str, supabase: Client, limit: int = 20) -> Optional[str]:
    """
    Retrieve previous user texts from Supabase to create style context.
    
    Args:
        book_id: The UUID of the book to get style context for
        limit: Maximum number of previous texts to retrieve
        
    Returns:
        Style context string or None if no texts found
    """
    try:
        # First get the book_question_ids for the specific book
        book_questions_response = (
            supabase.table("book_questions")
            .select("id")
            .eq("book_id", book_id)
            .execute()
        )
        
        if not book_questions_response.data:
            print(f"No book found with ID: {book_id}")
            return None
            
        # Extract the book_question_ids
        book_question_ids = [bq["id"] for bq in book_questions_response.data]
        
        # Get recent completed answers for style context
        response = (
            supabase.table("answers")
            .select("answer_text, updated_at")
            .in_("book_question_id", book_question_ids)
            .in_("status", ["Färdig","Pågående"])  # Only use completed texts for style
            .order("updated_at", desc=True)
            .limit(limit)
            .execute()
        )
        
        if not response.data:
            print(f"No completed answers found for book ID: {book_id}")
            return None
        # Extract text content
        meaningful_texts = [answer["answer_text"] for answer in response.data if answer["answer_text"]]
        
    
            
        # Create style context
        style_context = create_style_context(meaningful_texts)
        #style_context = meaningful_texts
        print(f"Created style context from {len(meaningful_texts)} previous texts")
        
        return style_context
        
    except Exception as e:
        print(f"Error retrieving style context: {e}")
        return None

