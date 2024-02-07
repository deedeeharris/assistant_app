# Importing required packages
import streamlit as st
import time
from openai import OpenAI

st.set_page_config(page_title='Chat by Yedidya', page_icon="💬")

# Initialize session state
if 'login_status' not in st.session_state:
    st.session_state.login_status = False

# Display input boxes for API key, assistant ID, and title
api_key = st.text_input("Enter API Key:")
assistant_id = st.text_input("Enter Assistant ID:")
title = st.text_input("Enter Title:")

# Display button to load keys and start chat
if st.button("Start Chat"):
    # Set login status to True
    st.session_state.login_status = True

    # Set title
    st.title(title)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Set OpenAI client and assistant
    client = OpenAI(api_key=api_key)
    my_assistant = client.beta.assistants.retrieve(assistant_id)
    thread = client.beta.threads.create()

    # Check in loop if assistant AI parses our request
    def wait_on_run(run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    # Initiate assistant AI response
    def get_assistant_response(user_input=""):
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id,
        )

        run = wait_on_run(run, thread)

        # Retrieve all the messages added after our last user message
        messages = client.beta.threads.messages.list(
            thread_id=thread.id, order="asc", after=message.id
        )

        return messages.data[0].content[0].text.value

    # React to user input
    user_input = st.text_input("What's on your mind?")
    if st.button("Send"):
        # Display user message in chat message container
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Get assistant response
        try:
            assistant_response = get_assistant_response(user_input)
        except:
            assistant_response = "Sorry, I'm not available to chat right now. Please try again later."

        # Display assistant response in chat message container
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.text_input("You:", value=message["content"], disabled=True)
        else:
            st.text_input("Assistant:", value=message["content"], disabled=True)
