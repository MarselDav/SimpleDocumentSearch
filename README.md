
### SimpleDocumentSearch

#### Туториал по запуску через docker:

1) Открыть файл __.env.example__ и заменить поля, со значениями  __replace__, сохранить как __.env__

   ```dotenv
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5433
   POSTGRES_DB=documents
   POSTGRES_USER=__replace__
   POSTGRES_PASSWORD=__replace__
   
   ELASTICSEARCH_URL=http://localhost:9200
   ELASTICSEARCH_USERNAME=elastic
   ELASTIC_PASSWORD=__replace__
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
    Здесь ``--url`` это ссылка на *.csv* файл на яндекс диске, ``--target`` - это то, куда будут загружены данные (можно выбрать один из ресурсов: __postgres__, __elasticsearch__ или все: __all__) 
    
    ##### Используйте:
    ```commandline
    docker compose run --rm api python -m scripts.import_data --help
    ```
   Чтобы узнать подробнее про import_data\
    ##### Важно: csv может не скачаться из-за VPN

5) После выполнения команд, сервисы должны успешно запуститься, можно открыть документацию: http://127.0.0.1:8000/docs

### Вы хотите запустить тесты?
Тесты выполняются в тестовой БД и в тестовом Индексе, тестовой индекс создаётся автоматически, тестовую БД PostgreSQL нужно создать:
1) Запустить PostgreSQL и создать тестовую БД *test_documents*

    ```commandline
   docker compose exec postgres psql -U postgres -d documents -c "CREATE DATABASE test_documents;"
    ```
   Где ``postgres`` - ваше фактическое **POSTGRES_USER** в __.env__ файле

2) Применить миграции alembic для тестовой БД:
    ```commandline
    docker compose exec -e POSTGRES_DB=test_documents api alembic upgrade head
    ```

3) Выполнить тесты
    ```commandline
    docker compose exec api pytest tests -v
    ```