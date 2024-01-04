from .models import Account
from news.models import News, Comments, Categories, Interacts
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from PBL6_Fake_News_Detection_BE.middleware import AdminAuthorizationMiddleware, UserAuthorizationMiddleware
from PBL6_Fake_News_Detection_BE.settings import SECRET_KEY
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializer import CategoriesSerializer, NewsSerializer, NewsSerializerUpdate, CommentsSerializer, CommentsSerializerUpdate, InteractsSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime
from keras.models import load_model
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from bs4 import BeautifulSoup
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import numpy as np
from auth_site.serializer import AccountSerializer
from django.db import transaction
from django.db.models import Count

class CustomPagination(PageNumberPagination):
    page_size = 10  # Đặt giá trị mặc định cho page_size
    page_size_query_param = 'page_size'
    max_page_size = 100  # Đặt giá trị mặc định cho max_page_size

MAX_SEQUENCE_LENGTH = 400
MAX_NUM_WORDS = 10000
EMBEDDING_VECTOR_FEATURES=50

# ---------------------------------     ADMIN  ROUTE     ---------------------------------
        
@api_view(['GET'])
def news_list_admin(request,number,page):
    try:
        # Get all news items
        news = News.objects.all()
        # Check for 'page_number' parameter in the request, default to 1 if not present
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, number)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def news_list_by_category_admin(request, category_id,number,page):
    try:
        news = News.objects.filter(category=category_id)
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, number)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def news_list_by_author_admin(request, author_id,number,page):
    try:
        news = News.objects.filter(account=author_id)
         # Check for 'page_number' parameter in the request, default to 1 if not present
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, number)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def comments_list_by_user(request, user_id,number,page):
    try:
        comments = Comments.objects.filter(account=user_id)
        # Check for 'page_number' parameter in the request, default to 1 if not present
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(comments, number)
        try:
            comments_list = paginator.page(page_number)
        except PageNotAnInteger:
            comments_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
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
                'author' : item.news.account.username,
                'avatar' : item.news.account.avatar,
                }
                for item in comments_list
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])  
def total_news(request, current_year):
    months = list(range(1, 13))
    month_names = [datetime(2000, month, 1).strftime('%B') for month in months]
    data1 = []
    data2 = []
    for i, month_name in enumerate(month_names, start=1):
        news_real_count = News.objects.filter(label = 'real', created_at__year=current_year, created_at__month=i).count()
        data1.append({
            'month': month_name,
            'total': news_real_count,
        })

        news_fake_count = News.objects.filter(label = 'fake', created_at__year=current_year, created_at__month=i).count()
        data2.append({
            'month': month_name,
            'total': news_fake_count,
        })
    return JsonResponse(
        data={
            'success': True,
            'message': 'Successfully',
            'year': current_year,
            'total_real_news': data1,
            'total_fake_news': data2,
        },
        status=status.HTTP_200_OK
    )

def total_comments(request, current_year):
    months = list(range(1, 13))
    month_names = [datetime(2000, month, 1).strftime('%B') for month in months]
    data1 = []
    data2 = []
    for i, month_name in enumerate(month_names, start=1):
        comment_count = Comments.objects.filter(created_at__year=current_year, created_at__month=i).count()
        data1.append({
            'month': month_name,
            'total': comment_count,
        })

    return JsonResponse(
        data={
            'success': True,
            'message': 'Successfully',
            'year': current_year,
            'total_comment': data1,
        },
        status=status.HTTP_200_OK
    )
@api_view(['GET'])  
def total(request):
    total_news = News.objects.count()
    total_user = Account.objects.filter(role = 'user').count()
    total_comment = Comments.objects.count()
    return JsonResponse(
        data={
            'success': True,
            'message': 'Successfully',
            'total_comment': total_comment,
            'total_news': total_news,
            'total_user': total_user,
        },
        status=status.HTTP_200_OK
    )

