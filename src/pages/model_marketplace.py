from pathlib import Path

import streamlit as st
from huggingface_hub import HfApi

from model_api_providers.model_api_provider import ModelApiProvider
from model_api_providers.model_api_providers_list import MODEL_API_PROVIDERS
from utils.local_models_utils import (
    download_local_model_artifacts,
    is_local_model_available,
    uninstall_local_model_artifacts,
)

MODELS_LIST_PATH = Path(__file__).parent.parent.parent / "data" / "global" / "models.json"


def download_local_model(model_id: str, revision: str | None = None) -> None:
    with st.spinner(f"Downloading {model_id}..."):
        try:
            local_path = download_local_model_artifacts(model_id, revision=revision)
        except Exception as error:
            st.error(f"Failed to download {model_id}: {error}")
            return

    st.success(f"Downloaded {model_id} to {local_path}")


def uninstall_local_model(model_id: str) -> None:
    with st.spinner(f"Uninstalling {model_id}..."):
        try:
            uninstall_local_model_artifacts(model_id)
        except Exception as error:
            st.error(f"Failed to uninstall {model_id}: {error}")
            return

    st.success(f"Uninstalled {model_id}")

@st.dialog("Setup Model Provider")
def setup_model_provider(model_api_provider: ModelApiProvider) -> None:
    st.write(f"Enter API key for {model_api_provider.name}")
    api_key_input = st.text_input("API Key", type="password")
    if st.button("Save"):
        model_api_provider.set_api_key(api_key_input)
        st.success(f"API key for {model_api_provider.name} saved successfully!")

def model_marketplace() -> None:
    st.title("Model Marketplace")

    # Persist selection across reruns so action buttons don't reset the active tab.
    model_type = st.radio(
        "Model Type",
        options=["API Models", "Local Models"],
        horizontal=True,
        key="model_marketplace_model_type",
    )
    
    if model_type == "API Models":
        st.subheader("Available API Models")
        for model_provider in MODEL_API_PROVIDERS:
            for model_name in model_provider.get_model_names():
                st.write(f"- {model_name} by {model_provider.name}")
                if model_provider.is_setup():
                    pass
                else:
                    st.button(label=f"Setup {model_provider.name}", on_click=lambda: setup_model_provider(model_provider))
    else:
        st.subheader("Popular Local Models on Hugging Face")
        api = HfApi()
        models_local = api.list_models(filter="llama.cpp", sort="downloads", direction=-1, limit=10)
        for model_local in models_local:
            if "/" in model_local.id:
                hf_model_provider, model_name = model_local.id.split("/", 1)
            else:
                hf_model_provider, model_name = "unknown", model_local.id

            is_available = is_local_model_available(model_local.id)

            info_col, action_col = st.columns([4, 1])
            with info_col:
                availability_status = "Installed" if is_available else "Not Installed"
                st.write(f"- {model_name} by {hf_model_provider} ({availability_status})")

            with action_col:
                if is_available:
                    if st.button("Uninstall", key=f"uninstall-{model_local.id}"):
                        uninstall_local_model(model_local.id)
                        st.rerun()
                else:
                    if st.button("Download", key=f"download-{model_local.id}"):
                        download_local_model(model_local.id, revision=model_local.sha)
                        st.rerun()
    st.write("Explore and select different language models for your applications.")

if __name__ == "__main__":
    model_marketplace()