from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Movie(models.Model):
    title = models.CharField(max_length=150)
    year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(2200)],
        default=timezone.datetime.now().year,
    )
    rating = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        validators=[MinValueValidator(0.000), MaxValueValidator(5.000)],
        default=0.000,
    )
    nratings = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.year})"


class PersonalRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "movie"]


class MovieParty(models.Model):
    members = models.ManyToManyField(User, related_name="movie_parties")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Movie Party {self.id}"
