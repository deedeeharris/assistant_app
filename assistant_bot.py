# Importing required packages
import streamlit as st
import time
from openai import OpenAI

st.set_page_config(page_title='Chat by Yedidya', page_icon="💬")


if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'assistant_id' not in st.session_state:
    st.session_state.assistant_id = None
if 'title' not in st.session_state:
    st.session_state.title = None
    
# Initialize session state
if 'login_status' not in st.session_state:
    st.session_state.login_status = False

# Display login page if not logged in
if not st.session_state.login_status:
    api_key = st.text_input("Enter API Key:")
    assistant_id = st.text_input("Enter Assistant ID:")
    title = st.text_input("Enter Title:")
    login_button = st.button("Login")

    if login_button: 
        # Set login status to True
        st.session_state.login_status = True
        st.session_state.api_key = api_key
        st.session_state.assistant_id = assistant_id
        st.session_state.title = title
        st.rerun()
else:
    # App title with creator's name and LinkedIn link
    api_key = st.session_state.api_key
    assistant_id = st.session_state.assistant_id
    title = st.session_state.title
    st.title(title)

    
    st.markdown(f"#### by [Yedidya Harris](https://www.linkedin.com/in/yedidya-harris/), 01/2024")
    # add divider
    st.markdown("---")

    # Set openAi client, assistant ai and assistant ai thread
    @st.cache_resource
    def load_openai_client_and_assistant():
        client = OpenAI(api_key=api_key)
        my_assistant = client.beta.assistants.retrieve(assistant_id)
        thread = client.beta.threads.create()

        return client, my_assistant, thread

    # Function to clear cache and reset thread
    def reset_thread():
        st.cache_resource.clear()
        st.session_state.messages = []
        st.rerun()

    # Check if the reset button was clicked and reset the thread
    if st.button("איפוס שיחה"):
        reset_thread()
    if st.button("התנתק"):
        # Set login status to False
        st.session_state.login_status = False
        # Clear the session state and rerun the app
        st.session_state.clear()
        st.rerun()
    try:
        client, my_assistant, assistant_thread = load_openai_client_and_assistant()
    except:
        st.warning("לא ניתן להתחבר כעת.")

    # check in loop if assistant ai parses our request
    def wait_on_run(run, thread):
        while run.status == "queued" or run.status == "in_progress":
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(0.5)
        return run

    # initiate assistant ai response
    def get_assistant_response(user_input=""):
        message = client.beta.threads.messages.create(
            thread_id=assistant_thread.id,
            role="user",
            content=user_input,
        )

        run = client.beta.threads.runs.create(
            thread_id=assistant_thread.id,
            assistant_id=assistant_id,
        )

        run = wait_on_run(run, assistant_thread)

        # Retrieve all the messages added after our last user message
        messages = client.beta.threads.messages.list(
            thread_id=assistant_thread.id, order="asc", after=message.id
        )

        return messages.data[0].content[0].text.value

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        avatar = '🕵🏼' if message["role"] == 'user' else '🧔🏻'
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # React to user input
    user_input = st.chat_input("מה נשמע?")
    if user_input:
        # Display user message in chat message container
        with st.chat_message("user", avatar='🕵🏼'):
            st.markdown(user_input)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input, "avatar": '🕵🏼'})

        # Get assistant response
        try:
            assistant_response = get_assistant_response(user_input)
        except:
            assistant_response = "מצטער, אני לא זמין עכשיו לשוחח. נסו בהזדמנות אחרת."

        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar='🧔🏻'):
            st.markdown(assistant_response)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response, "avatar": '🧔🏻'})
