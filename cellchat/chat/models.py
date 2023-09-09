from django.db import models
import uuid

# Create your models here.

class Room(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.CharField(max_length=64)
    password = models.CharField(max_length=64, blank=True, default='')
    
    def __str__(self):
        return f"{self.name} - {self.id}"

class Message(models.Model):
    sender = models.CharField(max_length=64)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    message_text = models.CharField(max_length=640)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return f"{self.sender}@{self.room.name} - {self.message_text}"

