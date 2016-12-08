import logging, inspect

from django.core.management.base import BaseCommand
import json

from nouapp.models import  Quote

def update_quotes( dictio ):
    logger = logging.getLogger(__name__)

    nq = 0
    oq = 0
    for key, value in  dictio.items() :
        if key.startswith( 'record' ):
            author = value['author']
            quote = value['quote'] 
            if ( author == '' or quote == '' ):
                logger.info("File error. Empty register: {}".format( key ) )
                print("File error. Empty register: {}".format( key ) )
            else:                
                try:
                    Quote.objects.get( author=author, text=quote )
                    logger.info( "Quote: <{}> - <{}> already exists".format( author[:30].encode("utf-8",'ignore'), quote[:30].encode("utf-8",'ignore') ) )
                    oq += 1
                except Quote.DoesNotExist:
                    # insert record
                    # To create and save an object in a single step, use the create() method.
                    Quote.objects.create( author = author, text = quote )
                    logger.info( "Inserting quote:  <{}> - <{}>".format( author[:30].encode("utf-8",'ignore'), quote[:30].encode("utf-8",'ignore') ) )
                    nq += 1
                    
               
        elif isinstance(value, dict):
            [nq, oq] = [x + y for x, y in zip([nq,oq], update_quotes(value))] 
            print( "New quotes = {}, Old quotes = {}".format( nq, oq ) )
            
    return [ nq, oq ]
            
                    


class Command(BaseCommand):
    help = 'Populate Quote table from a file'

    def add_arguments(self, parser):
        parser.add_argument('quotefile', metavar='Quote file', type=str )

    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        logger.info("------------------------------------------------------------" )
        logger.info("Starting {}".format( inspect.stack()[0][3]) )

        # open QuoteFile
        logger.info("Quote File = {}".format( options['quotefile'] ) )
        with open(options['quotefile'], 'r') as infile:
            jsonquotes = json.load( infile )
            
        # json format
        # { page_0000 : { record_00000: { 'quote' : 'xxx' , 'author' : 'xxxx' },
        #                 record_00001: { 'quote' : 'xxx' , 'author' : 'xxxx' },
        #                },
        #   page_0001 : { record_00000: { 'quote' : 'xxx' , 'author' : 'xxxx' },
        #                 record_00001: { 'quote' : 'xxx' , 'author' : 'xxxx' },
        #                },
        # }             
        # print(json.dumps(jsonquotes, sort_keys=True, indent=4))
        
        [nq, oq] = update_quotes( jsonquotes )
                    
        logger.info( "{} records inserted in Quote table".format( nq ) )
        logger.info( "{} records existed already in Quote table".format( oq ) )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated the database QUOTE (new={}, old={})'.format(nq,oq) ))
