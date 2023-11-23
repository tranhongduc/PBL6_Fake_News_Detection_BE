import random
from factory import Factory, Faker, LazyAttribute, Sequence
from .models import Categories, News, Comments, Interacts
from auth_site.models import Account

categories = ["Sport", "Cuisine", "Tourism", "Technology", "Health", "Education", "Music", "Movie", "Political", "Science"]

def get_image_url(category_name):
    # Đặt đường dẫn của thư mục news trong Firebase Storage
    storage_path = "gs://pbl6-8431d.appspot.com/news"
    # Tạo đường dẫn đầy đủ đến thư mục của category
    category_path = f"{storage_path}/{category_name}"
    # Sinh ngẫu nhiên một số từ 1 đến 10 để chọn ảnh
    random_image_number = random.randint(1, 10)
    # Tạo đường dẫn đầy đủ đến ảnh trong thư mục category
    image_path = f"{category_path}/{category_name.lower()}{random_image_number}.jpeg"
    return image_path

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
    image = LazyAttribute(lambda x: get_image_url(x.category.name))
    label = LazyAttribute(lambda x: random.choice(['fake'] * 3 + ['real'] * 7))
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    category = Faker('random_element', elements=Categories.objects.all())

class CommentsFactory(Factory):                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           
    class Meta:
        model = Comments
    
    text = Faker('text', max_nb_chars=500)
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    news = Faker('random_element', elements=News.objects.filter(label='real'))

class InteractsFactory(Factory):
    class Meta:
        model = Interacts
    label = LazyAttribute(lambda x: random.choice(['news'] * 4 + ['comment'] * 3 + ['account'] * 3))
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    target_type = LazyAttribute(lambda x: 
                                'like' if x.label == 'comment' 
                                else 'follow' if x.label == 'account' 
                                else random.choice(['like', 'save']))
    target_id = LazyAttribute(lambda x: 
                              random.choice(News.objects.filter(label='real').values_list('id', flat=True)) if x.label == 'news' 
                              else random.choice(Comments.objects.values_list('id', flat=True)) if x.label == 'comment'
                              else random.choice(Account.objects.filter(role='user').values_list('id', flat=True)))

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