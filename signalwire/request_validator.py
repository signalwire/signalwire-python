import base64
import hmac
import json
from hashlib import sha1
from urllib.parse import urlparse
from twilio.request_validator import compare, remove_port, add_port, RequestValidator as TwilioRequestValidator


class RequestValidator(object):
    def __init__(self, token):
        self.compatibility_validator = TwilioRequestValidator(token)
        self.token = token.encode()

    def build_signature_with_compatibility(self, uri, params):
        return self.compatibility_validator.compute_signature(uri, params)
    
    def validate_with_compatibility(self, uri, params, signature):
        return self.compatibility_validator.validate(uri, params, signature)
    
    def build_signature(self, uri, params):
        s = uri
        if params:
            s += params
        
        hmac_buffer = hmac.new(self.token, s.encode(), sha1)
        result = hmac_buffer.digest().hex()

        return result.strip()

    def validate(self, uri, params, signature):

        if isinstance(params, str):
            parsed_uri = urlparse(uri)
            with_port = add_port(parsed_uri)
            without_port = remove_port(parsed_uri)

            valid_signature_without_port = compare(
                self.build_signature(without_port, params),
                signature
            )
            valid_signature_with_port = compare(
                self.build_signature(with_port, params),
                signature
            )

            if valid_signature_without_port or valid_signature_with_port:
                return True

            try:
                parsed_params = json.loads(params)
                return self.validate_with_compatibility(uri, parsed_params, signature)
            except json.JSONDecodeError as e:
                return False
        
        return self.validate_with_compatibility(uri, params, signature)
