import logging
import wishful_upis as upis
import wishful_framework as wishful_module
import _thread as thread

import traceback
import threading
import time

import getopt
import sys

from .coapthon_server import *
from coapthon.client.helperclient import HelperClient
from coapthon.utils import parse_uri

__author__ = "Carlo Vallati, Giacomo Tanganelli"
__copyright__ = "Copyright (c) 2018, University of Pisa"
__version__ = "0.1.0"
__email__ = "{carlo.vallati, giacomo.tanganelli}@iet.unipi.it"

'''
    Create a coapthon server or client.
'''


@wishful_module.build_module
class CoapthonModule(wishful_module.AgentModule):
    def __init__(self):
        super(CoapthonModule, self).__init__()
        self.log = logging.getLogger('CoapthonModule.main')
        self.running = False
        self.interval = 5
        self.payload = 0

        # stats
        self.timestamps = {}
        self.overall_delay = 0
        self.num_received = 0

        # measurements
        self.measurements = {}
        self.measurements['app_stats'] = {}
        self.measurements['app_stats']['app_requests'] = 0
        self.measurements['app_stats']['app_avg_delay'] = 0
        self.measurements['app_stats']['app_avg_retx'] = 0 # Still to be implemented
        self.measurements['app_stats']['app_avg_loss'] = 0

    @wishful_module.bind_function(upis.net.create_packetflow_sink)
    def start_server(self, port):
        self.log.debug("Starts Coap server on port {}".format(port))
        ip = "0.0.0.0"
        multicast = False
        self.server = CoAPServer(ip, port, multicast)

        try:
            thread.start_new_thread(self.server.listen, (10,))
        except:
            traceback.print_exc(file=sys.stdout)

        return "Server_started"


    @wishful_module.bind_function(upis.net.destroy_packetflow_sink)
    def stop_server(self):
        self.log.debug("Stops Coap server.")

        self.server.close()

        return "Server_stopped"

    def receive_response(self, response):

        if response.timeouted is True:
            self.measurements['app_stats']['app_avg_loss'] = self.measurements['app_stats']['app_avg_loss'] + 1
        else:
            if response.mid in self.timestamps.keys():
                self.overall_delay = (time.time() - self.timestamps[response.mid])

                del(self.timestamps[response.mid])

                self.num_received = self.num_received + 1

                self.measurements['app_stats']['app_avg_delay'] =  float(self.overall_delay / self.num_received)
            else:
                self.measurements['app_stats']['app_avg_loss'] = self.measurements['app_stats']['app_avg_loss'] + 1

        self.measurements['app_stats']['app_avg_retx']= self.client.protocol.avg_retx()

        print((response.pretty_print()))

    def generate_traffic(self):
        while self.running is True:

               self.measurements['app_stats']['app_requests'] = self.measurements['app_stats']['app_requests'] + 1

               if self.payload == 0:

                       request = self.client.get("basic", self.receive_response)

               else:

                       payload = ''.join('x' for x in range(self.payload))        

                       request = self.client.put("basic", payload, self.receive_response)

               print((request.pretty_print()))

               self.timestamps[request.mid] = time.time()

               time.sleep( self.interval )

        self.client.stop()



    @wishful_module.bind_function(upis.net.start_packetflow)
    def start_packetflow(self, dest_ip, port):
        self.log.debug("Start Coap client.")

        self.client = HelperClient(server=(dest_ip, port))

        if self.running is True:
               return "Client started"

        self.running = True

        try:
            thread.start_new_thread(self.generate_traffic, ())
        except:
            traceback.print_exc(file=sys.stdout)

        return "Client started"


    @wishful_module.bind_function(upis.net.stop_packetflow)
    def stop_packetflow(self):
        self.log.debug("Stops Coap client.")

        self.running = False

        return "Client stopped"

    @wishful_module.bind_function(upis.net.set_parameters_net)
    def set_parameters_net(self, values):
        self.log.debug("Set parameters net called.")
        if 'app_payload_length' in values.keys():
               self.log.debug("App Payload set: "+str(values['app_payload_length']))
               self.payload = values['app_payload_length']
        if 'app_send_interval' in values.keys():
               self.log.debug("App Interval set: "+str(values['app_send_interval']))
               self.interval = values['app_send_interval']

    @wishful_module.bind_function(upis.net.get_measurements_net)
    def get_net_measurements(self, measurement_key_list):

        self.log.debug("Get Measurement called")

        ret = []
        for m in measurement_key_list:
                if m not in self.measurements.keys():
                    return False

                ret.append(self.measurements[m])

        return ret

    def get_net_measurements_periodic_worker(self, measurement_list, collect_period, report_period, num_iterations, report_callback):
        ret = self.get_net_measurements(measurement_list)
        report_callback(ret)

    @wishful_module.bind_function(upis.net.get_measurements_periodic_net)
    def get_net_measurements_periodic(self, measurement_key_list, collect_period, report_period, num_iterations, report_callback):
        try:
            thread.start_new_thread(self.get_net_measurements_periodic_worker, ( measurement_key_list, collect_period, report_period, num_iterations, report_callback,))
        except:
            traceback.print_exc(file=sys.stdout)