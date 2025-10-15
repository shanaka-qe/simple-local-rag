"""
Simple RAG
"""

from utils import process_documents_folder, search_documents


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
    
    # Step 2: Show collection info
    print("\n🔍 Step 3: Testing search...")
    
    # Test different queries
    test_queries = [
       "Who is Prof. Elena Rodriguez?",
        "What are the requirements for the project?",
        "What are the specifications?"
    ]
    
    for query in test_queries:
        print(f"\n--- Testing: {query} ---")
        search_documents(query, n_results=2)
    
    print("\n🎉 RAG system test completed!")


if __name__ == "__main__":
    main()