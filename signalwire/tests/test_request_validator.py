from unittest import TestCase
from multidict import MultiDict

class TestRequestValidator(TestCase):
    def test_should_validate_no_compatibility(self):
        from signalwire.request_validator import RequestValidator

        url = 'https://81f2-2-45-18-191.ngrok-free.app/'
        token = 'PSK_7TruNcSNTxp4zNrykMj4EPzF'
        signature = 'b18500437ebb010220ddd770cbe6fd531ea0ba0d'
        body = '{"call":{"call_id":"b5d63b2e-f75b-4dc8-b6d4-269b635f96c0","node_id":"fa3570ae-f8bd-42c2-83f4-9950d906c91b@us-west","segment_id":"b5d63b2e-f75b-4dc8-b6d4-269b635f96c0","call_state":"created","direction":"inbound","type":"phone","from":"+12135877632","to":"+12089806814","from_number":"+12135877632","to_number":"+12089806814","project_id":"4b7ae78a-d02e-4889-a63b-08b156d5916e","space_id":"62615f44-2a34-4235-b38b-76b5a1de6ef8"},"vars":{}}'

        validator = RequestValidator(token)
        computed = validator.build_signature(url, body)
        self.assertIsInstance(computed, str)
        self.assertEqual(signature, computed)
        valid = validator.validate(url, body, signature)
        self.assertTrue(valid)

    def test_should_validate_with_compatibity(self):
        from signalwire.request_validator import RequestValidator

        url = 'https://mycompany.com/myapp.php?foo=1&bar=2'
        token = '12345'
        signature = 'RSOYDt4T1cUTdK1PDd93/VVr8B8='
        body = {
            'CallSid': 'CA1234567890ABCDE',
            'Caller': '+14158675309',
            'Digits': '1234',
            'From': '+14158675309',
            'To': '+18005551212',
          }
        
        validator = RequestValidator(token)
        valid = validator.validate(url, body, signature)
        self.assertTrue(valid)

    def test_should_validate_with_compatibity_flask(self):
        from signalwire.request_validator import RequestValidator

        url = 'https://mycompany.com/myapp.php?foo=1&bar=2'
        token = '12345'
        signature = 'RSOYDt4T1cUTdK1PDd93/VVr8B8='
        body = MultiDict (
            [
                ('CallSid', 'CA1234567890ABCDE'),
                ('Caller', '+14158675309'),
                ('Digits', '1234'),
                ('From', '+14158675309'),
                ('To', '+18005551212')
            ]
          )
        
        validator = RequestValidator(token)
        valid = validator.validate(url, body, signature)
        self.assertTrue(valid)

    def test_should_validate_from_signalwire_http_request(self):
        from signalwire.request_validator import RequestValidator

        url = 'http://0aac-189-71-169-171.ngrok-free.app/voice'
        token = 'PSK_V3bF8oyeRNpJWGoRWHNYQMUU'
        signature = 'lf3nWPmUr2y6jSeeoMW4mg58vgI=' #From Lib
        body = {
            "AccountSid": "6bfbbe86-a901-4197-8759-2a0de1fa319d", 
            "ApiVersion": "2010-04-01", 
            "CallbackSource": "call-progress-events",  
            "CallSid": "0703574f-b151-465d-aedb-28972eb513c7",
            "CallStatus": "busy", 
            "Direction": "outbound-api", 
            "From": "sip:+17063958228@sip.swire.io",
            "HangupBy": "sip:jpsantos@joaosantos-2a0de1fa319d.sip.swire.io", 
            "HangupDirection": "inbound", 
            "Timestamp": "Thu, 09 Nov 2023 17:05:04 +0000", 
            "To": "sip:jpsantos@joaosantos-2a0de1fa319d.sip.swire.io", 
            "SipResultCode": "486"
        }
        
        validator = RequestValidator(token)
        valid = validator.validate(url, body, signature)
        self.assertTrue(valid)

    def test_should_validate_from_signalwire_https_request(self):
        from signalwire.request_validator import RequestValidator

        url = 'https://675d-189-71-169-171.ngrok-free.app/voice'
        token = 'PSK_V3bF8oyeRNpJWGoRWHNYQMUU'
        signature = 'muUMpldcBHlzuXGZ5gbw1ETZCYA='
        body = {
            "CallSid": "a97d4e8a-6047-4e2b-be48-fb96b33b5642", 
            "AccountSid": "6bfbbe86-a901-4197-8759-2a0de1fa319d", 
            "ApiVersion": "2010-04-01", 
            "Direction": "outbound-api", 
            "From": "sip:+17063958228@sip.swire.io", 
            "To": "sip:jpsantos@joaosantos-2a0de1fa319d.sip.swire.io", 
            "Timestamp": "Thu, 09 Nov 2023 14:40:55 +0000", 
            "CallStatus": "no-answer", 
            "CallbackSource": "call-progress-events", 
            "HangupDirection": "outbound", 
            "HangupBy": "sip:+17063958228@sip.swire.io", 
            "SipResultCode": "487"
        }

        
        validator = RequestValidator(token)
        valid = validator.validate(url, body, signature)
        self.assertTrue(valid)

    def test_should_validate_from_raw_json(self):
        from signalwire.request_validator import RequestValidator

        url = 'https://675d-189-71-169-171.ngrok-free.app/voice'
        token = 'PSK_V3bF8oyeRNpJWGoRWHNYQMUU'
        signature = 'muUMpldcBHlzuXGZ5gbw1ETZCYA='
        body = '''{
            "CallSid": "a97d4e8a-6047-4e2b-be48-fb96b33b5642", 
            "AccountSid": "6bfbbe86-a901-4197-8759-2a0de1fa319d", 
            "ApiVersion": "2010-04-01", 
            "Direction": "outbound-api", 
            "From": "sip:+17063958228@sip.swire.io", 
            "To": "sip:jpsantos@joaosantos-2a0de1fa319d.sip.swire.io", 
            "Timestamp": "Thu, 09 Nov 2023 14:40:55 +0000", 
            "CallStatus": "no-answer", 
            "CallbackSource": "call-progress-events", 
            "HangupDirection": "outbound", 
            "HangupBy": "sip:+17063958228@sip.swire.io", 
            "SipResultCode": "487"
        }'''

        
        validator = RequestValidator(token)
        valid = validator.validate(url, body, signature)
        self.assertTrue(valid)




