import sys
import os
from flask import Flask, request, jsonify
from pathlib import Path
import jsonpatch
import base64


admission_controller = Flask(__name__)

@admission_controller.before_request
def log_request():
    admission_controller.logger.debug("Request in JSON      %s\n", str(request.get_json()))
    admission_controller.logger.debug("Request data:        %s\n", request.data)
    admission_controller.logger.debug("Request args:        %s\n", request.args)
    admission_controller.logger.debug("Request form:        %s\n", request.form)
    admission_controller.logger.debug("Request ep  :        %s\n", request.endpoint)
    admission_controller.logger.debug("Request method:      %s\n", request.method)
    admission_controller.logger.debug("Request remote_addr: %s\n", request.remote_addr)
    return None

@admission_controller.route("/validate/checklabels", methods=["POST"])
def deployment_webhook():
    request_info = request.get_json()

    if request_info["request"]["object"]["metadata"]["labels"].get("creator"):
        
        return_allowed = jsonify(
            {
                "apiVersion": request_info.get("apiVersion"),
                "kind": request_info.get("kind"),
                "response": {
                    "uid": request_info["request"].get("uid"),
                    "allowed": True,
                },
            }
          )
        admission_controller.logger.debug("response if allowed %s\n", str(return_allowed.get_json()))
        return return_allowed
    return_denied = jsonify(
        {
            "apiVersion": request_info.get("apiVersion"),
            "kind": request_info.get("kind"),
            "response": {
                "uid": request_info["request"].get("uid"),
                "allowed": False,
                "status": {"message": "Deployment must have 'creator' label to be admitted in this namespace"},
            },
        }
      )
    admission_controller.logger.debug("response if denied %s\n",str(return_denied.get_json()))
    return return_denied 


if __name__ == "__main__":
    admission_controller.debug =  os.getenv("DEBUG", 'False').lower() in ('true', '1')
    admission_controller.run(
        host='0.0.0.0')

