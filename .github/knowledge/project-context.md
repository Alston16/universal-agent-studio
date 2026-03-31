# Universal Agent Studio - Project Context

Last updated: 2026-03-31 (local model artifact lifecycle synced)

## Overview
Universal Agent Studio (UAS) is intended to be an accessible platform for creating, running, and sharing AI agents. The README positions it as a unified system for:
- Agent chat
- LLM marketplace (API + local)
- MCP server marketplace
- No-code/low-code agent creation
- OpenAI-compatible and A2A-compatible serving

Current implementation is an early-stage Streamlit prototype with partial functionality.

## Current Runtime and Stack
- Language: Python
- App framework: Streamlit
- Environment/dependency manager: uv
- Minimum Python version: 3.13
- Lint/type/security/tests in CI: Ruff, mypy, Bandit, pytest

Key dependency highlights:
- streamlit
- langchain-perplexity
- huggingface-hub
- python-dotenv

## Application Entry Points
- Main app entry: src/main.py
- Pages registered in top navigation:
  - Home (chat): src/pages/chat_page.py
  - Model Marketplace: src/pages/model_marketplace.py
  - MCP Marketplace: src/pages/mcp_marketplace.py

## Implemented Features (Current)
- Streamlit app shell and top navigation are working.
- Chat page can call Perplexity via `ChatPerplexity` and render message history in Streamlit session state.
- API provider abstraction exists (`ModelApiProvider`) with Perplexity provider implementation.
- Perplexity models are loaded from `data/global/perplexity_models.json`.
- Model marketplace has a UI split between API and Local model views.
- Local model helpers maintain a persistent JSON list at `data/local/local_models.json`.
- Local model cards support real artifact lifecycle actions:
  - `Download`: downloads the Hugging Face model snapshot to `data/local/models/<repo-id>` and updates installed registry.
  - `Uninstall`: removes local model files and updates installed registry.

## Not Yet Implemented / Placeholder Areas
- MCP marketplace is currently placeholder text only.
- Agent creation studio flows described in README are not yet implemented in code.
- Hosting layer (OpenAI-compatible endpoints, A2A serving) is not implemented.
- RAG pipeline, citation flow, and tool execution logs are not implemented.

## Observed Gaps / Risks In Current Code
- Local model downloads currently use full repository snapshot behavior, which may be large for some model repos.
- Tests are minimal and currently validate only basic placeholder logic plus env manager behavior.

## Repository Layout (High Signal)
- src/
  - main.py
  - pages/
  - model_api_providers/
  - utils/
- data/
  - global/perplexity_models.json
- tests/
- .github/workflows/ci_build.yml

## Standard Local Commands
Setup:
- `uv sync`

Run app:
- `uv run -m streamlit run src/main.py`

Tests:
- `uv run pytest --maxfail=1 --disable-warnings -q`

Lint/type/security checks:
- `uvx ruff check .`
- `uvx mypy .`
- `uvx bandit -r -c bandit.yaml .`

## Context Notes for Future Contributors
- Treat README as product vision and roadmap, not parity with current code.
- Prioritize stabilizing core flows (provider setup, model selection, basic state handling) before adding broader marketplace/hosting features.
- Expand tests around page logic, provider behavior, and utility file path correctness as implementation grows.
