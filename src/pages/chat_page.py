import streamlit as st
from langchain_perplexity import ChatPerplexity


def chat_page() -> None:
    model = ChatPerplexity(temperature=0, model="sonar")
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    user_input = st.chat_input("Ask something...")

    if user_input:
        # Display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        bot_reply = model.invoke(user_input)

        # Display bot response
        st.session_state.messages.append({"role": "assistant", "content": bot_reply.content})
        with st.chat_message("assistant"):
            st.markdown(bot_reply.content)

if __name__ == "__main__":
    chat_page()