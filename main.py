import sys
import ssl
import socket
import _thread
import argparse

# send a TCP DNS query to the upstream DNS server over TLS
def sendTCP(DNSserverIP, DNSserverName, DNSserverPort, query, CacertLocation):
    try:
        # create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(100)

        # wrap the socket in a tls context
        context = ssl.create_default_context()
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(CacertLocation)

        wrappedSocket = context.wrap_socket(sock, server_hostname=DNSserverIP)

        # connect, query, and return reply
        wrappedSocket.connect((DNSserverIP, DNSserverPort))
        remote_cert = wrappedSocket.getpeercert()
        print(remote_cert)
        valid = ssl.match_hostname(remote_cert, DNSserverName)
        if valid == None : print("Certificate validated.")

        wrappedSocket.send(query)  	
        data = wrappedSocket.recv(1024)
        return data
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating")
    finally:
        if 'wrappedSocket' in vars() or 'wrappedSocket' in globals() : wrappedSocket.close()
        if 'sock' in vars() or 'sock' in globals() : sock.close()

def handler(data, addr, socket, DNSserverIP, DNSserverName, DNSserverPort, CacertLocation):
    TCPanswer = sendTCP(DNSserverIP, DNSserverName, DNSserverPort, data, CacertLocation)
    if TCPanswer:
        print("Success!")
        socket.sendto(TCPanswer, addr)
    else:
        print("Some error occured, please investigate!")
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # default is the cloudflare DoT server
    parser.add_argument("-s", "--server", help="address of the upsream DoT server",
        default="1.1.1.1")
    parser.add_argument("-n", "--name", help="name of the upsream DoT server",
        default="cloudflare-dns.com")
    # default DoT port if not provided
    parser.add_argument("-p", "--port", help="port of the upsream DoT server",
        default=853, type=int)
    # should include digicert root ca for cloudflare
    parser.add_argument("-c", "--cacert", help="location of the ca-certificates.crt file",
        default="/etc/ssl/certs/ca-certificates.crt")
    args = parser.parse_args()
    
    DNSserverIP = args.server
    DNSserverName = args.name
    DNSserverPort = args.port
    CacertLocation = args.cacert

    try:
        # socket to listen on tcp/53
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', 53))
        sock.listen(2)
        while True:
            conn, addr = sock.accept()
            data = conn.recv(1024)
            # handle every new connection in a different thread
            _thread.start_new_thread(handler, 
                (data, addr, conn, DNSserverIP, DNSserverName, DNSserverPort, CacertLocation))
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        print("Caught KeyboardInterrupt, terminating")
    finally:
        if 'conn' in vars() or 'conn' in globals() : conn.close()
        if 'sock' in vars() or 'sock' in globals() : sock.close()