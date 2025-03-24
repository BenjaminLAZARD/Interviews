from pathlib import Path

import pytest
from pymongo import ReplaceOne

from src.databases.content_db import ContentDB, wait_for_mongo


# Test for wait_for_mongo function
class TestWaitForMongo:
    def test_mongo_ready(self, mocker, capfd) -> None:
        """
        Checks that wait_for_mongo executes properly if there is a valid connection


        Parameters
        ----------
        - `mocker` (MagicMock())
        """
        # Mock the mongoclient and sleep module. simulate successful connection
        mock_mongo_client = mocker.patch("src.databases.content_db.MongoClient")
        mock_sleep = mocker.patch("src.databases.content_db.sleep", return_value=None)
        mock_client_instance = mock_mongo_client.return_value
        mock_client_instance.server_info.return_value = True

        wait_for_mongo()

        # check the sleep function was not called
        mock_mongo_client.assert_called_once()
        mock_client_instance.server_info.assert_called_once()
        mock_sleep.assert_not_called()

        # Capture the output and check if the expected print statement was called
        captured = capfd.readouterr()
        assert "MongoDB is up!" in captured.out

    def test_mongo_waits(self, mocker, capfd) -> None:
        """
        Check that wait_for_mongo waits as expected if there is no valid connection.
        """
        # Mock the mongoclient and sleep module. simulate successful connection
        mock_mongo_client = mocker.patch("src.databases.content_db.MongoClient")
        mock_sleep = mocker.patch("src.databases.content_db.sleep", return_value=None)
        mock_client_instance = mock_mongo_client.return_value

        # Simulate 2 exceptions and 1 success
        mock_client_instance.server_info.side_effect = [
            Exception("MongoDB not ready"),  # First call raises an exception
            Exception("MongoDB not ready"),  # Second call raises an exception
            True,  # Third call succeeds
        ]

        wait_for_mongo()

        # check sleep was called twice.
        mock_mongo_client.assert_called()
        assert mock_sleep.call_count == 2

        # Capture the output and check if the expected print statement was called
        captured = capfd.readouterr()
        assert "Waiting for MongoDB to be ready..." in captured.out


# Test for ContentDB class
class TestContentDB:
    @pytest.fixture
    def mock_collection(self, mocker):
        """
        Mock the MongoDB collection


        Parameters
        ----------
        - `mocker` (MagicMock())

        Returns
        -------
        - mocker object
        """
        return mocker.MagicMock()

    @pytest.fixture
    def content_db(self, mock_collection) -> ContentDB:
        """
        moccking a collection within a contentDB object


        Parameters
        ----------
        - `mock_collection` (MagicMock) : MagicMock()

        Returns
        -------
        - a ContentDB object partially mocked
        """
        # Create a ContentDB instance with a mocked collection
        content_db = ContentDB(persist_dir="/mock/path")
        content_db.collection = mock_collection
        return content_db

    # def test_init(self, mocker):
    #     # Mock the MongoClient
    #     mock_mongo_client = mocker.patch("src.databases.content_db.MongoClient")

    #     # Create a mock database and collection
    #     mock_database = mocker.Mock()
    #     mock_collection = mocker.Mock()

    #     # Set the name for the mock database
    #     mock_database.name = "content_db"  # Mock the database name
    #     mock_collection.name = "contents"  # Mock the collection name

    #     # Set up the mock return values
    #     # Simulate MongoClient returning the mock database
    #     mock_mongo_client.return_value.__getitem__.return_value = mock_database
    #     # Simulate database returning the mock collection
    #     mock_database.__getitem__.return_value = mock_collection

    #     base_uri = "localhost"
    #     persist_dir = Path("/fake/dir")

    #     content_db = ContentDB(persist_dir)

    #     assert content_db.persist_dir == persist_dir
    #     assert mock_mongo_client.call_args[0][0] == f"mongodb://{base_uri}:27017/"
    #     assert content_db.db.name == "content_db"
    #     assert content_db.collection.name == "contents"

    def test_add_or_replace_articles_adding(self, mocker) -> None:
        """
        Checks that an article can be added


        Parameters
        ----------
        - `mocker` (MagicMock)
        """
        mock_mongo_client = mocker.patch("src.databases.content_db.MongoClient")
        persist_dir = Path("/fake/dir")
        content_db = ContentDB(persist_dir)

        feed = [
            {"_id": "1", "title": "Article 1"},
            {"_id": "2", "title": "Article 2"},
        ]

        mock_collection = mock_mongo_client().db["contents"]
        content_db.collection = mock_collection

        content_db.add_or_replace_articles(feed)

        operations = [
            ReplaceOne({"_id": "1"}, {"_id": "1", "title": "Article 1"}, upsert=True),
            ReplaceOne({"_id": "2"}, {"_id": "2", "title": "Article 2"}, upsert=True),
        ]
        mock_collection.bulk_write.assert_called_once_with(operations)

    def test_add_or_replace_articles_replacement(
        self, content_db, mock_collection
    ) -> None:
        """
        Checks that an article can be modified if it is already there.


        Parameters
        ----------
        - `mocker` (MagicMock)
        """
        # Existing article
        existing_article = {"_id": 1, "title": "Old Title", "content": "Old Content"}
        # New article with the same _id but updated information
        new_article = {"_id": 1, "title": "New Title", "content": "New Content"}

        # Simulate adding the existing article
        content_db.add_or_replace_articles([existing_article])

        # Ensure that the ReplaceOne operation is called with the old article
        mock_collection.bulk_write.assert_called_once_with(
            [ReplaceOne({"_id": 1}, existing_article, upsert=True)]
        )

        # Reset the mock for the next test case
        mock_collection.bulk_write.reset_mock()

        # Simulate adding the new article
        content_db.add_or_replace_articles([new_article])

        # Ensure that ReplaceOne operation is called again, replacing the old article
        mock_collection.bulk_write.assert_called_once_with(
            [ReplaceOne({"_id": 1}, new_article, upsert=True)]
        )
