**Summary**: Experiment Precis event listener stops parsing OpenStack service notification messages.

**Consequences**: Users will get Experiment Precis reports with missing information.

### Possible causes

**OpenStack service is not working**: broken OpenStack services will affect emitting notifications to the message bus. Check if the services are running properly and check if the service topic exists using `rabbitmqctl list_exchanges | grep <service name>`.

**Message format is incorrect**: Experiment Precis requires 2.0 message format. In the configuration files, make sure `oslo_messaging_notifications` has `driver` set to `messagingv2`.

**Message queue is not binding to the OpenStack service exchange**: A queue named `experiment_precis_event_queue` needs to be bound to the OpenStack exchanges so that the messages can flow from the exchange (the source) to the queue (the destination). Use `rabbitmqctl list_bindings | grep precis` to check if the bindings exist.

If the binding does not exist, re-running the `precis.yml` playbook should resolve it: `./cc-ansible --playbook playbooks/precis.yml`.

**Experiment Precis event listener is broken**: check if the event listener container is running and check the logs for errors. 