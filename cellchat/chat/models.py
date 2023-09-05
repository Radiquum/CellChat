from django.db import models

# Create your models here.

class Room(models.Model):
    id = models.CharField(max_length=32, primary_key=True)
    password = models.CharField(max_length=32, blank=True, default='')
    
    def __str__(self):
        return f"{self.id}"

class Message(models.Model):
    sender = models.CharField(max_length=64)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    message_text = models.CharField(max_length=320)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return f"{self.sender}@{self.room.id} - {self.message_text}"
