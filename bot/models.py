
from django.db import models


class Guilds(models.Model):
    guild_id = models.CharField(max_length=50,unique=True)
    guild_name = models.CharField(max_length=200)
    bot_added_date = models.DateTimeField()

class Boids(models.Model):
    guild = models.ForeignKey(Guilds,on_delete=models.CASCADE)
    username = models.CharField(max_length=50)
    boid = models.CharField(max_length=20)


