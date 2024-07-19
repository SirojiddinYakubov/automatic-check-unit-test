from articles.models import Article, Topic, ArticleStatus
from faker import Faker
import factory
from .user_factory import UserFactory


fake = Faker()


class TopicFactory(factory.django.DjangoModelFactory):
    """ This class will create fake data for topic """

    class Meta:
        model = Topic

    id = factory.Faker('pyint', min_value=1, max_value=1000)
    name = factory.LazyAttribute(lambda _: fake.word())


class ArticleFactory(factory.django.DjangoModelFactory):
    """ This class will create fake data for article """

    class Meta:
        model = Article

    id = factory.Faker('pyint', min_value=1, max_value=1000)
    title = factory.LazyAttribute(lambda _: fake.sentence())
    summary = factory.LazyAttribute(lambda _: fake.text())
    status = ArticleStatus.PUBLISH
    content = factory.LazyAttribute(lambda _: fake.text())
    thumbnail = fake.image_url()[:30]
    author = factory.SubFactory(UserFactory)

    @factory.post_generation
    def topics(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for topic in extracted:
                self.topics.add(topic)
