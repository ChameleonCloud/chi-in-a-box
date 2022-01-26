# maintenance\_reservation

Often, you'll need to schedule work on a node, and need to indicate that its not available for reservation during that period. Setting the ironic `maintenance` flag doesn't contain information about the expected duration, so we have a tool for this.

Run the hammer on one of your controller nodes:

```
sudo cc-hammer python3 hammers/scripts/maintenance_reservation.py \
    --operator "your_user_name \
    --nodes "list,of_node,names" \
    --reason "some_string" \
    --start-time "yyyy-mm-dd hh:mm:ss" \
    --estimate-hours "24" \
    --dry-run
```

It will attempt to create a lease for each node in `list,of_node,names` starting at `start-time`, and with the duration of `estimate-hours`. Users will be able to make leases either before or after this duration.

{% hint style="info" %}
Remove --dry-run to actually make the leases!
{% endhint %}
