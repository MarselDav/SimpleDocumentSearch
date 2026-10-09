from elasticsearch import AsyncElasticsearch
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

ELASTICSEARCH_URL = os.environ["ELASTICSEARCH_URL"]
ELASTICSEARCH_USERNAME=os.environ["ELASTICSEARCH_USERNAME"]
ELASTIC_PASSWORD=os.environ["ELASTIC_PASSWORD"]

INDEX_NAME = "documents"

async def create_documents_index():
    async with AsyncElasticsearch(
        ELASTICSEARCH_URL,
        basic_auth=(
            ELASTICSEARCH_USERNAME,
            ELASTIC_PASSWORD
        )
    ) as client:
        print("Elasticsearch connected: ", await client.ping())

        exists = await client.indices.exists(index=INDEX_NAME)

        if not exists:
            await client.indices.create(
                index=INDEX_NAME,
                mappings={
                    "properties" : {
                        "id" : {"type" : "long"},
                        "text" : {"type" : "text"},
                    }
                }
            )

        await client.indices.refresh(index=INDEX_NAME)


if __name__ == "__main__":
    asyncio.run(create_documents_index())