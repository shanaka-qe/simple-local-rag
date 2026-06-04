"""
Simple RAG
"""

from utils import process_documents_folder, answer_question


def main():
    """Run RAG system with document processing and search"""
    print("🚀 RAG System - Document Processing and Search")
    print("=" * 60)
    
    # Step 1: Process documents from folder
    print("📄 Step 1: Processing documents...")
    collection = process_documents_folder()
    
    if not collection:
        print("❌ No documents processed. Exiting.")
        return
    
    # Step 2: Ask questions — retrieve context and generate an answer
    print("\n🔍 Step 2: Testing question answering...")

    # Test different queries
    test_queries = [
        "What is the refund window in the returns policy?",
        "Who is the lead scientist on Project Meridian?",
        "What is Prof. Elena Rodriguez's research focus?"
    ]

    for query in test_queries:
        print(f"\n--- Testing: {query} ---")
        result = answer_question(query, n_results=2)
        print(f"💬 Answer: {result['answer']}")
        print(f"📚 (based on {len(result['contexts'])} retrieved chunks)")
    
    print("\n🎉 RAG system test completed!")


if __name__ == "__main__":
    main()