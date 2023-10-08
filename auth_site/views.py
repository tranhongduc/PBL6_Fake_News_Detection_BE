from .forms import RegistrationForm
from .models import Account
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from .serializer import AccountSerializer
from rest_framework import permissions, status
from rest_framework.decorators import api_view

@api_view(['POST'])
def login(request):
    # Nhận đầu vào từ người dùng
    email = request.POST['email']
    password = request.POST['password']
    try:
        # Tìm tài khoản dựa trên địa chỉ email
        account = Account.objects.get(email=email)

        # Kiểm tra mật khẩu
        if (password, account.password):
            if account.status == 'active':
                account_created_at = account.created_at.strftime("%Y-%m-%d %H:%M:%S")
                account_updated_at = account.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                # Đăng nhập thành công, lưu thông tin người dùng vào phiên làm việc
                request.session['account_id'] = account.id
                request.session['account_email'] = account.email
                request.session['account_role'] = account.role
                request.session['account_avatar'] = account.avatar
                request.session['account_status'] = account.status
                request.session['account_created_at'] = account_created_at
                request.session['account_updated_at'] = account_updated_at

                # Điều hướng tới trang tương ứng
                if account.role == 'user':
                    # Sử dụng Serializer để chuyển Account model sang JSON
                    serializer = AccountSerializer(account)
                    print(serializer.data)
                    # Điều hướng sang trang account
                    return JsonResponse(
                        data={
                            'user': serializer.data,
                            'success': True,
                            'message': 'Đăng nhập thành công',
                            'redirect_url': '/user'
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    # Điều hướng sang trang admin
                    return JsonResponse(
                        data={
                            'user': serializer.data ,
                            'success': True,
                            'message': 'Đăng nhập thành công',
                            'redirect_url': '/admin'
                        },
                        status=status.HTTP_200_OK
                    )
            else:
                # Tài khoản không còn hiệu lực, thông báo lỗi
                return JsonResponse(
                    data={
                        'success': False,
                        'error_message': 'Tài khoản không hoạt động'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            # Mật khẩu không đúng, thông báo lỗi
            return JsonResponse(
                data={
                    'success': False,
                    'error_message': 'Mật khẩu không đúng'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Account.DoesNotExist:
        # Không tìm thấy tài khoản với địa chỉ email đã cung cấp, thông báo lỗi
        return JsonResponse(
            data={
                'success': False,
                'error_message':  'Tài khoản không tồn tại'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
def register(request):
    form = RegistrationForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        confirm_password = form.cleaned_data['confirm_password']
        
        print('Username:', username)
        print('Email:', email)
        print('Password:', password)
        print('Confirm Password:', confirm_password)

        # Sử dụng make_password để mã hóa mật khẩu
        hashed_password = make_password(password)

        # Tạo người dùng mới và lưu vào cơ sở dữ liệu với mật khẩu đã mã hóa
        account = Account(username=username, email=email, password=hashed_password)
        account.save()

        accounts = Account.objects.all().order_by('id')
        if cache.get('account_list') is not None :
            cache.delete('account-list')
        cache.set('account_list', accounts, 600)

        return JsonResponse(
            data={
                'success': True,
                'message': 'Đăng ký thành công',
                'redirect_url': '/login'
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

@api_view(['GET'])
def session_info(request):
    # Kiểm tra xem người dùng đã đăng nhập và có phiên làm việc không
    if 'account_id' in request.session and 'account_role' in request.session and 'account_email' in request.session and 'account_status' in request.session and 'account_created_at' in request.session and 'account_updated_at' in request.session:
        # Hiển thị thông tin về phiên làm việc
        account_session_data = {
            'id': request.session['account_id'],
            'role': request.session['account_role'],
            'email': request.session['account_email'],
            'status': request.session['account_status'],
            'created_at': request.session['account_created_at'],
            'update_at': request.session['account_updated_at'],
        }
        return JsonResponse(
            data=account_session_data, 
            safe=False, 
            status=status.HTTP_200_OK
        )
    else:
        # Phiên làm việc không tồn tại, đưa người dùng đến trang đăng nhập
        return JsonResponse(
            data={
                'success': False,
                'message': 'Chưa đăng nhập vào hệ thống',
                'redirect_url': '/login'
            },
            status=status.HTTP_401_UNAUTHORIZED
        ) 
    
@api_view(['POST'])
def logout(request):
    if 'account_id' in request.session:
        # Xóa hết các thông tin trong session
        request.session.clear()
        # Điều hướng đến trang đăng nhập sau khi logout
        return JsonResponse(
            data={
                'success': True,
                'message': 'Đăng xuất thành công',
                'redirect_url': '/login'
            },
            status=status.HTTP_200_OK
        ) 
    else:
        # Người dùng chưa đăng nhập, điều hướng đến trang đăng nhập
        return JsonResponse(
            data={
                'success': False,
                'message': 'Chưa đăng nhập vào hệ thống',
                'redirect_url': '/login'
            },
            status=status.HTTP_401_UNAUTHORIZED
        ) 
