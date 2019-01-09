from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import DishSerializer, TimingSerializer
from .models import Dish


class DishView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_dishes = Dish.objects.filter(users__id=request.user.id)

        serializer = DishSerializer(user_dishes, many=True)

        response_data = serializer.data

        return Response(data=response_data, status=200)

    def post(self, request):

        serializer = DishSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(cook=request.user)

        return Response(data=serializer.data, status=201)


class TimingView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, dish_id):
        dish = Dish.objects.filter(users__id=request.user.id,
                                   pk=dish_id).first()
        if not dish:
            return Response(
                data=f"User not allowed to edit dish with id {dish_id}",
                status=403
            )

        timings = dish.timings.all()

        serializer = TimingSerializer(timings, many=True)

        return Response(data=serializer.data, status=200)

    def post(self, request, dish_id):
        dish = Dish.objects.filter(users__id=request.user.id,
                                   pk=dish_id).first()
        if not dish:
            return Response(
                data=f"User not allowed to edit dish with id {dish_id}",
                status=403
            )

        serializer = TimingSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(dish=dish)

        return Response(data=serializer.data, status=201)
