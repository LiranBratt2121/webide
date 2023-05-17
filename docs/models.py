from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, default='Cool project')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
