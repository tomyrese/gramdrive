import os
import csv
import asyncio
from typing import List, Dict, Any, Optional
from core.database import Database
from core.uploader import Uploader
from core.downloader import Downloader
from core.telegram_client import TelegramClient

class FileManager:
    def __init__(self, db: Database, telegram_client: TelegramClient, uploader: Uploader, downloader: Downloader):
        self.db = db
        self.client = telegram_client
        self.uploader = uploader
        self.downloader = downloader

    def upload_file(self, file_path: str) -> str:
        return self.uploader.add_to_queue(file_path)

    def download_file(self, filename: str, file_hash: str, dest_path: str) -> None:
        self.downloader.add_to_queue(filename, file_hash, dest_path)

    def search_file(self, query: str) -> List[Dict[str, Any]]:
        return self.db.search_files(query)

    async def delete_file(self, file_id: int) -> bool:
        file_meta = self.db.get_file(file_id)
        if not file_meta:
            return False
        
        filename = file_meta["filename"]
        file_hash = file_meta["hash"]
        
        chunks = self.db.get_file_chunks(filename, file_hash)
        for chunk in chunks:
            msg_id = chunk.get("telegram_message_id")
            if msg_id:
                await self.client.delete_message(msg_id)
                
        self.db.delete_file_group(filename, file_hash)
        return True

    def get_storage_usage(self) -> Dict[str, Any]:
        return self.db.get_total_usage()

    @staticmethod
    def scan_file_ai(file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"type": "Unknown", "tags": [], "category": "Unknown"}

        size = os.path.getsize(file_path)
        ext = os.path.splitext(file_path)[1].lower().strip(".")
        
        category = "Other"
        tags = []

        images = ["jpg", "jpeg", "png", "gif", "bmp", "webp", "svg"]
        videos = ["mp4", "mkv", "avi", "mov", "flv", "wmv"]
        documents = ["pdf", "docx", "doc", "xlsx", "xls", "pptx", "ppt", "txt", "csv", "md"]
        archives = ["zip", "rar", "7z", "tar", "gz"]
        executables = ["exe", "msi", "bat", "sh"]

        if ext in images:
            category = "Image"
            tags.append("media")
            tags.append("visual")
        elif ext in videos:
            category = "Video"
            tags.append("media")
            tags.append("motion")
        elif ext in documents:
            category = "Document"
            tags.append("text")
            tags.append("office")
        elif ext in archives:
            category = "Archive"
            tags.append("compressed")
            tags.append("backup")
        elif ext in executables:
            category = "Executable"
            tags.append("program")
            tags.append("system")

        if size > 100 * 1024 * 1024:
            tags.append("very_large")
        elif size > 10 * 1024 * 1024:
            tags.append("large")
        else:
            tags.append("small")

        if ext in ["py", "js", "html", "css", "cpp", "c", "h", "java", "go", "rs"]:
            category = "Code"
            tags.append("programming")
            tags.append("text")

        tags.append(ext)
        return {
            "type": ext.upper(),
            "tags": list(set(tags)),
            "category": category
        }

    def export_metadata_csv(self, dest_path: str) -> None:
        files = self.db.get_all_files()
        if not files:
            return
        
        keys = files[0].keys()
        with open(dest_path, "w", newline="", encoding="utf-8") as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(files)

    def import_metadata_csv(self, src_path: str) -> None:
        with open(src_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                file_data = {
                    "filename": row["filename"],
                    "size": int(row["size"]),
                    "type": row["type"],
                    "upload_date": row["upload_date"],
                    "telegram_message_id": row["telegram_message_id"],
                    "telegram_file_id": row["telegram_file_id"],
                    "chunk_index": int(row["chunk_index"]),
                    "total_chunks": int(row["total_chunks"]),
                    "encrypted": int(row["encrypted"]),
                    "hash": row["hash"],
                    "local_cache_path": row["local_cache_path"],
                    "tags": row["tags"],
                    "favorite": int(row["favorite"])
                }
                self.db.add_file(file_data)
