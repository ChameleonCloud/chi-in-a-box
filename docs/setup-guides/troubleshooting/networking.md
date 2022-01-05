# Networking

### Intermittent Connectivity

A common cause of intermittent connectivity, especially when multiple interfaces are on the same L2 segment, is the default behavior of ARP on linux.

#### Reproduce the issue

First, identify your gateway IP address, referred to hereafter as `gateway_ip`

```shell-session
[root@chi-edge etc]# ip route show default
default via 129.114.34.254 dev brpublic proto static metric 427
```

Attempt to ping this address, both from the host, and from inside the neutron router namespace.

`-D` Print timestamp (unix time + microseconds as in `gettimeofday`) before each line.

`-O` Report outstanding ICMP ECHO reply before sending next packet. This is useful together with the timestamp -D to log output to a diagnostic file and search for missing answers.

`-n` Numeric output only. No attempt will be made to lookup symbolic names for host addresses.

```shell-session
[shermanm@chi-edge ~]$ ping -D -O -n 129.114.34.254
PING 129.114.34.254 (129.114.34.254) 56(84) bytes of data.
[1642959883.911513] 64 bytes from 129.114.34.254: icmp_seq=1 ttl=64 time=2.21 ms
[1642959884.910674] 64 bytes from 129.114.34.254: icmp_seq=2 ttl=64 time=1.83 ms
```

```shell-session
[shermanm@chi-edge ~]$ sudo ip netns exec qrouter-33cbf0c8-ff4e-40f3-b704-55bc9cbb5dcf bash
[root@chi-edge shermanm]# ping -D -O -n 129.114.34.254
PING 129.114.34.254 (129.114.34.254) 56(84) bytes of data.
[1642959964.131076] 64 bytes from 129.114.34.254: icmp_seq=1 ttl=64 time=1.29 ms
[1642959965.137204] 64 bytes from 129.114.34.254: icmp_seq=2 ttl=64 time=6.02 ms
```

If you observe this failing from one or the other namespace, check the system arp table.

```shell-session
[root@chi-edge etc]# ip -s  neighbor show 129.114.34.254
129.114.34.254 dev br-ex lladdr 50:c7:09:09:e9:60 used 153459/153519/153459 probes 0 STALE
129.114.34.254 dev brpublic lladdr 50:c7:09:09:e9:60 ref 1 used 661/1/661 probes 4 REACHABLE
```

