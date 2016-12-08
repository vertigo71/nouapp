import logging
import inspect
import datetime

from . import misc

# get google calendar
'''
    if create == True
        if the calendar doesnt exist, it is created
    calendar_in = {
        'summary':  CAL_NAME,
        'description': CAL_DESCRIPTION,
        'location': CAL_LOCATION,
        'timeZone': CAL_TIMEZONE
    }
    returns the calendar
'''
def getgcal( service , calendar_in, person_id, create = True):
    
    logger = logging.getLogger(__name__)
    misc.logXuser( logger.info, "Starting {}".format( inspect.stack()[0][3]) , person_id, 2)

    cal_created = False
    
    # get NOU calendar 
    try:
        page_token = None
        calendar = None
        while True:
            calendar_list = service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                if calendar_list_entry['summary'] == calendar_in["summary"]:
                    calendar = calendar_list_entry
                    misc.logXuser( logger.info, "Calendar {} already exists".format( calendar_in["summary"]) , person_id, 4)
                    break
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
    except:
        misc.logXuser( logger.error, "Error accessing the list of calendars", person_id, 0)
        raise
    
    # create NOU calendar if it doesn't exists
    try:
        if not calendar and create:
            misc.logXuser( logger.info, "{} calendar not found. Creating the calendar".format( calendar_in["summary"]) , person_id, 4)
            calendar = service.calendars().insert(body=calendar_in).execute()
            cal_created = True
        
        misc.logXuser( logger.info, "Calendar {} =".format( calendar["summary"]) , person_id, 4)
        misc.logdict(calendar, logger, person_id, depth=6)

    except:
        misc.logXuser( logger.error, "Error creating {} calendar".format( calendar_in["summary"]) , person_id, 0)
        raise
        
    return calendar, cal_created

    
# get an event from the goocal calendar
# returns the event associated with
# summary, starttime and endtime (timezone = ty)
def getcalevent(service, goocal, person_id, summary, starttime, endtime, tz ):

    logger = logging.getLogger(__name__)
    misc.logXuser( logger.info, "Starting {}".format( inspect.stack()[0][3]) , person_id, 4 )
    
    misc.logXuser( logger.info, "Event = {}".format( summary) , person_id, 6 )
    
    # upperbound event starting time in datetime (excluding)
    starttime = datetime.datetime.combine(starttime, datetime.time.max)
    # lowerbound event ending time in datetime (including)
    endtime = datetime.datetime.combine(endtime, datetime.time.min)

    # rfc3339 format
    starttime = misc.datetime2rfc3339(starttime, tz)
    endtime = misc.datetime2rfc3339(endtime, tz)
    misc.logXuser( logger.info, "Event start,end time = <{},{}>".format( starttime, endtime) , person_id, 6 )
    
    page_token = None
    event_found = None
    while True:
        events = service.events().list(calendarId=goocal['id'], 
                                        timeMax = starttime,
                                        timeMin = endtime,
                                        pageToken=page_token
                                        ).execute()
        if len( events['items'] ) > 1: 
            misc.logXuser( logger.warning ,  "Number of filtered events (should be 1) = {}".format( len( events['items'] ) ) , person_id, 6 )
        for event in events['items']:
            if event['summary'] == summary:
               misc.logXuser( logger.info, "Event <{}> exists at day <{}>".format( summary, event['start']['date']) , person_id, 6 )
               event_found = event
               break
        page_token = events.get('nextPageToken')
        if not page_token:
            break
    return event_found
      
# uploads all nou values to the calendar
'''
        event = {
          'summary': '',
          'description': CAL_DESCRIPTION,
          'location': CAL_LOCATION,
          'start': {
            'date': '',
            'timeZone': CAL_TIMEZONE,
          },
          'end': {
            'date': '',
            'timeZone': CAL_TIMEZONE,
          }
        }
'''
def nou2cal(service,goocal, person_id, query, event):

    logger = logging.getLogger(__name__)
    misc.logXuser( logger.info, "Starting {}".format( inspect.stack()[0][3]) , person_id, 2 )
    
    num_events_inserted = 0
    num_events_skipped = 0
    
    for record in query:
        event['description'] = '\n'.join( ( str(record.quote.author) , str(record.quote.text) ) )
        name = ''.join( n[0].upper()  for n in record.person.name.split() )
        nou = ' - '.join( [ str( record.num ) , name ] )
        date = record.date
        misc.logXuser( logger.info, "Uploading NOU = {} for day = {}".format(  nou, date) , person_id, 4 )
        
        # check if the event already exists
        event_found = getcalevent(service, goocal, person_id, str(nou), date, date, event['start']['timeZone'] )

        # insert event if it doesn't exist
        if event_found:
            num_events_skipped += 1
            misc.logXuser( logger.info, "NOU has already this item", person_id, 6 )
        else:       
            # add an event to calnou
            event['summary'] = nou
            event['start']['date'] = str(date)
            event['end']['date'] = str(date)
            
            ins_event = service.events().insert(calendarId=goocal['id'], body=event).execute()
            num_events_inserted += 1
            misc.logXuser( logger.info , 'Event created: {}'.format(  str(ins_event.get('htmlLink'))) , person_id, 6 )
               
    return num_events_inserted, num_events_skipped
