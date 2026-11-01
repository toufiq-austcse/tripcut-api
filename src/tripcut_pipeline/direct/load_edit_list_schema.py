import json
from pathlib import Path


def load_edit_list_schema() -> dict:
    """The JSON schema the director must answer with (segment ids per version; renderer times come later)."""
    path = Path(__file__).with_name("edit_list_schema.json")
    return json.loads(path.read_text(encoding="utf-8"))
