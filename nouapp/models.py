from django.db import models

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
       return ' : '.join( (self.person.name , str(self.date) , str(self.num)) )

class LogActivity(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    calendar_created = models.BooleanField()    # was the calendar created?
    num_events_inserted = models.IntegerField() # number of events that have been inserted in the database
    num_events_skipped = models.IntegerField()  # register the number of events already in the database
    date_from = models.DateField()
    date_to = models.DateField()
    strerror = models.CharField(max_length=128 )

    added = models.DateTimeField(auto_now_add=True)

    def __str__(self):              # __unicode__ on Python 2
        return ' : '.join( (self.person.name, str( self.calendar_created ), 
                            str( self.num_events_inserted ), str( self.num_events_skipped ), 
                            str( self.date_from ), str( self.date_to ) , self.strerror ) )
