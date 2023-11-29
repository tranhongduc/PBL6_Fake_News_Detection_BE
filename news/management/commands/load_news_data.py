from django.core.management.base import BaseCommand
from news.factories import NewsFactory  # Thay your_app bằng tên ứng dụng Django của bạn

class Command(BaseCommand):
    help = 'Load news data from CSV'

    def handle(self, *args, **options):
        csv_file_path = '../PBL6_Fake_News_Detection_BE/data/train.csv'  # Đặt đường dẫn tới file CSV của bạn
        limit = None  # Đặt giới hạn nếu bạn muốn

        # Gọi hàm để đọc dữ liệu và lưu vào bảng News
        NewsFactory.load_news_data(csv_file_path, limit)
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded news data.'))