from rest_framework import permissions

from .models import Stove, Cook


class CooksOnly(permissions.BasePermission):
    expects_authentication = True

    def has_permission(self, request, view):
        stove_id = view.kwargs.get('stove_id', 0)

        stove = Stove.objects.filter(id=stove_id).first()
        if not stove:
            self.message = (
                'Cook permission denied. Stove id was not found'
            )

            return False

        if request.method in permissions.SAFE_METHODS:
            cook = stove.cooks.filter(user=request.user).first()

            if not cook:
                self.message = (
                    f'Cook permission denied. User '
                    f'{request.user.id} is not a cook of '
                    f'a stove {stove_id}'
                )

                return False
        else:
            if len(stove.cooks.all()):
                self.message = (f'Cook permission denied. '
                                f'Stove {stove_id} already has a chief')
                return False
            elif stove.serial_id != request.data.get('stove_serial_id', ''):
                self.message = (f'Cook permission denied. '
                                f'Stove serial ids do not match')

                return False

        return True


class ChiefsOnly(permissions.BasePermission):
    expects_authentication = True

    def has_permission(self, request, view):

        stove_id = view.kwargs.get('stove_id', 0)

        stove = Stove.objects.filter(id=stove_id).first()
        if not stove:
            self.message = 'Chief permission denied. Stove id was not found'

            return False

        cook = stove.cooks.filter(user=request.user).first()

        if not cook:
            self.message = (f'User {request.user.id} is not a cook of a stove '
                            f'{stove_id}')
            return False
        elif not cook.is_chief:
            self.message = (f'Cook '
                            f'{request.user.id} has no chief permission '
                            f'for a stove {stove_id}')
            return False

        return True



