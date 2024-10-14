# Gossip Semantic Search

## Exercise

The context is provided in [Gossip_Semantic_Search.pdf](./Gossip_Semantic_Search.pdf)

## Run Locally

- Install [MongoDB](https://www.mongodb.com/try/download/shell) anc corresponding [tools](https://www.mongodb.com/try/download/database-tools)
- Create a .env file matching .env.example pattern
- Launch mongodb from the root directory of this project `mongod.exe --dbpath "data/articles_content" --bind_ip 127.0.0.1`
- run in a separate terminal `python main.py`
- backend only can be tested through `python "tests/api/test_live_api.py"`
- The front can be used by logging to <http://127.0.0.2:8000/> (unsecure connection)

## Run on Docker

- run `docker-compose -p linkup-img  up --build`
- check the status of the containers, in particular the fastapi_app status (can take a few mins to boot). Even after the app has started, the search bar can return empty results if you don't wait for long enough.
- The front can be used by logging to <http://127.0.0.2:8000/> (unsecure connection)

## Notes

This is a bare-metal solution satisfying the requirements from the exercise.

### Choosing a data structure

In this case we want to store embeddings, article content and metadata. Several solutions are possible here.
In the end what remains is:

- ChromaDB, a popular vector DB with more support for metadata than FAISS. This DB has its own support for an embedding function... It might have been cleverer to use it, here I just decided to use a custom embedder an to pass embeddings as list of float (chromaDB supports this). ChromaDB simplifies the process for similarity search (as the bahavior is already coded within)
- MongoDB, for the article content and metadata I picked. A No-Relational database. Assuming document content can be very long, it is best not to store this in a RelationDB.

I thought of using SQLite at some point to store relational data between documents, sources, links, authors, etc. and traces of this are left in the code. In the end for this particular usecase it was overkill to use 3 databases.
As a matter of fact given how small the articles are, ChromaDB could have sufficed here. The approach I picked is potentially more scalable though.

For the sake of the exercise, I decided to make both databases persistent and stored under data/ . Whenever both databases are started they load from their previous state as the exercise demanded.

### Choosing an embedding strategy

Here I decided to rely on a very popular, simple and light approach: the default sentence-transformer embedder with model all-MiniLM-L6-v2. A more complex model and a higher dimension would potentially lead to a better performance when looking for similarity.

I decided to leave to chroma_DB API the similarity search, but usually it is done internally by comparing all vectors through cosine distance and retrieving the k best results.

### Populating the database

The database is populated from both gossip websites using a FeedHandler object, attached to the databases. Rather tha scrapping the websites, it will read the RSS from both news websites and .

### Backend

I used FAstAPI as a tool convenient for prototyping and yet easily scalable. Databases pointers are stored within the app state for proper dependency injection when calling the routes, which is not a topic I understand very well yet.
The API is usable without the front.

Through a POST method, the query is embedded the same way the articles are, compare with others in the vector_DB, then closest embeddings_ids metadata is retrieved from the content_DB.

### Frontend

Since front-end is not my core skill, I heavily relied on chatgpt to create a static html and css file. The search bar triggers javascript code that makes the call to the backend and generates the table on the fly.
NB: it would be much more professional and scalable to use a framework like react. However, I did not get to experiment on this, given the time contraint.

### Containerization

As often, this was a challenge. We need at least 2 separate services: potentially more. Basically the databases are containers on their own and communicate through networking with the app. Also "localhost" can be "mongodb" if you're running from a container instead of locally. Current code addresses several such problems.

### Code Structure

Most of the code is packaged under src.

- Databases dir contains the code for the embedding db, and content_db. the metadatadb (the relational one) is not used in the end but I left the code just for show.
- etl dir contains the code for reading the feed, and using the databases properly. the embedding logic relies in there.
- orm_models dir contains the code for pydantic modules used for the creation of the relational db. no longer in use in the current code.
- query dir contains the logic to embed a query and compare it to the t of the databse, then retrieve similar articles content.
- static contains the html, css etc. used for the frontend rendering.

### Unit tests

Many unit tests could be written, only a fraction are provided here under tests (lack of time to do a complete run). Pytest was used. Testing MongoDB connection implied a heavy use of mocking.

## TODO

- [x] use the persistent client in chromadb plutot que le dump chelou h5py
- [x] make sure that databases actually are more object oriented (each db handles the addition of articles)
- [ ] do I use correctly the dependency injection mechanism for dbs in the app? I should at least explain that I do not know
- [x] make sure I keep track of articles added in mongodb so that I don't reinsert existing ones in the chromadb
- [x] create unit tests
- [x] check structure
- [x] check comments and doctstings
- [x] have a working dockerfile
- [x] in mongodb, if the db was not started, I should raise an error
- [x] is it actually more relevant to have it all in mongodb instead of having an sqlite db?
- [ ] can i use pydantic instead of json to create the feed
- [ ] raise an explicit error if sourcename does not exist in  retrieveLatestRssFeed
- [x] I won't do all tests, but for exp I should be careful of upsert operations in the sql db or in the faiss db
- [x] skip test_live_api.py from the tests when running the pytest cmd.

## Example query

    "Quel est le rapport entre Pierre Garnier et la star academy, cette emission de danse?"
