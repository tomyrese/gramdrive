import os
import hashlib
from typing import List, Tuple

class ChunkManager:
    @staticmethod
    def calculate_hash(file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(64 * 1024)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()

    @classmethod
    def split_file(cls, file_path: str, chunk_size: int, output_dir: str) -> List[Tuple[str, int, str]]:
        os.makedirs(output_dir, exist_ok=True)
        chunks = []
        base_name = os.path.basename(file_path)
        
        with open(file_path, "rb") as f:
            chunk_index = 0
            while True:
                chunk_data = f.read(chunk_size)
                if not chunk_data:
                    break
                
                chunk_name = f"{base_name}.part{chunk_index}"
                chunk_path = os.path.join(output_dir, chunk_name)
                
                with open(chunk_path, "wb") as chunk_file:
                    chunk_file.write(chunk_data)
                
                chunk_hash = cls.calculate_hash(chunk_path)
                chunks.append((chunk_path, chunk_index, chunk_hash))
                chunk_index += 1
                
        return chunks

    @classmethod
    def merge_chunks(cls, chunk_paths: List[str], output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, "wb") as f_out:
            for path in chunk_paths:
                with open(path, "rb") as f_in:
                    while True:
                        data = f_in.read(64 * 1024)
                        if not data:
                            break
                        f_out.write(data)
                        
        return cls.calculate_hash(output_path)
