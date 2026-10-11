from datetime import datetime
import pytest

@pytest.mark.parametrize(
    ["documents_data", "query", "expected_status_code", "expected_result"],
    [
        (
            [],
            "Привет, это тестовый запрос",
            200,
            []
        ),
        (
            [{"id" : 1,
              "text" : "Тестовый текст",
              "created_date" : datetime.strptime("2019-07-25 12:42:13",
                                                 '%Y-%m-%d %H:%M:%S'),
              "rubrics" : ["vk-01", "vk-02"],},
             ],
            "текст",
            200,
            [{"id": 1,
              "text": "Тестовый текст",
              "created_date": '2019-07-25T12:42:13',
              "rubrics": ["vk-01", "vk-02"], },
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


@pytest.mark.parametrize(
    ["documents_data", "id", "expected_status_code", "expected_result"],
    [
        (
            [{"id" : 1,
              "text" : "Тестовый текст",
              "created_date" : datetime.strptime("2019-07-25 12:42:13",
                                                 '%Y-%m-%d %H:%M:%S'),
              "rubrics" : ["vk-01", "vk-02"],},
             ],
            1,
            200,
            {
                'elasticsearch_result': {
                    '_index': 'test_document',
                    '_id': '1',
                    '_version': 2,
                    'result': 'deleted',
                    '_shards': {
                        'total': 2,
                        'successful': 1,
                        'failed': 0,
                    },
                    '_seq_no': 1,
                    '_primary_term': 1,
                    },
                     'postgres_result': True,
                },
        ),
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
        )
    ]
)
async def test_delete_document(
                            test_client,
                            seed_documents,
                            documents_data,
                            id,
                            expected_status_code,
                            expected_result):

    await seed_documents(documents_data)

    response = await test_client.delete(
        f'/delete_document/{id}'
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_result