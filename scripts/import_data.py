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

import argparse

def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser()

  parser.add_argument(
    "--url",
    type=str,
    required=True,
    help="Ссылка на яндекс диск с CSV файлом"
  )

  parser.add_argument(
    "--target",
    choices=["postgres", "elasticsearch", "all"],
    default="all",
    help="Куда импортировать данные из CSV файла. "
         "Все данные, которые хранились до этого - удалятся"
  )

  return parser.parse_args()


# PUBLIC_URL = 'https://disk.360.yandex.ru/d/UYooXd9q2yqTMQ'

API_URL = (
    f'https://cloud-api.yandex.net/v1/disk/public/resources/download'
)

load_dotenv()

ELASTICSEARCH_URL = os.environ["ELASTICSEARCH_URL"]
ELASTICSEARCH_USERNAME = os.environ["ELASTICSEARCH_USERNAME"]
ELASTIC_PASSWORD = os.environ["ELASTIC_PASSWORD"]

INDEX_NAME = "documents"

def get_data_yandex_disk(url : str) -> pd.DataFrame:
  response = requests.get(
      API_URL,
    params={
      "public_key": url
    },
    timeout=15,
  )
  download_url = response.json().get('href')

  if not download_url:
    raise ValueError('[YandexDisk] Не удалось получить прямую ссылку на файл.')

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
  if df.empty:
    return

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
    print("[Elasticsearch] Подключение: ", await client.ping())

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

    success, failed = await async_bulk(client=client,
                                       actions=records,
                                       raise_on_error=False)

    print(f"[Elasticsearch] Успешно добавлено документов: {success}")
    print(f"[Elasticsearch] Ошибок при добавлении: {failed}")

    await client.indices.refresh(index=INDEX_NAME)


async def main():
  args = parse_args()

  dataframe = get_data_yandex_disk(args.url)

  if args.target == "postgres" or args.target == "all":
    await import_data_postgres(dataframe)

  if args.target == "elasticsearch" or args.target == "all":
    await import_data_elastic(dataframe)

if __name__ == "__main__":
  asyncio.run(main())