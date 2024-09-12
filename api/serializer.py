from rest_framework import serializers
from django.contrib.auth import get_user_model
from friends.models import FriendRequest, Friendship

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

class UserSignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    password = serializers.CharField(required=True)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)

class RequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

class RequestActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=FriendRequest.ACTIONS, required=True)
    email = serializers.EmailField(required=True)
        
class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['from_user', 'to_user', 'is_accepted', 'is_rejected']

class FriendshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Friendship
        fields = ['user1', 'user2']
