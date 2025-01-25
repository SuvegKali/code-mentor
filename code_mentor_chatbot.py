import streamlit as st
from openai import OpenAI
import openai
import os
from dotenv import load_dotenv
import time

# Initialize the OpenAI client using Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Title of the app
st.title("Code Mentor Chatbot 🤖")

# Initialize session state to store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to interact with GPT-4
def get_gpt4_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Use "gpt-4" or "gpt-4-1106-preview" for GPT-4 Turbo
            messages=[
                {"role": "system", "content": "You are a coding mentor. Help students learn to code by providing hints, debugging tips, and simplifying error messages. Do not provide direct solutions; instead, guide them to find the answer on their own."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,  # Adjust as needed
            temperature=0.7,  # Control creativity (0 = strict, 1 = creative)
            stream=True,  # Enable streaming for real-time responses
        )
        return response
    except Exception as e:
        return f"Error: {str(e)}"

# User input for chat
if prompt := st.chat_input("Ask your coding question or paste your code..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get GPT-4 response (streaming)
    with st.chat_message("assistant"):
        response_placeholder = st.empty()  # Placeholder for streaming response
        full_response = ""
        for chunk in get_gpt4_response(prompt):
            if hasattr(chunk.choices[0].delta, "content"):
                chunk_content = chunk.choices[0].delta.content
                if chunk_content:
                    full_response += chunk_content
                    response_placeholder.markdown(full_response + "▌")  # Add typing cursor
                    time.sleep(0.02)  # Simulate typing speed

        # Finalize the response
        response_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# Debugging section in the main window
st.write("### Debug Your Code")
code = st.text_area("Paste your code here for debugging:", height=200)
if st.button("Debug Code"):
    if code.strip():
        debug_prompt = f"Explain any errors in this code and provide hints to fix them:\n\n{code}"
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            for chunk in get_gpt4_response(debug_prompt):
                if hasattr(chunk.choices[0].delta, "content"):
                    chunk_content = chunk.choices[0].delta.content
                    if chunk_content:
                        full_response += chunk_content
                        response_placeholder.markdown(full_response + "▌")
                        time.sleep(0.02)

            # Finalize the response
            response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        st.warning("Please paste your code first.")

# Clear chat history
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.success("Chat history cleared!")
