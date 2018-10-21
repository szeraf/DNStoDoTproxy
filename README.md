# DNS to DNS over TLS (DoT) proxy

The project is written in python 3. It listens on TCP port 53 for DNS queries, and forwards them to the specified DNS over TLS server on the spacified port, after establishing a secure channel. The project does not implement any packet level checks, simply forwards the recieved information to the remote server.

## Usage

The prgram works with __four__ parameters:

- --server, -s -> IP address of the upstream DNS over TLS capable server, defaults to _1.1.1.1_
- --port, -p -> port number of the above server, defaults to _853_
- --name, -n -> hostname of the above server for the cert to validate against, defaults to _cloudflare-dns.com_
- --cacert, -c -> path to the ca-certificates.crt file, defaults to _/etc/ssl/certs/ca-certificates.crt_

### Usage with docker
Go in the directory where the Dockerfile and the python script is, and issue the folowing commands:

```
docker build -t your/tag:version .
```

```
docker run [-d] -p 53:53 -p 853:853 your/tag:version [-s '1.1.1.1'] [-p 853] [-n 'cloudflare-dns.com'] [-c 'path/to/certs']
```
You can test the connection:
```
dig -p 53 @127.0.0.1 www.google.com +tcp
```
## Security

- Since the proxy listens on port 53, it needs root privileges to run
- The proxy binds to 0.0.0.0, change it for more security
- Make sure that the remote server is a trusted entity
- The remote DoT server is a single point of failure
- There may be no DoT connection after the specified upstream server
- The proxy does not implement any packet level checks, simply forwards the recieved information to the remote server. 

## Place in a Microservice environment

- When DNS based service discovery is in use, DoT can provide a proper security layer to hide sensitive information.
- In a multiple datacenter environment, querying remote services over the internet can be made more secure with DoT

## Room for improvement

- Incoming UDP queries
- Multiple upstream servers
- Caching
___
Bence Ver

2018