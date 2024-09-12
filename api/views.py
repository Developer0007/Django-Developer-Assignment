import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from api.serializer import FriendRequestSerializer, FriendshipSerializer, RequestActionSerializer, RequestSerializer, UserLoginSerializer, UserSerializer, UserSignUpSerializer
from common import utils
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from friends.models import FriendRequest, Friendship

# Create your views here.
logger = logging.getLogger('django')

User = get_user_model()
class SignupAPI(GenericAPIView):
    allowed_methods = ("POST",)

    def post(self, request):
        try:
            data = request.data
            serializer = UserSignUpSerializer(data=data)
            if serializer.is_valid():
                email = data.get("email")
                if User.objects.filter(email=email, is_active=True).exists():
                    return utils.dispatch_response("User already exists with This email.",status=status.HTTP_406_NOT_ACCEPTABLE)
                else:
                    User.objects.create_user(email=email, password=data.get("password"), first_name = data.get("first_name"), last_name = data.get("last_name"))
                    return utils.dispatch_response("User created successfully.")
            else:
                return utils.dispatch_response("Invalid Login reuqest.",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return utils.dispatch_response("Something went wrong.",status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPI(GenericAPIView):
    allowed_methods = ("POST",)

    def post(self, request):
        try:
            data = request.data
            serializer = UserLoginSerializer(data=data)
            if serializer.is_valid():
                try:
                    email = data.get("email")
                    user = User.objects.get(email=email.lower(), is_active = True)
                    if user.check_password(data.get("password")):
                        token = {
                            "access_token" : f"{settings.AUTH_PREFIX}{AccessToken.for_user(user)}"
                            }
                        return utils.dispatch_response(data= token, msg="Logged in")

                    else:
                        return utils.dispatch_response("Incorrect user name/ password",status=status.HTTP_401_UNAUTHORIZED)

                except User.DoesNotExist:
                    return utils.dispatch_response("User Dose Not Exists",status=status.HTTP_404_NOT_FOUND)
            else:
                return utils.dispatch_response("Invalid signup reuqest.",status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(e)
            return utils.dispatch_response("Something went wrong.",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class SearchUserAPI(GenericAPIView):
    allowed_methods = ("GET",)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            keyword = request.query_params.get('keyword', '')
            if not keyword:
                return utils.dispatch_response("Search keyword is required",status=status.HTTP_400_BAD_REQUEST)

            data = None

            try:
                EmailValidator()(keyword)
                user = User.objects.filter(email=keyword, is_active=True).exclude(email = request.user.email)
                if user:
                    serializer = UserSerializer(user)
                    data = serializer.data

            except ValidationError:
                pass

            if data is None:
                users = User.objects.filter(
                    Q(email__icontains=keyword) | Q(first_name__icontains=keyword),
                    is_active=True
                ).exclude(email = request.user.email)
                
                page = int(request.query_params.get('page', 1))
                per_page = settings.PAGINATION_LIMIT
                start_index = (page - 1) * per_page
                end_index = page * per_page
                paginated_users = users[start_index:end_index]
                
                serializer = UserSerializer(paginated_users, many=True)
                data = serializer.data

            return utils.dispatch_response(data=serializer.data)

        except Exception as e:
            logger.error(e)
            return utils.dispatch_response("Something went wrong.",status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SendFriendRequestAPI(GenericAPIView):
    allowed_methods = ("POST",)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            serializer = RequestSerializer(data=request.data)
            if not serializer.is_valid():
                return utils.dispatch_response("Invalid reuqest.",status=status.HTTP_400_BAD_REQUEST)
            data = serializer.data
            receiver_email = data.get("email")
            receiver = User.objects.filter(email=receiver_email).first()
            if not receiver:
                return utils.dispatch_response(msg="Receiver does not exist", status=status.HTTP_404_NOT_FOUND)
            
            sender = request.user
            if sender == receiver:
                return utils.dispatch_response(msg="You cannot send a friend request to yourself", status=status.HTTP_400_BAD_REQUEST)

            if FriendRequest.objects.filter(from_user=sender, to_user=receiver).exists():
                return utils.dispatch_response(msg="Friend request already sent", status=status.HTTP_400_BAD_REQUEST)
            
            recent_requests = FriendRequest.objects.filter(from_user=sender, created_at__gte=timezone.now()-timezone.timedelta(minutes=1)).count()
            if recent_requests >= 3:
                return utils.dispatch_response(msg="Cannot send more than 3 requests per minute", status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            friend_request = FriendRequest.objects.create(from_user=sender, to_user=receiver)
            return utils.dispatch_response(data=FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(e)
            return utils.dispatch_response("Something went wrong.",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class FriendRequestActionAPI(GenericAPIView):
    allowed_methods = ("POST",)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            serializer = RequestActionSerializer(data=request.data)
            if not serializer.is_valid():
                return utils.dispatch_response("Invalid reuqest.",status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.data
            sender_email = data.get('email')

            sender = User.objects.filter(email=sender_email).first()
            if not sender:
                return utils.dispatch_response(msg="Sender does not exist", status=status.HTTP_404_NOT_FOUND)
            
            action = data.get("action")
            try:
                friend_request = FriendRequest.objects.get(from_user=sender, to_user=request.user, is_accepted = False, is_rejected=False)
                if friend_request:
                    if action== 1:
                        friend_request.is_accepted = True
                        Friendship.objects.create(user1=sender, user2=request.user)
                    else:
                        friend_request.is_rejected = True
                    
                    friend_request.save()
                    
                    msg = "Friend request accepted" if action == 1 else "Friend request rejected"
                    return utils.dispatch_response(msg=msg, status=status.HTTP_200_OK)
                else:
                    return utils.dispatch_response(msg="Request does not exist", status=status.HTTP_404_NOT_FOUND)
                
            except FriendRequest.DoesNotExist:
                return utils.dispatch_response("Request not found", status=status.HTTP_404_NOT_FOUND)
            
        except Exception as e:
            logger.error(e)
            return utils.dispatch_response("Something went wrong.",status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PendingRequestAPI(GenericAPIView):
    allowed_methods = ("GET",)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            
            pending_requests = FriendRequest.objects.filter(to_user=request.user, is_accepted = False, is_rejected=False)
            serializer = FriendRequestSerializer(pending_requests, many=True)
            return utils.dispatch_response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(e)
            return utils.dispatch_response("Something went wrong.",status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AcceptedRequestByOthersAPI(GenericAPIView):
    allowed_methods = ("GET",)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            
            pending_requests = FriendRequest.objects.filter(from_user=request.user, is_accepted = True)
            serializer = FriendRequestSerializer(pending_requests, many=True)
            return utils.dispatch_response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(e)
            return utils.dispatch_response("Something went wrong.",status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class AllFriendsAPI(GenericAPIView):
    allowed_methods = ("GET",)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            
            pending_requests = Friendship.objects.filter(Q(user1=request.user) | Q(user2=request.user))
            serializer = FriendshipSerializer(pending_requests, many=True)
            return utils.dispatch_response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(e)
            return utils.dispatch_response("Something went wrong.",status=status.HTTP_500_INTERNAL_SERVER_ERROR)