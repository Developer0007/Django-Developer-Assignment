from django.db import models
from django.utils import timezone
from user.models import User

# Create your models here.
class FriendRequest(models.Model):
    ACTIONS= [
        (1,'Accepted'),
        (2,'Rejected')
    ]
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.first_name} {self.to_user.first_name}"
    
class Friendship(models.Model):
    user1 = models.ForeignKey(User, related_name='friendship1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name='friendship2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user1.first_name} {self.user2.first_name}"