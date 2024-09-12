# myapp/admin.py
from django.contrib import admin
from .models import FriendRequest, Friendship

class FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('to_user', 'from_user', 'created_at')
    search_fields = ('to_user', 'from_user')

    list_filter = ('is_accepted', 'is_rejected')

class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2')
    search_fields = ('user1', 'user2')

admin.site.register(Friendship, FriendshipAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
