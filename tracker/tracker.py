from __future__ import print_function
from cgi import parse_qsl
from wsgiref.simple_server import make_server
from urllib import unquote
from base64 import b16encode
import backend


#TODO Remove this
import sys
sys.dont_write_bytecode = True


def announce(peer_ip, query):
    error = False
    ret = "200 OK"
    head = [('Content-Type', 'text/plain')]
    msg=""

    query_copy = query.copy()
    query_copy['ip'] = peer_ip
    # Checking that the info_hash is there and valid-ish
    if 'info_hash' in query:
        if len(unquote(query['info_hash'])) == 20:
            query_copy['info_hash'] = b16encode(query['info_hash'])
        else:
            error = True
            ret = "150 Invalid infohash"
            msg = "infohash is not 20 bytes long."
    else:
        error = True
        ret = "101 Missing infohash"
        msg = ""

    # Checking that the peer_id is there and valid-ish
    if 'peer_id' in query:
        if len(query['peer_id']) == 20:
            query_copy['peer_id'] = b16encode(query['peer_id'])
        else:
            error = True
            ret = "151 Invalid peerid"
            msg = "peerid is not 20 bytes long."
    else:
        error = True
        ret = "102 Missing peerid"
        msg = ""

    # Checking that the port is there and valid-ish
    if not 'port' in query:
        error = True
        ret = "103 Missing port"
        msg = ""

    if not error:
        error, msg = backend.announce(query_copy)
        print(msg)

    return (ret, head, msg)

def scrape(peer_ip, query):
    error = False
    ret = "200 OK"
    head = [('Content-Type', 'text/plain')]
    msg = "Scrape is not implemented"
    query_copy = query.copy()
    query_copy['ip'] = peer_ip
    if not error:
        error, msg = backend.scrape(query_copy)
        print(msg)

    return (ret, head, msg)

def peer_ip(environ):
    ip_addr = environ['REMOTE_ADDR']
    if "HTTP_X_FORWARDED_FOR" in environ:
        ip_addr = environ['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
    return ip_addr

    
def application(environ, start_response):
    """Main WSGI entry point"""
    ret = "200 OK"
    head = [('Content-Type', 'text/plain')]
    msg = "Default message"

    if environ['REQUEST_METHOD'] == 'GET':
        query = unquote(environ['QUERY_STRING'])
        ip_addr = peer_ip(environ)

        if environ['PATH_INFO'] == "/announce":
            ret, head, msg = announce(ip_addr, dict(parse_qsl(query)))
        elif environ['PATH_INFO'] == "/scrape":
            ret, head, msg = scrape(ip_addr, dict(parse_qsl(query)))

    else:
        ret = '100 Invalid request type'
        head = [('Content-Type', 'text/plain')]
        msg = 'The request was not a GET\n'

    start_response(ret, head)
    yield msg

if __name__=='__main__':
    httpd = make_server('', 8000, application)
    print("Serving on port 8000...")
    httpd.serve_forever()

