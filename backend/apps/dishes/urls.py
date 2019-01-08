from django.urls import path, include

from . import views

urlpatterns = [
    path('dishes/', include([
        path('', views.DishView.as_view()),
        path('<int:dish_id>/timings', views.TimingView.as_view()),
    ])),
]
