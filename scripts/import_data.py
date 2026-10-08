import asyncio
from datetime import datetime
import io
import pandas as pd
import requests
from app.db.models.document import DocumentORM
from app.db.database import AsyncSessionFactory
from ast import literal_eval
from sqlalchemy import delete, insert

PUBLIC_URL = 'https://disk.360.yandex.ru/d/UYooXd9q2yqTMQ'

API_URL = (
    f'https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key={PUBLIC_URL}'
)

async def import_data() -> None:
  response = requests.get(API_URL)
  download_url = response.json().get('href')

  if not download_url:
    raise ValueError('Не удалось получить прямую ссылку на файл.')

  file_data = requests.get(download_url)
  file_data.raise_for_status()

  df = pd.read_csv(io.StringIO(file_data.content.decode('utf-8')))

  records = [{
    "text": row["text"],
    "created_date": datetime.strptime(row["created_date"], '%Y-%m-%d %H:%M:%S'),
    "rubrics": literal_eval(row["rubrics"])} for _, row in df.iterrows()]

  async with AsyncSessionFactory() as session:
    await session.execute(delete(DocumentORM))

    if records:
      await session.execute(insert(DocumentORM), records)

    await session.commit()

if __name__ == "__main__":
  asyncio.run(import_data())