from django.shortcuts import redirect, render, get_object_or_404
from main.models import Movie
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from django.db.models import F, Avg, Q, Count
from decimal import Decimal
from .models import PersonalRating
from django.contrib.auth.models import User
from .models import MovieParty


def index(request):
    return render(request, "index.html")


def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("profile")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile(request):
    return render(request, "profile.html", {"user": request.user})


@login_required
def index(request):
    return redirect("profile")


@login_required
def movies(request):
    rated_movies = (
        Movie.objects.filter(personalrating__user=request.user)
        .prefetch_related("personalrating_set")
        .order_by("title")
    )

    unrated_movies = Movie.objects.exclude(personalrating__user=request.user).order_by(
        "title"
    )

    context = {"rated_movies": rated_movies, "unrated_movies": unrated_movies}
    return render(request, "movies.html", context)


@login_required
def rate_movie(request, movie_id):
    if request.method != "POST":
        return redirect("movies")

    movie = get_object_or_404(Movie, id=movie_id)
    rating = int(request.POST.get("rating", 0))

    if not 1 <= rating <= 5:
        return redirect("movies")

    personal_rating, created = PersonalRating.objects.get_or_create(
        user=request.user, movie=movie, defaults={"rating": rating}
    )

    if created:
        movie.rating = (movie.rating * movie.nratings + Decimal(rating)) / (
            movie.nratings + 1
        )
        movie.nratings = F("nratings") + 1
    else:
        old_rating = personal_rating.rating
        personal_rating.rating = rating
        personal_rating.save()
        movie.rating = (
            movie.rating * movie.nratings + Decimal(rating - old_rating)
        ) / movie.nratings

    movie.save()
    return redirect("movies")


@login_required
def delete_rating(request, movie_id):
    if request.method != "POST":
        return redirect("movies")

    movie = get_object_or_404(Movie, id=movie_id)
    try:
        rating = PersonalRating.objects.get(user=request.user, movie=movie)
        old_rating = rating.rating
        rating.delete()

        if movie.nratings > 1:
            movie.rating = (movie.rating * movie.nratings - Decimal(old_rating)) / (
                movie.nratings - 1
            )
        else:
            movie.rating = Decimal("0.000")
        movie.nratings = F("nratings") - 1
        movie.save()
    except PersonalRating.DoesNotExist:
        pass

    return redirect("movies")


@login_required
def recommendations(request):
    user = request.user

    rated_movies = Movie.objects.filter(personalrating__user=user)

    liked_movies = Movie.objects.filter(
        personalrating__user=user, personalrating__rating__gte=3
    )

    clan_members = (
        User.objects.filter(
            personalrating__movie__in=liked_movies, personalrating__rating__gte=3
        )
        .exclude(id=user.id)
        .distinct()
    )

    if clan_members.exists() and liked_movies.exists():
        clan_recommendations = (
            Movie.objects.exclude(id__in=rated_movies)
            .filter(personalrating__user__in=clan_members)
            .annotate(
                clan_rating=Avg(
                    "personalrating__rating",
                    filter=Q(personalrating__user__in=clan_members),
                )
            )
            .filter(clan_rating__isnull=False)
            .order_by("-clan_rating", "title")[:5]
        )

        using_clan = True
    else:
        clan_recommendations = Movie.objects.exclude(id__in=rated_movies).order_by(
            "-rating", "title"
        )[:5]

        using_clan = False

    context = {
        "recommendations": clan_recommendations,
        "using_clan": using_clan,
        "clan_members": clan_members if using_clan else None,
    }

    return render(request, "recommendations.html", context)


@login_required
def movie_parties(request):
    if request.method == "POST" and "create_party" in request.POST:
        party = MovieParty.objects.create()
        party.members.add(request.user)
        messages.success(request, "New movie party created!")
        return redirect("movie_parties")

    joined_parties = MovieParty.objects.filter(members=request.user)

    other_parties = MovieParty.objects.exclude(members=request.user)

    context = {"joined_parties": joined_parties, "other_parties": other_parties}
    return render(request, "movie_parties.html", context)


@login_required
def join_party(request, party_id):
    if request.method == "POST":
        party = get_object_or_404(MovieParty, id=party_id)
        if party.members.count() >= 10:
            messages.error(request, "This party is already full!")
        else:
            party.members.add(request.user)
            messages.success(request, "Successfully joined the movie party!")
    return redirect("movie_parties")


@login_required
def leave_party(request, party_id):
    if request.method == "POST":
        party = get_object_or_404(MovieParty, id=party_id)
        party.members.remove(request.user)
        messages.success(request, "Successfully left the movie party!")
        if party.members.count() == 0:
            party.delete()
    return redirect("movie_parties")


@login_required
def party_recommendations(request, party_id):
    party = get_object_or_404(MovieParty, id=party_id)
    if request.user not in party.members.all():
        messages.error(request, "You must be a party member to view recommendations.")
        return redirect("movie_parties")

    rated_movies = (
        Movie.objects.filter(personalrating__user__in=party.members.all())
        .annotate(
            party_rating=Avg(
                "personalrating__rating",
                filter=Q(personalrating__user__in=party.members.all()),
            )
        )
        .filter(party_rating__isnull=False)
        .order_by("-party_rating", "title")[:5]
    )

    context = {
        "party": party,
        "members": party.members.order_by("username"),
        "recommendations": rated_movies,
    }

    return render(request, "party_recommendations.html", context)


@login_required
def system_report(request):
    total_movies = Movie.objects.count()
    total_users = User.objects.count()
    total_ratings = PersonalRating.objects.count()
    total_parties = MovieParty.objects.count()

    avg_ratings_per_movie = total_ratings / total_movies if total_movies > 0 else 0
    avg_ratings_per_user = total_ratings / total_users if total_users > 0 else 0
    avg_users_per_party = (
        MovieParty.objects.annotate(member_count=Count("members")).aggregate(
            avg=Avg("member_count")
        )["avg"]
        or 0
    )

    avid_users = User.objects.annotate(rating_count=Count("personalrating")).order_by(
        "-rating_count", "username"
    )[:10]

    popular_users = User.objects.annotate(party_count=Count("movie_parties")).order_by(
        "-party_count", "username"
    )[:10]

    context = {
        "total_movies": total_movies,
        "total_users": total_users,
        "total_ratings": total_ratings,
        "total_parties": total_parties,
        "avg_ratings_per_movie": round(avg_ratings_per_movie, 2),
        "avg_ratings_per_user": round(avg_ratings_per_user, 2),
        "avg_users_per_party": round(avg_users_per_party, 2),
        "avid_users": avid_users,
        "popular_users": popular_users,
    }

    return render(request, "system_report.html", context)
