from django.contrib import admin
from .models import Variation, ReviewRating, Movie, Actor, CastCredit




class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'budget', 'release_date', 'popularity', 'vote_average')
    list_filter = ('release_date',)
    search_fields = ('title',)
    date_hierarchy = 'release_date'
    prepopulated_fields = {'homepage': ('title',)}

class CastCreditAdmin(admin.ModelAdmin):
    list_display = ('movie_title', 'actor_name','character_name','gender')  # Sử dụng các phương thức đã định nghĩa

    def movie_title(self, obj):
        return obj.movie.title
    movie_title.short_description = 'Movie Title'

    def actor_name(self, obj):
        return obj.actor.name
    actor_name.short_description = 'Actor Name'
    
admin.site.register(ReviewRating)
admin.site.register(Movie, MovieAdmin)
admin.site.register(Actor)
admin.site.register(CastCredit, CastCreditAdmin)
