import random
from factory import Factory, Sequence, Faker, LazyAttribute
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

avatars = [
    "Aether",
    "Albedo",
    "Alhaitham",
    "Aloy",
    "Amber",
    "Ayaka",
    "Ayato",
    "Baizhu",
    "Barbara",
    "Beidou",
    "Bennett",
    "Candace",
    "Charlotte",
    "Childe",
    "Chongyun",
    "Collei",
    "Cyno",
    "Dehya",
    "Diluc",
    "Diona",
    "Dori",
    "Eula",
    "Faruzan",
    "Fischl",
    "Freminet",
    "Furina",
    "Ganyu",
    "Gorou",
    "Heizou",
    "Hu Tao",
    "Itto",
    "Jean",
    "Kaeya",
    "Kaveh",
    "Kazuha",
    "Keqing",
    "Kirara",
    "Klee",
    "Kokomi",
    "Kuki Shinobu",
    "Layla",
    "Lisa",
    "Lumine",
    "Lynette",
    "Lyney",
    "Mika",
    "Mona",
    "Nahida",
    "Neuvillette",
    "Nilou",
    "Ningguang",
    "Noelle",
    "Qiqi",
    "Raiden",
    "Razor",
    "Rosaria",
    "Sara",
    "Sayu",
    "Shenhe",
    "Sucrose",
    "Thoma",
    "Tighnari",
    "Venti",
    "Wanderer",
    "Wriothesley",
    "Xiangling",
    "Xiao",
    "Xingqiu",
    "Xinyan",
    "Yae Miko",
    "Yanfei",
    "Yaoyao",
    "Yelan",
    "Yoimiya",
    "Yun Jin",
    "Zhongli",
]

def get_avatar_url(avatar):
    # Đặt đường dẫn của thư mục avatars trong Firebase Storage
    storage_path = "gs://pbl6-8431d.appspot.com/avatars"
    # Tạo đường dẫn đầy đủ đến thư mục của category
    avatar_path = f"{storage_path}/{avatar}"
    # Tạo đường dẫn đầy đủ đến ảnh trong thư mục category
    image_path = f"{avatar_path}.png"
    return image_path

class AccountFactory(Factory):
    class Meta:
        model = get_user_model()   # Sử dụng `get_user_model()` để có thể sử dụng mô hình người dùng mặc định của Django
    
    username = Faker('user_name')
    email = Faker('email')  # Tạo email hợp lệ
    password = LazyAttribute(lambda x: make_password('12345678')) # Sử dụng `Faker` để tạo mật khẩu mô phỏng
    role = LazyAttribute(lambda x: random.choice(['admin'] * 3 + ['user'] * 7))
    status = LazyAttribute(lambda x: random.choice(['unactive'] * 3 + ['active'] * 7))
    avatar = Sequence(lambda n: get_avatar_url(avatars[n % len(avatars)]))