
from django.urls import reverse
from category.models import Category
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
    
    
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    budget = models.IntegerField(null=True, blank=True)
    overview = models.TextField()
    popularity = models.FloatField()
    price = models.FloatField(default=0)
    vote_average = models.FloatField()
    vote_count = models.IntegerField()
    release_date = models.DateTimeField()
    image_urls = models.URLField(max_length=200, blank=True)
    genres = models.ManyToManyField(Category)  # Assuming Category model exists and is properly defined
    slug = models.SlugField(max_length=200, unique=True, default="n/a")

    homepage = models.URLField(max_length=200, blank=True)
    original_language = models.CharField(max_length=2, blank=True)
    original_title = models.CharField(max_length=200, blank=True)
    revenue = models.IntegerField(null=True, blank=True)
    runtime = models.FloatField(null=True, blank=True)
    status_film = models.CharField(max_length=200, blank=True)
    tagline = models.CharField(max_length=200, blank=True)

    def get_url(self):
        return reverse('movie_detail', args=[str(self.id)])
    
    def __str__(self):
        return self.title

class Actor(models.Model):
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(max_length=200, unique=True, default="n/a")
    name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=30, default="N/A1", blank=True)
    GENDER_CHOICES = (
        (0, 'Not specified'),
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Other'),
    )
    
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)

    def __str__(self):
        return self.name


class CastCredit(models.Model):
    # id = models.AutoField(primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)   # Khi xóa movie thì CastCredit bị xóa
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE, default=1)   # Khi xóa actor thì CastCredit bị xóa
    character_name = models.CharField(max_length=200)
    
    GENDER_CHOICES = (
        (0, 'Not specified'),
        (1, 'Male'),
        (2, 'Female'),
        (3, 'Other'),
    )
    
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)
    order = models.IntegerField()

    def __str__(self):
        return f"{self.character_name} in {self.movie.title} played by {self.actor.name}"


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)

class Variation(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, default=1)
    slug = models.SlugField(max_length=200, unique=True, default="n/a")
    variation_category = models.CharField(max_length=100, choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class ReviewRating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

class ReviewMovieRating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)