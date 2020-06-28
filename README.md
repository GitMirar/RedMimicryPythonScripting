# RedMimicry Python Scripting

This repository contains a library which provides a Python API for some of the functionality of the HTTP server API.

## [bot.py](bot.py) -  Agent Scripting Example

A simple bot that executes few typical host enumeration commands for agents which are running in the *svchost.exe* process. This is the case after the *Winnti (2015)* breach emulation playbook executed successfully and can be used to extend the emulation playbook.

```text
usage: bot.py [-h] -H HOSTNAME -t AUTH_TOKEN [-v] [-s]

An actor emulation script for RedMimicry

optional arguments:
  -h, --help            show this help message and exit
  -H HOSTNAME, --hostname HOSTNAME
                        hostname of the RedMimicry server
  -t AUTH_TOKEN, --auth-token AUTH_TOKEN
                        RedMimicry server auth-token
  -v, --verbose         verbose output
  -s, --tls;            enable TLS
```
