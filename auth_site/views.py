from .forms import RegistrationForm
from .models import Account
from news.models import News, Comments, Interacts
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .serializer import AccountSerializer
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
from .serializer import AccountSerializer, AccountSerializerUpdate, ChangePasswordSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # Sử dụng trường 'email' thay vì 'username'
    username_field = 'email'

    def validate(self, attrs):
        data = super().validate(attrs)

        # Lấy thông tin người dùng từ request
        user = self.user

        print(user)

        # Bổ sung các thuộc tính của model Account vào kết quả trả về của MyTokenObtainPairSerializer
        data['account_id'] = user.id
        data['username'] = user.username
        data['email'] = user.email
        data['role'] = user.role

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role

        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
def register(request):
    form = RegistrationForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        avatar = form.cleaned_data['avatar']
        
        print('Username:', username)
        print('Email:', email)
        print('Password:', password)

        # Sử dụng make_password để mã hóa mật khẩu
        hashed_password = make_password(password)

        # Tạo người dùng mới và lưu vào cơ sở dữ liệu với mật khẩu đã mã hóa
        account = Account(username=username, email=email, password=hashed_password, avatar=avatar)
        account.save()

        return JsonResponse(
            data={
                'success': True,
                'message': 'Đăng ký thành công',
                'redirect_url': '/auth/login/'
            },
            status=status.HTTP_201_CREATED
        ) 
    else:
        return JsonResponse(
            data={
                'success': False,
                'message': 'Đăng ký thất bại',
                'error': form.errors,
            },
            status=status.HTTP_400_BAD_REQUEST
        ) 

