import os
import time
import asyncio
from typing import Callable, List, Optional, Dict, Any
from core.database import Database
from core.encryptor import Encryptor
from core.chunk_manager import ChunkManager
from core.telegram_client import TelegramClient

class UploadTask:
    def __init__(self, file_path: str, file_id: str, size: int):
        self.file_path = file_path
        self.file_id = file_id
        self.size = size
        self.progress = 0
        self.status = "Queued"
        self.speed = 0.0
        self.error = ""

class Uploader:
    def __init__(self, db: Database, client: TelegramClient):
        self.db = db
        self.client = client
        self.queue: List[UploadTask] = []
        self.active_task: Optional[UploadTask] = None
        self.is_running = False
        self.cancel_requested = False

    def add_to_queue(self, file_path: str) -> str:
        file_id = str(int(time.time() * 1000))
        size = os.path.getsize(file_path)
        task = UploadTask(file_path, file_id, size)
        self.queue.append(task)
        return file_id

    async def run_queue(
        self, 
        progress_cb: Optional[Callable[[UploadTask], None]] = None,
        complete_cb: Optional[Callable[[UploadTask], None]] = None
    ) -> None:
        if self.is_running:
            return
        self.is_running = True
        self.cancel_requested = False

        while self.queue and not self.cancel_requested:
            self.active_task = self.queue.pop(0)
            self.active_task.status = "Processing"
            if progress_cb:
                progress_cb(self.active_task)

            try:
                await self._upload_file(self.active_task, progress_cb)
                self.active_task.status = "Completed"
                if complete_cb:
                    complete_cb(self.active_task)
            except Exception as e:
                self.active_task.status = "Failed"
                self.active_task.error = str(e)
                if complete_cb:
                    complete_cb(self.active_task)
            finally:
                self.active_task = None

        self.is_running = False

    async def _upload_file(self, task: UploadTask, progress_cb: Optional[Callable[[UploadTask], None]]) -> None:
        encrypt_enabled = self.db.get_setting("encryption_enabled", "0") == "1"
        passphrase = self.db.get_setting("encryption_key", "")
        chunk_size_setting = int(self.db.get_setting("chunk_size", str(40 * 1024 * 1024)))

        temp_dir = "temp/upload"
        os.makedirs(temp_dir, exist_ok=True)

        work_file = task.file_path
        is_encrypted = 0

        if encrypt_enabled and passphrase:
            enc_file_path = os.path.join(temp_dir, f"{task.file_id}.enc")
            task.status = "Encrypting"
            if progress_cb:
                progress_cb(task)
            await asyncio.to_thread(Encryptor.encrypt_file, task.file_path, enc_file_path, passphrase)
            work_file = enc_file_path
            is_encrypted = 1

        task.status = "Calculating Hash"
        if progress_cb:
            progress_cb(task)
        file_hash = await asyncio.to_thread(ChunkManager.calculate_hash, task.file_path)

        task.status = "Splitting File"
        if progress_cb:
            progress_cb(task)
        chunks = await asyncio.to_thread(ChunkManager.split_file, work_file, chunk_size_setting, temp_dir)
        total_chunks = len(chunks)

        task.status = "Uploading"
        start_time = time.time()
        uploaded_bytes = 0

        for chunk_path, chunk_index, chunk_hash in chunks:
            if self.cancel_requested:
                task.status = "Cancelled"
                break

            chunk_size = os.path.getsize(chunk_path)
            
            def chunk_progress(current, total):
                nonlocal uploaded_bytes
                current_uploaded = uploaded_bytes + current
                task.progress = int((current_uploaded / task.size) * 100)
                elapsed = time.time() - start_time
                if elapsed > 0:
                    task.speed = current_uploaded / elapsed
                if progress_cb:
                    progress_cb(task)

            res = await self.client.upload_chunk(chunk_path, chunk_progress)
            if not res:
                raise Exception(f"Failed to upload chunk {chunk_index}")

            uploaded_bytes += chunk_size
            
            self.db.add_file({
                "filename": os.path.basename(task.file_path),
                "size": task.size,
                "type": os.path.splitext(task.file_path)[1].lower().strip("."),
                "upload_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "telegram_message_id": res["message_id"],
                "telegram_file_id": res["file_id"],
                "chunk_index": chunk_index,
                "total_chunks": total_chunks,
                "encrypted": is_encrypted,
                "hash": file_hash,
                "local_cache_path": "",
                "tags": "",
                "favorite": 0
            })

            try:
                os.remove(chunk_path)
            except Exception:
                pass

        if encrypt_enabled and work_file != task.file_path:
            try:
                os.remove(work_file)
            except Exception:
                pass

    def cancel_upload(self) -> None:
        self.cancel_requested = True
        if self.active_task:
            self.active_task.status = "Cancelled"
