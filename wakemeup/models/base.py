from django.db import models

class MyModel(models.Model):

    class Meta:
        managed = False
        abstract = True
    
    def save(self, *args, **kwargs):
        return type(self).objects.save(self)
    
    def delete(self):
        return type(self).objects.delete(self)