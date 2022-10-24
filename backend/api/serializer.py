import random
import string

import django.dispatch.dispatcher
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers, status
from .models import UserManager, User, Offer, Transaction
from .auth_backend import PasswordLessAuthBackend
from rest_framework.response import Response


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,
                                     required=False,
                                     style={'input_type': 'password', 'placeholder': 'Password'})
    is_oauth = serializers.BooleanField(required=True)
    province = serializers.CharField(max_length=255, required=False)
    city = serializers.CharField(max_length=255, required=False)
    phone = serializers.CharField(max_length=255, required=False)
    fullname = serializers.CharField(max_length=300, required=False)
    admin = serializers.BooleanField(required=False)
    staff = serializers.BooleanField(required=False)
    iban_id = serializers.CharField(max_length=255, required=True)
    credit_id = serializers.CharField(max_length=255, required=True)
    id_card = serializers.CharField(max_length=255, required=True)
    ref_id = serializers.CharField(max_length=255, required=False)
    ref_used = serializers.BooleanField(required=False)
    ref_used_id = serializers.CharField(max_length=255, required=False)
    money_balance = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'id', 'is_oauth', 'province', 'city', 'phone', 'fullname', 'admin', 'staff',
                  'iban_id', 'credit_id', 'id_card', 'ref_id', 'ref_used',
                  'money_balance', 'ref_used_id', 'points', 'sold_coins']

    def create(self, validated_data):
        is_oauth = validated_data['is_oauth']

        email = validated_data['email']
        # province = validated_data['province']
        # city = validated_data['city']
        phone = validated_data['phone']
        fullname = validated_data['fullname']
        id_card = validated_data["id_card"]
        iban = validated_data["iban_id"]
        ccn = validated_data["credit_id"]
        try:
            referral = validated_data["ref_used_id"]
            if User.is_referral_valid(referral):

                ref_used = True
                # Points giving handled in models.py
                ref_id = f"ref-u{email}" \
                         f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
                if is_oauth:
                    user = User.objects.create(email=email, is_oauth=is_oauth, id_card=id_card, credit_id=ccn,
                                               iban_id=iban,
                                               fullname=fullname, phone=phone, ref_used=ref_used, ref_used_id=referral,
                                               ref_id=ref_id)
                    user.ref_id = f"ref-u{user.id}" \
                                  f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
                    user.save()
                    referred_user = User.objects.get(ref_id=referral)
                    referred_user.points += 10
                    referred_user.save()
                    return user
                else:
                    user = User.objects.create(email=email, id_card=id_card, credit_id=ccn, iban_id=iban,
                                               fullname=fullname, phone=phone, ref_used=ref_used, ref_used_id=referral,
                                               ref_id=ref_id)
                    user.ref_id = f"ref-u{user.id}" \
                                  f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
                    password = validated_data['password']
                    user.set_password(password)
                    user.save()
                    referred_user = User.objects.get(ref_id=referral)
                    referred_user.points += 10
                    referred_user.save()
                    return user
            else:
                ref_used = False
                ref_id = f"ref-u{email}" \
                         f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
                if is_oauth:
                    user = User.objects.create(email=email, is_oauth=is_oauth, id_card=id_card,
                                               credit_id=ccn,
                                               iban_id=iban,
                                               fullname=fullname, phone=phone, ref_used=ref_used,
                                               ref_id=ref_id)
                    user.ref_id = f"ref-u{user.id}" \
                                  f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
                    user.save()
                    return user
                else:
                    user = User.objects.create(email=email, id_card=id_card, credit_id=ccn, iban_id=iban,
                                               fullname=fullname, phone=phone, ref_used=ref_used,
                                               ref_id=ref_id)
                    user.ref_id = f"ref-u{user.id}" \
                                  f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
                    password = validated_data['password']
                    user.set_password(password)
                    user.save()
                    return user
        except KeyError:
            # django.dispatch.dispatcher.logger.log(0, "Non referral registration")
            ref_id = f"ref-u{email}" \
                     f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
            if is_oauth:
                user = User.objects.create(email=email, is_oauth=is_oauth, id_card=id_card, credit_id=ccn, iban_id=iban,
                                           fullname=fullname, phone=phone, ref_used=False,
                                           ref_id=ref_id)

                user.ref_id = f"ref-u{user.id}" \
                              f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
                user.save()
                return user
            else:
                user = User.objects.create(email=email, id_card=id_card, credit_id=ccn, iban_id=iban,
                                           fullname=fullname, phone=phone, ref_used=False,
                                           ref_id=ref_id)
                user.ref_id = f"ref-u{user.id}" \
                              f"{''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))}"
                password = validated_data['password']
                user.set_password(password)
                user.save()
                return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    # Serializer authentication object
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        required=False
    )
    is_oauth = serializers.BooleanField(required=True)
    oauth_token = serializers.CharField(max_length=255, required=False)

    def validate(self, attrs):
        # Validate and authenticate the user
        email = attrs.get('username')
        password = attrs.get('password')
        is_oauth = attrs.get('is_oauth')
        o_token = attrs.get('oauth_token')
        if not is_oauth:
            user = authenticate(
                request=self.context.get('context'),
                email=email,
                password=password
            )
            if not user:
                message = _("Unable to authenticate with provided credentials")
                raise serializers.ValidationError(message, code='authentication')
            attrs['user'] = user
            return attrs
        else:
            if len(o_token) > 20:
                user = PasswordLessAuthBackend().authenticate(email=email)
                if not user:
                    message = _("Unable to authenticate with provided credentials")
                    raise serializers.ValidationError(message, code='authentication')
                attrs['user'] = user
                return attrs


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['auto_id', 'user', 'price', 'date', 'amount']

    def create(self, validated_data):
        user = validated_data['user']
        price = validated_data['price']
        date = validated_data['date']
        amount = validated_data['amount']
        offer = Offer.objects.create(user=user, price=price, date=date, amount=amount)
        offer.save()
        return offer


class TransactionSerializer(serializers.ModelSerializer):
    date = serializers.DateField(read_only=True)
    confirmed = serializers.BooleanField(default=False)

    class Meta:
        model = Transaction
        fields = ['id', 'sender', 'receiver', 'offer', 'amount', 'date', 'confirmed']

    def create(self, validated_data):
        sender = validated_data['sender']
        receiver = validated_data['receiver']
        offer = validated_data['offer']
        amount = validated_data['amount']
        try:
            if amount > offer.amount:
                return Response(status=status.HTTP_404_NOT_FOUND, data="Invalid Request: Amount Exceeded")

            offer.amount -= amount
            offer.save()

            transaction = Transaction.objects.create(sender=sender, receiver=receiver, offer=offer, amount=amount)
            transaction.save()
            if offer.amount == 0:
                offer.delete()

            receiver.sold_coins += amount
            receiver.save()

            return transaction
        except Offer.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data="Offer Does Not Exist")

