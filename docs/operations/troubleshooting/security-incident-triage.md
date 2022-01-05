This page documents some useful snippets you can employ when trying to determine the nature of a compromised or malicious user-provisioned node.

## Current activity

To get a list of all logged in users and what they're doing (and how many resources they're using) (yes it really is just "w"):

```shell
w
```

To see a more detailed readout of system utilization:

```shell
htop
iotop # for I/O operations (might not be installed)
iftop # for network (might not be installed)
ps aux
```

> **Note**: Make sure you hold this open for a bit - do you see any weird processes? Something taking up a lot of resources, especially one that has a weird or very simple name?

To get a list of open files and processes for a given user:

```shell
lsof -u $user
```

To kill anything being done by a user (this is *very* destructive :bomb:):

```
kill -9 $(lsof -t -u $user)
```

More fun `lsof` tips can be found [here](https://danielmiessler.com/study/lsof/).

## Open ports

Check to see which ports are open for TCP (replace TCP with UDP to see UDP servers, though these will be common). `-n` disables reverse hostname resolution, and `-P` disables port naming.

```shell
lsof -nP -i -sTCP:LISTEN
```

Check to see if any processes are listening on all interfaces. If one is, it will show up like this, with an asterisk in place of the bind address:

```
TCP *:22 (LISTEN)
```

Anything listening on all interfaces will by default be accessible over the public Internet if the bare metal node has a Floating IP assigned.

To close off a port, you can just stop the process that is listening on that port. If for some reason this is not sufficient, you can close the port via iptables. You can use `hostname -I` to list all IP addresses assigned to the host and pick a particular one you want to whitelist for the port, and close off any connection to that port for any other destination:

```shell
iptables -A OUTPUT -p tcp -d ! $ip --dport $port -j DROP
```

To close all ports to any TCP request not bound for a given IP:

```shell
iptables -A OUTPUT -p tcp -d ! $ip -j DROP
```

You can save the rules so they persist across reboots, in case the user wants to keep using the node but you want to ensure some protection remains (by default rules are cleared on boot):

```shell
service iptables save
```

## Command history

The command history can give you a sense of whether a user has acted maliciously. Only commands entered via an interactive session can appear in the command history; commands run via an SSH command directly are not logged. Additionally, users can always clear this history or invoke commands such that they don't get logged, so this is a bit unreliable, but can often be helpful.

```shell
sudo -u $user -H sh -c 'less $HOME/.bash_history'
```

Another way requires logging in to the target user's shell and using the `history` builtin:

```shell
sudo su -l $user
history
```

For commands executed in sudo, you can view the sudo logs:

```shell
journalctl -e _COMM=sudo
```

## Malicious processes

If you've identified a weird looking process with `lsof`, `htop`, or similar, it can be helpful to figure out where it's coming from. Once you have the PID of the process, you can look up its executable via the `/proc` filesystem:

```shell
ls -l /proc/$PID/exe
```

Sometimes, to avoid detection, a malicious binary will start and then delete itself on the disk, retaining the running process in memory. You can tell if this has happened because the file entry will have "(deleted)" printed next to it in the output of `ls -l`. In this case, if you read the exe file, the kernel is giving you access to the open file/process directly.

Wherever the binary contents are (either in /proc/$PID/exe directly, in the above case, or elsewhere on the filesystem, in the simpler case), you can safely generate a hash of its contents so that you can compare against known malicious hashes (this is how most simple anti-virus works.)

```shell
sha256sum /path/to/malicious/binary
```

Once you have the hash, you can search [VirusTotal](https://www.virustotal.com/gui/home/search) for it to see if there are matches. If more than 1 scanner report that it's malicious, it's a good chance it's a true positive. You can explore a bit more about what the file is on VirusTotal.