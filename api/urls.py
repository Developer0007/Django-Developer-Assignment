from django.urls import path
from .views import AcceptedRequestByOthersAPI, FriendRequestActionAPI, LoginAPI, PendingRequestAPI, SearchUserAPI, SendFriendRequestAPI, SignupAPI
 
urlpatterns = [
    path('signup/', SignupAPI.as_view(), name='signup'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('search/', SearchUserAPI.as_view(), name='search'),
    path('send_request/', SendFriendRequestAPI.as_view(), name='send_request'),
    path('action_on_request/', FriendRequestActionAPI.as_view(), name='action_on_request'),
    path('pending_request/', PendingRequestAPI.as_view(), name='pending_request'),
    path('request_acc_by_other/', AcceptedRequestByOthersAPI.as_view(), name='request_acc_by_other'),
    path('all_friends/', AcceptedRequestByOthersAPI.as_view(), name='all_friends'),

]