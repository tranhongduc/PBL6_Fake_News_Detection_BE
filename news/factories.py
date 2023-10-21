import random
from factory import Factory, SubFactory, Faker, LazyAttribute
from .models import Categories, News, Comments
from auth_site.models import Account
from auth_site.factories import AccountFactory
from django.db.models import Max

class CategoriesFactory(Factory):
    class Meta:
        model = Categories
    
    name = Faker('sentence', nb_words=2)

class NewsFactory(Factory):
    class Meta:
        model = News

    title = Faker('sentence', nb_words=4)
    text = Faker('text')
    image = Faker('file_name', extension='jpg')
    label = LazyAttribute(lambda x: random.choice(['fake'] * 3 + ['real'] * 7))
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    category = Faker('random_element', elements=Categories.objects.all())

class CommentsFactory(Factory):    
    class Meta:
        model = Comments
    
    text = Faker('text')
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    news = Faker('random_element', elements=News.objects.all())
# # Tạo danh sách News ngẫu nhiên
num_objects = 100
news = [NewsFactory() for _ in range(num_objects)]
# Tạo danh sách Comments ngẫu nhiên
num_object = 100
comments = [CommentsFactory() for _ in range(num_object)]