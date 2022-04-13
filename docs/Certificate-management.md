# Certificate management

All CHI-in-a-Box APIs and application endpoints are exposed over the public Internet via TLS-encrypted proxies served by HAProxy. A valid SSL certificate is needed for the `kolla_external_fqdn` you provide. You can use either an automated LetsEncrypt workflow or provide a certificate you have obtained from another certificate authority (by default, this will be, relative to your site configuration directory, `./certificates/haproxy.pem`).

### LetsEncrypt

#### Setup

In order to use the LetsEncrypt method, you must first enable the LetsEncrypt agents for your deployment:

```yaml
enable_letsencrypt: yes
letsencrypt_email: <email_addr@for.cert.renewals>
letsencrypt_domains:
  - "{{ kolla_external_fqdn }}"
```

Ensure the agents are deployed before proceeding:

```shell
./cc-ansible deploy --tags letsencrypt,haproxy,horizon
```

At this point, verify that the ACME server is running by visiting: `http://<kolla_external_fqdn>/.well-known/acme-challenge/`

If everything has gone well, you'll get a 404 from nginx.

#### Initial certificate generation

Currently, the initial certificate generation is not yet automated ([https://github.com/ChameleonCloud/chi-in-a-box/issues/116](Certificate-management.md#116)). You must perform the following steps:

```shell
# Make a directory for your certs
docker exec -it letsencrypt_certbot mkdir -p /www/data/<kolla_external_fqdn>/
# Request the initial certificate
docker exec -it letsencrypt_certbot certbot certonly --noninteractive --agree-tos
# If all goes well, restart haproxy
docker restart haproxy
```

Finally, enable external TLS in your defaults.yml

```
kolla_enable_tls_external: true
```

And reconfigure `./cc-ansible reconfigure --tags haproxy`

#### Certificate renewal

Any LetsEncrypt certificates will be automatically renewed. **However**, HAProxy will not automatically restart when this happens, meaning it will not detect or pick up the new certificates (see [https://github.com/ChameleonCloud/chi-in-a-box/issues/125](Certificate-management.md#125)). For the time being, you may wish to set up a periodic task to restart HAProxy every few weeks.

### Bring your own certificate

When providing your own certificate file, care must be taken to format it for HAProxy. HAProxy requires a PEM file with the following information, concatenated in order:

1. Your private key
2. Your public certificate
3. (Optional) Your intermediate certificates. Place them in reverse order here, the uppermost certificate coming last.

This should end up looking something like:

```
-----BEGIN PRIVATE KEY-----
[Your private key]
-----END PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
[Your certificate]
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
[Intermidate#2 certificate]
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
[Intermidate#1 certificate]
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
[Root certificate]
-----END CERTIFICATE-----
```

Most likely you will not need to add more than one intermediate certificate.

Place your PEM file in `$site_config/certificates/haproxy.pem` (or whatever the value of `kolla_external_fqdn_cert`) and ensure it is not world-readable (`chmod 400`). Then, run a reconfiguration of HAProxy to copy the new certificate and restart HAProxy:

```shell
./cc-ansible reconfigure --tags haproxy
```

### Debugging certificates

If you're having trouble with your certs failing verification, [What's my Chain Cert?](https://whatsmychaincert.com) is an excellent debugging tool and can help pinpoint issues such as an expired intermediate certificate.
