"""rflix URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path

from main import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("movies/", views.movies, name="movies"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("rate/<int:movie_id>/", views.rate_movie, name="rate_movie"),
    path("delete-rating/<int:movie_id>/", views.delete_rating, name="delete_rating"),
    path("recommendations/", views.recommendations, name="recommendations"),
    path("parties/", views.movie_parties, name="movie_parties"),
    path("parties/join/<int:party_id>/", views.join_party, name="join_party"),
    path("parties/leave/<int:party_id>/", views.leave_party, name="leave_party"),
    path(
        "parties/<int:party_id>/recommendations/",
        views.party_recommendations,
        name="party_recommendations",
    ),
    path("report/", views.system_report, name="system_report"),
]
