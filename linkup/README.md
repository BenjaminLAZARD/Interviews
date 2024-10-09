# Gossip Semantic Search

## Exercise

The context is provided in [Gossip_Semantic_Search.pdf](./Gossip_Semantic_Search.pdf)

- download mongodb and mongodb tools
- launch mongo_db with command `mongod.exe --dbpath "data/articles_content" --bind_ip 127.0.0.1`
- persistence is automatic now
- populate .env modifying .env.example

## To Explain

## TODO

- [ ] use the persistent client in chromadb plutot que le dump chelou h5py
- [ ] make sure that databases actually are more object oriented (each db handles the addition of articles)
- [ ] make sure I keep track of articles added in mongodb so that I don't reinsert existing ones in the chromadb
- [ ] create unit tests
- [ ] check structure
- [ ] check comments and doctstings
- [ ] have a working dockerfile
- [ ] in mongodb, if the db was not started, I should raise an error
- [ ] is it actually more relevant to have it all in mongodb instead of having an sqlite db?
- [ ] can i use pydantic instead of json to create the feed
- [ ] raise an explicit error if sourcename does not exist in  retrieveLatestRssFeed
- [ ] I won't do all tests, but for exp I should be careful of upsert operations in the sql db or in the faiss db
