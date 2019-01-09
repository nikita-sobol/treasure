from rest_framework import permissions

from .models import Stove


class ChiefOnly(permissions.BasePermission):
    expects_authentication = True

    def has_permission(self, request, view, *args, **kwargs):
        stove_id = view.kwargs.get('stove_id', 0)

        stove = Stove.objects.filter(id=stove_id).first()

        if not stove:
            self.message = f'Invalid stove id was provided'

            return False

        cook = stove.cooks.filter(user=request.user).first()

        if not cook:
            self.message = (f'User {request.user.id} is not a ' 
                            f'cook of stove {stove_id}')
            return False
        elif not cook.is_chief:
            self.message = (f'User access denied. User '
                            f'{request.user.id} has no chief permission '
                            f'for a stove {stove_id}')
            return False

        return True
