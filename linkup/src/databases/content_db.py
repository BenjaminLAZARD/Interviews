import os
import platform
import subprocess
from pathlib import Path
from time import sleep, time

from pymongo import MongoClient, ReplaceOne


def wait_for_mongo():
    base_uri = os.getenv(
        "MONGODB_HOST_NAME", "localhost"
    )  # Use an env variable or default to localhost
    mongo_uri = f"""mongodb://{base_uri}:27017/"""

    while True:
        try:
            client = MongoClient(mongo_uri)
            client.server_info()  # This will throw an exception if MongoDB is not ready
            print("MongoDB is up!", flush=True)
            break
        except Exception:
            print("Waiting for MongoDB to be ready...", flush=True)
            time.sleep(5)


class ContentDB:
    def __init__(
        self,
        persist_dir: Path,
        mongodb_path: Path = Path("."),
        mongodb_tools_path: Path = Path("."),
    ) -> None:
        self.persist_dir = persist_dir
        self.mongodb_path = mongodb_path
        self.mongodb_tools_path = mongodb_tools_path
        # if local_dev:
        #     self.start_mongodb()
        base_uri = os.getenv("MONGODB_HOST_NAME", "localhost")
        self.client = MongoClient(f"""mongodb://{base_uri}:27017/""")
        self.db = self.client["content_db"]
        self.collection = self.db["contents"]

    def add_or_replace_articles(self, feed: list[dict[str, str]]):
        operations = [
            ReplaceOne({"_id": article["_id"]}, article, upsert=True)
            for article in feed
        ]
        self.collection.bulk_write(operations)

    def start_mongodb(self) -> None:
        """
        Starts the server (only in local development and if mongod is not launched separately)


        Parameters
        ----------
        `mongodb_path` : Path, optional
            local bin dir where to find the mongod executable, by default Path(".")
        """
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        if platform.system() == "Windows":
            self.mongod_process = subprocess.Popen(
                [
                    self.mongodb_path / "mongod.exe",
                    "--dbpath",
                    self.persist_dir.as_posix(),
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
                    self.persist_dir.as_posix(),
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
                    self.persist_dir.as_posix(),
                    "--bind_ip",
                    "127.0.0.1",
                ],
            )
        sleep(3)

    def stop_mongodb(self) -> None:
        self.mongod_process.terminate()
        self.mongod_process.wait()
