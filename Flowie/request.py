import requests

url = "http://127.0.0.1:8000/add_to_collection"
files = [('files', open("uploads/padim_paper.pdf", 'rb'))]
resp = requests.post(url=url, files=files, data={"id": "user1", "password": "password1"})
print(resp.json())

url = "http://127.0.0.1:8000/query"
query= "What is the point of dimensionality reduction in the PADIM paper?"
resp = requests.post(url=url, data={"id": "user1", "password": "password1", "q":query})
print(resp.json())