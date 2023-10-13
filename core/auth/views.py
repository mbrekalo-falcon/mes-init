from core.__init__ import *
from django.contrib.auth import authenticate
from django.core.files import File

from models.user.models import UserModel, UserDetail
from models.cluster.models import ClusterUser, UserApplicationRole

from .serializers import LoginUserSerializer, SocialAuthSerializer

from core.helpers.enum import LoginEnum, ActivateToken
from core.user.serializers import UserCreateSerializer
from core.helpers.mixin import capture_auth_image, generate_custom_uuid, update_user_auth_provider, create_token
from core.helpers.emails import SystemMail


class UserLoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginUserSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return rest_default_response(message=serializer.errors, status=status.HTTP_403_FORBIDDEN)

        # Check if user exists
        qv_user = UserModel.custom_manager.alive().filter(email=data.get('email').lower())
        if not qv_user.exists():
            return rest_default_response(message=LoginEnum.USER_NOT_FOUND.value, status=status.HTTP_404_NOT_FOUND)

        user = qv_user.first()

        user_auth = authenticate(username=user.username, password=data.get('password'))
        if not user_auth:
            return rest_default_response(message=LoginEnum.USER_NOT_FOUND.value, status=status.HTTP_404_NOT_FOUND)

        data = create_token(user)

        # Check which clusters user has access to
        if not user.is_superuser:
            qv_cluster_user = ClusterUser.custom_manager.alive().filter(user_id=user.id)
            if not qv_cluster_user.exists():
                return rest_default_response(status=status.HTTP_403_FORBIDDEN, message=LoginEnum.USER_NOT_ON_CLUSTER.value)

            cur = UserApplicationRole.custom_manager.alive().filter(user_id=user.id)
            if not cur.exists():
                return rest_default_response(status=status.HTTP_403_FORBIDDEN, message=LoginEnum.USER_NO_PERMISSIONS.value)
            data['application_role'] = [
                {
                    'role_id': x.cluster_role.application_role.id,
                    'name': x.cluster_role.application_role.name,
                    'cluster_id': x.cluster_role.cluster.id,
                    'cluster_name': x.cluster_role.cluster.name,
                }
                for x in cur
            ]
        clusters = ClusterUser.custom_manager.alive().filter(user=user.id).values('cluster')
        data['clusters'] = clusters

        # Check if user has logged in since user creation, for password reset
        data['previously_logged_in'] = True
        if not user.check_last_login():
            data['previously_logged_in'] = False
            return rest_default_response(data=data, status=status.HTTP_200_OK)

        qv_user.update(last_login=datetime.datetime.now())
        return rest_default_response(data=data, status=status.HTTP_200_OK)


class ActivateAccountView(APIView):
    """

        Activate user account.
        Just send

    """
    permission_classes = (AllowAny,)

    def get(self, request, token_id):
        qv_check_token = UserDetail.custom_manager.alive().filter(email_verified=False, email_verified_code=token_id)

        if not qv_check_token.exists():
            return rest_default_response(message=ActivateToken.USER_NOT_FOUND.value, status=status.HTTP_404_NOT_FOUND)

        user = qv_check_token.first().user
        qv_check_token.update(email_verified_code='', email_verified=True)

        # Activate user for next login or all time
        UserModel.custom_manager.alive().filter(id=user.id).update(is_active=True)

        return rest_default_response(message=ActivateToken.USER_ACTIVATED.value, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    """
        Post method:
    """
    permission_classes = (AllowAny,)

    def get(self, request, email):
        qv_user = UserModel.custom_manager.alive().filter(email=email.lower(), is_active=True)
        if not qv_user:
            return rest_default_response(message=ActivateToken.USER_NOT_FOUND.value, status=status.HTTP_404_NOT_FOUND)
        qv_user.first().set_new_user_detail_token()  # Set new token
        # Call email and send user full path for request
        SystemMail.reset_password(qv_user.first())
        return rest_default_response(message=ActivateToken.USER_ACTIVATE_PASSWORD.value, status=status.HTTP_200_OK)

    def post(self, request, token_id):
        qv_check_token = UserDetail.custom_manager.alive().filter(token_code=token_id)

        if not qv_check_token.exists():
            return rest_default_response(
                message=ActivateToken.USER_NOT_FOUND.value, status=status.HTTP_404_NOT_FOUND
            )
        user_details = qv_check_token.first()

        data = request.data
        password = data.get('password')
        if not password:
            return rest_default_response(
                message=ActivateToken.USER_DATA_PASSWORD.value, status=status.HTTP_403_FORBIDDEN
            )

        user = UserModel.custom_manager.alive().filter(id=user_details.user.id).first()
        user.set_password(password)
        user.save()

        qv_check_token.update(token_code='')

        return rest_default_response(message=ActivateToken.USER_CHANGE_PASSWORD.value, status=status.HTTP_200_OK)


class SocialAuthView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = SocialAuthSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if not serializer.is_valid():
            return rest_default_response(message=serializer.errors, status=status.HTTP_403_FORBIDDEN)

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        photo_url = data.get('photo_url')
        provider = data.get('provider')
        auth_id = data.get('auth_id')

        um = UserModel.custom_manager.alive()
        um_email = um.filter(email=email.lower())
        if um_email.exists():
            user = um_email.first()
            update_user_auth_provider(user, provider, auth_id)
            um_email.update(last_login=datetime.datetime.now())
            return rest_default_response(data=create_token(user), status=status.HTTP_200_OK)
        else:
            save_data = {}
            save_data['username'] = str(generate_custom_uuid())
            save_data['password'] = str(generate_custom_uuid())
            save_data['is_active'] = True
            save_data['first_name'] = first_name
            save_data['last_name'] = last_name
            save_data['email'] = email.lower()
            serializer = UserCreateSerializer(data=save_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                user_id = UserModel.custom_manager.alive().filter(email=email.lower()).first()
                ud = UserDetail.custom_manager.alive().filter(user_id=user_id.id).first()
                if photo_url:
                    ud.profile_picture.save('{}'.format(str(generate_custom_uuid())),
                                            File(capture_auth_image(photo_url)))
                update_user_auth_provider(user_id, provider, auth_id)
                return rest_default_response(data=create_token(user_id), status=status.HTTP_201_CREATED)
            return rest_default_response(status=status.HTTP_400_BAD_REQUEST, message=serializer.errors)
