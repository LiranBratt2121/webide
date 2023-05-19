from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, default='Cool project')
    description = models.TextField(blank=True)
    content = models.TextField(blank=True, default='''
def main():
    # Your code goes here
    print("Hello, world!")

if __name__ == "__main__":
    main()
''')
    def __str__(self):
        return self.name
