import random
from factory import Factory, SubFactory, Faker, LazyAttribute
from django.contrib.auth import get_user_model

class AccountFactory(Factory):
    class Meta:
        model = get_user_model()   # Sử dụng `get_user_model()` để có thể sử dụng mô hình người dùng mặc định của Django
    
    username = Faker('user_name')
    email = Faker('email')  # Tạo email hợp lệ
    password = '12345678'  # Sử dụng `Faker` để tạo mật khẩu mô phỏng
    role = LazyAttribute(lambda x: random.choice(['admin'] * 3 + ['user'] * 7))
    status = LazyAttribute(lambda x: random.choice(['unactive'] * 3 + ['active'] * 7))
    avatar = Faker('image_url')