def total_month(request):
    current_month = datetime.now().month
    current_year = datetime.now().year
    total_comments = Comments.objects.filter(created_at__year=current_year, created_at__month=current_month).count()
    total_user = Account.objects.filter(role = 'user', created_at__year=current_year, created_at__month=current_month).count()
    total_news_real = News.objects.filter(label = 'real', created_at__year=current_year, created_at__month=current_month).count()
    total_news_fake = News.objects.filter(label = 'fake', created_at__year=current_year, created_at__month=current_month).count()
    data1 = {
        "id": 'Total Comments',
        "name": 'Total Comments',
        "total": total_comments
    }

    data2 = {
        "id": 'Total User',
        "name": 'Total User',
        "total": total_user
    }

    data3 = {
        "id": 'Total News Real',
        "name": 'Total News Real',
        "total": total_news_real
    }
    
    data4 = {
        "id": 'Total News Fake',
        "name": 'Total News Fake',
        "total": total_news_fake
    }
    data = [data4, data3, data2, data1]

    return JsonResponse({
        'status': 200,
        'message': 'Successfully',
        'data':  data,
    })

def total_category(request):
    categories = Categories.objects.all()
    category_info = []
    for category in categories:
        news_count = News.objects.filter(category=category).count()
        category_info.append({
            'id': category.name,
            'name': category.name,
            'news_count': news_count,
        })
    return JsonResponse({'categories': category_info},status=status.HTTP_200_OK)

 # ---------------------------------     ALL    ---------------------------------   

