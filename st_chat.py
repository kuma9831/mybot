"""Streamlit chat app with LLM rest api."""
import requests
import streamlit as st
from streamlit_chat import message

MAX_CONTEXT_LEN: int = 400


def falcon_model_response(prompt: str) -> str:
    """Make post request to falcon model."""
    return requests.post(
        "http://127.0.0.1:8000/generate/",
        json={"prompt": prompt},
        headers={"accept": "application/json"},
    ).json()["answer"]


def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.user_input = ""
    st.session_state.past.append(user_input)

    model_prompt = {
        "instruction": user_input,
        "context": "\n".join(st.session_state.context[-MAX_CONTEXT_LEN:]),
    }
    prompt = (
        "You (I) are chatting with a user R. Write a reply to his message.\n\n"
        f"### Your previous communication:\n{model_prompt['context']}\n\n"
        f"### His new message:\n{model_prompt['instruction']}\n\n### Response:"
    )
    generated_text = falcon_model_response(prompt)
    st.session_state.context.append(f"I:{user_input}\nR:{generated_text}")
    st.session_state.generated.append({"data": generated_text})


def on_btn_click():
    """Clear history chat."""
    del st.session_state.past[:]
    del st.session_state.generated[:]
    del st.session_state.context[:]


st.session_state.setdefault("past", [])
st.session_state.setdefault("generated", [])
st.session_state.setdefault("context", [])


st.title("Chat")
chat_placeholder = st.empty()
with chat_placeholder.container():
    for i in range(len(st.session_state["generated"])):
        message(
            st.session_state["past"][i],
            is_user=True,
            key=f"{i}_user",
            logo="https://cdn-icons-png.flaticon.com/512/4140/4140048.png",
        )
        message(
            st.session_state["generated"][i]["data"],
            key=f"{i}",
            allow_html=True,
            is_table=False,
        )

    st.button("Clear message", on_click=on_btn_click)

with st.container():
    st.text_input("User Input:", on_change=on_input_change, key="user_input")
