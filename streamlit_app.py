import streamlit as st
from openai import OpenAI

# Initialize OpenAI client with API key from secrets
client = OpenAI(api_key=st.secrets["openai"]["api_key"])

# Get assistant ID from secrets
assistant_id = st.secrets["openai"]["assistant_id"]

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = client.beta.threads.create().id

def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def process_user_input(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=prompt
    )

def get_assistant_response():
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id
    )

    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )

    messages = client.beta.threads.messages.list(thread_id=st.session_state.thread_id)
    return messages.data[0].content[0].text.value

def main():
    st.title("💬 AI Assistant Chatbot")
    st.write(
        "This chatbot uses OpenAI's assistant interface to generate responses. "
        "Feel free to ask any questions!"
    )

    initialize_session_state()
    display_chat_messages()

    if prompt := st.chat_input("What would you like to know?"):
        process_user_input(prompt)
        
        assistant_message = get_assistant_response()

        st.session_state.messages.append({"role": "assistant", "content": assistant_message})
        with st.chat_message("assistant"):
            st.markdown(assistant_message)

if __name__ == "__main__":
    main()