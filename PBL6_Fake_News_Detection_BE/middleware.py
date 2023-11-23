from django.http import JsonResponse, HttpResponse
import jwt
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from auth_site.models import Account
from PBL6_Fake_News_Detection_BE.settings import SECRET_KEY
from auth_site.serializer import AccountSerializer
from rest_framework.renderers import JSONRenderer
import json
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

class AdminAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        # Các logic xử lý middleware ở đây
        return self.get_response(request, *args, **kwargs)
    
    def process_request(self, request, *args, **kwargs):
        print('MIDDLEWARE')
        # Kiểm tra xem request có chứa access_token không
        if 'HTTP_AUTHORIZATION' in request.META:
            authorization_header = request.META['HTTP_AUTHORIZATION']

            # Token thường có định dạng "Bearer <access_token>", nên chúng ta tách nó ra.
            # Điều này chỉ áp dụng khi ta sử dụng Token Authentication.
            access_token = authorization_header.split(' ')[1] if authorization_header.startswith('Bearer ') else authorization_header

            try:
                # Giải mã access_token để lấy thông tin người dùng
                # options {'verify_exp': False} để vô hiệu hóa kiểm tra thời gian hết hạn (exp)
                payload = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'], options={'verify_exp': False})
                # print(payload)

                user_id = payload.get('user_id')
                user = Account.objects.get(id=user_id)

                # Sử dụng serializer để serialize đối tượng user thành một từ điển
                user_serializer = AccountSerializer(user)
                # print(user_serializer)

                # Chuyển từ điển user thành JSON và in ra
                user_json = JSONRenderer().render(user_serializer.data)
                # print(user_json)

                # Chuyển dữ liệu JSON thành một từ điển Python
                user = json.loads(user_json)
                # print(user)

                if user['role'] == 'admin':
                    print('Admin')
                    # Người dùng có quyền admin, cho phép request tiếp tục xử lý
                    return self.get_response(request, *args, **kwargs)
                else:
                    # Người dùng không có quyền admin, trả về lỗi
                    return JsonResponse(
                        data={
                            'success': False,
                            'error': 'Không có quyền truy cập'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except InvalidSignatureError as e:
                # In ra thông điệp lỗi để biết lỗi xảy ra tại đâu
                print(str(e))
                # Xử lý lỗi khi không thể giải mã access_token
                return JsonResponse(
                    data={
                        'success': False,
                        'error_message': 'access_token không hợp lệ'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except ExpiredSignatureError as e:
                # In ra thông điệp lỗi để biết lỗi xảy ra tại đâu
                print(str(e))
                # Xử lý lỗi khi access_token hết hạn
                return JsonResponse(
                    data={
                        'success': False,
                        'error_message': 'access_token hết hạn'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except Exception as e:
                # In ra thông điệp lỗi để biết lỗi xảy ra tại đâu
                print(str(e))
                # Xử lý lỗi khác
                return JsonResponse(
                    data={
                        'success': False,
                        'error_message': 'Không thể xử lý access_token'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return JsonResponse(
            data={
                'success': False,
                'error_message': 'Chưa cung cấp access_token'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )
    
class UserAuthorizationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        return self.process_request(request, *args, **kwargs)
    
    def process_request(self, request, *args, **kwargs):
        # Kiểm tra xem request có chứa access_token không
        if 'HTTP_AUTHORIZATION' in request.META:
            authorization_header = request.META['HTTP_AUTHORIZATION']

            # Token thường có định dạng "Bearer <access_token>", nên chúng ta tách nó ra.
            # Điều này chỉ áp dụng khi ta sử dụng Token Authentication.
            access_token = authorization_header.split(' ')[1] if authorization_header.startswith('Bearer ') else authorization_header

            try:
                # Giải mã access_token để lấy thông tin người dùng
                payload = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                user = Account.objects.get(id=user_id)

                # Sử dụng serializer để serialize đối tượng user thành một từ điển
                user_serializer = AccountSerializer(user)
                # print(user_serializer)

                # Chuyển từ điển user thành JSON và in ra
                user_json = JSONRenderer().render(user_serializer.data)
                # print(user_json)

                # Chuyển dữ liệu JSON thành một từ điển Python
                user = json.loads(user_json)
                # print(user)

                if user['role'] == 'user':
                    print('User')
                    # Người dùng có quyền user, cho phép request tiếp tục xử lý
                    return self.get_response(request, *args, **kwargs)
                else:
                    # Người dùng không có quyền user, trả về lỗi
                    return JsonResponse(
                        data={
                            'success': False,
                            'error': 'Không có quyền truy cập.'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            except InvalidSignatureError:
                # Xử lý lỗi khi không thể giải mã access_token
                return JsonResponse(
                    data={
                        'success': False,
                        'error_message': 'access_token không hợp lệ'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except ExpiredSignatureError:
                # Xử lý lỗi khi access_token hết hạn
                return JsonResponse(
                    data={
                        'success': False,
                        'error_message': 'access_token hết hạn'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except Exception:
                # Xử lý lỗi khác
                return JsonResponse(
                    data={
                        'success': False,
                        'error_message': 'Không thể xử lý access_token'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        return JsonResponse(
            data={
                'success': False,
                'error_message': 'Chưa cung cấp access_token'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )