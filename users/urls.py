from django.urls import path, include
from .views import SignUp, SignIn, UserView, LogoutView, AllUsersView, UserSearch

urlpatterns = [
    path('signIn', SignIn.as_view(), name='signIn'),
    path('signUp', SignUp.as_view(), name="signUp"),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('allUsers', AllUsersView.as_view()),
    path('search', UserSearch.as_view(), name='user-search'),
]
