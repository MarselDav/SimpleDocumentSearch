from datetime import datetime
import pytest
from app.db.models.document import DocumentORM
from sqlalchemy import select


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["documents_data", "query", "expected_status_code", "expected_result"],
    [
        # Проверка, что ничего не возвращает, когда нет документов
        (
            [],
            "Привет, это тестовый запрос",
            200,
            []
        ),
        # Проверка, что возвращает правильный документ
        (
            [{"id" : 1,
              "text" : "Тестовый текст",
              "created_date" : datetime(2019, 7, 25, 12, 42, 13),
              "rubrics" : ["vk-01", "vk-02"],},
             ],
            "текст",
            200,
            [{"id": 1,
              "text": "Тестовый текст",
              "created_date": '2019-07-25T12:42:13',
              "rubrics": ["vk-01", "vk-02"], },
             ],
        ),
        # Проверка, что возвращает максимум 20 и в правильном порядке по дате
        (
            [{"id" : i,
              "text" : f"Тест {i}",
              "created_date" : datetime(2019 + i, 7, 25, 12, 42, 13),
                "rubrics": ["vk-01", "vk-02"],
              } for i in range(25)
             ],
            "Тест",
            200,
            [{"id" : i,
              "text" : f"Тест {i}",
              "created_date" : f"{2019 + i}-07-25T12:42:13",
                "rubrics": ["vk-01", "vk-02"],
              } for i in range(19, -1, -1)
             ],
        )

    ]
)
async def test_get_documents(
                            test_client,
                            seed_documents,
                            documents_data,
                            query,
                            expected_status_code,
                            expected_result):
    await seed_documents(documents_data)

    response = await test_client.get(
        '/get_documents/',
        params={"query": query}
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_result

@pytest.mark.asyncio
@pytest.mark.parametrize(
    ["documents_data", "doc_id", "expected_status_code", "expected_result", "exist"],
    [
        # Проверка, что удаляет правильный документ
        (
            [{"id" : 1,
              "text" : "Тестовый текст",
              "created_date" : datetime(2019, 7, 25, 12, 42, 13),
              "rubrics" : ["vk-01", "vk-02"],},
             ],
            1,
            200,
            {
                'elasticsearch_result': {
                    'index': 'test_document',
                    'id': '1',
                    'result': 'deleted',
                    },
                     'postgres_result': True,
            },
            False
        ),
        # Проверка, что вызывается правильная ошибка, если нет документа с таким id
        (
            [{"id": 1,
              "text": "Тестовый текст",
              "created_date": datetime.strptime("2019-07-25 12:42:13",
                                                '%Y-%m-%d %H:%M:%S'),
              "rubrics": ["vk-01", "vk-02"], },
             ],
            2,
            404,
            {
                "detail" : "Необходимый документ с id=2 не найден."
            },
            False
        )
    ]
)
async def test_delete_document(
                            test_client,
                            seed_documents,
                            test_pg_session_factory,
                            test_es_client,
                            documents_data,
                            doc_id,
                            expected_status_code,
                            expected_result,
                            exist):

    await seed_documents(documents_data)

    response = await test_client.delete(
        f'/delete_document/{doc_id}'
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_result

    # Проверяем что действительно произошло в PostgreSQL
    async with test_pg_session_factory() as session:
        db_result = await session.execute(
            select(DocumentORM).where(DocumentORM.id == doc_id)
        )
        if exist:
            assert db_result.scalar_one_or_none() is not None
        else:
            assert db_result.scalar_one_or_none() is None

    # Проверяем что действительно произошло в Elasticsearch
    exists = await test_es_client.exists(
        index="test_document",
        id=str(doc_id),
    )
    assert exists.body is exist
