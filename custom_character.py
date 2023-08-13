import argparse
import os
import json
import requests
import time

_apiServerUrl = 'https://service.deepmotion.com'

def check_json(fpath):
    if not os.path.exists(fpath):
        raise argparse.ArgumentTypeError('Filename %r doesn\'t exist.' % fpath)
    
    if fpath[-5:] != '.json':
        raise argparse.ArgumentTypeError('%r is not a JSON file.' % fpath)

    return fpath

def parse_user_credentials():
    parser = argparse.ArgumentParser(prog='DMBT API CLI Demo', 
            description='Specify JSON file with user credentials')
    parser.add_argument('credentials', 
        nargs='?', type=check_json, 
        help='A JSON file must be specified')

    parser.add_argument('video', type=str, help='A video file must be specified')
    args = parser.parse_args()
    return args.credentials

def read_user_credentials(fpath):
    with open(fpath) as f:
        jsonData = json.load(f)
        global _sessionCredentials
        _sessionCredentials = jsonData['clientId'], jsonData['clientSecret']
        global session
        session = get_session()
        print('Credentials successfully read. \n')

def get_session():
    authUrl = _apiServerUrl + '/session/auth'
    session = requests.Session()
    session.auth = _sessionCredentials
    request = session.get(authUrl)
    if request.status_code == 200:
        return session
    else:
        print('Failed to authenticate ' + str(request.status_code) + '\n')

def get_response(urlPath):
    respUrl = _apiServerUrl + urlPath
    resp = session.get(respUrl)
    if resp.status_code == 200:
        return resp
    else:
        print('Failed to contact server ' + resp.status_code + '\n')

def list_successes():
    successes = json.loads(get_response('/list/SUCCESS').text)
    return successes


def main():
    read_user_credentials(args)
    print(list_successes())


if __name__ == "__main__":
    args = parse_user_credentials()
    main()

    curr_path = os.path.abspath(os.path.dirname(__file__))
    input_path = "inputs/KaranBadminton.MOV"
    full_path = os.path.normpath(os.path.join(curr_path, input_path))

    v_file = None
    with open(full_path, 'rb') as f:
        v_file = f.read()
    if v_file == None:
        raise argparse.ArgumentParserError('Could not read %r.' % full_path)

    