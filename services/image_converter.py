import os
from PIL import Image

def convert_image(input_path: str, output_path: str, target_format: str) -> str:
    """Convert an image to the specified format.

    Args:
        input_path: Path to the source image file.
        output_path: Desired output file path (extension will be set based on target_format).
        target_format: One of "png", "jpg", "jpeg", "jfif" (case‑insensitive).

    Returns:
        The path to the converted image.
    """
    target_format = target_format.lower()
    if target_format == 'jpeg':
        target_format = 'jpg'
    if target_format not in {'png', 'jpg', 'jfif'}:
        raise ValueError(f"Formato de imagem não suportado: {target_format}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with Image.open(input_path) as img:
        rgb_img = img.convert('RGB')  # garante compatibilidade para JPG/JFIF
        rgb_img.save(output_path, format=target_format.upper())
    return output_path
