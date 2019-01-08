from django.urls import path, include

from . import views

urlpatterns = [
    path('users/', include([
        path('token-validation', views.TokenValidation.as_view()),
        path('login', views.UserLogin.as_view()),
        path('logout', views.UserLogout.as_view()),
        path('register', views.UserRegistration.as_view()),
        path('activate/<str:encrypted_email>/<slug:email_token>',
             views.UserActivation.as_view()),
        path('activate/retry-activation', views.UserRetryActivation.as_view()),
        path('<int:id>', views.UserProfile.as_view()),
        path('<int:id>/data', views.UserProfile.as_view()),
        path('<int:id>/password', views.UserPassword.as_view()),
        path('<int:id>/email', views.UserEmail.as_view()),
    ])),
]
