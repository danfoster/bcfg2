"""RPC client access to cobalt components.

Classes:
ComponentProxy -- an RPC client proxy to Cobalt components

Functions:
load_config -- read configuration files
"""

__revision__ = '$Revision: $'

import logging
import socket
import time
import urlparse
import xmlrpclib
from xmlrpclib import _Method
import Bcfg2.tlslite.errors
from Bcfg2.tlslite.integration.XMLRPCTransport import XMLRPCTransport
import Bcfg2.tlslite.X509, Bcfg2.tlslite.X509CertChain
import Bcfg2.tlslite.utils.keyfactory

__all__ = ["ComponentProxy", "RetryMethod"]

class RetryMethod(_Method):
    """Method with error handling and retries built in"""
    log = logging.getLogger('xmlrpc')
    def __call__(self, *args):
        max_retries = 4
        for retry in range(max_retries):
            try:
                return _Method.__call__(self, *args)
            except xmlrpclib.ProtocolError, err:
                self.log.error("Server failure: Protocol Error: %s %s" % \
                              (err.errcode, err.errmsg))
                raise xmlrpclib.Fault(20, "Server Failure")
            except xmlrpclib.Fault:
                raise
            except socket.error, err:
                if retry == 3:
                    self.log.error("Server failure: %s" % err)
                    raise xmlrpclib.Fault(20, err)
            except Bcfg2.tlslite.errors.TLSFingerprintError, err:
                raise
            except Bcfg2.tlslite.errors.TLSError, err:
                self.log.error("Unexpected TLS Error: %s. Retrying" % (err))
            except:
                self.log.error("Unknown failure", exc_info=1)
                break
            time.sleep(0.5)
        raise xmlrpclib.Fault(20, "Server Failure")

# sorry jon
xmlrpclib._Method = RetryMethod

def ComponentProxy (url, user=None, password=None, fingerprint=None,
                    key=None, cert=None):
    
    """Constructs proxies to components.
    
    Arguments:
    component_name -- name of the component to connect to
    
    Additional arguments are passed to the ServerProxy constructor.
    """
    
    if user and password:
        method, path = urlparse.urlparse(url)[:2]
        newurl = "%s://%s:%s@%s" % (method, user, password, path)
    else:
        newurl = url
    if key and cert:
        pdata = open(key).read()
        pemkey = Bcfg2.tlslite.utils.keyfactory.parsePEMKey(pdata, private=True)
        xcert = Bcfg2.tlslite.X509.X509()
        cdata = open(cert).read()
        xcert.parse(cdata)
        certChain = Bcfg2.tlslite.X509CertChain.X509CertChain([xcert])
    else:
        certChain = None
        pemkey = None
    ssl_trans = XMLRPCTransport(x509Fingerprint=fingerprint, certChain=certChain,
                                privateKey=pemkey)
    return xmlrpclib.ServerProxy(newurl, allow_none=True, transport=ssl_trans)

