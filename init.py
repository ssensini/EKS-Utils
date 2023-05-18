from InquirerPy import prompt
from prompt_toolkit.validation import Validator, ValidationError
import re
import sys
import subprocess
from subprocess import PIPE
import json
import os
import signal

from os.path import exists

print("################")
print("Ready to login to EKS?")
print("Insert all the required information and wait for the connection...")
print("################")


class AccessKeyIDValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('((?:ASIA|AKIA|AROA|AIDA)([A-Z0-7]{16}))')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid Access Key ID. Only upper case alphanumeric characters.",
                cursor_position=len(document.text))


class SecretAccessKeyValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('([a-zA-Z0-9+/]{40})')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text.lower()
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid Secret Access Key. A string of 40 digits is expected; only upper case alphanumeric characters, and '+' or '/' symbols are admitted.",
                cursor_position=len(document.text))


class StringValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('^[A-Za-z0-9-_]+$')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text.lower()
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid string, with no trailing spaces.",
                cursor_position=len(document.text))


class AccountIDValidator(Validator):

    def contains_symbols(self, value):
        regex = re.compile('^\d{12}$')
        is_match = regex.match(value) is not None
        return is_match

    def validate(self, document):
        try:
            check = document.text.lower()
            if not self.contains_symbols(check):
                raise ValueError
        except ValueError:
            raise ValidationError(
                message="Please enter a valid Account ID. Only 12 digits are admitted.",
                cursor_position=len(document.text))


def runcmd_call(cmd):
    try:
        p = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        # p = subprocess.call(cmd)
    except subprocess.CalledProcessError as suberr:
        p = suberr.returncode
    except Exception as e:
        print(e)
    return p


questions = [
    {
        "type": "input",
        "message": "Access Key ID:",
        "name": "access_key_id",
        "validate": AccessKeyIDValidator()
    },
    {
        "type": "input",
        "message": "Secret Access Key:",
        "name": "secret_access_key",
        "validate": SecretAccessKeyValidator()
    },
    {
        "type": "list",
        "message": "Region:",
        "choices": ["eu-central-1", "eu-west-1", "eu-west-2", "eu-south-1", "eu-west-3", "eu-south-2", "eu-north-1",
                    "eu-central-2"],
        "name": "region"
    },
    {
        "type": "input",
        "message": "Cluster name:",
        "name": "cluster_name",
        "validate": StringValidator()
    },
    {
        "type": "input",
        "message": "Account ID:",
        "name": "account_id",
        "validate": AccountIDValidator()
    },
    {
        "type": "input",
        "message": "Role name:",
        "name": "role_name",
        "validate": StringValidator()
    },
    {
        "type": "input",
        "message": "Username:",
        "name": "username"
    },
    {
        "type": "input",
        "message": "Service account to connect to the dashboard:",
        "name": "service_account"
    },
    {
        "type": "confirm", "message": "Confirm?",
        "name": "confirmation"
    },
]

use_config = [
    {
        "type": "confirm", "message": "File config.json with some configuration found. Use this file to proceed?",
        "name": "confirmation"
    },
]


