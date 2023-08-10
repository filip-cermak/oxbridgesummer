from fastapi import FastAPI, UploadFile
from pypdf import PdfReader
import numpy as np
import openai
import os
import aiofiles
from qdrant_client.http import models
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse

#API key for qdrant
client = QdrantClient(
    url="https://4ca181cc-8041-489a-8f48-b298d1c51b8b.eu-central-1-0.aws.cloud.qdrant.io/", 
    api_key="RGjydwl2SiTJ4b87cm4W2pd3B-SDp8xPAHGIgyDVBgnBJbT2gwPbxg",
)

openai.api_key='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'
app = FastAPI()

def search(x):
    resp = client.search(
    collection_name="FatherlessChildren",
    search_params=models.SearchParams(
        hnsw_ef=128,
        exact=False
    ),
    query_vector = x['data'][0]['embedding'],
    limit=3,
    )
    return resp


def insert(x):
    vectors = x
    client.upsert(
        collection_name="FatherlessChildren",
        points=[
            PointStruct(
               id=np.random.randint(10000),
               vector = vectors['data'][0]['embedding'],
               payload={"color": "red"}
            )
        ]
    )

def embed_vectors(a):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input = a
    )
    return response

print(search(embed_vectors("hello")))


@app.post("/files/")
async def create_files(files: list[bytes] = File()):
    return {"file_sizes": [len(file) for file in files]}

@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    print("hello")
    reader = PdfReader(str(files[0].filename))
    page = reader.pages[0]
    text = page.extract_text()
    embedding = embed_vectors(str(text))
    insert(embedding)
    return {"embed": embedding}

@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

@app.get("/ping")
async def pong():
    return "pong"

@app.post("/insert_cv/")
async def insert_cv(file: UploadFile = File(...)):
    async with aiofiles.open(file.filename, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    reader = PdfReader(file.filename)
    page = reader.pages[0]
    text = page.extract_text()
    embedding = embed_vectors(str(text))
    insert(embedding)
    return {"embed": embedding}

@app.post("/search_cv/")
async def search_cv(file: UploadFile = File(...)):
    async with aiofiles.open(file.filename, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    reader = PdfReader(file.filename)
    page = reader.pages[0]
    text = page.extract_text()
    embedding = embed_vectors(str(text))
    return search(embedding)