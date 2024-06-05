import os
import time
import streamlit as st
from openai import OpenAI
# from dotenv import load_dotenv
# load_dotenv()

# https://discuss.streamlit.io/t/display-llm-response-stream-from-openai-assistant-api/67041/3 참고
# assistant 생성은 미리 진행.
# assistant = client.beta.assistants.create(
#     name="드라이브 스케치",
#     instructions="드라이브 스케치 provides travel routes within a 2-hour drive from the user's location, focusing on destinations with convenient parking. It suggests nearby attractions that can be visited together, optimizing the travel experience. It includes details about parking facilities and also mentions local specialties or must-try foods at each destination to enhance the travel experience.",
#     model="gpt-4-1106-preview",
# )
# print(assistant)

# openai에 stream으로 요청
def ask(assistant_id, thread_id, user_message):
  client.beta.threads.messages.create(
    thread_id=thread_id, role="user", content=user_message
  )
  stream = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
    stream=True
  )
  return stream

# stream 출력을 위한 함수
def data_streamer():
  for response in st.session_state.stream:
    if response.event == 'thread.message.delta':
      value = response.data.delta.content[0].text.value
      yield value
      time.sleep(0.1)

st.title('드라이브 스케치')
api_key = st.text_input('OPENAI API KEY를 입력하세요.')

if api_key:
    client = OpenAI(api_key=api_key)
    assistant_id = os.environ["ASSISTANT_ID"]

    if "thread_id" not in st.session_state:
      st.session_state.thread_id = client.beta.threads.create().id
    thread_id = st.session_state.thread_id

    if "messages" not in st.session_state:
        st.session_state.messages = []
        greeting = f"어디로 여행가고 싶나요?"
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("가고 싶은 여행지를 입력해보세요."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.stream = ask(assistant_id, thread_id, prompt)
        with st.chat_message("assistant"):
          response = st.write_stream(data_streamer)
          st.session_state.messages.append({"role": "assistant", "content": response})
        