import random
from factory import Factory, SubFactory, Faker, LazyAttribute
from .models import Categories, News, Comments, Interacts
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
    total_like = Faker('random_int', min=0, max=1000)
    total_save = Faker('random_int', min=0, max=1000)
    total_view = Faker('random_int', min=0, max=10000)

class CommentsFactory(Factory):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
    class Meta:
        model = Comments
    
    text = Faker('text')
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    news = Faker('random_element', elements=News.objects.filter(label='real'))
    total_like = Faker('random_int', min=0, max=1000)

class InteractsFactory(Factory):
    class Meta:
        model = Interacts
    label = LazyAttribute(lambda x: random.choice(['news'] * 3 + ['comment'] * 7))
    target_type = LazyAttribute(lambda x: 'like' if x.label == 'comment' else random.choice(['like', 'save']))
    # target_id = LazyAttribute(lambda x: News.objects.filter(label='real').first().id if x.label == 'news' else Comments.objects.first().id)
    target_id = LazyAttribute(lambda x: random.choice(News.objects.filter(label='real').values_list('id', flat=True)) if x.label == 'news' else random.choice(Comments.objects.values_list('id', flat=True)))


# Tạo danh sách News ngẫu nhiên
num_objects = 100
news = [NewsFactory() for _ in range(num_objects)]
# Tạo danh sách Comments ngẫu nhiên
num_object = 100
comments = [CommentsFactory() for _ in range(num_object)]
# # Tạo danh sách Interacts ngẫu nhiên
num_interacts = 1000
interacts = [InteractsFactory.create() for _ in range(num_interacts)]
Interacts.objects.bulk_create(interacts)