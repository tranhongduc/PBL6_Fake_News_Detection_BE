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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

class CustomPagination(PageNumberPagination):
    page_size = 10  # Đặt giá trị mặc định cho page_size
    page_size_query_param = 'page_size'
    max_page_size = 100  # Đặt giá trị mặc định cho max_page_size

# ---------------------------------     ADMIN  ROUTE     ---------------------------------
        
@api_view(['GET'])
def news_list_admin(request, page):
    try:
        # Get all news items
        news = News.objects.all()
        # Check for 'page_number' parameter in the request, default to 1 if not present
        page_number = request.GET.get("page_number",page)
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

@api_view(['GET'])
def news_list_by_category(request, category_id, page):
    try:
        news = News.objects.filter(category=category_id)
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, 25)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        response_data = {
            'current_page': news_list.number,
            'total_pages': paginator.num_pages,
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
                    'author': item.account.username,
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

@api_view(['GET'])
def news_list_by_author(request, author_id, page):
    try:
        news = News.objects.filter(account=author_id)

        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, 25)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        response_data = {
            'current_page': news_list.number,
            'total_pages': paginator.num_pages,
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
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
        error_message = 'No news found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)

@api_view(['GET'])
def comments_list_by_user(request, user_id, page):
    try:
        comments = Comments.objects.filter(account=user_id)
        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(comments, 25)
        try:
            comments_list = paginator.page(page_number)
        except PageNotAnInteger:
            comments_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        response_data = {
            'current_page': comments_list.number,
            'total_pages': paginator.num_pages,
            'comments': [
                {
                'id': item.id,
                'text': item.text,
                'created_at' : item.created_at,
                'news_id' : item.news.id,
                'news' : item.news.title,
                'author' : item.news.account.username
                }
                for item in comments_list
            ]
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
 # ---------------------------------     ALL    ---------------------------------   
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
    
@api_view(['GET'])
def news_detail(request, news_id):
    try:
        news = News.objects.get(id = news_id)
        news_data = {
            'id' : news.id,
            'title' : news.title,
            'text' : news.text,
            'image' : news.image,
            'author' : news.account.username,
            'category' : news.category.name,
            'comments_count' : Comments.objects.filter(news = news).count(),
            'created_at' : news.created_at,
            'author_id' : news.account_id,
            'category_id' : news.category_id
        }
        return JsonResponse(news_data, status = status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        error_message = 'News does not exist'
        return JsonResponse({'error': error_message}, status = status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
    
@api_view(['GET'])
def comments_list_by_news(request, news_id, page):
    try:
        comments = Comments.objects.filter(news=news_id).order_by('-created_at')
        page_number = request.GET.get("page_number",page)
        paginator = Paginator(comments, 25)
        try:
            comment_list = paginator.page(page_number)
        except PageNotAnInteger:
            comment_list = paginator.page(1)
        except EmptyPage:
            return JsonResponse({'error': 'Empty page'}, status = status.HTTP_204_NO_CONTENT)
        response_data = {
            'current_page' : comment_list.number,
            'total_pages' : paginator.num_pages,
            'comments' :[
            {
                'id': item.id,
                'author':item.account.username,
                'avatar':item.account.avatar,
                'text': item.text,
                'created_at' : item.created_at,
            } 
            for item in comment_list
            ]
        }
        return JsonResponse(response_data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        error_message = 'News does not exist.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)

# ---------------------------------     USER  ROUTE     ---------------------------------
@api_view(['GET'])
def news_list_user(request):
    try:
        news = News.objects.filter(label = 'read')

        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        news_info = []

        # Lặp qua danh sách danh mục và tính số lượng tin tức cho mỗi danh mục
        for item in news:
            comments_count = Comments.objects.filter(news=item).count()
            author = item.account.username
            category = item.category.name
            news_info.append({
                'id': item.id,
                'title': item.title,
                'author' : author,
                'category' : category,
                'label': item.label,
                'comments_count': comments_count,
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

@api_view(['GET'])
def get_all_comments(request):
    comments = Comments.objects.all()
    serializer = CommentsSerializer(comments, many=True)
    return JsonResponse(
        data={
            'success': True,
            'comments': serializer.data
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])  
def get_news_detail(request, **kwargs):
    news_id = kwargs.get('id')
    news_detail = get_object_or_404(News, id=news_id)
    serializer = NewsSerializer(news_detail)
    return JsonResponse(
        data={
            'success': True,
            'news_detail': serializer.data
        },
        status=status.HTTP_200_OK
    )

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
#-------News-------
@api_view(['POST'])
def store_news(request):
    serializer = NewsSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_news(request, news_id):
    try:
        news = News.objects.get(id=news_id)
    except News.DoesNotExist:
        return JsonResponse({"error": "News not found"}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra xem người đăng nhập có phải là người tạo tin tức hay không
    if request.user != news.account.id:
        return JsonResponse({"error": "You don't have permission to update this news"}, status=status.HTTP_403_FORBIDDEN)

    serializer = NewsSerializer(news, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def delete_news(request, news_id):
    try:
        news = News.objects.get(id=news_id)
    except News.DoesNotExist:
        return JsonResponse({"error": "News not found"}, status=status.HTTP_404_NOT_FOUND)

    news.delete()
    return JsonResponse({"message": "News deleted successfully"}, status=status.HTTP_204_NO_CONTENT)