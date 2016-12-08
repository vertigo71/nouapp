from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.conf import settings

from oauth2client.contrib.django_util import decorators
from apiclient.discovery import build

import datetime,logging,inspect

from .forms import SelectorForm
from .models import Nou, LogActivity, Person
from . import vw_gcal, misc

DATEFORMAT = '%Y%m%d'

# Select Person, datafrom and datato
# If post, obtain the data and redirect to selectionlist
# if get, show the form with intial data
@login_required
def selector(request, person_id=None, datefrom=None, dateto=None):
    logger = logging.getLogger(__name__)
    misc.logXuser( logger.info, "Starting {}".format( inspect.stack()[0][3]) , person_id, 0 )

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SelectorForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            n = form.cleaned_data['name'].pk 
            d1 = form.cleaned_data['datefrom'].strftime(DATEFORMAT)            
            d2 = form.cleaned_data['dateto'].strftime(DATEFORMAT)
            misc.logXuser( logger.info, 'Name = <{}>, DateFrom = <{}>, DateTo = <{}>'.format( n, d1, d2) , person_id, 2)
            
            # redirect to a new URL:
            # Always return an HttpResponseRedirect after successfully dealing
            # with POST data. This prevents data from being posted twice if a
            # user hits the Back button.
            # All data is correct. Proceed to show the list of Persons with the date and Nou Number
            return HttpResponseRedirect(reverse('nouapp:selectionlist', args=(n,d1,d2) ))

    elif person_id and datefrom and dateto:
        # if a GET (or any other method) we'll create a form 
        # to pass the initial value to the form we need the date in this format '%Y-%m-%d'
        datefrom = datetime.datetime.strptime(datefrom, DATEFORMAT).date().strftime('%Y-%m-%d')
        dateto = datetime.datetime.strptime(dateto, DATEFORMAT).date().strftime('%Y-%m-%d')
        data = { 'name' : person_id,
                'datefrom' : datefrom,
                'dateto' : dateto
                }
        misc.logXuser( logger.info, 'Data =' , person_id, 2)
        misc.logdict(data, logger, person_id, depth=4)
        form = SelectorForm( initial=data )
    else:
        # if a GET (or any other method) we'll create a blank form
        misc.logXuser( logger.info, 'Blank Form' , person_id, 2)
        form = SelectorForm( )
     
    # show a selection page with fields to choose the name and dates
    return render(request, 'nouapp/selector.html', {'form': form})

# show a list of persons, and nou nums according to the selection
@login_required
def selectionlist(request, person_id, datefrom, dateto ):
    logger = logging.getLogger(__name__)
    misc.logXuser( logger.info, "Starting {}".format( inspect.stack()[0][3]) , person_id, 0 )

    data = { 'person_id' : person_id,
            'datefrom' : datefrom,
            'dateto' : dateto
            }
    datefrom = datetime.datetime.strptime(datefrom, DATEFORMAT).date()
    dateto = datetime.datetime.strptime(dateto, DATEFORMAT).date()
    
    misc.logXuser( logger.info, 'Name = <{}>, DateFrom = <{}>, DateTo = <{}>'.format( person_id, datefrom, dateto) , person_id, 2)
    
    try:
        query = Nou.objects.filter(person = person_id, date__gte=datefrom, date__lte=dateto )
        misc.logXuser( logger.info, 'Query: number of elements = <{}>'.format( query.count() ) , person_id, 2  )
    except Nou.DoesNotExist:
        raise Http404("Database malfunction")
    
    # list of Persons with the date and Nou Number 
    return render(request, 'nouapp/selectionlist.html', {'query': query, 'data':data })
    
# update the google calendar for a user with the selection made in selector view
@decorators.oauth_required   
@login_required
def updatecal(request, person_id, datefrom, dateto):
    logger = logging.getLogger(__name__)
    misc.logXuser( logger.info, "Starting {}".format( inspect.stack()[0][3]) , person_id, 0 )

    datefrom = datetime.datetime.strptime(datefrom, DATEFORMAT).date()
    dateto = datetime.datetime.strptime(dateto, DATEFORMAT).date()

    misc.logXuser( logger.info, "Email = {}".format( request.oauth.credentials.id_token['email'] ) , person_id, 2 )

    try:
        query = Nou.objects.filter(person = person_id, date__gte=datefrom, date__lte=dateto )
        misc.logXuser( logger.info, 'Query: number of elements = <{}>'.format( query.count() ) , person_id, 2 )
    except Nou.DoesNotExist:
        raise Http404("Database malfunction")
    
    # get service    
    service = build(serviceName='calendar', version='v3', http=request.oauth.http )
    misc.logXuser( logger.info, 'Service = <{}>'.format( service ) , person_id, 2 )
    
    # new LogActivity record
    # To create and save an object in a single step, use the create() method.
    lact = LogActivity( person = Person.objects.get( pk=person_id) ,
                         calendar_created = False ,  
                         num_events_inserted = 0,
                         num_events_skipped = 0, 
                         date_from = datefrom,
                         date_to = dateto,
                         strerror = ''
                        )
    
    # get Google Calendar
    try:
        calendar = {
            'summary':  settings.CAL_NAME,
            'description': settings.CAL_DESCRIPTION,
            'location': settings.CAL_LOCATION,
            'timeZone': settings.CAL_TIMEZONE,
        }
        goocal, c = vw_gcal.getgcal(service, calendar, person_id, create=True)
        lact.calendar_created = c
    except:
        lact.strerror = 'vw_gcal.getgcal'
        lact.save()
        raise
    
    # copy query to Google Calendar
    try:
        event = {
                 'summary': '',
                 'description': '',
                 'location': settings.CAL_LOCATION,
                 'start': {
                           'date': '',
                           'timeZone': settings.CAL_TIMEZONE,
                           },
                 'end': {
                        'date': '',
                        'timeZone': settings.CAL_TIMEZONE,
                        }
                }
        i,s= vw_gcal.nou2cal(service,goocal, person_id, query, event)
        lact.num_events_inserted = i
        lact.num_events_skipped = s
    except:
        lact.strerror = 'vw_gcal.nou2cal'
        lact.save()
        raise

    lact.save()
    
    # response
    return render(request, 'nouapp/summary.html', {'item': lact })
    
 
