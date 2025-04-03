# MySQL Replication Error

> **Note**: this alert is out-of-date, as replication is not turned on for most deployments anymore. This runbook may be removed at a later date.

**Summary**: This error occurs when the MySQL slave server for some reason cannot replicate changes made to the master database.

**Consequences**: While there is any error, replication will not take place. This means that projects and users will not be mirrored to a secondary site, so users who registered after the replication stopped may find that they cannot properly log in to those sites (because their accounts are not in the secondary site's Keystone database.)

#### Possible causes

**Network connectivity broken between sites**: Try pinging the address of the master host (`show slave status\G`). If network works, it could have been broken temporarily. This has in the past caused the slave to stop and not recover. Restarting the slave process can often fix this: `stop slave; start slave;`. Use `show slave status\G` to verify any fix.

**Data mistakenly written to slave Keystone database**: In this case, data was accidentally added to the Keystone database, which can often cause a duplicate key problem when the master database tries to replicate over a row that already exists. To solve this problem you must reset the replication. You will need access to both the MySQL master and the slave to accomplish this.

1. On a node with access to the master database, run [`scripts/mysql_replication_snapshot`](https://github.com/ChameleonCloud/ansible-playbooks/blob/master/scripts/mysql\_replication\_snapshot). The script should write out a copy of the Keystone database to the working directory and also print the binlog position; take note of this position as you will need it later.
2. Copy the Keystone database file to a node with access to the slave database.

> _Tip_: Use `scp -3 hostA:mysql_keystone_master-*.sql.gz hostB:` if there is no remote authentication set up between two sites; the `-3` flag instructs scp to use your local credentials to first download from hostA, then upload to hostB.

1. On the node with access to the slave database, run [`scripts/mysql_replication_restore`](https://github.com/ChameleonCloud/ansible-playbooks/blob/master/scripts/mysql\_replication\_restore). This script takes in a path to the Keystone database snapshot and a binlog position. It will wipe away the slave Keystone database tables and replace it with values from the master, and then set up replication starting from the binlog position at which the snapshot was taken. Once this completes, the databases should be in sync again.
2. Check `show slave status\G` on the slave to verify replication is working again.
