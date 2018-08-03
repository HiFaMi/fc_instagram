from django.urls import path

from .. import apis

urlpatterns = [
    path('', apis.UserList.as_view()),
    path('auth-token/', apis.AuthToken.as_view()),
    path('auth-test/', apis.AuthenticationTest.as_view()),
]
