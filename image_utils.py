import base64
import mimetypes
import os
from pathlib import Path
from typing import Dict, Union

# Supported image extensions and corresponding MIME types
SUPPORTED_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".gif": "image/gif",
}


def load_and_encode_image(image_input: Union[str, Path, Dict[str, str]]) -> Dict[str, str]:
    """Validates a local image path and converts the image to base64 format for Gemini.

    Args:
        image_input: A file path string, Path object, or a dict containing 'image_path'.

    Returns:
        dict: A dictionary containing 'data_url', 'mime_type', and 'image_path'.

    Raises:
        FileNotFoundError: If the provided image path does not exist.
        ValueError: If the file is not a valid or supported image file.
    """
    if isinstance(image_input, dict):
        raw_path = image_input.get("image_path")
        if not raw_path:
            raise ValueError("Dictionary input must contain an 'image_path' key.")
    else:
        raw_path = image_input

    path = Path(raw_path).resolve()

    # 1. Validate that the path exists
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    # 2. Validate that it is a regular file
    if not path.is_file():
        raise ValueError(f"Specified path is not a file: {path}")

    # 3. Verify supported image extension
    extension = path.suffix.lower()
    mime_type = SUPPORTED_MIME_TYPES.get(extension)
    if not mime_type:
        # Fallback to mimetypes detection
        guessed_type, _ = mimetypes.guess_type(str(path))
        if guessed_type and guessed_type.startswith("image/"):
            mime_type = guessed_type
        else:
            supported_exts = ", ".join(SUPPORTED_MIME_TYPES.keys())
            raise ValueError(
                f"Unsupported image format '{extension}'. Supported formats: {supported_exts}"
            )

    # 4. Read image and encode to base64
    try:
        with open(path, "rb") as image_file:
            image_bytes = image_file.read()

        if len(image_bytes) == 0:
            raise ValueError(f"Image file is empty: {path}")

        base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        raise IOError(f"Failed to read image file {path}: {str(exc)}") from exc

    data_url = f"data:{mime_type};base64,{base64_encoded}"

    return {
        "image_path": str(path),
        "mime_type": mime_type,
        "data_url": data_url,
    }
