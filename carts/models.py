from django.contrib.auth.models import User
from django.db import models

from store.models import Movie


class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, default=1)  # Ensure there is a Movie with ID 1
    # variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.quantity * self.movie.price

    def __unicode__(self):
        return self.movie