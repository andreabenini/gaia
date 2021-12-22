# Generate CA, server and client certificates
HOWTO generate a CA, a server and a client certificate for it, basically everything you need to get your hands dirty:
```sh
# Create to keys directory...
mkdir -p certs

# Generate a self signed certificate for the CA along with a key.
# NOTE: I'm using -nodes, this means that once anybody gets
# their hands on this particular key, they can become this CA.
openssl req -x509 -nodes -days 3650 -newkey rsa:4096 \
            -keyout certs/ca_key.pem -out certs/ca_cert.pem \
            -subj "/C=IT/ST=Mental State/L=Cloud City/O=Ben Corp./CN=andreabenini.github.io"

# Create server private key and certificate request
openssl genrsa -out certs/server_key.pem 4096
openssl req -new -key certs/server_key.pem -out certs/server.csr \
            -subj "/C=IT/ST=Mental State/L=Cloud City/O=Ben Corp./CN=server.andreabenini.github.io"

# Create client private key and certificate request
openssl genrsa -out certs/client_key.pem 4096
openssl req -new -key certs/client_key.pem -out certs/client.csr \
            -subj "/C=IT/ST=Mental State/L=Cloud City/O=Ben Corp./CN=botctl"

# Generate certificates with newly created CA
openssl x509 -req -days 1460 -in certs/server.csr -CA certs/ca_cert.pem -CAkey certs/ca_key.pem -CAcreateserial -out certs/server_cert.pem
openssl x509 -req -days 1460 -in certs/client.csr -CA certs/ca_cert.pem -CAkey certs/ca_key.pem -CAcreateserial -out certs/client_cert.pem
```

# Testing
Now to test both the server and the client

**On one shell, run the following:**
```
openssl s_server -CAfile certs/ca_cert.pem -cert certs/server_cert.pem -key certs/server_key.pem -Verify 1
```
**On another shell, run the following:**
```
openssl s_client -CAfile certs/ca_cert.pem -cert client/client_cert.pem -key client/client_key.pem
```
Once the negotiation is complete, any line you type is sent over to the other side.
By line, I mean some text followed by a keyboard return press.
