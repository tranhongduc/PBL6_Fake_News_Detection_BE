from .models import Account
from news.models import News, Comments, Categories
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.utils import timezone
import jwt
import uuid
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError
from PBL6_Fake_News_Detection_BE.settings import SECRET_KEY
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def categories_list():
    try:
        categories = Categories.objects.all()
    
        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        category_info = []

        # Lặp qua danh sách danh mục và tính số lượng tin tức cho mỗi danh mục
        for category in categories:
            news_count = News.objects.filter(category=category).count()
            category_info.append({
                'id': category.id,
                'name': category.name,
                'news_count': news_count
            })
        return JsonResponse({'categories': category_info},status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no admin users are found
        error_message = 'No category users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
    
def news_list(request):
    try:
        # Get all news items
        news = News.objects.all()
        # Check for 'page_number' parameter in the request, default to 1 if not present
        page_number = request.GET.get("page_number",1)
        # Create a Pa ginator object
        paginator = Paginator(news, 25)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
        # Lặp qua danh sách danh mục và tính số lượng tin tức cho mỗi danh mục
        response_data = {
            'current_page': news_list.number,
            'total_pages': paginator.num_pages,
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
                    'text': item.text,
                    'author': item.account.username,
                    'category': item.category.name,
                    'label': item.label,
                    'comments_count': Comments.objects.filter(news=item).count(),
                    'created_at': item.created_at
                }
                for item in news_list
            ]
        }

        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no admin users are found
        error_message = 'No item users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
def news_list_by_category(request,category_id):
    try:
        news = News.objects.filter(category=category_id)

        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        news_info = []

        # Lặp qua danh sách danh mục và tính số lượng tin tức cho mỗi danh mục
        for item in news:
            news_count = Comments.objects.filter(news=item).count()
            # author = Account.objects.filter(id=item.account).first().username
            # category = Categories.objects.filter(id=item.category).first().name
            author = item.account.username
            news_info.append({
                'id': item.id,
                'title': item.title,
                'author' : author,
                'label': item.label,
                'news_count': news_count,
                'created_at' : item.created_at
            })

        return JsonResponse({'news': news_info},status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no admin users are found
        error_message = 'No item users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
def news_list_by_author(request,author_id):
    try:
        news = News.objects.filter(account=author_id)

        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        news_info = []

        # Lặp qua danh sách danh mục và tính số lượng tin tức cho mỗi danh mục
        for item in news:
            news_count = Comments.objects.filter(news=item).count()
            # author = Account.objects.filter(id=item.account).first().username
            # category = Categories.objects.filter(id=item.category).first().name
            category = item.category.name
            news_info.append({
                'id': item.id,
                'title': item.title,
                'category' : category,
                'label': item.label,
                'news_count': news_count,
                'created_at' : item.created_at 
            })

        return JsonResponse({'news': news_info},status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no admin users are found
        error_message = 'No item users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
def coments_list_by_user(request,user_id):
    try:
        comments = Comments.objects.filter(account=user_id)

        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        news_info = []

        # Lặp qua danh sách danh mục và tính số lượng tin tức cho mỗi danh mục
        for item in comments:
            # author = Account.objects.filter(id=item.account).first().username
            # category = Categories.objects.filter(id=item.category).first().name
            news_name = item.news.title
            # author_id = item.news.account
            author = item.news.account.username
            news_info.append({
                'id': item.id,
                'text': item.text,
                'created_at' : item.created_at,
                'news' : news_name,
                'author' : author
            })

        return JsonResponse({'news': news_info},status=status.HTTP_200_OK)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
def news_detail(request, id):
    try:
        news = News.objects.get(id=id)
        comments = Comments.objects.filter(news=news.id)

        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        news_info = []

        # Lặp qua danh sách danh mục và tính số lượng tin tức cho mỗi danh mục
        for item in comments:
            # author = Account.objects.filter(id=item.account).first().username
            # category = Categories.objects.filter(id=item.category).first().name
            # author_id = item.news.account
            author = item.news.account.username
            news_info.append({
                'id': item.id,
                'text': item.text,
                'created_at' : item.created_at,
            })
        # Đếm số lượng tin tức và bình luận của người dùng
        account = news.account.username
        category = news.category.name
        comments_count = Comments.objects.filter(news=news).count()
        
        # Convert the account object and counts to a dictionary
        news_data = {
            'id': news.id,
            'title': news.title,
            'text': news.text,
            'image': news.image,
            'author' : account,
            'news_count': category,
            'comments_count': comments_count,
            'created_at' : news.created_at,
            'comments' : news_info
        }
        return JsonResponse(news_data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        error_message = 'Account not found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)  
def test(request):
    news = News.objects.all()
    cate = news.category
    return  JsonResponse(cate,status=status.HTTP_200_OK)
