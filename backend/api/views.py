from django.shortcuts import render
from django.http import HttpResponse
from oauth2_provider.views import ProtectedResourceView
from rest_framework import generics, mixins, authentication, permissions, status
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from django.conf import settings
from .serializer import UserSerializer, OfferSerializer, AuthTokenSerializer, TransactionSerializer
from .models import User, UserManager, Offer, Transaction
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from google.oauth2 import id_token
from google.auth.transport import requests
from google.auth import environment_vars
from rest_framework import authentication
from itertools import chain


class UserView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        _id = kwargs['pk']
        user = User.objects.get(id=_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        _id = kwargs['pk']
        user = User.objects.get(id=_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
        return Response(serializer.data)


class CreateTokenView(ObtainAuthToken):
    # Create a new auth token for user
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    # Manage the authenticated user
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication, authentication.BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    # def get(self, request, *args, **kwargs):
    #     print(request)
    #
    #     return

    def get_object(self):
        return self.request.user


class OfferView(ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs['pk']
        user = User.objects.get(id=user_id)
        offer_id = request.data["offer_id"]
        try:
            offer = Offer.objects.get(auto_id=offer_id)
            if user.is_admin or user.is_staff or int(user_id) == offer.user.id:
                self.perform_destroy(offer)
                return Response(status=status.HTTP_204_NO_CONTENT, data=f"Deleted {offer.auto_id}")
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Offer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data=f"Object Not found {offer_id}")

    def retrieve(self, request, *args, **kwargs):
        u_id = kwargs['pk']
        try:
            offer_id = request.GET.get("offer_id")
            session = Offer.objects.get(auto_id=offer_id)
            serializer = OfferSerializer(session)
            return Response(serializer.data)
        except KeyError:
            pass
        except Offer.DoesNotExist:
            pass

        try:
            session = Offer.objects.filter(user=u_id)
            serializer = OfferSerializer(session, many=True)
            return Response(serializer.data)
        except Offer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)



class TransactionView(ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def retrieve(self, request, *args, **kwargs):
        t_id = kwargs['pk']
        try:
            transaction_s = Transaction.objects.filter(sender=t_id)
            transaction_r = Transaction.objects.filter(receiver_id=t_id)
            transaction = list(chain(transaction_s, transaction_r))
            serializer = TransactionSerializer(transaction, many=True)
            return Response(serializer.data)
        except Transaction.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        user_id = kwargs['pk']

        try:
            transaction = Transaction.objects.filter(user=user_id)
            self.perform_destroy(transaction)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Transaction.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        print(request.user)


class GoogleView(ViewSet):

    def create(self, request):
        token = {'id_token': request.data.get('id_token')}
        print(token)

        try:
            # Specify the CLIENT_ID of the app that accesses the backend:

            idinfo = id_token.verify_oauth2_token(token['id_token'], requests.Request(),
                                                  settings.GOOGLE_OAUTH_CLIENT_ID)
            print(idinfo)

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            return Response(idinfo)
        except ValueError as err:
            # Invalid token
            print(err)
            content = {'message': 'Invalid token'}
            return Response(content)
