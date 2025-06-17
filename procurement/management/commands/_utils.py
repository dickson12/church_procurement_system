from django.contrib.auth.models import Group, User

def add_user_to_group(username, group_name):
    try:
        group = Group.objects.get(name=group_name)
        user = User.objects.get(username=username)
        user.groups.add(group)
        print(f"Added {username} to {group_name} group")
    except Group.DoesNotExist:
        print(f"Group {group_name} does not exist")
    except User.DoesNotExist:
        print(f"User {username} does not exist")