#-----Category------
@api_view(['GET'])
def categories_list(request):
    try:
        categories = Categories.objects.all()
    
        # Tạo danh sách để lưu trữ thông tin của từng danh mục và số lượng tin tức
        category_info = []

        # Lặp qua danh sách danh mục và tính số lượng tin tức cho mỗi danh mục
        for category in categories:
            news_count = News.objects.filter(category=category).count()
            news_count_real = News.objects.filter(category=category, label = 'real').count()
            category_info.append({
                'id': category.id,
                'name': category.name,
                'news_count': news_count,
                'news_count_real' :  news_count_real
            })
        return JsonResponse({'categories': category_info},status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no admin users are found0
        error_message = 'No category users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
#--------News----------   
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def news_detail(request, news_id):
    try:
        news = News.objects.get(id = news_id)

        if request.user.is_authenticated:
            save_me = Interacts.objects.filter(label='news', target_type='save', account=request.user.id, target_id=news_id).count()
            save = Interacts.objects.filter(label='news', target_type='save', account=request.user.id, target_id=news_id)
            like_me = Interacts.objects.filter(label='news', target_type='like', account=request.user.id, target_id=news_id).count()
            like = Interacts.objects.filter(label='news', target_type='like', account=request.user.id, target_id=news_id)
        else:
            # Set default values for unauthenticated users
            save_me = 0
            save = []
            like_me = 0
            like = []
        total_like = Interacts.objects.filter(label = 'news',target_type = 'like',target_id = news_id).count()
        total_save = Interacts.objects.filter(label = 'news',target_type = 'save',target_id = news_id).count()
        news_data = {
            'id' : news.id,
            'title' : news.title,
            'text' : news.text,
            'image' : news.image,
            'author' : news.account.username,
            'category' : news.category.name,
            'comments_count' : Comments.objects.filter(news = news).count(),
            'created_at' : news.created_at,
            'save_me' : save_me,
            'save' :  [{
                'id': item.id,
                }
                for item in save],
            'like_me' : like_me,
            'like' :  [{
                'id': item.id,
                }
                for item in like],
            'total_like' : total_like,
            'total_save' : total_save,
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_news(request, news_id):
    try:
        news = News.objects.get(id=news_id)
        comments = Comments.objects.filter(news=news_id)
        interacts_news = Interacts.objects.filter(label='news', target_id=news_id)
    except News.DoesNotExist:
        return JsonResponse({"error": "News not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role == 'admin' or request.user.id == news.account.id:
        try:
            with transaction.atomic():
                news.delete()

                # Check if interacts_comment exists before deleting
                if interacts_news.exists():
                    interacts_news.delete()

                # Check if sub_comments exist before deleting
                for comment in comments:
                    comment_id = comment.id
                    interacts_comment = Interacts.objects.filter(label='comment', target_id=comment_id)
                    if interacts_comment.exists():
                        interacts_comment.delete()
                    comment.delete()
                        
        except Exception as e:
            return JsonResponse({"error": f"Failed to delete comment and interactions. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        return JsonResponse({"message": "News deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"error": "You don't have permission to delete this news"}, status=status.HTTP_403_FORBIDDEN)
#------Comments--------   
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def comments_list_by_news(request, news_id, page):
    try:
        comments = Comments.objects.filter(news=news_id, parent_comment_id = None).order_by('-created_at')

        page_number = request.GET.get("page_number",page)
        paginator = Paginator(comments, 25)
        try:
            comment_list = paginator.page(page_number)
        except PageNotAnInteger:
            comment_list = paginator.page(1)
        except EmptyPage:
            return JsonResponse({'error': 'Empty page'}, status = status.HTTP_204_NO_CONTENT)

        response_data = {
            'current_page': comment_list.number,
            'total_pages': paginator.num_pages,
            'comments': [
                {
                    'id': item.id,
                    'author': item.account.username,
                    'avatar': item.account.avatar,
                    'text': item.text,
                    'created_at': item.created_at,
                    'like_me': 0 if not request.user.is_authenticated else Interacts.objects.filter(label='comment', target_type='like', account=request.user.id, target_id=item.id).count(),
                    'like': [] if not request.user.is_authenticated else [{'id': item_like.id} for item_like in Interacts.objects.filter(label='comment', target_type='like', account=request.user.id, target_id=item.id)],
                    'total_like': Interacts.objects.filter(label='comment', target_type='like', target_id=item.id).count(),
                    'sub_comment': [{
                        'id': sub_item.id,
                        'author': sub_item.account.username,
                        'avatar': sub_item.account.avatar,
                        'text': sub_item.text,
                        'created_at': sub_item.created_at,
                        'like_me': 0 if not request.user.is_authenticated else Interacts.objects.filter(label='comment', target_type='like', account=request.user.id, target_id=sub_item.id).count(),
                        'like': [] if not request.user.is_authenticated else [{'id': sub_item_like.id} for sub_item_like in Interacts.objects.filter(label='comment', target_type='like', account=request.user.id, target_id=sub_item.id)],
                        'total_like': Interacts.objects.filter(label='comment', target_type='like', target_id=sub_item.id).count()
                    } for sub_item in Comments.objects.filter(news=news_id, parent_comment_id=item.id).order_by('-created_at')],
                    'sub_comment_count': Comments.objects.filter(news=news_id, parent_comment_id=item.id).order_by('-created_at').count()
                }
                for item in comment_list
            ]
        }
        return JsonResponse(response_data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no admin users are found0
        error_message = 'No comment users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def get_like_counts(account_id):
    # Query để lấy tổng số lượng like bài viết của một người dùng
    like_counts = Interacts.objects.filter(
        account_id=account_id,
        label='comment',
        target_type='like'
    ).aggregate(total_likes=Count('id'))

    return like_counts['total_likes'] if like_counts else 0

def get_comment_counts(account_id):
    # Query để lấy tổng số lượng comment của một người dùng
    comment_counts = Comments.objects.filter(
        account_id=account_id
    ).count()

    return comment_counts
    
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = Comments.objects.get(id=comment_id)
        news = News.objects.get(id=comment.news.id)
        sub_comments = Comments.objects.filter(parent_comment_id=comment_id)
        interacts_comment = Interacts.objects.filter(label='comment', target_id=comment_id)
    except Comments.DoesNotExist:
        return JsonResponse({"error": "comment not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role == 'admin' or request.user.id == comment.account.id or request.user.id == news.account.id:
        try:
            with transaction.atomic():
                comment.delete()

                # Check if interacts_comment exists before deleting
                if interacts_comment.exists():
                    interacts_comment.delete()

                # Check if sub_comments exist before deleting
                if sub_comments.exists():
                    for sub_comment in sub_comments:
                        sub_comment_id = sub_comment.id
                        interacts_sub_comment = Interacts.objects.filter(label='comment', target_id=sub_comment_id)

                        # Check if interacts_sub_comment exists before deleting
                        if interacts_sub_comment.exists():
                            interacts_sub_comment.delete()

                        sub_comment.delete()
        except Exception as e:
            return JsonResponse({"error": f"Failed to delete comment and interactions. {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({"message": "comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"error": "You don't have permission to delete this comment"}, status=status.HTTP_403_FORBIDDEN)
# ---------------------------------     USER  ROUTE     ---------------------------------
#-------News------
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def news_list_user(request,number,page):
    try:
        news = News.objects.filter(label = 'real').order_by('-created_at')  # Sắp xếp theo created_at giảm dần
        news_count = News.objects.filter(label = 'real').count()
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, number)
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
            'news_count': news_count,
            'news': [
                {
                    'id': item.id,
                    'image': item.image,
                    'title': item.title,
                    'text': item.text,
                    'author': item.account.username,
                    'category': item.category.name,
                    'label': item.label,
                    'comments_count': Comments.objects.filter(news=item).count(),
                    'created_at': item.created_at,
                    'like_me': 0 if not request.user.is_authenticated else Interacts.objects.filter(label='news', target_type='like', account=request.user.id, target_id=item.id).count(),
                    'like': [] if not request.user.is_authenticated else [{'id': item_like.id} for item_like in Interacts.objects.filter(label='news', target_type='like', account=request.user.id, target_id=item.id)],
                    'total_like': Interacts.objects.filter(label='news', target_type='save', target_id=item.id).count(),
                    'save_me': 0 if not request.user.is_authenticated else Interacts.objects.filter(label='news', target_type='save', account=request.user.id, target_id=item.id).count(),
                    'save': [] if not request.user.is_authenticated else [{'id': item_save.id} for item_save in Interacts.objects.filter(label='news', target_type='save', account=request.user.id, target_id=item.id)],
                    'total_save': Interacts.objects.filter(label='news', target_type='save', target_id=item.id).count(),
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def search_news(request,number,page):
    # Get the category and search term from the request
    category = request.GET.get('category', '')
    search_term = request.GET.get('search', '')

    # Query the News model with filters
    # news_query = data
    news_query = News.objects.filter(label = 'real').order_by('-created_at')  # Sắp xếp theo created_at giảm dần

    if category:
        news_query = news_query.filter(category=category)

    if search_term:
        # Use case-insensitive search on title field
        news_query = news_query.filter(Q(title__icontains=search_term))

    # Retrieve the filtered news articles
    news_articles = news_query
    news_count = news_query.count()
    page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
    paginator = Paginator(news_articles, number)
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
        'news_count': news_count,
        'news': [
            {
                'id': item.id,
                'image': item.image,
                'title': item.title,
                'text': item.text,
                'author': item.account.username,
                'category': item.category.name,
                'label': item.label,
                'comments_count': Comments.objects.filter(news=item).count(),
                'created_at': item.created_at,
                'like_me': 0 if not request.user.is_authenticated else Interacts.objects.filter(label='news', target_type='like', account=request.user.id, target_id=item.id).count(),
                'like': [] if not request.user.is_authenticated else [{'id': item_like.id} for item_like in Interacts.objects.filter(label='news', target_type='like', account=request.user.id, target_id=item.id)],
                'total_like': Interacts.objects.filter(label='news', target_type='save', target_id=item.id).count(),
                'save_me': 0 if not request.user.is_authenticated else Interacts.objects.filter(label='news', target_type='save', account=request.user.id, target_id=item.id).count(),
                'save': [] if not request.user.is_authenticated else [{'id': item_save.id} for item_save in Interacts.objects.filter(label='news', target_type='save', account=request.user.id, target_id=item.id)],
                'total_save': Interacts.objects.filter(label='news', target_type='save', target_id=item.id).count(),
            }
            for item in news_list
        ],
        'selected_category': category,
        'search_term': search_term,
    }
    return JsonResponse(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_news_real_by_author(request, author_id, number, page):
    try:
        news = News.objects.filter(account=author_id, label = 'real').order_by('-created_at')  # Sắp xếp theo created_at giảm dần
        news_count = News.objects.filter(account=author_id, label = 'real').count()
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, number)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
        
        response_data = {
            'current_page': news_list.number,
            'total_pages': paginator.num_pages,
            'news_count': news_count,
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
                    'text': item.text,
                    'image': item.image,
                    'author': item.account.username,
                    'category': item.category.name,
                    'label': item.label,
                    'total_like' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
                    'comments_count': Comments.objects.filter(news=item).count(),
                    'created_at': item.created_at,
                    'like_me' : Interacts.objects.filter(label = 'news',target_type = 'like',account = request.user.id,target_id = item.id).count(),
                    'like' : [{
                        'id': item_like.id,
                        }
                        for item_like in Interacts.objects.filter(label = 'news',target_type = 'like',account = request.user.id,target_id = item.id)],
                    'total_like' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
                    'save_me' : Interacts.objects.filter(label = 'news',target_type = 'save',account = request.user.id,target_id = item.id).count(),
                    'save' : [{
                        'id': item_save.id,
                        }
                        for item_save in Interacts.objects.filter(label = 'news',target_type = 'save',account = request.user.id,target_id = item.id)],
                    'total_save' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def search_news_real_by_author(request,author_id,number,page):
    # Get the category and search term from the request
    category = request.GET.get('category', '')
    search_term = request.GET.get('search', '')

    # Query the News model with filters
    news_query = News.objects.filter(account=author_id,label = 'real').order_by('-created_at')  # Sắp xếp theo created_at giảm dần

    if category:
        news_query = news_query.filter(category=category)

    if search_term:
        # Use case-insensitive search on title field
        news_query = news_query.filter(Q(title__icontains=search_term))

    # Retrieve the filtered news articles
    news_articles = news_query
    news_count = news_query.count()
    page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
    paginator = Paginator(news_articles, number)
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
        'news_count':news_count,
        'news': [
            {
                'id': item.id,
                'image': item.image,
                'title': item.title,
                'text' : item.text,
                'author': item.account.username,
                'category': item.category.name,
                'label': item.label,
                'total_like' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
                'comments_count': Comments.objects.filter(news=item).count(),
                'created_at': item.created_at,
                'like_me' : Interacts.objects.filter(label = 'news',target_type = 'like',account = request.user.id,target_id = item.id).count(),
                'like' : [{
                    'id': item_like.id,
                    }
                    for item_like in Interacts.objects.filter(label = 'news',target_type = 'like',account = request.user.id,target_id = item.id)],
                'total_like' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
                'save_me' : Interacts.objects.filter(label = 'news',target_type = 'save',account = request.user.id,target_id = item.id).count(),
                'save' : [{
                    'id': item_save.id,
                    }
                    for item_save in Interacts.objects.filter(label = 'news',target_type = 'save',account = request.user.id,target_id = item.id)],
                'total_save' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
            }
            for item in news_list
        ],
        'selected_category': category,
        'search_term': search_term,
    }
    return JsonResponse(response_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_news_like_by_you(request,number,page):
    try:
        liked_target_ids = Interacts.objects.filter(
                    label='news', target_type='like', account=request.user.id
                ).values_list('target_id', flat=True)

        # Filter News objects based on the liked_target_ids
        news = News.objects.filter(id__in=liked_target_ids, label='real').order_by('-created_at') # Sắp xếp theo created_at giảm dần
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, number)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
        response_data = {
            'current_page': news_list.number,
            'total_pages': paginator.num_pages,
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
                    'text': item.text,
                    'image': item.image,
                    'author': item.account.username,
                    'category': item.category.name,
                    'label': item.label,
                    'like_me' : Interacts.objects.filter(label = 'news',target_type = 'like',account = request.user.id,target_id = item.id).count(),
                    'like' : [{
                        'id': item_like.id,
                        }
                        for item_like in Interacts.objects.filter(label = 'news',target_type = 'like',account = request.user.id,target_id = item.id)],
                    'total_like' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
                    'save_me' : Interacts.objects.filter(label = 'news',target_type = 'save',account = request.user.id,target_id = item.id).count(),
                    'save' : [{
                        'id': item_save.id,
                        }
                        for item_save in Interacts.objects.filter(label = 'news',target_type = 'save',account = request.user.id,target_id = item.id)],
                    'total_save' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_news_save_by_you(request,number,page):
    try:
        liked_target_ids = Interacts.objects.filter(
                    label='news', target_type='save', account=request.user.id
                ).values_list('target_id', flat=True)

        # Filter News objects based on the liked_target_ids
        news = News.objects.filter(id__in=liked_target_ids, label='real').order_by('-created_at') # Sắp xếp theo created_at giảm dần
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, number)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
        response_data = {
            'current_page': news_list.number,
            'total_pages': paginator.num_pages,
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
                    'text': item.text,
                    'image': item.image,
                    'author': item.account.username,
                    'category': item.category.name,
                    'label': item.label,
                    'like_me' : Interacts.objects.filter(label = 'news',target_type = 'like',account = request.user.id,target_id = item.id).count(),
                    'like' : [{
                        'id': item_like.id,
                        }
                        for item_like in Interacts.objects.filter(label = 'news',target_type = 'like',account = request.user.id,target_id = item.id)],
                    'total_like' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
                    'save_me' : Interacts.objects.filter(label = 'news',target_type = 'save',account = request.user.id,target_id = item.id).count(),
                    'save' : [{
                        'id': item_save.id,
                        }
                        for item_save in Interacts.objects.filter(label = 'news',target_type = 'save',account = request.user.id,target_id = item.id)],
                    'total_save' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def list_news_fake_by_author(request,number,page):
    try:
        news = News.objects.filter(account=request.user, label = 'fake').order_by('-created_at')  # Sắp xếp theo created_at giảm dần
        news_count = News.objects.filter(account=request.user, label = 'fake').count()
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(news, number)
        try:
            news_list = paginator.page(page_number)
        except PageNotAnInteger:
            news_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
        
        response_data = {
            'current_page': news_list.number,
            'total_pages': paginator.num_pages,
            'news_count': news_count,
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
                    'text': item.text,
                    'image': item.image,
                    'author': item.account.username,
                    'category': item.category.name,
                    'label': item.label,
                    'total_like' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
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
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def search_news_fake_by_author(request,number,page):
    # Get the category and search term from the request
    category = request.GET.get('category', '')
    search_term = request.GET.get('search', '')

    # Query the News model with filters
    news_query = News.objects.filter(account=request.user,label = 'fake').order_by('-created_at')  # Sắp xếp theo created_at giảm dần

    if category:
        news_query = news_query.filter(category=category)

    if search_term:
        # Use case-insensitive search on title field
        news_query = news_query.filter(Q(title__icontains=search_term))

    # Retrieve the filtered news articles
    news_articles = news_query
    news_count = news_query.count()
    page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
    paginator = Paginator(news_articles, number)
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
        'news_count':news_count,
        'news': [
            {
                'id': item.id,
                'image': item.image,
                'title': item.title,
                'text' : item.text,
                'author': item.account.username,
                'category': item.category.name,
                'label': item.label,
                'total_like' : Interacts.objects.filter(label = 'news',target_type = 'save',target_id = item.id).count(),
                'comments_count': Comments.objects.filter(news=item).count(),
                'created_at': item.created_at
            }
            for item in news_list
        ],
        'selected_category': category,
        'search_term': search_term,
    }
    return JsonResponse(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def store_news(request):
    data_copy = request.data.copy()
    data_copy['account'] = request.user.id

    rnn_model = load_model('./ai_model/trained_model/rnn_model.h5')
    lstm_model = load_model('./ai_model/trained_model/lstm_model.h5')
    bid_model = load_model('./ai_model/trained_model/bid_model.h5')
    my_model = load_model('./ai_model/trained_model/my_model.h5')
    
    serializer = NewsSerializer(data=data_copy)

    if serializer.is_valid():
        print('Serializer data: ', serializer.validated_data)

        # Loại bỏ các cặp thẻ HTML từ giá trị của field text
        text_without_html = BeautifulSoup(serializer.validated_data['text'], 'html.parser').get_text(separator=' ')

        # Nối chuỗi title và text đã loại bỏ các thẻ HTML
        combined_text = f"{serializer.validated_data['title']} {text_without_html}"
        print('Combined text:', combined_text)

        # Chuẩn hóa văn bản
        combined_text_stemming = perform_stemming(combined_text)
        print('Combined text after stemming:', combined_text_stemming)

        # Dự đoán xem bài viết có phải là thật hay giả
        label = predict_fake_or_real(combined_text_stemming, bid_model)
        print('Label:', label)

        # Chuyển đối tượng Account thành JSON serializable
        # Lấy đối tượng Account từ ID

        # print('Account:', account)
        # print('Account ID:', account.id)

        # account_serializer = AccountSerializer(account)
        # account_data = account_serializer.data

        # Lấy giá trị ID của tài khoản
        # account_id = account.id

        # Gán giá trị cho trường label và trường account
        serializer.validated_data['label'] = label
        # serializer.validated_data['account'] = account.id

        serializer.save()
        
        return JsonResponse({"message": "News created successfully",
                             "data": serializer.validated_data}, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def perform_stemming(text):
    # Tải stop words nếu chưa tải
    try:
        stopwords.words('english')
    except LookupError:
        import nltk
        nltk.download('stopwords')

    # Khởi tạo đối tượng PorterStemmer
    porter_stemmer = PorterStemmer()

    # Xử lý văn bản
    review = re.sub('[^a-zA-Z]', ' ', text)
    review = review.lower()
    review = review.split()

    review = [porter_stemmer.stem(word) for word in review if not word in stopwords.words('english')]
    review = ' '.join(review)

    return review

def predict_fake_or_real(news_content, model):
    # Chuẩn bị dữ liệu đầu vào cho mô hình
    # Khởi tạo một đối tượng Tokenize
    tokenizer = Tokenizer(num_words=MAX_NUM_WORDS)

    sequence = tokenizer.texts_to_sequences([news_content])
    # Đảm bảo rằng chuỗi có chiều dài là 400
    sequence_padded = pad_sequences(sequence, maxlen=MAX_SEQUENCE_LENGTH)

    # Dự đoán
    prediction = model.predict(sequence_padded)
    print('Prediction:', prediction)

    # Chuyển đổi giá trị dự đoán thành nhãn ("Fake" hoặc "Real"), điều này phụ thuộc vào cách bạn đào tạo mô hình
    # Ví dụ: Nếu giá trị dự đoán > 0.9, bạn có thể xem nó là "Real", ngược lại là "Fake"
    label = "real" if prediction > 0.9 else "fake"

    return label

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_news(request, news_id):
    try:
        news = News.objects.get(id=news_id)
    except News.DoesNotExist:
        return JsonResponse({"error": "News not found"}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra xem người đăng nhập có phải là người tạo tin tức hay không
    if request.user.id != news.account.id:
        return JsonResponse({"error": "You don't have permission to update this news",}, status=status.HTTP_403_FORBIDDEN)

    original_news_data = NewsSerializerUpdate(news).data

    serializer = NewsSerializerUpdate(news, data=request.data)

    rnn_model = load_model('./ai_model/trained_model/rnn_model.h5')
    lstm_model = load_model('./ai_model/trained_model/lstm_model.h5')
    bid_model = load_model('./ai_model/trained_model/bid_model.h5')

    if serializer.is_valid():
        serializer.save()
        if 'text' in request.data or 'title' in request.data:
            # Loại bỏ các cặp thẻ HTML từ giá trị của field 'text'
            text_without_html = BeautifulSoup(serializer.validated_data['text'], 'html.parser').get_text(separator=' ')

            # Nối chuỗi 'title' và 'text' đã loại bỏ các thẻ HTML
            combined_text = f"{serializer.validated_data['title']} {text_without_html}"

            # Chuẩn hóa văn bản
            combined_text_stemming = perform_stemming(combined_text)

            # Dự đoán xem bài viết có phải là thật hay giả
            label = predict_fake_or_real(combined_text_stemming, lstm_model)
            serializer.validated_data['label'] = label
            serializer.save()
        changes_made = serializer.data != original_news_data
        if changes_made:
            return JsonResponse({"message": "News updated successfully"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"error": "No changes made."}, status=status.HTTP_200_OK)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#---Comments-----
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def store_comment(request):
    data_copy = request.data.copy()
    data_copy['account'] = request.user.id

    serializer = CommentsSerializer(data=data_copy)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse({"message": "Comments created successfully",
                             "data": serializer.data}, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_comment(request, comment_id):
    try:
        comment = Comments.objects.get(id=comment_id)
    except comment.DoesNotExist:
        return JsonResponse({"error": "comment not found"}, status=status.HTTP_404_NOT_FOUND)

    # Kiểm tra xem người đăng nhập có phải là người tạo tin tức hay không
    if request.user.id != comment.account.id:
        return JsonResponse({"error": "You don't have permission to update this comment",}, status=status.HTTP_403_FORBIDDEN)
    original_comment_data = CommentsSerializerUpdate(comment).data

    serializer = CommentsSerializerUpdate(comment, data=request.data)

    if serializer.is_valid():
        serializer.save()

        changes_made = serializer.data != original_comment_data
        if changes_made:
            return JsonResponse({"message": "Comment updated successfully"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"error": "No changes made."}, status=status.HTTP_200_OK)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#-----------------------------Interacts---------------
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def store_interact(request):
    data_copy = request.data.copy()
    data_copy['account'] = request.user.id

    serializer = InteractsSerializer(data=data_copy)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse({"message": "Interacts created successfully",
                             "data": serializer.data}, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_interact(request, interact_id):
    try:
        interact = Interacts.objects.get(id=interact_id)
    except interact.DoesNotExist:
        return JsonResponse({"error": "interact not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.id == interact.account.id:
        interact.delete()
        return JsonResponse({"message": "interact deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"error": "You don't have permission to delete this interact"}, status=status.HTTP_403_FORBIDDEN)
    


