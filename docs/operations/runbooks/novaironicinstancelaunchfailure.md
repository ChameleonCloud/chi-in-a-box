**Summary**: A large number of instance launches have failed recently.

**Consequences**: If this is sustained, it indicates that users are probably experiencing errors with the platform. This is a very general canary alarm and probably indicates a wider issue, perhaps one that is also alerting.

### Possible causes

There are many different causes; it is impossible to say specifically. Check the centralized logging (Kibana) for error logs, or check the local logs on the host (`/var/log/kolla`) for errors.