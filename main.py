"""
Interactive control console for the Local RAG system.

Run with:  uv run python main.py
"""

from utils import (
    process_documents_folder,
    search_documents,
    answer_question,
    get_index_status,
)

MENU = """
========================================
🤖  Local RAG — Control Console
========================================
  1) Build / rebuild the index from data/documents
  2) Show index status
  3) Search (show matching chunks, no answer)
  4) Ask a single question
  5) Chat (interactive)
  0) Exit
----------------------------------------"""


def build_index():
    """Wipe and rebuild the vector index from data/documents."""
    process_documents_folder()


def show_status():
    """Print whether the index exists and how many chunks it holds."""
    status = get_index_status()
    if status["exists"]:
        print(f"✅ Index ready — {status['count']} chunks in collection.")
    else:
        print("⚠️ No index found. Choose option 1 to build it.")


def require_index() -> bool:
    """Return True if the index exists, otherwise explain how to build it."""
    if not get_index_status()["exists"]:
        print("⚠️ No index yet — choose option 1 to build it first.")
        return False
    return True


def do_search():
    """Retrieve and print matching chunks (no LLM)."""
    if not require_index():
        return
    query = input("🔎 Search query: ").strip()
    if query:
        search_documents(query, n_results=3, verbose=True)


def ask_once():
    """Ask a single question and print the generated answer."""
    if not require_index():
        return
    query = input("❓ Your question: ").strip()
    if query:
        print_answer(query)


def chat():
    """Interactive question loop until the user exits."""
    if not require_index():
        return
    print("💬 Chat mode — type 'exit' (or leave blank) to return to the menu.")
    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query or query.lower() in {"exit", "quit"}:
            break
        print_answer(query)


def print_answer(query: str):
    """Generate an answer for a question and show its source chunks."""
    result = answer_question(query, n_results=3)
    print(f"\n🤖 {result['answer']}")
    print("📚 Sources:")
    for i, chunk in enumerate(result["contexts"], start=1):
        preview = " ".join(chunk.split())[:120]
        print(f"   {i}. {preview}...")


def main():
    """Run the interactive control console."""
    actions = {
        "1": build_index,
        "2": show_status,
        "3": do_search,
        "4": ask_once,
        "5": chat,
    }
    while True:
        print(MENU)
        try:
            choice = input("Select an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            choice = "0"

        if choice == "0":
            print("👋 Bye!")
            break

        action = actions.get(choice)
        if action:
            print()
            action()
        else:
            print("❓ Unknown option — please choose 0-5.")


if __name__ == "__main__":
    main()
