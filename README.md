# hidex_module

Contains `hidex_node`, providing an interface and adapter that works alongside the Hidex Plate Reader's first party driver to control the instrument.

## Installation Notes

To make the server accessible, run the following in a terminal as Administrator

```
netsh http add urlacl url=http://+:2005/ user=<USER> listen=yes delegate=yes
```

Replace `2005` with the port you intend to use, if it differs from the default, and `<USER>` with the username that will be running the server (you may need to use the form `DOMAIN/USER`)

To interface with the module from another device, you'll need to [open up the port](https://www.windowscentral.com/how-open-port-windows-firewall) you intend to run the module's server on (2005 by default). 
