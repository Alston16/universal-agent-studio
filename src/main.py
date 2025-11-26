import streamlit as st
from dotenv import load_dotenv

from pages.chat_page import chat_page
from pages.mcp_marketplace import mcp_marketplace
from pages.model_marketplace import model_marketplace

load_dotenv()

st.set_page_config(
    page_title="Universal Agent Studio",
    page_icon="🧠"
)

pg = st.navigation(
    [
        st.Page(chat_page, title="Home", default=True),
        st.Page(model_marketplace, title="Model Marketplace"),
        st.Page(mcp_marketplace, title="MCP Marketplace")
    ],
    position="top",
)
pg.run()
