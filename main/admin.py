from django.contrib import admin
from .models import Movie, PersonalRating, MovieParty
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "rating", "nratings")
    list_filter = ("year", "rating")
    search_fields = ("title",)
    ordering = ("title", "year")
    list_per_page = 20


@admin.register(PersonalRating)
class PersonalRatingAdmin(admin.ModelAdmin):
    list_display = ("user", "movie", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "movie__title")
    ordering = ("-created_at",)
    list_per_page = 20
    raw_id_fields = ("user", "movie")


@admin.register(MovieParty)
class MoviePartyAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "get_member_count", "get_members_list")
    list_filter = ("created_at",)
    filter_horizontal = ("members",)
    ordering = ("-created_at",)
    list_per_page = 20

    def get_member_count(self, obj):
        return obj.members.count()

    get_member_count.short_description = "Number of Members"

    def get_members_list(self, obj):
        return ", ".join([user.username for user in obj.members.all()])

    get_members_list.short_description = "Members"


# Customize the existing User admin
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "date_joined",
        "last_login",
        "is_staff",
        "get_rating_count",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "date_joined")
    search_fields = ("username", "email")
    ordering = ("username",)

    def get_rating_count(self, obj):
        return obj.personalrating_set.count()

    get_rating_count.short_description = "Ratings Count"


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
