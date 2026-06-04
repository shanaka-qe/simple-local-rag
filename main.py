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
    
    # Step 2: Test search using the returned results
    print("\n🔍 Step 2: Testing search...")

    # Test different queries
    test_queries = [
        "What is the refund window in the returns policy?",
        "Who is the lead scientist on Project Meridian?",
        "What is Prof. Elena Rodriguez's research focus?"
    ]

    for query in test_queries:
        print(f"\n--- Testing: {query} ---")
        result = search_documents(query, n_results=2)
        for i, chunk in enumerate(result["chunks"], start=1):
            print(f"  {i}. {chunk[:300]}...")
    
    print("\n🎉 RAG system test completed!")


if __name__ == "__main__":
    main()