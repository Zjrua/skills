---
name: zerotier
description: Install, configure, and manage ZeroTier virtual networks — join networks, set up Moon relay nodes, and connect devices across NAT.
tags: [vpn, zerotier, moon, networking]
---

# ZeroTier

ZeroTier is a zero-config VPN / virtual LAN overlay. This skill covers installation, network joining, and Moon relay node setup.

## Install

```bash
curl -s https://install.zerotier.com | bash
```

Installs `zerotier-one` package, enables and starts the systemd service. Node address is printed at the end (e.g. `32344743e0`).

## Join a Network

```bash
zerotier-cli join <network-id>
```

Status will be `ACCESS_DENIED` until the node is authorized in the [ZeroTier Central](https://my.zerotier.com) dashboard → Network → Members → ✅ Authorize.

Verify with `zerotier-cli listnetworks` — status should become `OK` and show assigned IP.

## Moon Relay Node Setup

Moon nodes act as stable relay/coordination servers, reducing latency and improving NAT traversal for peers in the same network.

### When to set up a Moon
- Server has a **public static IP**
- Peers are in China or behind restrictive NAT (ZeroTier's default PLANET servers are overseas, high latency)
- You want faster peer-to-peer hole-punching

### Steps (on the server)

```bash
# 1. Generate initial moon definition
cd /var/lib/zerotier-one
zerotier-idtool initmoon identity.public > moon.json

# 2. Edit moon.json — set stableEndpoints to public IP:port
#    Port 9993 is ZeroTier's default
#    "stableEndpoints": ["YOUR_PUBLIC_IP/9993"]

# 3. Generate signed moon file
zerotier-idtool genmoon moon.json
# Output: 000000<node-id>.moon

# 4. Place in moons.d
mkdir -p /var/lib/zerotier-one/moons.d
cp 000000*.moon moons.d/

# 5. Restart service
systemctl restart zerotier-one
```

### Pitfalls

- **Moon node shows as LEAF in its own `listpeers`** — this is expected. The moon node doesn't relay to itself; it appears as MOON only to *other* nodes that orbit it.
- **`stableEndpoints` must use the public IP**, not the ZeroTier virtual IP. Include the port: `1.2.3.4/9993`.
- If the server is behind a firewall, ensure **UDP 9993** is open inbound.
- The moon file name format is `000000<16-char-node-id>.moon` (zero-padded to 10 digits).

### How other nodes join the Moon

**Method A: orbit command (recommended)**
```bash
zerotier-cli orbit <moon-node-id> <moon-node-id>
```
Both arguments are the moon node's address (e.g. `32344743e0 32344743e0`).

**Method B: copy moon file manually**
Place the `.moon` file in the device's `moons.d/` directory, then restart ZeroTier:

| OS | Path |
|---|---|
| Linux | `/var/lib/zerotier-one/moons.d/` |
| macOS | `/Library/Application Support/ZeroTier/One/moons.d/` |
| Windows | `C:\ProgramData\ZeroTier\One\moons.d\` |

### Verify Moon is working (from a peer node)

```bash
zerotier-cli listpeers | grep MOON
# Should show: <moon-id> <public-ip>/9993 ... MOON
```

## Useful Commands

| Command | Purpose |
|---|---|
| `zerotier-cli info` | Node address, version, online status |
| `zerotier-cli listnetworks` | Joined networks + assigned IPs |
| `zerotier-cli listpeers` | All peers (PLANET/MOON/LEAF) |
| `zerotier-cli join <id>` | Join a network |
| `zerotier-cli leave <id>` | Leave a network |
| `zerotier-cli orbit <moon-id> <moon-id>` | Join a moon |
| `zerotier-cli deorbit <moon-id>` | Leave a moon |
| `zerotier-cli status` | Service status |

## Server Environment

ZeroTier service runs as `zerotier-one` user. Moon files in `moons.d/` must be readable by this user. Config and identity live in `/var/lib/zerotier-one/`.
