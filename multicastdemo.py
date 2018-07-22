#!/usr/bin/python

"""
linuxrouter.py: Example network with Linux IP router

This example converts a Node into a router using IP forwarding
already built into Linux.

The example topology creates a router and three IP subnets:

    - 192.168.1.0/24 (r0-eth1, IP: 192.168.1.1)
    - 172.16.0.0/12 (r0-eth2, IP: 172.16.0.1)
    - 10.0.0.0/8 (r0-eth3, IP: 10.0.0.1)

Each subnet consists of a single host connected to
a single switch:

    r0-eth1 - s1-eth1 - h1-eth0 (IP: 192.168.1.100)
    r0-eth2 - s2-eth1 - h2-eth0 (IP: 172.16.0.100)
    r0-eth3 - s3-eth1 - h3-eth0 (IP: 10.0.0.100)

The example relies on default routing entries that are
automatically created for each router interface, as well
as 'defaultRoute' parameters for the host interfaces.

Additional routes may be added to the router or hosts by
executing 'ip route' or 'route' commands on the router or hosts.
"""


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import os

print 'PATH', os.environ['PATH']

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )
        self.cmd( 'sysctl net.ipv4.icmp_echo_ignore_broadcasts=0' )
        self.cmd( 'sysctl net.ipv4.conf.r0-eth1.force_igmp_version=2' )
        self.cmd( 'sysctl net.ipv4.conf.r0-eth2.force_igmp_version=2' )
        self.cmd( 'sysctl net.ipv4.conf.r0-eth3.force_igmp_version=2' )
        self.cmd( '/opt/smcroute/sbin/smcrouted -l debug -I smcroute-r0' )
        self.cmd( 'sleep 1')
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 '
                  'add r0-eth1 239.0.0.1 r0-eth2 r0-eth3' )
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 '
                  'add r0-eth2 239.0.0.2 r0-eth1 r0-eth3' )
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 '
                  'add r0-eth3 239.0.0.3 r0-eth1 r0-eth2' )
        self.cmd( 'npx dns-discovery listen &' )
        self.dnsDiscoveryPid = int( self.cmd( 'echo $!' ) )
        info( '\ndns-discovery PID:', self.dnsDiscoveryPid )


    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 kill' )
        self.cmd( 'kill %d' % self.dnsDiscoveryPid )
        super( LinuxRouter, self ).terminate()

class EdgeNode( Node ):
    "A Node with multicast stuff."

    def config( self, **params ):
        super( EdgeNode, self).config( **params )
        intfName = self.intfNames()[0]
        self.cmd( 'sysctl net.ipv4.icmp_echo_ignore_broadcasts=0' )
        self.cmd( 'route add -net 224.0.0.0 netmask 240.0.0.0 dev ' + intfName )
        self.cmd( '/opt/smcroute/sbin/smcrouted -l debug -I smcroute-' + self.name )
        self.cmd( 'sleep 1')
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-' + self.name +
                  ' join ' + intfName + ' 239.0.0.1' )
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-' + self.name +
                  ' join ' + intfName + ' 239.0.0.2' )
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-' + self.name +
                  ' join ' + intfName + ' 239.0.0.3' )

    def terminate( self ):
        self.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-' + self.name + ' kill' )
        super( EdgeNode, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):

        defaultIP = '192.168.1.1/24'  # IP address for r0-eth1
        router = self.addNode( 'r0', cls=LinuxRouter, ip=defaultIP )

        s1, s2, s3 = [ self.addSwitch( s ) for s in ( 's1', 's2', 's3' ) ]

        self.addLink( s1, router, intfName2='r0-eth1',
                      params2={ 'ip' : defaultIP } )  # for clarity
        self.addLink( s2, router, intfName2='r0-eth2',
                      params2={ 'ip' : '172.16.0.1/12' } )
        self.addLink( s3, router, intfName2='r0-eth3',
                      params2={ 'ip' : '10.0.0.1/8' } )

        h1 = self.addHost( 'h1',
                           cls=EdgeNode,
                           ip='192.168.1.100/24',
                           defaultRoute='via 192.168.1.1' )
        h2 = self.addHost( 'h2',
                           cls=EdgeNode,
                           ip='172.16.0.100/12',
                           defaultRoute='via 172.16.0.1' )
        h3 = self.addHost( 'h3', 
                           cls=EdgeNode,
                           ip='10.0.0.100/8',
                           defaultRoute='via 10.0.0.1' )

        for h, s in [ (h1, s1), (h2, s2), (h3, s3) ]:
            self.addLink( h, s )

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )  # controller is used by s1-s3
    net.start()

    """
    r0 = net['r0']
    r0.cmd( 'sysctl net.ipv4.conf.r0-eth1.force_igmp_version=2' )
    r0.cmd( 'sysctl net.ipv4.conf.r0-eth2.force_igmp_version=2' )
    r0.cmd( 'sysctl net.ipv4.conf.r0-eth3.force_igmp_version=2' )
    r0.cmd( '/opt/smcroute/sbin/smcrouted -l debug -I smcroute-r0' )
    r0.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 add r0-eth1 239.0.0.1 r0-eth2 r0-eth3' )
    """

    info( '*** Routing Table on Router:\n' )
    info( net[ 'r0' ].cmd( 'route' ) )
    CLI( net )
    # r0.cmd( '/opt/smcroute/sbin/smcroutectl -I smcroute-r0 kill' )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
