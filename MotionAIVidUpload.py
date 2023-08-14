import argparse
import os
import json
import requests
import time
import streamlit as st

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
        main_options()


def get_response(urlPath):
    respUrl = _apiServerUrl + urlPath
    resp = session.get(respUrl)
    if resp.status_code == 200:
        return resp
    else:
        print('Failed to contact server ' + resp.status_code + '\n')
        main_options()


def print_list_portion(inputList, nameDelim, idDelim, timeDelim, currPos):
    endOfPortion = currPos + 25
    if endOfPortion > len(inputList):
        endOfPortion = len(inputList)
    while currPos < endOfPortion:
        cPosStr = str(currPos + 1) + ')'
        while len(cPosStr) < 6:
            cPosStr += ' '
        print(cPosStr + inputList[currPos][nameDelim], end='')
        if idDelim != '':
            print('\t\t' + inputList[currPos][idDelim], end='')
        if timeDelim != '':
            print('\t\t' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(inputList[currPos][timeDelim] / 1000.0)),
                  end='')
        currPos += 1
        print('')

    listFinished = False
    if endOfPortion >= len(inputList):
        listFinished = True
    listStatus = (currPos, listFinished)
    return listStatus


def call_print_list_portion(inputList, nameDelim, idDelim='', timeDelim=''):
    currPos = 0
    listComplete = False
    selection = 'Y'
    while not listComplete:
        print('')
        if currPos != 0:
            selection = st.text_input('Press Y to show more inputs, N to exit: ')

        selection = selection.lower()
        if selection == 'n':
            break
        if selection != 'y':
            st.write('Please use "y", "Y", "n", or "N"')
            continue
        print('')
        listStatus = print_list_portion(inputList, nameDelim, idDelim, timeDelim, currPos)
        listComplete = listStatus[1]
        currPos = listStatus[0]


def list_models():
    print('')
    respText = get_response('/character/listModels').text
    jsonResp = json.loads(respText)
    call_print_list_portion(jsonResp['list'], 'name', 'id')
    print('')
    main_options()


def get_job_list(listPath):
    respText = get_response(listPath).text
    jsonResp = json.loads(respText)
    return jsonResp


def list_jobs():
    print("""\n=== Job Status List Filter ===
    1) IN PROGRESS
    2) SUCCEEDED
    3) FAILED
    4) ALL\n""")
    selection = int(input('Select option number from the list: '))
    print('')
    jobList = []

    if selection == 1 or selection == 4:
        jsonResp = get_job_list('/list/PROGRESS')
        print('Jobs in progress: ' + str(jsonResp['count']))
        jobList += jsonResp['list']

    if selection == 2 or selection == 4:
        jsonResp = get_job_list('/list/SUCCESS')
        print('Jobs succeeded: ' + str(jsonResp['count']))
        jobList += jsonResp['list']

    if selection == 3 or selection == 4:
        jsonResp = get_job_list('/list/FAILURE')
        print('Jobs failed: ' + str(jsonResp['count']))
        jobList += jsonResp['list']

    call_print_list_portion(sorted(jobList, key=lambda x: x['ctime'], reverse=True), 'fileName', 'rid', 'ctime')

    print('')
    main_options()


download_format = {
    1: 'bvh',
    2: 'fbx',
    3: 'mp4'
}
character_select = {
    1: 'male-young',
    2: 'male-normal',
    3: 'male-fat',
    4: 'female-normal',
    5: 'female-thin',
    6: 'child'
}


def download_job(file_path, fileRid):
#     print('download job started\n')
#     print("""A list of jobs will appear. Once you find the job you
# want to download, exit the listing and input the number of the
# job you want to download.\n""")
#     input('Press Enter to continue...\n')
    jobListJson = get_job_list('/list/SUCCESS')
    numJobs = jobListJson['count']
    jobListJson['list'] = sorted(jobListJson['list'], key=lambda x: x['ctime'], reverse=True)
    #st.write('Jobs available for download: ' + str(numJobs))
    print('Jobs available for download: ' + str(numJobs))
    call_print_list_portion(jobListJson['list'], 'fileName', 'rid', 'ctime', )
    jobSelection = 1
    rid = jobListJson['list'][jobSelection - 1]['rid']
    while rid != fileRid:
        time.sleep(10)
        print(rid)
        print(fileRid)
        jobListJson = get_job_list('/list/SUCCESS')
        jobListJson['list'] = sorted(jobListJson['list'], key=lambda x: x['ctime'], reverse=True)
        rid = jobListJson['list'][jobSelection - 1]['rid']



    dPath = os.getcwd() + os.path.sep + rid + '.'
    downloadResp = get_response('/download/' + rid)
    downloadRespTxt = downloadResp.text
    downloadRespJson = json.loads(downloadRespTxt)
    print(downloadRespJson)
    if downloadRespJson['count'] > 0:
        urls = downloadRespJson['links'][0]['urls']
        for fileUrl in urls:
            files = fileUrl['files']

            for file in files:
                if 'bvh' in file:
                    uri = file['bvh']
                    dowloadResp = session.get(uri)
                    with open(dPath + 'bvh', 'wb') as f:
                        f.write(dowloadResp.content)
                        print('\nFile saved to ' + dPath + 'bvh')
                if 'fbx' in file:
                    uri = file['fbx']
                    dowloadResp = session.get(uri)
                    with open(dPath + 'zip', 'wb') as f:
                        f.write(dowloadResp.content)
                        print('\nFile saved to ' + dPath + 'zip')
                if 'mp4' in file:
                    uri = file['mp4']
                    #st.video(uri, format="video/mp4", start_time=0)
                    dowloadResp = session.get(uri)
                    st.video(dowloadResp.content, format="video/mp4", start_time=0)
    print('')


