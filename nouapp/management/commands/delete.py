import logging, inspect
from django.utils import timezone

from django.core.management.base import BaseCommand

from nouapp.models import  Quote, Nou, Person, LogActivity
from nouapp import  misc


def delete( table, query, message=None ):
    
    num = query.count()
    
    if not message:
        message = 'ALL <{}> records of <{}> table will be deleted'.format( num, table )
        
    if misc.query_yes_no( message,'no' ):
        print( "Deleting records..." )
        query.delete()
    else:
        print('No action taken')

class Command(BaseCommand):
    help = 'Delete tables'

    def add_arguments(self, parser):
        parser.add_argument('--quote', '-q', action='store_true',  dest='quote', default=False, required=False , help='Delete Quote table')
        parser.add_argument('--person', '-p', action='store_true',  dest='person', default=False, required=False , help='Delete Person table')
        parser.add_argument('--log', '-l', action='store_true',  dest='log', default=False, required=False , help='Delete LogActivity table')
        parser.add_argument('--all', action='store_true',  dest='all', default=False, required=False , help='Delete ALL tables')
        parser.add_argument('--nou', '-n', action='store_true',  dest='nou', default=False, required=False , help='Delete Nou table')
        parser.add_argument('--purgenou', '-u', action='store_true',  dest='purgenou', default=False, required=False , 
                            help='Delete all Nou records before today')

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        logger.info("------------------------------------------------------------" )
        logger.info("Starting {}".format( inspect.stack()[0][3]) )

        if options['quote'] or options['all']:
            delete ( 'Quote', Quote.objects.all() )
        if options['person'] or options['all']:
            delete ( 'Person', Person.objects.all() )
        if options['log'] or options['all']:
            delete ( 'LogActivity', LogActivity.objects.all() )
        if options['nou'] or options['all']:
            delete ( 'Nou', Nou.objects.all() )
        elif options['purgenou']:
            query = Nou.objects.filter( date__lt=timezone.now().date() )
            delete ( 'Nou', query, 'All Nou records before today will be deleted ({} records)'.format(query.count()) )
        
        self.stdout.write(self.style.SUCCESS('Successfully done '))
