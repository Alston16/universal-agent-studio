import json
import shutil
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

LOCAL_MODELS_LIST_FILE_PATH = (
    Path(__file__).parent.parent.parent / "data" / "local" / "local_models.json"
)
LOCAL_MODELS_STORAGE_DIR = Path(__file__).parent.parent.parent / "data" / "local" / "models"


def _ensure_local_models_file_exists() -> None:
    LOCAL_MODELS_LIST_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LOCAL_MODELS_LIST_FILE_PATH.exists():
        with open(LOCAL_MODELS_LIST_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4)


def _ensure_local_models_storage_dir_exists() -> None:
    LOCAL_MODELS_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_local_model_storage_path(model_name: str) -> Path:
    """Return the deterministic local directory used to store a model's files."""
    safe_model_name = model_name.replace("/", "--")
    return LOCAL_MODELS_STORAGE_DIR / safe_model_name

def load_local_models_list() -> list[str]:
    """Load the list of local models from a JSON file."""
    if not LOCAL_MODELS_LIST_FILE_PATH.exists():
        return []

    with open(LOCAL_MODELS_LIST_FILE_PATH, "r", encoding="utf-8") as file:
        try:
            models = json.load(file)
        except json.JSONDecodeError:
            return []

    return models

def is_local_model_available(model_name: str) -> bool:
    """Check if a local model is available."""
    return model_name in load_local_models_list()

def save_local_models_list(models: list[str]) -> None:
    """Save the list of local models to a JSON file."""
    _ensure_local_models_file_exists()
    with open(LOCAL_MODELS_LIST_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(models, file, indent=4)

def add_local_model(model_name: str) -> None:
    """Add a new local model to the list."""
    local_models = load_local_models_list()
    if model_name not in local_models:
        local_models.append(model_name)
        save_local_models_list(local_models)

def remove_local_model(model_name: str) -> None:
    """Remove a local model from the list."""
    local_models = load_local_models_list()
    if model_name in local_models:
        local_models.remove(model_name)
        save_local_models_list(local_models)


def _resolve_repo_revision(repo_id: str) -> str:
    """Resolve the repository HEAD commit SHA so downloads are pinned to an immutable revision."""
    model_info = HfApi().model_info(repo_id=repo_id)
    if not model_info.sha:
        msg = f"Unable to resolve pinned revision for '{repo_id}'."
        raise ValueError(msg)

    return model_info.sha


def download_local_model_artifacts(model_name: str, revision: str | None = None) -> Path:
    """Download model artifacts from Hugging Face and register the model as installed."""
    _ensure_local_models_storage_dir_exists()
    local_model_path = get_local_model_storage_path(model_name)
    local_model_path.mkdir(parents=True, exist_ok=True)

    pinned_revision = revision or _resolve_repo_revision(model_name)

    snapshot_download(
        repo_id=model_name,
        revision=pinned_revision,
        local_dir=str(local_model_path),
    )
    add_local_model(model_name)
    return local_model_path


def uninstall_local_model_artifacts(model_name: str) -> None:
    """Delete local model artifacts and remove model from the installed registry."""
    local_model_path = get_local_model_storage_path(model_name)
    if local_model_path.exists() and local_model_path.is_dir():
        shutil.rmtree(local_model_path)

    remove_local_model(model_name)