from django.urls import path, include

from . import views

urlpatterns = [
    path('stoves/<int:stove_id>/', include([
        path('cooks', views.StoveCooksView.as_view()),
    ])),
]

