import os
import shutil
from typing import Optional
from PIL import Image

class CacheManager:
    def __init__(self, cache_dir: str = "temp"):
        self.cache_dir = cache_dir
        self.thumbnail_dir = os.path.join(cache_dir, "thumbnails")
        os.makedirs(self.thumbnail_dir, exist_ok=True)

    def clean_temp_dirs(self) -> None:
        for folder in ["upload", "download"]:
            path = os.path.join(self.cache_dir, folder)
            if os.path.exists(path):
                shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)

    def get_thumbnail(self, file_path: str) -> Optional[str]:
        if not os.path.exists(file_path):
            return None
        
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"]:
            return None

        file_name = os.path.basename(file_path)
        thumb_name = f"thumb_{file_name}.png"
        thumb_path = os.path.join(self.thumbnail_dir, thumb_name)

        if os.path.exists(thumb_path):
            return thumb_path

        try:
            with Image.open(file_path) as img:
                img.thumbnail((120, 120))
                img.save(thumb_path, "PNG")
            return thumb_path
        except Exception:
            return None

    def clear_all_cache(self) -> None:
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
        os.makedirs(self.thumbnail_dir, exist_ok=True)
