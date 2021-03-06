# coding: utf-8
import shutil
import tempfile

import unittest
from django.test import override_settings
import responses

from django.conf import settings

import sendsms


if not settings.configured:
    settings.configure(
        SENDSMS_BACKEND='sendsms.backends.locmem.SmsBackend',
        ESENDEX_USERNAME='niwibe',
        ESENDEX_PASSWORD='123123',
        ESENDEX_ACCOUNT='123123',
        ESENDEX_SANDBOX=True,
    )


class TestApi(unittest.TestCase):
    def test_send_simple_sms(self):
        from sendsms.message import SmsMessage

        obj = SmsMessage(body="test", from_phone='111111111', to=['222222222'])
        obj.send()

        self.assertEqual(len(sendsms.outbox), 1)

    def test_send_esendex_sandbox(self):
        from sendsms.message import SmsMessage
        from sendsms.api import get_connection

        connection = get_connection('sendsms.backends.esendex.SmsBackend')
        obj = SmsMessage(body="test", from_phone='111111111', to=['222222222'], connection=connection)
        res = obj.send()
        self.assertEqual(res, 1)

    @responses.activate
    def test_svyaznoy(self):
        responses.add(responses.GET, 'https://smsinfo.zagruzka.com/aggrweb',
                      content_type='application/json')
        from sendsms.message import SmsMessage
        from sendsms.api import get_connection

        connection = get_connection('sendsms.backends.svyaznoy.SmsBackend')
        obj = SmsMessage(body=u"test ☃", from_phone='111111111', to=['+222222222'], connection=connection)
        res = obj.send()
        self.assertEqual(res, 1)
        self.assertEqual(len(responses.calls), 1)
        self.assertIn('clientId=222222222', responses.calls[0].request.url)

    def test_filebased(self):
        from sendsms.api import send_sms
        tmpdir = tempfile.mkdtemp()
        with override_settings(SENDSMS_BACKEND='sendsms.backends.filebased.SmsBackend',
                               SMS_FILE_PATH=tmpdir):
            try:
                send_sms(body=u'test ☃', from_phone='-', to=['+222222222'])
            finally:
                shutil.rmtree(tmpdir)

    @override_settings(SENDSMS_BACKEND='sendsms.backends.console.SmsBackend')
    def test_console(self):
        from sendsms.api import send_sms
        send_sms(body=u'test ☃', from_phone='-', to=['+222222222'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
