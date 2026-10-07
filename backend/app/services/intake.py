import os
import zipfile
import shutil
import tempfile
import subprocess
import logging
from typing import Tuple, Dict, Any, List

logger = logging.getLogger("securesupply.intake")

class IntakeService:
    @staticmethod
    def extract_zip(zip_path: str, extract_to: str) -> List[str]:
        extracted_files = []
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            for root, _, files in os.walk(extract_to):
                for file in files:
                    extracted_files.append(os.path.join(root, file))
        return extracted_files

    @staticmethod
    def process_file_upload(file_content: bytes, filename: str, target_dir: str) -> str:
        os.makedirs(target_dir, exist_ok=True)
        file_path = os.path.join(target_dir, filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        if filename.endswith(".zip"):
            extract_dir = os.path.join(target_dir, "extracted")
            os.makedirs(extract_dir, exist_ok=True)
            IntakeService.extract_zip(file_path, extract_dir)
            return extract_dir
        return file_path

    @staticmethod
    def clone_git_repo(git_url: str, target_dir: str) -> str:
        os.makedirs(target_dir, exist_ok=True)
        repo_dir = os.path.join(target_dir, "repo")
        try:
            cmd = ["git", "clone", "--depth", "1", git_url, repo_dir]
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
            logger.info(f"Cloned repository {git_url} to {repo_dir}")
            return repo_dir
        except Exception as e:
            logger.error(f"Failed to clone git repo {git_url}: {e}")
            raise ValueError(f"Failed to clone Git repository: {str(e)}")
