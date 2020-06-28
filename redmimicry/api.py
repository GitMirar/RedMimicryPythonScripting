import os
import requests
import struct
import time


class Api:
    """Implements a subset of the RedMimicry HTTP server API.

    :param host: hostname of the RedMimicry server
    :param auth_token: authentication token displayed in the cli putput of the RedMimicry server
    """

    api_port = 8080
    base_path = "%s:%d/v0/%s"
    polling_interval = 3

    def __init__(self, host, auth_token, tls=False):
        self.auth_token = auth_token
        self.host = host
        self.tls = tls
        self.active = True

    def stop(self):
        self.active = False

    def do_api_request(self, action, parameters):
        """Perform a POST request against the RedMimicry HTTP API.
        """
        request_url = self.base_path % (self.host, self.api_port, action)
        if self.tls:
            request_url = "https://" + request_url
        else:
            request_url = "http://" + request_url
        response = requests.post(request_url, json=parameters, headers= { "auth" : self.auth_token })
        if response.status_code != 200:
            raise Exception("api request failed", response)
        return response

    def list_implants(self):
        """List implants.
        """
        return self.do_api_request("list_implants", None).json()

    def get_agent_binary(self):
        """Download and return the Agent.exe binary.
        """
        return self.do_api_request("payload/assessment_agent", { "arch": "x64" }).content

    def get_shell_command_results(self, implant_id, command_id):
        """Return results of a given shell command identified by the command_id.
        """
        response = self.do_api_request("shell/get_command_results_paged", {
            "implant_id": implant_id,
            "command_id": command_id, 
            "index": 0
            }).json()
        return response

    def get_report(self):
        """Get the breach emulation report data.
        """
        ids = self.do_api_request("assessment/list_assessments", None).json()
        if ids == None:
            return None
        return [ self.do_api_request("assessment/get_assessment_data", { "implant_id": i}).json() for i in ids ]

    def shell(self, implant_id, shell_command):
        """Execute the provided shell_command string in the implant shell and returns the resulting shell output.

        Blocks until the command has completed..
        The API used here is identical with the frontend API.
        """
        command_id = struct.unpack("<I", os.urandom(4))[0]
        self.do_api_request("shell/exec", {
            "implant_id": implant_id,
            "commandline": shell_command,
            "command_id" : command_id ,
            })
        completed = False
        while not completed and self.active:
            results = self.get_shell_command_results(implant_id, command_id)
            for r in results:
                if r["completed"]:
                    return results
            time.sleep(self.polling_interval)
