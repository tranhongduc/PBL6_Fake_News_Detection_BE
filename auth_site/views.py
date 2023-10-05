from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.http import JsonResponse, HttpRequest
from django.contrib.auth.hashers import make_password, check_password
from django.core.cache import cache
from rest_framework import permissions, status
from rest_framework.decorators import api_view

@api_view(['GET', 'POST'])
def login(request):
    if request.method == 'POST':
        # Nhận đầu vào từ người dùng
        email = request.POST['email']
        password = request.POST['password']
        try:
            # Tìm tài khoản dựa trên địa chỉ email
            account = Account.objects.get(email=email)

            # Kiểm tra mật khẩu
            if check_password(password, account.password):
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
                        # Điều hướng sang trang account
                        return JsonResponse(
                            {
                                'success': True,
                                'redirect_url': '/ /'
                            }
                        )
                    else:
                        # Điều hướng sang trang admin
                        return JsonResponse(
                            {
                                'success': True,
                                'redirect_url': '/ /'
                            }
                        )
                else:
                    return JsonResponse(
                        {
                            'success': False,
                            'error_message': 'Tài khoản không hoạt động.'
                        }
                    )
            else:
                # Mật khẩu không đúng, thông báo lỗi
                return JsonResponse(
                    {
                        'success': False,
                        'error_message': 'Mật khẩu không đúng.'
                    }
                )
        except Account.DoesNotExist:
            # Không tìm thấy tài khoản với địa chỉ email này, thông báo lỗi
            return JsonResponse(
                {
                    'success': False,
                    'error_message':  'Tài khoản không tồn tại.'
                }
            )

    # Nếu là GET request hoặc không thành công, hiển thị trang đăng nhập
    return JsonResponse(
        {
            'success': False, 
            'error_message': 'Phương thức không hợp lệ.'
        }
    )

@api_view(['GET', 'POST'])
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Sử dụng make_password để mã hóa mật khẩu
            hashed_password = make_password(password)

            # Tạo người dùng mới và lưu vào cơ sở dữ liệu với mật khẩu đã mã hóa
            account = Account(email=email, password=hashed_password)
            account.save()

            accounts = Account.objects.all().order_by('id')
            if cache.get('account_list') is not None :
                cache.delete('account-list')
            cache.set('account_list', accounts, 600)

            # Chuyển hướng svscode-file://vscode-app/c:/accounts/lyvan/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.htmlau khi đăng ký thành công
            return JsonResponse(
                {
                    'success': True,
                    'redirect_url': '/login/'
                }
            )  # Điều hướng đến trang đăng nhập (cần thiết phải có URL 'login')
        else:
            print(form.errors)
            return JsonResponse(
                {
                'error': form.errors,
                # 'redirect_url': '/login/'
                }
            ) 

    else:
        form = RegistrationForm()

    return JsonResponse(
        {
            'success': False,
            'form': form
        }
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
        return JsonResponse(account_session_data, safe=False, status=status.HTTP_200_OK)
    else:
        # Phiên làm việc không tồn tại, đưa người dùng đến trang đăng nhập
        return JsonResponse(
            {
                'success': True,
                'redirect_url': '/login/'
            }
        ) 
def logout_view(request):
    if 'account_id' in request.session:
        # Xóa hết các thông tin trong session
        request.session.clear()
        # Điều hướng đến trang đăng nhập sau khi logout
        return JsonResponse(
            {
                'success': True,
                'redirect_url': '/login/'
            }
        ) 
    else:
        # Người dùng chưa đăng nhập, điều hướng đến trang đăng nhập
        return JsonResponse(
            {
                'success': True,
                'redirect_url': '/login/'
            }
        ) 
