from .forms import RegistrationForm
from .models import Account
from news.models import News, Comments
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
        
        print('Username:', username)
        print('Email:', email)
        print('Password:', password)

        # Sử dụng make_password để mã hóa mật khẩu
        hashed_password = make_password(password)

        # Tạo người dùng mới và lưu vào cơ sở dữ liệu với mật khẩu đã mã hóa
        account = Account(username=username, email=email, password=hashed_password)
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

                # Token thường có định dạng "Bearer <access_token>", nên chúng ta tách nó ra.
                # Điều này chỉ áp dụng khi ta sử dụng Token Authentication.
                refresh_token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header

                try:
                    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256']) # mã hóa refresh_token
                    print('Payload:', payload)

                    is_refresh_token_expired = False
                    # Refresh token còn hiêu lực -> Tạo mới access_token, giữ nguyên refresh_token
                    # Thay đổi jti để tạo một new_access_token duy nhất
                    payload['jti'] = str(uuid.uuid4())
                    # Tạo lại access_token sử dụng payload thay đổi
                    new_access_token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
                    print('New access token:', new_access_token)
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
                            'message': 'Đăng nhập thành công',
                            'redirect_url': '/user',
                        },
                        status=status.HTTP_200_OK
                    )
                elif is_refresh_token_expired == False: # refresh_token đính kèm theo vẫn còn hiệu lực
                    return JsonResponse(
                        data={
                            'user': serializer.data,
                            'access_token': str(new_access_token),
                            'refresh_token': str(refresh_token),
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
                                'access_token': str(refresh.access_token),
                                'refresh_token': str(refresh),
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
                print('Con cac')             
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
                            'access_token': str(new_access_token),
                            'refresh_token': str(refresh_token),
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
                                'access_token': str(refresh.access_token),
                                'refresh_token': str(refresh),
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
def admin_user_list(request):
    try:
        admin_users = Account.objects.filter(role='admin')
        admin_user_data = [
            {
                'account_id':user.id,
                'username': user.username, 
                'email': user.email,
                'status' : user.status
            } for user in admin_users]
        data = {'admin_users': admin_user_data}
        return JsonResponse(data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no admin users are found
        error_message = 'No admin users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
def user_list(request):
    try:
        users = Account.objects.filter(role='user')
        user_data = [
            {
                'account_id': user.id,
                'username': user.username, 
                'email': user.email,
                'status' : user.status
            } for user in users]
        data = {'users': user_data}
        return JsonResponse(data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        # Handle the case where no user users are found
        error_message = 'No user users found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        # Handle other unexpected errors
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)
def user_detail(request, user_id):
    try:
        account = Account.objects.get(id=user_id)
        
        # Đếm số lượng tin tức và bình luận của người dùng
        news_count = News.objects.filter(account=account).count()
        comments_count = Comments.objects.filter(account=account).count()
        
        # Convert the account object and counts to a dictionary
        user_data = {
            'id': account.id,
            'username': account.username,
            'email': account.email,
            'role': account.role,
            'avatar' : account.avatar,
            'news_count': news_count,
            'comments_count': comments_count,
        }
        return JsonResponse(user_data,status=status.HTTP_200_OK)
    except ObjectDoesNotExist as e:
        error_message = 'Account not found.'
        return JsonResponse({'error': error_message}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        error_message = 'An error occurred while processing the request.'
        return JsonResponse({'error': error_message}, status=status.HTTP_500_Internal_Server_Error)  