from .models import Account
from news.models import News, Comments, Categories
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from PBL6_Fake_News_Detection_BE.middleware import AdminAuthorizationMiddleware, UserAuthorizationMiddleware
from PBL6_Fake_News_Detection_BE.settings import SECRET_KEY
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializer import CategoriesSerializer, NewsSerializer, CommentsSerializer
from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10  # Đặt giá trị mặc định cho page_size
    page_size_query_param = 'page_size'
    max_page_size = 100  # Đặt giá trị mặc định cho max_page_size

# ---------------------------------     ADMIN  ROUTE     ---------------------------------

@AdminAuthorizationMiddleware
@api_view(['GET'])
def categories_list(request):
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
        
# @AdminAuthorizationMiddleware
@api_view(['GET'])
def news_list(request):
    try:
        news = News.objects.all()

        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        news_info = []

        # Lặp qua danh sách danh mục và tính số lượng tin tức cho mỗi danh mục
        for item in news:
            news_count = Comments.objects.filter(news=item).count()
            # author = Account.objects.filter(id=item.account).first().username
            # category = Categories.objects.filter(id=item.category).first().name
            author = item.account.username
            category = item.category.name
            news_info.append({
                'id': item.id,
                'title': item.title,
                'author' : author,
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

# @AdminAuthorizationMiddleware   
@api_view(['GET'])
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

# @AdminAuthorizationMiddleware
@api_view(['GET'])
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

# @AdminAuthorizationMiddleware 
@api_view(['GET'])
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

# @AdminAuthorizationMiddleware
@api_view(['GET'])
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
    
# ---------------------------------     USER  ROUTE     ---------------------------------

@UserAuthorizationMiddleware
@api_view(['GET'])
def get_all_categories(request):
    categories = Categories.objects.all()
    serializer = CategoriesSerializer(categories, many=True)
    return JsonResponse(
        data={
            'success': True,
            'categories': serializer.data
        },
        status=status.HTTP_200_OK
    )

@UserAuthorizationMiddleware
@api_view(['GET'])
def get_all_news(request):
    news = News.objects.all()
    serializer = NewsSerializer(news, many=True)
    return JsonResponse(
        data={
            'success': True,
            'news': serializer.data
        },
        status=status.HTTP_200_OK
    )

@UserAuthorizationMiddleware
@api_view(['GET'])
def get_all_comments(request):
    comments = Comments.objects.all()
    serializer = CommentsSerializer(comments, many=True)
    return JsonResponse(
        data={
            'success': True,
            'coments': serializer.data
        },
        status=status.HTTP_200_OK
    )

@UserAuthorizationMiddleware
@api_view(['GET'])  
def total_news(request):
    news_count = News.objects.count()
    return JsonResponse(
        data={
            'success': True,
            'news_count': news_count
        },
        status=status.HTTP_200_OK
    )

@UserAuthorizationMiddleware
@api_view(['GET'])
def paging(request):
    page_number = int(request.query_params.get('page_number', 1))
    page_size = int(request.query_params.get('page_size', 10))

    start = (page_number - 1) * page_size
    end = start + page_size

    queryset = News.objects.all()[start:end]
    serialized_data = NewsSerializer(queryset, many=True)

    return JsonResponse(
        data={
            'list_news': serialized_data.data,
            'page_number': page_number,
            'page_size': page_size
        },
        status=status.HTTP_200_OK
    )
