from django.db import models

class MyModel(models.Model):

    class Meta:
        managed = False
        abstract = True
    
    def save(self, *args, **kwargs):
        return type(self).objects.save(self, *args, **kwargs)
    
    def delete(self):
        return type(self).objects.delete(self)

class Object():
    pass