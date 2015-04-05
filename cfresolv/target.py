import http.client
import socket
from detect import Detector


class Target:

    host = {
        'domain': None,
        'ip': None,
        'cf-ip': None,
    }

    http = {
        'response': None,
        'status': None,
        'enabled': None,
        'cf-ray': None,
    }

    def __init__(self, domain):
        self.host['domain'] = domain
        self.ip(domain)
        if not self.host['ip']:
            return None
        self.http_response(domain)

    def on_cloudflare(self):
        return bool(self.http['cf-ray'])

    def infos(self):
        print('Target: '+self.host['domain'])
        if not self.host['ip']:
            print('> not-found')
            return

        print('> ip: '+self.host['ip'])
        print('> cf-ip: '+str(self.host['cf-ip']))
        print('> cf-ray: '+str(self.http['cf-ray']))
        print('> http: '+str(self.http['enabled']))
        print('> status: '+str(self.http['status']))

    def ip(self, domain):
        try:
            host_ip = socket.gethostbyname(domain)
        except:
            return

        d = Detector()
        self.host['ip'] = host_ip
        self.host['cf-ip'] = d.in_range(host_ip)

    def http_response(self, domain):
        try:
            connection = http.client.HTTPConnection(domain)
            connection.request("HEAD", "/")
            response = connection.getresponse()
            connection.close()
        except:
            return

        self.http['response'] = response

        if response:
            self.http['cf-ray'] = response.getheader('CF-RAY')
            self.http['enabled'] = \
                response.getheader('Server') \
                + ' ' \
                + response.getheader('X-Powered-By')
            self.http['status'] = \
                str(response.status) + ' ' + response.reason
        else:
            self.http['cf-ray'] = None
            self.http['enabled'] = False
