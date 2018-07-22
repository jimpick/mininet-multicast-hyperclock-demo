const fs = require('fs')
const hyperclock = require('hyperclock')
const ram = require('random-access-memory')
const swarmDefaults = require('dat-swarm-defaults')
const discSwarm = require('discovery-swarm')

const clock = hyperclock(ram, {interval: 1000})

clock.ready(() => {
  fs.writeFileSync('./key', clock.key)
  console.log('Key:', clock.key.toString('hex'))
  console.log('Discovery Key:', clock.discoveryKey.toString('hex'))

  // TCP
  const sw = discSwarm(swarmDefaults({
    tcp: true,
    utp: false,
    dht: false,
    live: true,
    hash: false,
    dns: {
      server: ['192.168.1.1'], domain: 'dat.local'
    },
    stream: () => clock.replicate({live: true})
  }))
  sw.join(clock.discoveryKey)
  sw.on('connection', function (peer, info) {
    console.log('new connection', info.host, info.port,
                info.initiator ? 'outgoing' : 'incoming') 
    peer.on('close', function () {
      console.log('peer disconnected')
    })
  })

  clock.createReadStream({live: true}).on('data', console.log)
})


