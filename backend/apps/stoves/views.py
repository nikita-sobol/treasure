from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from .permissions import ChiefsOnly, CooksOnly
from .models import Cook, Stove
from .serializers import CookSerializer


class CRUDCooksView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, ChiefsOnly)

    def get(self, request, stove_id):
        stove_cooks = Stove.objects.get(id=stove_id).cooks

        serializer = CookSerializer(stove_cooks, many=True)

        return Response(data=serializer.data, status=200)

    def post(self, request, stove_id):
        new_cook_id = request.data.get('new_cook_id', 0)

        user = User.objects.filter(id=new_cook_id).first()
        stove = Stove.objects.filter(id=stove_id).first()

        if not user:
            return Response(f'User was not found',
                            status=404)

        if Cook.objects.filter(user=user, stove=stove).first():
            return Response(
                f'User {user.id} is already a cook of a'
                f' stove {stove.id}', status=403
            )

        Cook.objects.create(user=user, stove=stove, is_chief=False)

        return Response(status=201)


class CRUDChiefsView(APIView):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, CooksOnly)

    def get(self, request, stove_id):
        stove = Stove.objects.filter(id=stove_id).first()

        chief = stove.cooks.filter(is_chief=True).first()

        serializer = CookSerializer(chief)

        return Response(data=serializer.data, status=200)

    def post(self, request, stove_id):
        stove = Stove.objects.filter(id=stove_id).first()

        cook = Cook.objects.create(user=request.user, stove=stove,
                                   is_chief=True)

        stove.cooks.add(cook)

        return Response(status=201)
