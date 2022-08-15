# Changelog

## T-800 Model 101, v1.0
Features
- First barebone working version
- Chat engine reported as running and quite stable
- Listens on multiple interfaces
- Multi user, multiple clients are allowed by default
- SSL Certificates on both client and server side are required
- Host IP direct access is discouraged, names and certificates are mandatory when used outside localhost
- Keras based recognition
- Multi language lemmatizer

Bug fix
- tcp socket connections timeout
- concurrency on different clients and addresses