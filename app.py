"""
Streamlit chat UI for the Local RAG system.

Run with:  uv run streamlit run app.py
"""

import streamlit as st

from utils import answer_question, get_index_status, process_documents_folder

st.set_page_config(page_title="Local RAG Chat", page_icon="🤖")
st.title("🤖 Local RAG — Chat with your docs")

# Sidebar: index status and rebuild control
with st.sidebar:
    st.header("Index")

    # Show a one-time message left by the previous build action
    notice = st.session_state.pop("notice", None)
    if notice:
        getattr(st, notice[0])(notice[1])

    status = get_index_status()
    if status["exists"]:
        st.success(f"Ready — {status['count']} chunks")
    else:
        st.warning("No index yet. Build it to start.")

    if st.button("Build / rebuild index"):
        with st.spinner("Embedding documents…"):
            try:
                process_documents_folder()
                st.session_state["notice"] = ("success", "✅ Index rebuilt.")
            except Exception as exc:
                st.session_state["notice"] = ("error", f"Build failed: {exc}")
        st.rerun()

# Need an index before chatting
if not get_index_status()["exists"]:
    st.info(
        "Add `.md` files to `data/documents/`, then click "
        "**Build / rebuild index** in the sidebar."
    )
    st.stop()


def render_sources(contexts):
    """Show the retrieved chunks behind an answer in an expander."""
    with st.expander("Sources"):
        for i, chunk in enumerate(contexts, start=1):
            st.markdown(f"**{i}.** {chunk}")


# Replay the conversation so far
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("contexts"):
            render_sources(message["contexts"])

# Handle a new question
if query := st.chat_input("Ask a question about your documents"):
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            # Pass the recent conversation (everything before this question, last
            # few turns) so the chain can rewrite follow-ups into standalone ones.
            history = st.session_state.messages[:-1][-6:]
            try:
                result = answer_question(query, n_results=3, history=history)
            except Exception as exc:
                st.error(f"Could not generate an answer: {exc}")
                st.stop()
        st.markdown(result["answer"])
        render_sources(result["contexts"])

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "contexts": result["contexts"],
    })
