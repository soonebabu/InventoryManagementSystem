  # context_processors.py
from .utils import get_user_group_full_name

def user_group_full_name(request):
    user_group_full_name = None

    if request.user.is_authenticated:
        user_group_full_name = get_user_group_full_name(request.user)

    return {'user_group_full_name': user_group_full_name}


# def user_group_name(request):
#     user_group_name = None
#     if request.user.is_authenticated and request.user.groups.exists():
#         user_group_name = request.user.groups.first().name
#     return {'user_group_name': user_group_name}

from main.models import SubGroup

def user_group_name(request):
    user_group_name = None
    user_subgroup_name = None

    if request.user.is_authenticated:
        # Get the user's group name
        if request.user.groups.exists():
            user_group_name = request.user.groups.first().name

        # Get the user's subgroup name
        user_subgroups = SubGroup.objects.filter(users=request.user)
        if user_subgroups.exists():
            user_subgroup_name = user_subgroups.first().name

    return {'user_group_name': user_group_name, 'user_subgroup_name': user_subgroup_name}


from .models import Notification

def unread_notification_count(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        return {'unread_notification_count': notifications.count()}
    return {'unread_notification_count': 0}
