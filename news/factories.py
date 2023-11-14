import random
from factory import Factory, Faker, LazyAttribute, Sequence
from .models import Categories, News, Comments
from auth_site.models import Account

categories = ["Sport", "Cuisine", "Tourism", "Technology", "Health", "Education", "Music", "Movie", "Political News", "Science"]
class CategoriesFactory(Factory):
    class Meta:
        model = Categories
    
    # Sử dụng Sequence để đảm bảo mỗi lần tạo đều lấy giá trị từ danh sách categories
    name = Sequence(lambda n: categories[n % len(categories)])

class NewsFactory(Factory):
    class Meta:
        model = News

    title = Faker('sentence', nb_words=6)
    text = Faker('text', max_nb_chars=3000)
    image = Faker('file_name', extension='jpg')
    label = LazyAttribute(lambda x: random.choice(['fake'] * 3 + ['real'] * 7))
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    category = Faker('random_element', elements=Categories.objects.all())

class CommentsFactory(Factory):    
    class Meta:
        model = Comments
    
    text = Faker('text', max_nb_chars=500)
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    news = Faker('random_element', elements=News.objects.all())

# Tạo danh sách News ngẫu nhiên
num_objects = 100
news = [NewsFactory() for _ in range(num_objects)]
# Tạo danh sách Comments ngẫu nhiên
num_object = 100
comments = [CommentsFactory() for _ in range(num_object)]