def new_job():
    currPath = os.path.abspath(os.path.dirname(__file__))
    inputPath = st.text_input('Input relative path to video to upload: ')
    file_name = os.path.basename(inputPath)
    fullPath = os.path.normpath(os.path.join(currPath, inputPath))
    print(fullPath)
    vFile = None
    if not os.path.exists(fullPath):
        raise argparse.ArgumentTypeError('Filename %r doesn\'t exist.' % fullPath)
    with open(fullPath, 'rb') as f:
        vFile = f.read()
    if vFile == None:
        raise argparse.ArgumentTypeError('Could not read %r.' % fullPath)

    charResp = get_response('/character/listModels').text
    charRespJson = json.loads(charResp)
    charList = charRespJson['list']
    call_print_list_portion(charList, 'name', 'id')
    print(str(len(charList) + 1) + ') None')
    charSel = 1
    modelStr = ''
    if charSel != len(charList) + 1:
        modelStr = 'model=' + charList[charSel - 1]['id']
    print(modelStr)

    formatProcess = "formats=bvh,fbx,mp4"

    headerContent = {'Content-length': str(len(vFile)), 'Content-type': 'application/octet-stream'}
    vPath = os.path.basename(fullPath)
    vName, vExt = os.path.splitext(vPath)

    uploadUrl = _apiServerUrl + '/upload?name=' + vName + '&resumable=0'
    resp = session.get(uploadUrl)
    if resp.status_code == 200:
        jsonResp = json.loads(resp.text)
        gcsUrl = jsonResp['url']
        uploadResp = session.put(gcsUrl, headers=headerContent, data=vFile)
        if uploadResp.status_code == 200:
            processUrl = _apiServerUrl + '/process'
            processCfgJson = None
            if modelStr == '':
                processCfgJson = {
                    "url": gcsUrl,
                    "processor": "video2anim",
                    "params": [
                        "config=configDefault",
                        formatProcess
                    ]
                }
            else:
                processCfgJson = {
                    "url": gcsUrl,
                    "processor": "video2anim",
                    "params": [
                        "config=configDefault",
                        formatProcess,
                        modelStr
                    ]
                }
            processResp = session.post(processUrl, json=processCfgJson)
            if processResp.status_code == 200:
                pRespJson = json.loads(processResp.text)
                st.write('Job is processing: ' + pRespJson['rid'])
            else:
                st.write(processResp.status_code)
                st.write('failed to process')
        else:
            st.write(uploadResp.status_code)
            st.write('failed to upload')

    print('')
    download_job(file_name, pRespJson['rid'])

def upload_character():
    currPath = os.path.abspath(os.path.dirname(__file__))
    cInputPath = input('Input relative path of character model to upload: ')
    cFullPath = os.path.normpath(os.path.join(currPath, cInputPath))
    cFile = None
    if not os.path.exists(cFullPath):
        raise argparse.ArgumentTypeError('Filename %r doesn\'t exist.' % cFullPath)
    with open(cFullPath, 'rb') as f:
        cFile = f.read()
        f.close()
    if cFile == None:
        raise argparse.ArgumentTypeError('Could not read %r.' % cFullPath)
    cHeader = {'Content-Length': str(len(cFile)), 'Content-Type': 'application/octet-stream'}

    cFName, cExt = os.path.splitext(os.path.basename(cFullPath))
    uploadingUrl = _apiServerUrl + '/character/getModelUploadUrl?name=' + cFName + '&modelExt=' + cExt[
                                                                                                  1:] + '&resumable=0'
    resp = session.get(uploadingUrl)
    if resp.status_code == 200:
        jsonResp = json.loads(resp.text)
        gcsModelUrl = jsonResp['modelUrl']
        cUploadResp = session.put(gcsModelUrl, headers=cHeader, data=cFile)
        if cUploadResp.status_code == 200:
            print('Uploaded model ' + cFName)
        else:
            print('Failed to upload model')
            main_options()
        storeUrl = _apiServerUrl + '/character/storeModel'
        storeCfg = {
            "modelId": None,
            "modelUrl": gcsModelUrl,
            "thumbUrl": None,
            "modelName": cFName
        }
        storeResp = session.post(storeUrl, json=storeCfg)
        if storeResp.status_code == 200:
            print('Successfully stored model ' + json.loads(storeResp.text)['modelId'])
        else:
            print('Failed to store model')
    else:
        print('Failed to contact API server for upload.')

    print('')
    main_options()


def check_minutes_balance():
    respText = get_response('/account/creditBalance').text
    jsonResp = json.loads(respText)
    print(jsonResp['credits'])

    print('')
    main_options()


mainOptions = {
    1: list_models,
    2: list_jobs,
    3: download_job,
    4: new_job,
    5: upload_character,
    6: check_minutes_balance,
    7: exit
}


def main_options():
    st.write("""=== OPTIONS ===
    1) List Models
    2) List Jobs
    3) Download Completed Job
    4) Start New Job
    5) Upload Custom Character
    6) Check Minutes Balance
    7) Exit\n""")
    selection = st.text_input('Select option number from the list: ')
    #selection = int(input('Select option number from the list: '))
    if selection:
        mainOptions[int(selection)]()


def main():
    read_user_credentials(args)
    mainOptions[4]()
    #main_options()


if __name__ == '__main__':
    tab1, tab2 = st.tabs(["Motion Tracking", "Motion Insight"])

    args = parse_user_credentials()
    main()

