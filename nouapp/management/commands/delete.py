import logging, inspect

from django.core.management.base import BaseCommand, CommandError

from nouapp.models import  Quote, Nou, Person, LogActivity
from nouapp import  misc



class Command(BaseCommand):
    help = 'Populate Quote table from a file'

    def add_arguments(self, parser):
        parser.add_argument('--quote', '-q', action='store_true',  dest='quote', default=False, required=False , help='Delete Quote table')
        parser.add_argument('--person', '-p', action='store_true',  dest='person', default=False, required=False , help='Delete Person table')
        parser.add_argument('--log', '-l', action='store_true',  dest='log', default=False, required=False , help='Delete LogActivity table')
        parser.add_argument('--all', '-a', action='store_true',  dest='all', default=False, required=False , help='Delete ALL tables')
        parser.add_argument('--nou', '-n', action='store_true',  dest='nou', default=False, required=False , help='Delete Nou table')

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        logger.info("------------------------------------------------------------" )
        logger.info("Starting {}".format( inspect.stack()[0][3]) )

        if options['quote']:
            if misc.query_yes_no( 'All records of Quote table will be deleted','no' ):
                print( "deleting records..." )
            else:
                print('no action taken')
        
        self.stdout.write(self.style.SUCCESS('Successfully deleted '))
