import random
from factory import Factory, Faker, LazyAttribute, Sequence
from .models import Categories, News, Comments
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
    # Sử dụng LazyAttribute để gọi hàm get_image_url với tên category tương ứng
    image = LazyAttribute(lambda x: get_image_url(x.category.name))
    label = LazyAttribute(lambda x: random.choice(['fake'] * 3 + ['real'] * 7))
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    category = Faker('random_element', elements=Categories.objects.all())

class CommentsFactory(Factory):    
    class Meta:
        model = Comments
    
    text = Faker('text', max_nb_chars=500)
    account = Faker('random_element', elements=Account.objects.filter(role='user'))
    news = Faker('random_element', elements=News.objects.all())