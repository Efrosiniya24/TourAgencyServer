from django.urls import path, include
from .views import SignUp, SignIn, UserView, LogoutView, AllUsersView, UserSearch, UserCountView, AverageAgeView, \
    GenderDistributionView, AverageAgeByGenderView

urlpatterns = [
    path('signIn', SignIn.as_view(), name='signIn'),
    path('signUp', SignUp.as_view(), name="signUp"),
    path('user', UserView.as_view()),
    path('logout', LogoutView.as_view()),
    path('allUsers/', AllUsersView.as_view()),
    path('search', UserSearch.as_view(), name='user-search'),
    path('user-сount', UserCountView.as_view(), name='user-count'),
    path('average-age', AverageAgeView.as_view(), name='average-age'),
    path('gender-distribution', GenderDistributionView.as_view(), name='gender-distribution'),
    path('average-age-by-gender', AverageAgeByGenderView.as_view(), name='average-age-by-gender'),

]
