# -*- coding: utf-8 -*-
from __future__ import print_function

import sys
import os
import time

try:
    from subprocess import getoutput
except ImportError:
    from commands import getoutput

from dnslib import RR, QTYPE, RCODE, parse_time, A
from dnslib.label import DNSLabel
from dnslib.server import DNSServer, DNSHandler, BaseResolver, DNSLogger

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
DJANGO_PROJECT_PATH = os.path.join(BASE_PATH, 'pns_web/')

sys.path.insert(0, DJANGO_PROJECT_PATH)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'pns_web.settings')
import django
django.setup()
from endpoint.models import Mapping


ORIGIN = 'u.stmonicas.qld.edu.au'  # Origin domain label
TTL = '60s'  # Response TTL
PORT = 53
LISTEN = ''
LISTEN_UDP = True
UDPLEN = 0  # Max UDP packet length
LISTEN_TCP = True
LOG = "request,reply,truncated,error"
LOG_HOOKS = False  # "Log hooks to enable (default: +request,+reply,+truncated,+error,-recv,-send,-data)"
LOG_PREFIX = False  # Log prefix (timestamp/handler/resolver)


class PNSResolver(BaseResolver):
    """

    """
    def __init__(self, origin, ttl):
        self.origin = DNSLabel(origin)
        self.ttl = parse_time(ttl)

    def resolve(self, request, handler):
        reply = request.reply()
        qname = request.q.qname
        if qname.matchSuffix(ORIGIN):
            username = str(qname).split('.')[0]
            try:
                r = Mapping.objects.filter(username=username).filter(expired=False).get()
            except Mapping.DoesNotExist:
                reply.header.rcode = RCODE.NXDOMAIN
            except Mapping.MultipleObjectsReturned:
                # Special case if multiple records are returned, use the latest one
                r = Mapping.objects.filter(username=username).filter(expired=False).order_by('created')[0]
                reply.add_answer(RR(qname, QTYPE.A, ttl=self.ttl, rdata=A(r.ip_address)))
            else:
                reply.add_answer(RR(qname, QTYPE.A, ttl=self.ttl, rdata=A(r.ip_address)))
        else:
            reply.header.rcode = RCODE.NXDOMAIN
        return reply

if __name__ == '__main__':
    resolver = PNSResolver(ORIGIN, TTL)
    logger = DNSLogger(LOG, LOG_PREFIX)

    print("Starting Django Resolver (%s:%d) [%s]" % (LISTEN or "*", PORT, "UDP/TCP" if LISTEN_TCP else "UDP"))

    # if args.udplen:
    #     DNSHandler.udplen = args.udplen

    if LISTEN_UDP:
        udp_server = DNSServer(resolver,
                               port=PORT,
                               address=LISTEN,
                               logger=logger)
        udp_server.start_thread()

    if LISTEN_TCP:
        tcp_server = DNSServer(resolver,
                               port=PORT,
                               address=LISTEN,
                               tcp=True,
                               logger=logger)
        tcp_server.start_thread()

    while udp_server.isAlive():
        time.sleep(1)
