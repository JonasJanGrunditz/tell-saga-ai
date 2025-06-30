import os
from supabase import create_client, Client

url: str = "https://ccgwsairvzywoypwuoer.supabase.co/"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNjZ3dzYWlydnp5d295cHd1b2VyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc1ODc2NzksImV4cCI6MjA2MzE2MzY3OX0.AELHVJfCRDWSZd4y2QwkrgvVw89kRcmCTUvIQdWXYVg"
supabase: Client = create_client(url, key)



# Query to get all answers for a specific book with status "Pågående" or "Färdig"
book_id = "66cb466e-654a-4cff-93bb-343eb0abd86a"  # Replace with actual book UUID

# First get the book_question_ids for the specific book
book_questions_response = (
    supabase.table("book_questions")
    .select("id")
    .eq("book_id", book_id)
    .execute()
)

if book_questions_response.data:
    # Extract the book_question_ids
    book_question_ids = [bq["id"] for bq in book_questions_response.data]
    
    # Then get all answers for those questions with the desired status, sorted by latest first
    response = (
        supabase.table("answers")
        .select("""
            answer_text

        """)
        .in_("book_question_id", book_question_ids)
        .in_("status", ["Pågående", "Färdig"])
        .order("updated_at", desc=True)
        .execute()
    )
else:
    print(f"No book found with ID: {book_id}")
    response = None


print(response.data)  # Print the response data to see the results