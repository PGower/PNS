from endpoint.models import Mapping, Fullname
from django.shortcuts import render, get_object_or_404


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework import viewsets
from endpoint.serializers import MappingSerializer, FullnameSerializer

from haystack.query import SearchQuerySet

import logging

logger = logging.getLogger(__name__)


# API Views
class MappingAction(APIView):
    '''
    Generic API endpoint for the login/update/logout actions.
    '''
    def post(self, request, format=None):
        try:
            action = request.data.get('action')
            username = request.data.get('username')
        except KeyError as e:
            raise APIException('An action and username are required')

        # Update the Fullname mapping
        Fullname.objects.update_or_create(username=username, defaults={
                                          'username': username,
                                          'fullname': request.data.get('fullname', '')
                                          })
        logger.debug(request.data.get('fullname'))

        # Expire any existing records for this user
        Mapping.objects.filter(username=username).filter(expired=False).update(expired=True)
        new_mapping_serializer = MappingSerializer(data=request.data)
        if new_mapping_serializer.is_valid():
            if action == 'logout':
                r = new_mapping_serializer.save(expired=True)
            else:
                new_mapping_serializer.save()
            return Response('success')
        else:
            return Response(new_mapping_serializer.errors)


class InfoForGeneric(APIView):
    '''Base class for the following 2'''
    def query(self, term, expired):
        raise NotImplemented

    def get(self, request):
        errors = []
        response = {}
        term = request.query_params.get('term')
        try:
            current = self.query(term, False).get()
        except Mapping.MultipleObjectsReturned:
            current = self.query(term, False).order_by('created')[0]
            errors.append('More then one address mapping was returned as the current mapping. The latest one is being used.')
        except Mapping.DoesNotExist:
            current = None
            errors.append('There is currently no active mapping for {}.'.format(term))
        finally:
            if current is not None:
                serialized_current = MappingSerializer(current)
                response['current'] = serialized_current.data
            else:
                response['current'] = None

        history = self.query(term, True).order_by('created')
        if len(history) > 0:
            serialized_history = MappingSerializer(history, many=True)
            response['history'] = serialized_history.data
        else:
            errors.append('There does not appear to be any history for {}'.format(term))
            response['history'] = None
        response['errors'] = errors
        return Response(response)


class InfoForUser(InfoForGeneric):
    '''
    Return information about the username.
    '''
    def query(self, term, expired):
        return Mapping.objects.filter(username=term).filter(expired=expired)


class InfoForAddress(InfoForGeneric):
    '''
    Return information about an IP address.
    '''
    def query(self, term, expired):
        return Mapping.objects.filter(ip_address=term).filter(expired=expired)


class NameSearch(APIView):
    '''
    Given part of a name perform a full text search and find the username
    '''
    def get(self, request):
        # import pdb;pdb.set_trace()
        q = request.query_params.get('q')
        query = SearchQuerySet().autocomplete(text=q)
        results = query.load_all()
        results = FullnameSerializer(results, many=True)
        response = {'results': results.data}
        return Response(response)


class RealtimeUpdates(APIView):
    '''
    Return all new mappings since the last call
    '''
    def get(self, request, last_id=None):
        if last_id is None:
            results = Mapping.objects.order_by('-created')[:20]
        else:
            results = Mapping.objects.filter(pk__gt=last_id)
        if results.count() > 0:
            last_id = results[0].pk
        results = MappingSerializer(results, many=True)
        response = {'results': results.data, 'last_id': last_id}
        return Response(response)


# Actual Pages
def dashboard_page(request):
    return render(request, 'index.html.j2', {})
