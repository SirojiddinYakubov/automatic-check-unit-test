import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.fixture
def articles_data(user_factory, topic_factory, article_factory):
    """
    The function create articles data for testing.
    """

    topics = topic_factory.create_batch(3)
    user = user_factory.create()
    articles = article_factory.create_batch(5, author=user)

    for article in articles:
        article.topics.add(topics[0])
        article.topics.add(topics[1])
        article.topics.add(topics[2])

    return articles, topics


@pytest.mark.django_db
def test_articles(articles_data, api_client, tokens):
    """
    The function tests the articles.
    """

    articles, _ = articles_data
    user = articles[0].author
    access, _ = tokens(user)

    response = api_client(token=access).get('/articles/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 5


@pytest.mark.django_db
def test_articles_top(articles_data, api_client, tokens):
    """
    The function tests the association between articles and topics.
    """

    articles, topics = articles_data
    user = articles[0].author
    access, _ = tokens(user)

    response = api_client(token=access).get('/articles/?get_top_articles=2')
    print("Response data:", response.data)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2


@pytest.mark.django_db
def test_articles_topic_id(articles_data, api_client, tokens):
    """
    The function tests the association between articles and topics.
    """

    articles, topics = articles_data
    user = articles[0].author
    access, _ = tokens(user)

    topic_id = topics[0].id
    response = api_client(token=access).get(f'/articles/?topic_id={topic_id}')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 5
