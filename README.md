
### SimpleDocumentSearch

#### Туториал по запуску через docker:

1) Открыть файл *.env.example* и замените поля, со значениями  *__replace__*, сохраните как *.env*

   ```dotenv
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5433
   POSTGRES_DB=documents
   POSTGRES_USER=__replace__
   POSTGRES_PASSWORD=__replace__
   
   ELASTICSEARCH_URL=http://localhost:9200
   ELASTICSEARCH_USERNAME=elastic
   ELASTIC_PASSWORD=__replace__"
   ```

2) Выполнить из корневой папки проекта:
    ```commandline
    docker compose up -d --build
   ```
3) Применить миграции alembic
    ```commandline
    docker compose exec api alembic upgrade head
   ```
4) Загрузить данные с Яндекс.Диска (https://disk.360.yandex.ru)\
    ```commandline
    docker compose run --rm api python -m scripts.import_data --url url --target all
    ```
    Здесь ``--url`` это ссылка на *.csv* файл на яндекс диске и ``--target`` это то, куда будут загружены данные (можно выбрать один из ресурсов: postgres, elasticsearch или все: all ) 
    
    ##### Используйте:
    ```commandline
    docker compose run --rm api python -m scripts.import_data --help
    ```
   Чтобы узнать подробнее про import_data\
    ##### Важно: csv может не скачаться из-за VPN

5) После выполнения команд, сервисы должны успешно запуститься, можно открыть документацию: http://127.0.0.1:8000/docs

### Вы хотите запустить тесты?
Тесты выполняются в тестовой БД и в тестовом Индексе, тестовой индекс создастся автоматически, тестовую БД PostgreSQL нужно создать:
1) Запустить PostgreSQL

    ```commandline
    docker compose exec postgres psql -U postgres
    ```
2) Создать БД test_document
    ```commandline
    CREATE DATABASE test_document;
    ```
   Выйти:
    ```commandline
    \q
   ```
3) Применить миграции alembic для тестовой БД:
    ```commandline
    docker compose exec -e POSTGRES_DB=test_document api alembic upgrade head
    ```

4) Выполнить тесты
    ```commandline
    docker compose exec api pytest tests -v
    ```