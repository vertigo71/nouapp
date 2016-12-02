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
def getgcal( service , calendar_in, create = True):
    
    logger = logging.getLogger(__name__)
    logger.info("Starting {}".format( inspect.stack()[0][3]) )

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
                    logger.info("  Calendar {} already exists".format( calendar_in["summary"]) )
                    break
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
    except:
        logger.error("Error accessing the list of calendars")
        raise
    
    # create NOU calendar if it doesn't exists
    try:
        if not calendar and create:
            logger.info("  {} calendar not found. Creating the calendar".format( calendar_in["summary"]) )
            calendar = service.calendars().insert(body=calendar_in).execute()
            cal_created = True
        
        logger.info("  Calendar {} =".format( calendar["summary"]) )
        misc.logdict(calendar, logger, depth=4)

    except:
        logger.error("Error creating {} calendar".format( calendar_in["summary"]) )
        raise
        
    return calendar, cal_created

    
# get an event from the goocal calendar
# returns the event associated with
# summary, starttime and endtime (timezone = ty)
def getcalevent(service, goocal, summary, starttime, endtime, tz ):

    logger = logging.getLogger(__name__)
    logger.info("Starting {}".format( inspect.stack()[0][3]) )
    
    logger.info("  Event = {}".format( summary) )
    
    # upperbound event starting time in datetime (excluding)
    starttime = datetime.datetime.combine(starttime, datetime.time.max)
    # lowerbound event ending time in datetime (including)
    endtime = datetime.datetime.combine(endtime, datetime.time.min)

    # rfc3339 format
    starttime = misc.datetime2rfc3339(starttime, tz)
    endtime = misc.datetime2rfc3339(endtime, tz)
    logger.info("  Event start,end time = <{},{}>".format( starttime, endtime) )
    
    page_token = None
    event_found = None
    while True:
        events = service.events().list(calendarId=goocal['id'], 
                                        timeMax = starttime,
                                        timeMin = endtime,
                                        pageToken=page_token
                                        ).execute()
        if len( events['items'] ) > 1: 
            logger.warning ( "   Number of filtered events (should be 1) = {}".format( len( events['items'] ) ) )
        for event in events['items']:
            if event['summary'] == summary:
               logger.info("  Event <{}> exists at day <{}>".format( summary, event['start']['date']) )
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
def nou2cal(service,goocal, query, event):

    logger = logging.getLogger(__name__)
    logger.info("Starting {}".format( inspect.stack()[0][3]) )
    
    num_events_inserted = 0
    num_events_skipped = 0
    
    for record in query:
        event['description'] = '\n'.join( ( str(record.quote.author) , str(record.quote.text) ) )
        nou = record.num
        date = record.date
        logger.info("  Uploading NOU = {} for day = {}".format(  nou, date) )
        
        # check if the event already exists
        event_found = getcalevent(service, goocal, str(nou), date, date, event['start']['timeZone'] )

        # insert event if it doesn't exist
        if event_found:
            num_events_skipped += 1
            logger.info("    NOU has already this item")
        else:       
            # add an event to calnou
            event['summary'] = nou
            event['start']['date'] = str(date)
            event['end']['date'] = str(date)
            logger.info("  Event = ")
            misc.logdict(event, logger, depth=4)
            
            ins_event = service.events().insert(calendarId=goocal['id'], body=event).execute()
            num_events_inserted += 1
            logger.info ('    Event created: {}'.format(  str(ins_event.get('htmlLink'))) )
            
    return num_events_inserted, num_events_skipped
