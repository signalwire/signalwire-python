from twilio.base import values, deserialize
from twilio.rest.fax.v1.fax import FaxContext, FaxInstance

class SWFaxContext(FaxContext):
    def fetch(self):
        """
        Fetch the SWFaxInstance

        :returns: The fetched SWFaxInstance
        :rtype: signalwire.rest.fax.SWFaxInstance
        """
        payload = self._version.fetch(method='GET', uri=self._uri, )

        return SWFaxInstance(self._version, payload, sid=self._solution['sid'], )
    
    def update(self, status=values.unset):
        """
        Update the SWFaxInstance

        :param FaxInstance.UpdateStatus status: The new status of the resource

        :returns: The updated SWFaxInstance
        :rtype: signalwire.rest.fax.SWFaxInstance
        """
        data = values.of({'Status': status, })

        payload = self._version.update(method='POST', uri=self._uri, data=data, )

        return SWFaxInstance(self._version, payload, sid=self._solution['sid'], )

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Signalwire.Rest.Fax.SWFaxContext {}>'.format(context)


class SWFaxInstance(FaxInstance):
    def __init__(self, version, payload, sid=None):
        super().__init__(version, payload, sid)
        self._properties.update({
            "error_code": deserialize.integer(payload.get("error_code")),
            "error_message": payload.get("error_message"),
        })

    @property
    def error_code(self):
        """
        :returns: Returns the error code of the fax
        :rtype: int
        """
        return self._properties['error_code']

    @property
    def error_message(self):
        """
        The error message of the fax
        """
        return self._properties['error_message']

    def __repr__(self):
        """
        Provide a friendly representation

        :returns: Machine friendly representation
        :rtype: str
        """
        context = ' '.join('{}={}'.format(k, v) for k, v in self._solution.items())
        return '<Signalwire.Rest.Fax.SWFaxInstance {}>'.format(context)
