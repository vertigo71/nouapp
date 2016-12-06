import logging, inspect
from urllib.request import urlopen
from html.parser import HTMLParser
import json, os, sys

from django.core.management.base import BaseCommand, CommandError
from bs4 import BeautifulSoup

from nouapp.models import  Quote
from nouapp import  misc

# URL where the quotes are
BEST_QUOTES= 'http://www.goodreads.com/quotes'
SPIRIT_QUOTES = BEST_QUOTES + "/tag/spirituality"

# actual quotes to process 
ACTUAL_QUOTES = BEST_QUOTES
SUFFIX = "?page="
QUOTE_MIN = 2
QUOTE_MAX = 100
   

# join children strings
# WHILE children.tag.name in taglist 
# current tag.name is not evaluated with taglist
# don't add strings in exclude
def join_children_str( tag, taglist=['br'] , exclude=['―']):
    logger = logging.getLogger(__name__)
    
    str = ''
    
    if tag.name:
        logger.info( "TagName= {} - Children = {}".format( tag.name, len (tag.contents) ) )
        # navigate thorough all children
        for num, t in enumerate( tag.children ):
            stop = True
            if not t.name:
                # it's a string, we can continue
                stop = False
            elif taglist and t.name in taglist:
                # it's not a string but it's in taglist
                 stop = False
            
            if stop:
                logger.info( "Children number {} - Stop!!!".format( num ) )
                break
            else:
                logger.info( "Children number {} - Continue!!!".format( num ) )
                str = '\n'.join(filter(None, [str,join_children_str( t, taglist, exclude ) ]))
    else:
        # no children
        logger.info( "String = {}".format( tag.string.encode("utf-8",'ignore') ) )
        
        # take all spaces out        
        str = " ".join(tag.string.split())
        if str in exclude:
            str = ''
            
    return str
       

 
def url2json( url ):
    logger = logging.getLogger(__name__)
    logger.info("Starting {}".format( inspect.stack()[0][3]) )
  
    f = urlopen( url ) 
    html = f.read()
    f.close()  
    
    soup = BeautifulSoup( html , 'html.parser').prettify()
    soup = BeautifulSoup( soup , 'html.parser')
    
    jsontag = {}
    tags = soup.find_all( 'div',  class_="quoteText" )
    for num, tagdiv in enumerate( tags ):
        quote = join_children_str( tagdiv )
        logger.info( "quote = {}".format(quote.encode("utf-8",'ignore') ) )
        taga = tagdiv.find_all( 'a',  class_="authorOrTitle" )
        author = ''
        for tag in taga:
            author = '\n'.join(filter(None, [ author,join_children_str( tag ) ]))
        logger.info( "author = {}".format(author.encode("utf-8",'ignore') ) )
        jsontag [ 'record_{:06d}'.format(num) ] = { 'quote' : quote , 'author': author }
        # { record_000000 : { 
        #                 'quote' : 'xxx',
        #                 'author' : 'xxx'
        #                 }
        # }
    return jsontag
    
class Command(BaseCommand):
    help = 'Get quotes from internet and save them in a file'

    def add_arguments(self, parser):
        parser.add_argument('jsonfile', metavar='JSON File', type=str )
        
    def handle(self, *args, **options):
        logger = logging.getLogger(__name__)
        logger.info("------------------------------------------------------------" )
        logger.info("Starting {}".format( inspect.stack()[0][3]) )
        
        # check output file
        jsonfile = options['jsonfile']
        while True:
            if os.path.isfile( jsonfile ):
                if not misc.query_yes_no( 'File {} already exists. Overwrite?'.format( options['jsonfile'] ), 'no' ):
                    while True:
                        sys.stdout.write('Type filename: ')
                        jsonfile = input()
                        break
                else:
                    break
            else:
                break
        
        # json format
        # { page_0000 : { record_00000: { 'quote' : 'xxx' , 'author' : 'xxxx' },
        #                 record_00001: { 'quote' : 'xxx' , 'author' : 'xxxx' },
        #                },
        #   page_0001 : { record_00000: { 'quote' : 'xxx' , 'author' : 'xxxx' },
        #                 record_00001: { 'quote' : 'xxx' , 'author' : 'xxxx' },
        #                },
        # }             
        jsonurl = {'1':'2'}
        jsonurl[ 'page_{:06d}'.format(1) ] = url2json( ACTUAL_QUOTES )
        for u in range( QUOTE_MIN,QUOTE_MAX+1 ):
            print ( 'Iteration {}/{}'.format( u, QUOTE_MAX ) )
            jsonurl[ 'page_{:06d}'.format(u) ] =  url2json( ACTUAL_QUOTES + SUFFIX + str( u ) )
        
        # save the json to a file
        # print(json.dumps(jsonurl, sort_keys=True, indent=4))
        with open(jsonfile, 'w') as outfile:
            json.dump(jsonurl, outfile)          
                
        self.stdout.write(self.style.SUCCESS('File successfully written' ))
