# linux-router
Python script that configures a linux router.

The script takes a JSON config and writes config files for udev, systemd-networkd, dnsmasq, /etc/hosts, iptables, pppd.

Designed to work on top of Arch Linux, but with minimal modifications it can be made to work on other distros.

See examples/ for config examples.

- exmaples/movistar.json - Simple LAN with Movistar fibra optica uplink. If you have the OLD setup with the modem+router as separate gadgets: plug the wan port into the modem and ditch the router.
- exmaples/movistar-new.json - Simple LAN with Movistar fibra optica uplink. If you have the NEW setup with the all-in-one modem/router. You will have to login to the thing and switch it to "monopuesto".
- examples/complex.json - Complex LAN with 2 uplinks (movistar + static IP) and 3 vlans: management, main usage, security cameras.

Installation instructions and more features (web UI anyone?) coming soon.
