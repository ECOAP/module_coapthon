from coapthon.server.coap import CoAP
from coapthon import defines
from coapthon.resources.resource import Resource

class BasicResource(Resource):
    def __init__(self, name="BasicResource", coap_server=None):
        super(BasicResource, self).__init__(name, coap_server, visible=True,
                                            observable=True, allow_children=True)
        self.payload = "Basic Resource"
        self.resource_type = "rt1"
        self.content_type = "text/plain"
        self.interface_type = "if1"

    def render_GET(self, request):
        # payload form c=r&m=off&i=11&reqid=1549
        s=str(request.payload)
        info=s.split('&')
        burst_id = info[2].split('=')[1]
        req_id = info[3].split('=')[1]

        print("RICEVUTO")
        print(str(burst_id))
        print(str(req_id))

        return self

    def render_PUT(self, request):
        self.edit_resource(request)
        return self

    def render_POST_advanced(self, request, response    ):
        # payload form c=r&m=off&i=11&reqid=1549
        s=str(request.payload)
        info=s.split('&')
        burst_id = info[2].split('=')[1]
        req_id = info[3].split('=')[1]

        # Put in the response payload the burst id and the message id

        response.code = defines.Codes.CREATED.number

        response.payload = (defines.Content_types["text/plain"], str(burst_id) + " " + str(req_id) + "\0")

        return (self, response)

    def render_DELETE(self, request):
        return True


class CoAPServer(CoAP):
    def __init__(self, host, port, multicast=False):
        CoAP.__init__(self, (host, port), multicast)
        self.add_resource('hello/', BasicResource())

        print(("CoAP Server start on " + host + ":" + str(port)))
        print((self.root.dump()))
