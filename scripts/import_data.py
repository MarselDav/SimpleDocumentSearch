import asyncio
from datetime import datetime
import io

import pandas as pd
import requests
from app.db.models.document import DocumentORM
from app.db.database import AsyncSessionFactory
from ast import literal_eval
from sqlalchemy import delete, insert
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
import asyncio
import os
from dotenv import load_dotenv

PUBLIC_URL = 'https://disk.360.yandex.ru/d/UYooXd9q2yqTMQ'

API_URL = (
    f'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={PUBLIC_URL}'
)

load_dotenv()

ELASTICSEARCH_URL = os.environ["ELASTICSEARCH_URL"]
ELASTICSEARCH_USERNAME = os.environ["ELASTICSEARCH_USERNAME"]
ELASTIC_PASSWORD = os.environ["ELASTIC_PASSWORD"]

INDEX_NAME = "documents"

def get_data_yandex_disk() -> pd.DataFrame:
  response = requests.get(API_URL)
  download_url = response.json().get('href')

  if not download_url:
    raise ValueError('Не удалось получить прямую ссылку на файл.')

  file_data = requests.get(download_url)
  file_data.raise_for_status()

  return pd.read_csv(io.StringIO(file_data.content.decode('utf-8')))

async def import_data_postgres(df : pd.DataFrame) -> None:
  records = [{
    "id" : i,
    "text": row["text"],
    "created_date": datetime.strptime(row["created_date"], '%Y-%m-%d %H:%M:%S'),
    "rubrics": literal_eval(row["rubrics"])} for i, row in df.iterrows()]

  async with AsyncSessionFactory() as session:
    await session.execute(delete(DocumentORM))

    if records:
      await session.execute(insert(DocumentORM), records)

    await session.commit()


async def import_data_elastic(df : pd.DataFrame) -> None:
  records = [
  { "_index": INDEX_NAME,
    "_id":str(i),
    "_source": {"id" : i, "text": row["text"]}
  } for i, row in df.iterrows()]

  async with AsyncElasticsearch(
          ELASTICSEARCH_URL,
          basic_auth=(
              ELASTICSEARCH_USERNAME,
              ELASTIC_PASSWORD
          )
  ) as client:
    print("Elasticsearch connected: ", await client.ping())

    exists = await client.indices.exists(index=INDEX_NAME)

    if exists:
      await client.indices.delete(index=INDEX_NAME)

    await client.indices.create(
      index=INDEX_NAME,
      mappings={
        "properties": {
          "id": {"type": "long"},
          "text": {"type": "text"},
        }
      }
    )

    success, failed = await async_bulk(client=client, actions=records)

    print(f"Успешно добавлено документов: {success}")
    print(f"Ошибок при добавлении: {failed}")

    await client.indices.refresh(index=INDEX_NAME)


if __name__ == "__main__":
  dataframe = get_data_yandex_disk()
  asyncio.run(import_data_postgres(dataframe))
  asyncio.run(import_data_elastic(dataframe))