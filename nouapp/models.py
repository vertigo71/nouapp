from django.db import models
from django.forms import ModelForm

class Person(models.Model):
    name = models.CharField(max_length=128)
    
    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):              # __unicode__ on Python 2
        return self.name

class Quote(models.Model):
    author = models.CharField(max_length=128)
    text = models.TextField()

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):              # __unicode__ on Python 2
        return self.author

class Nou(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    num = models.IntegerField()
    date = models.DateField()

    added = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):              # __unicode__ on Python 2
       return self.person.name + ' : ' +  str(self.date) + ' : ' + str(self.num)

