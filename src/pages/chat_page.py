import json

import streamlit as st
from langchain_community.chat_models import ChatLlamaCpp
from langchain_core.language_models.chat_models import BaseChatModel

from model_api_providers.model_api_providers_list import MODEL_API_PROVIDERS
from utils.local_models_utils import get_local_model_storage_path, load_local_models_list


def _build_model_options() -> list[dict]:
    """Return a flat list of selectable model options from API providers and local GGUF models."""
    options: list[dict] = []

    for provider in MODEL_API_PROVIDERS:
        if provider.is_setup():
            for model_name in provider.get_model_names():
                options.append(
                    {
                        "label": f"{provider.name} — {model_name}",
                        "type": "api",
                        "provider": provider,
                        "model_name": model_name,
                    }
                )

    for repo_name in load_local_models_list():
        local_path = get_local_model_storage_path(repo_name)
        leap_dir = local_path / "leap"
        if leap_dir.exists():
            for leap_file in sorted(leap_dir.glob("*.json")):
                options.append(
                    {
                        "label": f"Local — {repo_name} ({leap_file.stem})",
                        "type": "local",
                        "repo_name": repo_name,
                        "leap_path": leap_file,
                    }
                )
        else:
            for gguf_file in sorted(local_path.glob("*.gguf")):
                if "mmproj" not in gguf_file.name:
                    options.append(
                        {
                            "label": f"Local — {repo_name} ({gguf_file.stem})",
                            "type": "local",
                            "repo_name": repo_name,
                            "gguf_path": gguf_file,
                        }
                    )

    return options


def _load_chat_model(option: dict) -> BaseChatModel:
    """Instantiate the appropriate LangChain chat model for the selected option."""
    if option["type"] == "api":
        return option["provider"].get_chat_model(option["model_name"])

    if "leap_path" in option:
        with open(option["leap_path"], "r", encoding="utf-8") as f:
            leap = json.load(f)
        # LEAP model paths are relative to the leap file's directory.
        model_path = (
            option["leap_path"].parent / leap["load_time_parameters"]["model"]
        ).resolve()
        sampling = leap.get("generation_time_parameters", {}).get("sampling_parameters", {})
        return ChatLlamaCpp(
            model_path=str(model_path),
            temperature=sampling.get("temperature", 0.1),
            repeat_penalty=sampling.get("repetition_penalty", 1.0),
            min_p=sampling.get("min_p", 0.05),
            verbose=False,
        )
    else:
        return ChatLlamaCpp(
            model_path=str(option["gguf_path"]),
            temperature=0.1,
            verbose=False,
        )


def chat_page() -> None:
    with st.sidebar:
        st.subheader("Model")
        model_options = _build_model_options()

        if not model_options:
            st.warning(
                "No models available. Configure an API provider in the Model Marketplace "
                "or download a local model."
            )
            st.stop()

        option_labels = [o["label"] for o in model_options]
        selected_label = st.selectbox("Select model", option_labels, key="selected_model_label")

    selected_option = next(o for o in model_options if o["label"] == selected_label)

    # Re-initialise chat model only when the selection changes
    if st.session_state.get("_loaded_model_label") != selected_label:
        with st.spinner(f"Loading {selected_label}…"):
            model = _load_chat_model(selected_option)
        if model is None:
            return
        st.session_state["_chat_model"] = model
        st.session_state["_loaded_model_label"] = selected_label
        st.session_state["messages"] = []

    model = st.session_state["_chat_model"]

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
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        bot_reply = model.invoke(user_input)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply.content})
        with st.chat_message("assistant"):
            st.markdown(bot_reply.content)


if __name__ == "__main__":
    chat_page()