@api_view(['POST'])
def login(request):
    # Nhận đầu vào từ người dùng
    email = request.POST['email']
    password = request.POST['password']

    # Xác thực người dùng
    user = authenticate(request, email=email, password=password)

    if user is not None:
        if user.status == 'active':
            is_refresh_token_expired = None
            is_refresh_token_blacklisted = False
            # Sử dụng Serializer để chuyển Account model sang JSON
            serializer = AccountSerializer(user)

            # Kiểm tra refresh_token có được gửi đến hay không
            if 'Authorization' in request.headers:
                # Nếu có, lấy refresh_token từ Authorization
                auth_header = request.headers['Authorization']
                print('Auth header:', auth_header)

                # Token thường có định dạng "Bearer <token>", nên chúng ta tách nó ra.
                # Điều này chỉ áp dụng khi ta sử dụng Token Authentication.
                token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header

                try:
                    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256']) # mã hóa refresh_token
                    print('Payload:', payload)
                    
                    # Truy cập thuộc tính token_type trong payload
                    token_type = payload.get('token_type')
                    
                    if token_type == 'refresh':
                        # Thực hiện các bước xử lý cho refresh_token
                        # Refresh token còn hiêu lực -> Tạo mới access_token, giữ nguyên refresh_token
                        is_refresh_token_expired = False
                        # Tạo refresh token mới
                        new_refresh = RefreshToken.for_user(user)
                    elif token_type == 'access':
                        return JsonResponse(
                            data={
                                'success': False,
                                'error_message': 'Token đính kèm phải là access_token'
                            },
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                except InvalidSignatureError:
                    return JsonResponse(
                        data={
                            'success': False,
                            'error_message': 'Refresh token không hợp lệ'
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                except ExpiredSignatureError:
                    is_refresh_token_expired = True

                    # options {'verify_exp': False} để vô hiệu hóa kiểm tra thời gian hết hạn (exp)
                    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'], options={'verify_exp': False})
                    print('Payload as expired token:', payload)

                    jti = payload.get('jti')
                    print('jti of expired refresh_token:', jti)

                    # Refresh token hết hạn -> Thực hiện 2 việc sau
                    # 1) Check xem refresh_token đã được blacklisted hay chưa
                    # 2) Tạo refresh token mới cho người dùng

                    # Kiểm tra xem jti của refresh_token có tồn tại trong bảng outstandingtoken hay ko
                    if OutstandingToken.objects.filter(jti=jti).exists():
                        outstanding_token = OutstandingToken.objects.get(jti=jti)
                        # Lấy giá trị của cột 'id' từ bản ghi tìm thấy
                        token_id = outstanding_token.id

                        # Kiểm tra xem refresh_token đó đã bị blacklisted trong bảng blacklist hay chưa
                        if BlacklistedToken.objects.filter(token_id=token_id).exists():
                            # Refresh token đã blacklisted
                            is_refresh_token_blacklisted = True
                        else:
                            # Nếu chưa, thêm id của token vào bảng BlacklistedToken -> Vô hiệu hóa refresh_token cũ đã expired
                            BlacklistedToken.objects.create(token_id=token_id)

            # nếu không có refresh_token đính kèm theo thì khả năng 1 trong 2 TH:
            # 1. Người dùng login lần đầu
            # 2. Bên client không lấy được giá trị của refresh_token (có thể người dùng đã chủ động xóa refresh_token khỏi local storage)
            else:
                # Tạo refresh token mới
                refresh = RefreshToken.for_user(user)
            
            # Điều hướng tới trang tương ứng
            if user.role == 'user':
                if is_refresh_token_expired == None: # Không có refresh_token đính kèm theo
                    return JsonResponse(
                        data={
                            'user': serializer.data,
                            'access_token': str(refresh.access_token),
                            'refresh_token': str(refresh),
                            'is_new_refresh_token': True,
                            'refresh_token_requested_status': 'Không đính kèm refresh_token',
                            'message': 'Đăng nhập thành công 1',
                            'redirect_url': '/user',
                        },
                        status=status.HTTP_200_OK
                    )
                elif is_refresh_token_expired == False: # refresh_token đính kèm theo vẫn còn hiệu lực
                    return JsonResponse(
                        data={
                            'user': serializer.data,
                            'access_token': str(new_refresh.access_token),
                            'refresh_token': str(token),
                            'is_new_refresh_token': False,
                            'refresh_token_requested_status': 'Còn hiệu lực',
                            'message': 'Đăng nhập thành công',
                            'redirect_url': '/user',
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    # Nếu refresh_token đã expired thì cần kiểm tra xem đã được blacklisted hay chưa
                    if is_refresh_token_blacklisted == False: # refresh_token chưa được blacklisted
                        # Tạo refresh token mới
                        refresh = RefreshToken.for_user(user)
                        return JsonResponse(
                            data={
                                'user': serializer.data,
                                'access_token': str(new_refresh.access_token),
                                'refresh_token': str(new_refresh),
                                'is_new_refresh_token': True,
                                'is_refresh_token_blacklisted': False,
                                'refresh_token_requested_status': 'Đã hết hạn nhưng chưa được blacklisted',
                                'message': 'Đăng nhập thành công',
                                'redirect_url': '/user',
                            },
                            status=status.HTTP_200_OK
                        )
                    else: # refresh_token đã được blacklisted
                        return JsonResponse(
                            data={
                                'success': False,
                                'error_message': 'Refresh token đã bị vô hiệu hóa (blacklisted)',
                            },
                            status=status.HTTP_401_UNAUTHORIZED
                        )
            elif user.role == 'admin':   
                if is_refresh_token_expired == None: # Không có refresh_token đính kèm theo
                    return JsonResponse(
                        data={
                            'user': serializer.data,
                            'access_token': str(refresh.access_token),
                            'refresh_token': str(refresh),
                            'is_new_refresh_token': True,
                            'refresh_token_requested_status': 'Không đính kèm refresh_token',
                            'message': 'Đăng nhập thành công',
                            'redirect_url': '/admin',
                        },
                        status=status.HTTP_200_OK
                    )
                elif is_refresh_token_expired == False: # refresh_token đính kèm theo vẫn còn hiệu lực
                    return JsonResponse(
                        data={
                            'user': serializer.data,
                            'access_token': str(new_refresh.access_token),
                            'refresh_token': str(new_refresh),
                            'is_new_refresh_token': False,
                            'refresh_token_requested_status': 'Còn hiệu lực',
                            'message': 'Đăng nhập thành công',
                            'redirect_url': '/admin',
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    # Nếu refresh_token đã expired thì cần kiểm tra xem đã được blacklisted hay chưa
                    if is_refresh_token_blacklisted == False: # refresh_token chưa được blacklisted
                        # Tạo refresh token mới
                        refresh = RefreshToken.for_user(user)
                        return JsonResponse(
                            data={
                                'user': serializer.data,
                                'access_token': str(new_refresh.access_token),
                                'refresh_token': str(new_refresh),
                                'is_new_refresh_token': True,
                                'is_refresh_token_blacklisted': False,
                                'refresh_token_requested_status': 'Đã hết hạn nhưng chưa được blacklisted',
                                'message': 'Đăng nhập thành công',
                                'redirect_url': '/admin',
                            },
                            status=status.HTTP_200_OK
                        )
                    else: # refresh_token đã được blacklisted
                        return JsonResponse(
                            data={
                                'success': False,
                                'error_message': 'Refresh token đã bị vô hiệu hóa (blacklisted)',
                            },
                            status=status.HTTP_401_UNAUTHORIZED
                        )
        else:
            # Tài khoản không còn hiệu lực, thông báo lỗi
            return JsonResponse(
                data={
                    'success': False,
                    'error_message': 'Tài khoản hết hiệu lực'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
    else:
        # Không tìm thấy tài khoản với địa chỉ email đã cung cấp, thông báo lỗi
        return JsonResponse(
            data={
                'success': False,
                'error_message':  'Mật khẩu không đúng hoặc tài khoản không tồn tại'
            },
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user  # Người dùng đã được xác thực
    print("User:", user)

    # Chuyển đổi thông tin người dùng thành JSON và trả về
    serializer = AccountSerializer(user)
    return JsonResponse(
        data={
            'user': serializer.data
        }, 
        status=status.HTTP_200_OK
    )
    
@api_view(['POST'])
def refresh_token(request):
    # Nhận đầu vào từ người dùng
    email = request.POST['email']
    password = request.POST['password']

    # Xác thực người dùng
    user = authenticate(request, email=email, password=password)

    if user is not None:
        if user.status == 'active':
            is_refresh_token_blacklisted = False
            # Kiểm tra refresh_token có được gửi đến hay không
            if 'Authorization' in request.headers:
                # Lấy refresh_token từ Authorization
                auth_header = request.headers['Authorization']
                print('Auth header:', auth_header)

                # Token thường có định dạng "Bearer <access_token>", nên chúng ta tách nó ra.
                # Điều này chỉ áp dụng khi ta sử dụng Token Authentication.
                token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header

                try:
                    # options {'verify_exp': False} để vô hiệu hóa kiểm tra thời gian hết hạn (exp)
                    payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'], options={'verify_exp': False})
                    jti = payload.get('jti')

                    if OutstandingToken.objects.filter(jti=jti).exists():
                        outstanding_token = OutstandingToken.objects.get(jti=jti)
                        # Lấy giá trị của cột 'id' từ bản ghi tìm thấy
                        token_id = outstanding_token.id

                        # Kiểm tra xem refresh_token đó đã bị blacklisted trong bảng blacklist hay chưa
                        if BlacklistedToken.objects.filter(token_id=token_id).exists():
                            # Refresh token đã blacklisted
                            is_refresh_token_blacklisted = True
                        else:
                            # Nếu chưa, thêm id của token vào bảng BlacklistedToken -> Vô hiệu hóa refresh_token cũ đã expired
                            BlacklistedToken.objects.create(token_id=token_id)
                except InvalidSignatureError:
                    return JsonResponse(
                        data={
                            'success': False,
                            'error_message': 'Refresh token không hợp lệ'
                        },
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                if is_refresh_token_blacklisted == True:
                    return JsonResponse(
                        data={
                            'success': False,
                            'error_message': 'Refresh token đã bị vô hiệu hóa (blacklisted)',
                        },
                        status=status.HTTP_200_OK
                    ) 
                else:
                    refresh = RefreshToken.for_user(user)
                    return JsonResponse(
                        data={
                            'success': True,
                            'old_refresh_token': token,
                            'new_access_token': str(refresh.access_token),
                            'new_refresh_token': str(refresh),
                        },
                        status=status.HTTP_200_OK
                    ) 
                
@api_view(['GET'])                
def admin_account_list(request):
    try:
        admins = Account.objects.filter(role='admin')
        response_data = {
            'admins' :[
            {
                'account_id': admin.id,
                'adminname': admin.username, 
                'email': admin.email,
                'status' : admin.status
            } 
            for admin in  admins]
        }
        return JsonResponse(response_data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no admin users are found
        error_message = 'No admin users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def user_account_list(request,number,page):
    try:
        users = Account.objects.filter(role='user')
        page_number = request.GET.get("page_number",page)
        # Create a Pa ginator object
        paginator = Paginator(users, number)
        try:
            users_list = paginator.page(page_number)
        except PageNotAnInteger:
            users_list = paginator.page(1)
        except EmptyPage:
            # Handle the case where the page is empty
            return JsonResponse({'error': 'Empty page.'}, status=status.HTTP_204_NO_CONTENT)
        response_data = {
            'current_page': users_list.number,
            'total_pages': paginator.num_pages,
            'users' :[
            {
                'account_id': user.id,
                'username': user.username, 
                'email': user.email,
                'status' : user.status,
                'news_count': News.objects.filter(account=user).count(),
                'comments_count': Comments.objects.filter(account=user).count(),
            } 
            for user in users_list]
        }
        return JsonResponse(response_data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no user users are found
        error_message = 'No user users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_detail(request,user_id):
    try:
        account = Account.objects.get(role = 'user', id=user_id)
        
        # Đếm số lượng tin tức và bình luận của người dùng
        news_count_real = News.objects.filter(account=account,label = 'real').count()
        news_count_fake = News.objects.filter(account=account,label = 'fake').count()
        interact_me = Interacts.objects.filter(label = 'account',target_type = 'follow',account = request.user.id,target_id = user_id).count()
        interact = Interacts.objects.filter(label = 'account',target_type = 'follow',account = request.user.id,target_id = user_id)
        comments_count = Comments.objects.filter(account=account).count()
        total_you_follow = Interacts.objects.filter(label = 'account',target_type = 'follow',account = user_id).count()
        total_following_you = Interacts.objects.filter(label = 'account',target_type = 'follow',target_id = user_id).count()
        # Convert the account object and counts to a dictionary
        user_data = {
            'id': account.id,
            'username': account.username,
            'email': account.email,
            'role': account.role,
            'avatar' : account.avatar,
            'news_count_real': news_count_real,
            'news_count_fake': news_count_fake,
            'comments_count': comments_count,
            'interact_me' : interact_me,
            'interact' :  [{
                'id': item.id,
                }
                for item in interact],
            'total_you_follow' : total_you_follow,
            'total_following_you' : total_following_you
        }
        return JsonResponse(user_data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        error_message = 'Account not found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_user_you_follow(request,page):
    try:
        target_ids = Interacts.objects.filter(label='account', target_type='follow', account=request.user).values('target_id')
        user_data = [target_id['target_id'] for target_id in target_ids]
        page_number = request.GET.get("page_number",page)
        paginator = Paginator(user_data, 25)
        try:
            user_list = paginator.page(page_number)
        except PageNotAnInteger:
            user_list = paginator.page(1)
        except EmptyPage:
            return JsonResponse({'error': 'Empty page'}, status = status.HTTP_204_NO_CONTENT)
        users = [Account.objects.get(id=target_id) for target_id in user_list]

        response_data = {
            'current_page': user_list.number,
            'total_pages': paginator.num_pages,
            'users': [
            {
                'id': user.id, 
                'username': user.username,
                'avatar' : user.avatar,
                'news_count_real': News.objects.filter(account=user,label = 'real').count()
            } 
            for user in users
            ]
        }
        return JsonResponse(response_data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        error_message = 'Account not found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
@api_view(['GET'])
def list_user_following_you(request, page):
    try:
        target_ids = Interacts.objects.filter(label='account', target_type='follow', target_id=request.user).values('target_id')
        user_data = [target_id['target_id'] for target_id in target_ids]
        page_number = request.GET.get("page_number",page)
        paginator = Paginator(user_data, 25)
        try:
            user_list = paginator.page(page_number)
        except PageNotAnInteger:
            user_list = paginator.page(1)
        except EmptyPage:
            return JsonResponse({'error': 'Empty page'}, status = status.HTTP_204_NO_CONTENT)
        users = [Account.objects.get(id=target_id) for target_id in user_list]

        response_data = {
            'current_page': user_list.number,
            'total_pages': paginator.num_pages,
            'users': [
            {
                'id': user.id, 
                'username': user.username,
                'avatar' : user.avatar,
                'news_count_real': News.objects.filter(account=user,label = 'real').count()
            } 
            for user in users
            ]
        }
        return JsonResponse(response_data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        error_message = 'Account not found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_profile(request):
    try:
        user = Account.objects.get(id=request.user.id, status = 'active')
    except user.DoesNotExist:
        return JsonResponse({"error": "Account unactive"}, status=status.HTTP_404_NOT_FOUND)

    original_user_data = AccountSerializerUpdate(user).data

    serializer = AccountSerializerUpdate(user, data=request.data)

    if serializer.is_valid():
        serializer.save()

        changes_made = serializer.data != original_user_data
        if changes_made:
            return JsonResponse({"message": "Updated successfully"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse({"error": "No changes made."}, status=status.HTTP_200_OK)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    account = request.user

    serializer = ChangePasswordSerializer(data=request.data)
 
    if serializer.is_valid():
        # Check if the old password is correct
        if not account.check_password(serializer.validated_data['old_password']):
            return JsonResponse({"error": "Old password is incorrect."}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.validate(request.data):
        # Validate and set the new password
        # Validate and set the new password
            new_password = request.data['new_password']
            hashed_password = make_password(new_password)
            account.password = hashed_password
            account.save()

        # Set the hashed password to the accountin

        return JsonResponse({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def change_user_account_permissions(request, user_id):
    try:
        user = Account.objects.get(id=user_id)
    except user.DoesNotExist:
        return JsonResponse({"error": "Account unactive"}, status=status.HTTP_404_NOT_FOUND)
    
    if request.user.role == 'admin':
        if user.status == 'active':
            user.status = 'unactive'
        else:
            user.status = 'active'
        user.save()
        return JsonResponse({"message": "update successfully"}, status=status.HTTP_204_NO_CONTENT)
    else:
        return JsonResponse({"error": "You don't have permission to delete this comment"}, status=status.HTTP_403_FORBIDDEN)