from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from .permissions import ChiefOnly
from .models import Cook, Stove
from .serializers import CookSerializer


class StoveCooksView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, ChiefOnly)

    def get(self, request, stove_id):

        serializer = CookSerializer(Stove.objects.get(id=stove_id).cooks,
                                    many=True)

        return Response(data=serializer.data, status=200)

    def post(self, request, stove_id):
        new_cook_id = request.data.get('new_cook_id', 0)

        user = User.objects.filter(id=new_cook_id).first()
        stove = Stove.objects.filter(id=stove_id).first()

        if not user:
            return Response(f'Valid user_id is required',
                            status=422)

        if Cook.objects.filter(user=user, stove=stove).first():
            return Response(
                f'User {user.id} is already a cook of a'
                f'stove {stove.id}', status=403
            )

        Cook.objects.create(user=user, stove=stove, is_chief=False)

        return Response(status=201)

