import platform
import subprocess
from pathlib import Path
from time import sleep

from pymongo import MongoClient


class ContentDB:
    def __init__(
        self,
        persist_filepath: Path,
        mongodb_path: Path = Path("."),
        mongodb_tools_path: Path = Path("."),
        local_dev: bool = False,
    ) -> None:
        self.persist_filepath = persist_filepath
        self.mongodb_path = mongodb_path
        self.mongodb_tools_path = mongodb_tools_path
        if local_dev:
            self.start_mongodb()
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["content_db"]
        self.collection = self.db["contents"]

        self.load()

    def start_mongodb(self) -> None:
        """
        Starts the server (only in local development and if mongod is not launched separately)


        Parameters
        ----------
        `mongodb_path` : Path, optional
            local bin dir where to find the mongod executable, by default Path(".")
        """
        self.persist_filepath.mkdir(parents=True, exist_ok=True)
        if platform.system() == "Windows":
            self.mongod_process = subprocess.Popen(
                [
                    self.mongodb_path / "mongod.exe",
                    "--dbpath",
                    self.persist_filepath.as_posix(),
                    "--bind_ip",
                    "127.0.0.1",
                ],
                shell=True,
            )
        elif platform.system() == "Linux":
            self.mongod_process = subprocess.Popen(
                [
                    "gnome-terminal",
                    "--",
                    self.mongodb_path / "mongod",
                    "--dbpath",
                    self.persist_filepath.as_posix(),
                    "--bind_ip",
                    "127.0.0.1",
                ],
            )
        else:
            self.mongod_process = subprocess.Popen(
                [
                    "open",
                    "-a",
                    "Terminal",
                    "--args",
                    self.mongodb_path / "mongod",
                    "--dbpath",
                    self.persist_filepath.as_posix(),
                    "--bind_ip",
                    "127.0.0.1",
                ],
            )
        sleep(3)

    def dump(self) -> None:
        if self.persist_filepath.exists():
            self.persist_filepath.unlink()

        mongod_command = (
            (self.mongodb_tools_path / "mongodump.exe")
            if platform.system() == "Windows"
            else (self.mongodb_path / "mongorestore")
        )
        if not mongod_command.exists():
            raise FileNotFoundError(f"{mongod_command} not found.")

        subprocess.run(
            [
                mongod_command,
                "--db",
                "content_db",
                "--out",
                self.persist_filepath.as_posix(),
            ]
        )

    def load(self) -> None:
        if self.persist_filepath.exists():
            self.db.drop_collection("contents")

            mongod_command = (
                (self.mongodb_tools_path / "mongorestore.exe")
                if platform.system() == "Windows"
                else (self.mongodb_path / "mongorestore")
            )
            if not mongod_command.exists():
                raise FileNotFoundError(f"{mongod_command} not found.")

            subprocess.run(
                [mongod_command, "--db", "content_db", self.persist_filepath.as_posix()]
            )

    def stop_mongodb(self) -> None:
        self.mongod_process.terminate()
        self.mongod_process.wait()
