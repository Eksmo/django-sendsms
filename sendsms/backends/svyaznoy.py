# coding: utf-8
from django.conf import settings
from sendsms.backends.base import BaseSmsBackend
import requests


SVYAZNOY_SERVICE_ID = getattr(settings, 'SENDSMS_SVYAZNOY_SERVICE_ID', '')
SVYAZNOY_PASSWORD = getattr(settings, 'SENDSMS_SVYAZNOY_PASSWORD', '')


class SmsBackend(BaseSmsBackend):
    """Svyaznoy sms backend"""
    base_url = 'https://smsinfo.zagruzka.com/aggrweb'

    def send_messages(self, messages):
        counter = 0

        for message in messages:
            for phone in message.to:
                phone = phone.replace('+', '')
                response = requests.get(
                    url=self.base_url,
                    params={
                        'clientId': phone,
                        'message': message.body,
                        'serviceId': SVYAZNOY_SERVICE_ID,
                        'shortNumber': '-',  # not used anyway
                        'pass': SVYAZNOY_PASSWORD
                    })
                response.raise_for_status()
                counter += 1

        return counter