def aws_configure(result):
    cmd = ['aws', 'configure', "set", "region", result["region"], "--profile", "eks-automation-py"]

    print('\n::: Set Region: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    if type(res) == int:
        print("Return code:", res)
        print(
            "Error during the execution. Run the command manually or check the documentation to get more details: http://bit.ly/3YdDA0f")
        sys.exit(-1)

    print("OK")

    cmd = ['aws', 'configure', "set", "aws_access_key_id", result["access_key_id"], "--profile", "eks-automation-py"]

    print('\n::: Set Access Key ID: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    if type(res) == int:
        print("Return code:", res)
        print(
            "Error during the execution. Run the command manually or check the documentation to get more details: http://bit.ly/3YdDA0f")
        sys.exit(-1)

    print("OK")

    cmd = ['aws', 'configure', "set", "aws_secret_access_key", result["secret_access_key"], "--profile",
           "eks-automation-py"]

    print('\n::: Set Secret Access Key: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    if type(res) == int:
        print("Return code:", res)
        print(
            "Error during the execution. Run the command manually or check the documentation to get more details: http://bit.ly/3YdDA0f")
        sys.exit(-1)

    print("OK")

    cmd = ['aws', 'configure', "set", "output", "json", "--profile", "eks-automation-py"]

    print('\n::: Set output to JSON by default: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    if type(res) == int:
        print("Return code:", res)
        print(
            "Error during the execution. Run the command manually or check the documentation to get more details: http://bit.ly/3YdDA0f")
        sys.exit(-1)

    print("Completed.")


def assume_role(result):
    cmd = ['aws', 'sts', "assume-role", "--role-arn",
           "arn:aws:iam::" + result["account_id"] + ":role/" + result["role_name"],
           "--role-session-name", result["username"], "--profile", "eks-automation-py",
           "--duration-seconds", "43200"]

    print('\n::: Assume role: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    if type(res) == int:
        print("Return code:", res)
        print(
            "Error during the execution. Run the command manually or check the documentation to get more details: http://bit.ly/3YdDA0f")
        sys.exit(-1)

    return res


def aws_set_assumed_profile(access_key_id, secret_access_key, session_token):
    cmd = ['aws', 'configure', "set", "aws_access_key_id", access_key_id, "--profile",
           "eks-assumed-profile"]

    print('\n::: Set Access Key ID: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    if type(res) == int:
        print("Return code:", res)
        print(
            "Error during the execution. Run the command manually or check the documentation to get more details: http://bit.ly/3YdDA0f")
        sys.exit(-1)

    print("OK")

    cmd = ['aws', 'configure', "set", "aws_secret_access_key", secret_access_key, "--profile",
           "eks-assumed-profile"]

    print('\n::: Set Secret Access Key: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    if type(res) == int:
        print("Return code:", res)
        print(
            "Error during the execution. Run the command manually or check the documentation to get more details: http://bit.ly/3YdDA0f")
        sys.exit(-1)

    print("OK")

    cmd = ['aws', 'configure', "set", "aws_session_token", session_token, "--profile",
           "eks-assumed-profile"]

    print('\n::: Set Secret Access Key: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    if type(res) == int:
        print("Return code:", res)
        print(
            "Error during the execution. Run the command manually or check the documentation to get more details: http://bit.ly/3YdDA0f")
        sys.exit(-1)

    print("OK")


def remove_profile(profile):
    home = os.path.expanduser('~')

    if os.name == "nt":
        file = os.path.join(home, ".aws\\credentials")
    else:
        file = os.path.join(home, ".aws/credentials")

    try:
        with open(file, "r") as f:
            lines = f.readlines()
            for number, line in enumerate(lines):
                if line.strip("\n") == profile:
                    start_index = number
    except FileNotFoundError as e:
        print(e)
        print("Configuration not found.")


def connect_to_dashboard(result):
    cmd = ['kubectl', '-n', 'kubernetes-dashboard', 'create', 'token', result["service_account"], "--duration=12h"]

    print('\n::: Getting token to connect to the Kubernetes Dashboard: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    return res.decode("utf-8")


def proxy_to_dashboard():
    cmd = ['kubectl', 'proxy']

    print('\n::: Connecting to Kubernetes dashboard... ' + ' '.join(cmd) + ' ::: \n')

    try:
        p = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE)
        print("You should now be authenticated.")
        print("Try with 'kubectl get pods' now to use the CLI, or connect to the following URL to connect")
        print("")
        print(
            "http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#!/login")
        print("")
        print("To stop the 'kubectl proxy', use Ctrl+C")
        print("-------")
        for line in p.stdout:
            print(line.decode("UTF-8"))
    except subprocess.CalledProcessError:
        print("Error during the connection to the dashboard. Check the previous logs and retry.")
        sys.exit(0)
    except Exception as e:
        print("Error during the connection to the dashboard. Check the previous logs and retry.")
        sys.exit(0)

def prompt_questions(questions):
    result = prompt(questions)
    if result["confirmation"]:
        print("Proceeding with inserted data.")
        return result
    else:
        print("To enter again the data, re-run the script. Bye!")
        sys.exit()


def main():
    # Step 0: preparing the environment

    result = None

    try:
        with open('config.json') as file:
            file_exists = exists("config.json")
            file_empty = False if os.stat("config.json").st_size == 0 else True
            json_object = json.load(file)
            if file_exists and file_empty != False and json_object and len(json_object) > 0:
                result = prompt(use_config)
                if result["confirmation"]:
                    print("Proceeding with existing data in config.json.")
                    result = json_object
                else:
                    result = prompt_questions(questions)
            else:
                result = prompt_questions(questions)

    except KeyboardInterrupt:
        print("User exited. Bye!")
    except FileNotFoundError as e:
        result = prompt_questions(questions)
    except Exception as e:
        print(e)
        print("Syntax error in config.json. Lint that file or REMOVE it!")
        sys.exit()

    # Store file for future use

    json_object = json.dumps(result, indent=4)

    with open("config.json", "w") as outfile:
        outfile.write(json_object)

    # Remove old profiles and keys

    remove_profile("[eks-automation-py]")

    # Step 1: AWS configure

    aws_configure(result)

    # Step 2: assume role through STS

    res = assume_role(result)

    # Step 3: replace/create profile

    remove_profile("[eks-assumed-profile]")

    credentials = json.loads(res)

    access_key_id = credentials["Credentials"]["AccessKeyId"]
    secret_access_key = credentials["Credentials"]["SecretAccessKey"]
    session_token = credentials["Credentials"]["SessionToken"]

    print(access_key_id)
    print(secret_access_key)
    print(session_token)

    aws_set_assumed_profile(access_key_id, secret_access_key, session_token)

    print("Completed.")

    # Step 4: login to EKS

    cmd = ["aws", "eks", "update-kubeconfig", "--name", result["cluster_name"], "--profile", "eks-assumed-profile",
           "--region", result["region"]]

    print('\n::: Assume role: ' + ' '.join(cmd) + ' ::: \n')

    res = runcmd_call(cmd)

    if type(res) == int:
        print("Return code:", res)
        print(
            "Error during the execution. Run the command manually or check the documentation to get more details: http://bit.ly/3YdDA0f")
        sys.exit(-1)

    # Step 5 (optional): if a dashboard is available, get the token to access it.


    try:

        if None != result["service_account"]:
            token = connect_to_dashboard(result)

            print("::: Generated token (valid for 12 hours) :::")
            print("::: COPY AND PASTE THIS :::")
            print("============================================")
            print(token)
            print("============================================")


            proxy_to_dashboard()

    except KeyboardInterrupt:
        print("")
        print("Closing connection to Kubernetes cluster...")
        print("Bye!")



main()
