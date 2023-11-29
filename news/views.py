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
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .serializer import CategoriesSerializer, NewsSerializer, NewsSerializerUpdate, CommentsSerializer, CommentsSerializerUpdate, InteractsSerializer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q

class CustomPagination(PageNumberPagination):
    page_size = 10  # Đặt giá trị mặc định cho page_size
    page_size_query_param = 'page_size'
    max_page_size = 100  # Đặt giá trị mặc định cho max_page_size

# ---------------------------------     ADMIN  ROUTE     ---------------------------------
        
@api_view(['GET'])
def news_list_admin(request):
    try:
        # Get all news items
        news = News.objects.all()
        # Check for 'page_number' parameter in the request, default to 1 if not present
        response_data = {
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
                for item in news
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
def news_list_by_category_admin(request, category_id):
    try:
        news = News.objects.filter(category=category_id)
        response_data = {
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
                    'author': item.account.username,
                    'label': item.label,
                    'comments_count': Comments.objects.filter(news=item).count(),
                    'created_at': item.created_at
                }
                for item in news
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
def news_list_by_author_admin(request, author_id):
    try:
        news = News.objects.filter(account=author_id)
        response_data = {
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
                    'category': item.category.name,
                    'label': item.label,
                    'comments_count': Comments.objects.filter(news=item).count(),
                    'created_at': item.created_at
                }
                for item in news
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
def comments_list_by_user(request, user_id):
    try:
        comments = Comments.objects.filter(account=user_id)
        response_data = {
            'comments': [
                {
                'id': item.id,
                'text': item.text,
                'created_at' : item.created_at,
                'news_id' : item.news.id,
                'news' : item.news.title,
                'author' : item.news.account.username
                }
                for item in comments
            ]
        }
        return JsonResponse(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
    
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
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
#--------News----------   
@api_view(['GET'])
def news_detail(request, news_id):
    try:
        news = News.objects.get(id = news_id)
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
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
    
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_news(request, news_id):
    try:
        news = News.objects.get(id=news_id)
    except News.DoesNotExist:
        return JsonResponse({"error": "News not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role == 'admin' or request.user.id == news.account.id:
        news.delete()
        return JsonResponse({"message": "News deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"error": "You don't have permission to delete this news"}, status=status.HTTP_403_FORBIDDEN)
#------Comments--------   
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
    
@api_view(['DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = Comments.objects.get(id=comment_id)
    except comment.DoesNotExist:
        return JsonResponse({"error": "comment not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.role == 'admin' or request.user.id == comment.account.id:
        comment.delete()
        return JsonResponse({"message": "comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"error": "You don't have permission to delete this comment"}, status=status.HTTP_403_FORBIDDEN)
# ---------------------------------     USER  ROUTE     ---------------------------------
#-------News------
@api_view(['GET'])
def news_list_user(request,number,page):
    try:
        news = News.objects.filter(label = 'real')
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

@api_view(['GET'])
def news_list_by_author_user_real(request, author_id, number, page):
    try:
        news = News.objects.filter(account=author_id, label = 'real')
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
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def news_list_by_author_user_fake(request):
    try:
        news = News.objects.filter(account=request.user.id, label = 'fake')
        response_data = {
            'news': [
                {
                    'id': item.id,
                    'title': item.title,
                    'text': item.text,
                    'image': item.image,
                    'category': item.category.name,
                    'label': item.label,
                    'comments_count': Comments.objects.filter(news=item).count(),
                    'created_at': item.created_at
                }
                for item in news
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
#-------News-------
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def store_news(request):
    data_copy = request.data.copy()
    data_copy['account'] = request.user.id

    serializer = NewsSerializer(data=data_copy)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse({"message": "News created successfully",
                             "data": serializer.data}, status=status.HTTP_201_CREATED)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    if serializer.is_valid():
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
    
def search_news(request,number,page):
    # Get the category and search term from the request
    category = request.GET.get('category', '')
    search_term = request.GET.get('search', '')

    # Query the News model with filters
    news_query = News.objects.filter(label = 'real')

    if category:
        news_query = news_query.filter(category=category)

    if search_term:
        # Use case-insensitive search on title field
        news_query = news_query.filter(Q(title__icontains=search_term))

    # Retrieve the filtered news articles
    news_articles = news_query
    news_count = news_query.count()
    # Pass the filtered news articles to the template
    # context = {
    #     'news_articles': news_articles,
    #     'selected_category': category,
    #     'search_term': search_term,
    # }
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
    return JsonResponse({"message": "Comment updated successfully", "data" : context}, status=status.HTTP_200_OK)