import os
import time
import asyncio
from typing import Callable, List, Optional, Dict, Any
from core.database import Database
from core.encryptor import Encryptor
from core.chunk_manager import ChunkManager
from core.telegram_client import TelegramClient

class DownloadTask:
    def __init__(self, filename: str, file_hash: str, dest_path: str, size: int):
        self.filename = filename
        self.file_hash = file_hash
        self.dest_path = dest_path
        self.size = size
        self.progress = 0
        self.status = "Queued"
        self.speed = 0.0
        self.error = ""

class Downloader:
    def __init__(self, db: Database, client: TelegramClient):
        self.db = db
        self.client = client
        self.queue: List[DownloadTask] = []
        self.active_task: Optional[DownloadTask] = None
        self.is_running = False
        self.cancel_requested = False

    def add_to_queue(self, filename: str, file_hash: str, dest_path: str) -> None:
        chunks = self.db.get_file_chunks(filename, file_hash)
        if not chunks:
            raise Exception("File metadata not found in database")
        size = chunks[0]["size"]
        task = DownloadTask(filename, file_hash, dest_path, size)
        self.queue.append(task)

    async def run_queue(
        self, 
        progress_cb: Optional[Callable[[DownloadTask], None]] = None,
        complete_cb: Optional[Callable[[DownloadTask], None]] = None
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
                await self._download_file(self.active_task, progress_cb)
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

    async def _download_file(self, task: DownloadTask, progress_cb: Optional[Callable[[DownloadTask], None]]) -> None:
        chunks = self.db.get_file_chunks(task.filename, task.file_hash)
        if not chunks:
            raise Exception("File not found in database")

        temp_dir = "temp/download"
        os.makedirs(temp_dir, exist_ok=True)
        
        chunk_paths = []
        downloaded_bytes = 0
        start_time = time.time()

        active_downloads = {}
        for chunk in chunks:
            chunk_filename = f"{task.filename}.part{chunk['chunk_index']}"
            chunk_path = os.path.join(temp_dir, chunk_filename)
            chunk_paths.append(chunk_path)
            if os.path.exists(chunk_path):
                active_downloads[chunk['chunk_index']] = os.path.getsize(chunk_path)
            else:
                active_downloads[chunk['chunk_index']] = 0

        async def download_single_chunk(sem, chunk):
            async with sem:
                if self.cancel_requested:
                    return

                chunk_filename = f"{task.filename}.part{chunk['chunk_index']}"
                chunk_path = os.path.join(temp_dir, chunk_filename)

                if os.path.exists(chunk_path):
                    return

                def chunk_progress(current, total):
                    active_downloads[chunk['chunk_index']] = current
                    total_downloaded = sum(active_downloads.values())
                    task.progress = int((total_downloaded / task.size) * 100)
                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        task.speed = total_downloaded / elapsed
                    if progress_cb:
                        progress_cb(task)

                success = await self.client.download_chunk(chunk["telegram_file_id"], chunk_path, chunk_progress)
                if not success:
                    raise Exception(f"Failed to download chunk {chunk['chunk_index']}")

                active_downloads[chunk['chunk_index']] = os.path.getsize(chunk_path)
                total_downloaded = sum(active_downloads.values())
                task.progress = int((total_downloaded / task.size) * 100)
                if progress_cb:
                    progress_cb(task)

        task.status = "Downloading"
        if progress_cb:
            progress_cb(task)

        sem = asyncio.Semaphore(3)
        tasks = [
            download_single_chunk(sem, chunk)
            for chunk in chunks
        ]
        await asyncio.gather(*tasks)

        if self.cancel_requested:
            return

        task.status = "Merging Chunks"
        if progress_cb:
            progress_cb(task)

        merge_dest = task.dest_path
        is_encrypted = chunks[0]["encrypted"] == 1

        if is_encrypted:
            merge_dest = os.path.join(temp_dir, f"{task.filename}.enc")

        merged_hash = await asyncio.to_thread(ChunkManager.merge_chunks, chunk_paths, merge_dest)

        if is_encrypted:
            task.status = "Decrypting File"
            if progress_cb:
                progress_cb(task)
            passphrase = self.db.get_setting("encryption_key", "")
            if not passphrase:
                raise Exception("Encryption passphrase not found in settings")
            
            try:
                await asyncio.to_thread(Encryptor.decrypt_file, merge_dest, task.dest_path, passphrase)
            finally:
                try:
                    os.remove(merge_dest)
                except Exception:
                    pass

        task.status = "Verifying Hash"
        if progress_cb:
            progress_cb(task)

        final_hash = await asyncio.to_thread(ChunkManager.calculate_hash, task.dest_path)
        if final_hash != task.file_hash:
            raise Exception("File hash verification failed")

        for path in chunk_paths:
            try:
                os.remove(path)
            except Exception:
                pass

    def cancel_download(self) -> None:
        self.cancel_requested = True
        if self.active_task:
            self.active_task.status = "Cancelled"
