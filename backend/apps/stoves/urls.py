from django.urls import path, include

from . import views

urlpatterns = [
    path('stoves/<int:stove_id>/', include([
        path('cooks', views.CRUDCooksView.as_view()),
        path('chiefs', views.CRUDChiefsView.as_view()),
    ])),
]

