# mininet-multicast-hyperclock-demo

This is a mininet setup based on:

* https://fojta.wordpress.com/2014/09/24/troubleshooting-multicast-with-linux/
* https://github.com/troglobit/smcroute
* https://github.com/mininet/mininet/blob/master/examples/linuxrouter.py

# Requirements

* Ubuntu 16.04 LTS
* apt install mininet
* sudo apt-get install openvswitch-testcontroller
* sudo ln -s /usr/bin/ovs-testcontroller /usr/bin/controller

(see https://stackoverflow.com/questions/21687357/mininet-ovs-controller-can-t-be-loaded-and-run)

Install smcroute from source:

```
./configure --prefix=/opt/smcroute --sysconfdir=/etc --localstatedir=/var
make
sudo make install
```

# Running demo

```
$ sudo ./multicastdemo.py
PATH /usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin
*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 r0
*** Adding switches:
s1 s2 s3
*** Adding links:
(h1, s1) (h2, s2) (h3, s3) (s1, r0) (s2, r0) (s3, r0)
*** Configuring hosts
h1 h2 h3 r0
dns-discovery PID: 11930
*** Starting controller
c0
*** Starting 3 switches
s1 s2 s3 ...
*** Routing Table on Router:
Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
10.0.0.0        *               255.0.0.0       U     0      0        0 r0-eth3
172.16.0.0      *               255.240.0.0     U     0      0        0 r0-eth2
192.168.1.0     *               255.255.255.0   U     0      0        0 r0-eth1
*** Starting CLI:
mininet> xterm r0 h1 h1 h1 h2 h3
mininet>
```

In r0 xterm:

```
g# /opt/smcroute/sbin/smcroutectl -I smcroute-r0 show
ROUTE (S,G)                        INBOUND             PACKETS      BYTES OUTBOUND                                     
(*, 239.0.0.3)                     r0-eth3          0000000000 0000000000  r0-eth1 r0-eth2
(*, 239.0.0.2)                     r0-eth2          0000000000 0000000000  r0-eth1 r0-eth3
(*, 239.0.0.1)                     r0-eth1          0000000000 0000000000  r0-eth2 r0-eth3
```

In h1 xterm #1:

```
# node server
Key: b2688ce718d932d7a7f279a3fc68df19b15be5aad3a9d62a8ddb47298e705bf8
Discovery Key: 01063b032d2164dc0752b6d42b26ead905b3d478f1ac0bfab48aead5afc31609
{ type: 'hyperclock' }
{ time: 1532299330289,
  random: <Buffer 51 0e c2 73 4c e6 fd 79 ed 29 09 ec 9f 14 ec 01 54 38 90 e0 cc 51 48 f0 65 2d 28 14 d3 28 1b ab> }
{ time: 1532299331294,
  random: <Buffer 12 01 b0 47 3b 15 86 29 44 50 19 d1 7e 99 32 f8 2e e7 db 18 fc 2c ae da d9 b8 fb 8a e5 54 46 c1> }
{ time: 1532299332298,
  random: <Buffer a8 77 cd f1 75 7f ef 3b 9f 88 0f bf 67 50 e8 85 67 30 a8 c2 94 72 c3 c4 39 1a 0f 4d 32 f6 19 6a> }
{ time: 1532299333299,
  random: <Buffer f8 c9 5c 08 a1 84 bd 4e 09 13 ef 86 21 aa 3b e3 48 ae e9 46 01 67 c8 e2 f2 ef b4 44 9e 65 52 91> }
{ time: 1532299334301,
  random: <Buffer f7 b4 22 35 8b e9 42 9d 46 b8 4f 7f d9 8f 42 3a ce 05 cc 59 4d 30 a8 4b f2 12 5f 6c bf d2 32 6d> }

...
```

In h1 xterm #2:

```
# node proxy-transmitter
Proxying feed from swarm to multicast
Key: b2688ce718d932d7a7f279a3fc68df19b15be5aad3a9d62a8ddb47298e705bf8
Discovery Key: 01063b032d2164dc0752b6d42b26ead905b3d478f1ac0bfab48aead5afc31609
new connection 192.168.1.100 34421 outgoing
Append 17
Download 0 <Buffer 0a 0a 68 79 70 65 72 63 6c 6f 63 6b>
Jim length 17
Download 2 <Buffer 08 de 8d a1 a1 cc 2c 12 20 12 01 b0 47 3b 15 86 29 44 50 19 d1 7e 99 32 f8 2e e7 db 18 fc 2c ae da d9 b8 fb 8a e5 54 46 c1>
Download 3 <Buffer 08 ca 95 a1 a1 cc 2c 12 20 a8 77 cd f1 75 7f ef 3b 9f 88 0f bf 67 50 e8 85 67 30 a8 c2 94 72 c3 c4 39 1a 0f 4d 32 f6 19 6a>
Download 4 <Buffer 08 b3 9d a1 a1 cc 2c 12 20 f8 c9 5c 08 a1 84 bd 4e 09 13 ef 86 21 aa 3b e3 48 ae e9 46 01 67 c8 e2 f2 ef b4 44 9e 65 52 91>
Download 5 <Buffer 08 9d a5 a1 a1 cc 2c 12 20 f7 b4 22 35 8b e9 42 9d 46 b8 4f 7f d9 8f 42 3a ce 05 cc 59 4d 30 a8 4b f2 12 5f 6c bf d2 32 6d>

...
```

In h1 xterm #3:

```
# node client
Loading clock feed.
Bootstrapping off of TCP, then switching to multicast-only...
Key: b2688ce718d932d7a7f279a3fc68df19b15be5aad3a9d62a8ddb47298e705bf8
Discovery Key: 01063b032d2164dc0752b6d42b26ead905b3d478f1ac0bfab48aead5afc31609
new connection 192.168.1.100 44595 outgoing
new connection 192.168.1.100 34421 outgoing
Length 24
Bootstrapping (TCP): 1532299353324
Bootstrapping (TCP): 1532299354324
Bootstrapping (TCP): 1532299355326
new connection 172.16.0.100 39291 outgoing
Closing TCP swarm
peer disconnected
peer disconnected
peer disconnected
Multicast only: 1532299356328
Multicast only: 1532299357330
Multicast only: 1532299358330
Multicast only: 1532299359331

...
```

In h2 xterm:

```
# node client
Loading clock feed.
Bootstrapping off of TCP, then switching to multicast-only...
Key: b2688ce718d932d7a7f279a3fc68df19b15be5aad3a9d62a8ddb47298e705bf8
Discovery Key: 01063b032d2164dc0752b6d42b26ead905b3d478f1ac0bfab48aead5afc31609
new connection ::ffff:192.168.1.100 57852 incoming
new connection ::ffff:192.168.1.100 57854 incoming
new connection ::ffff:192.168.1.100 57856 incoming
peer disconnected
new connection 192.168.1.100 34421 outgoing
Length 27
peer disconnected
Bootstrapping (TCP): 1532299356328
Bootstrapping (TCP): 1532299357330
Closing TCP swarm
peer disconnected
peer disconnected
Multicast only: 1532299358330
Multicast only: 1532299359331
Multicast only: 1532299360333
Multicast only: 1532299361334

...
```

In h3 xterm:

```
o# node client
Loading clock feed.
Bootstrapping off of TCP, then switching to multicast-only...
Key: b2688ce718d932d7a7f279a3fc68df19b15be5aad3a9d62a8ddb47298e705bf8
Discovery Key: 01063b032d2164dc0752b6d42b26ead905b3d478f1ac0bfab48aead5afc31609
new connection ::ffff:192.168.1.100 36800 incoming
new connection ::ffff:192.168.1.100 36802 incoming
peer disconnected
new connection 192.168.1.100 34421 outgoing
Length 30
Bootstrapping (TCP): 1532299359331
Bootstrapping (TCP): 1532299360333
Bootstrapping (TCP): 1532299361334
Closing TCP swarm
peer disconnected
peer disconnected
Multicast only: 1532299362335
Multicast only: 1532299363335
Multicast only: 1532299364338
Multicast only: 1532299365340

...
```
