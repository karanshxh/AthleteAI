import os
import json
import requests
import time
from zipfile import ZipFile
import tempfile

class DeepMotionHandler:
    _apiServerUrl = 'https://service.deepmotion.com'

    def __init__(self):
        with open("static/credentials.json") as f:
            jsonData = json.load(f)
            self.session_credentials = jsonData['clientId'], jsonData['clientSecret']
            self.session = self.get_session()
            print("Credentials read.\n", flush=True)

    def get_session(self):
        authUrl = self._apiServerUrl + '/session/auth'
        session = requests.Session()
        session.auth = self.session_credentials
        request = session.get(authUrl)
        if request.status_code == 200:
            return session
        else:
            print('Failed to authenticate ' + str(request.status_code) + '\n')

    def get_response(self, url_path):
        resp_url = self._apiServerUrl + url_path
        resp = self.session.get(resp_url)
        if resp.status_code == 200:
            return resp
        else:
            print("Failed to contact server " + resp.status_code + "\n")

    def get_job_list(self, list_path):
        resp_text = self.get_response(list_path).text
        json_resp = json.loads(resp_text)
        return json_resp

    def new_job(self, input_file, download=True):
        if not os.path.exists(input_file):
            raise Exception("Input path does not exist")
        
        with open(input_file, 'rb') as f:
            input_video = f.read()

        if input_video == None:
            raise Exception(f"Could not read {input_file}")


        format_process = "formats=fbx"
        header_content = {
            'Content-length': str(len(input_video)), 
            'Content-type': 'application/octet-stream'
            }
        
        video_name, _ = os.path.splitext(input_file)

        upload_url = self._apiServerUrl + '/upload?name=' + video_name + '&resumable=0'

        resp = self.session.get(upload_url)
        if resp.status_code == 200:
            json_resp = json.loads(resp.text)
            gcs_url = json_resp['url']
            upload_resp = self.session.put(gcs_url, headers=header_content, data=input_video)

            if upload_resp.status_code == 200:
                process_url = self._apiServerUrl + '/process'
                process_cfj_json = {
                    "url": gcs_url,
                    "processor": "video2anim",
                    "params": [
                        "config=configDefault",
                        format_process
                    ]
                }
            
                process_resp = self.session.post(process_url, json=process_cfj_json)
                if process_resp.status_code == 200:
                    p_resp_json = json.loads(process_resp.text)
                    # TODO: add procesing job message
                else:
                    print("failed to process job")

            else:
                print("failed to upload")
    
        if download:
            return self.download_job(p_resp_json, os.path.splitext(input_file))
        else:
            return p_resp_json, os.path.splitext(input_file)

    def download_job(self, file_rid, file_name):
        """file_rid: {'rid': rid}"""
        def get_curr_jobs_info():
            job_list_json = self.get_job_list('/list/SUCCESS')
            num_jobs = job_list_json['count']
            job_list_json['list'] = sorted(job_list_json['list'], key=lambda x: x['ctime'], reverse=True)

            rids = [x['rid'] for x in job_list_json['list']]

            #rid = job_list_json['list'][0]['rid']
            return job_list_json, num_jobs, rids
        
        job_list_json, num_jobs, rids = get_curr_jobs_info()

        while file_rid['rid'] not in rids:
            time.sleep(10)
            print(rids)
            print(file_rid["rid"])

            job_list_json, num_jobs, rids = get_curr_jobs_info()

        tempdir = tempfile.gettempdir()
        download_path = f"{tempdir}/{os.path.basename(file_name[0])}."
        download_resp = self.get_response("/download/" + file_rid['rid'])
        download_resp_json = json.loads(download_resp.text)
        
        if download_resp_json['count'] > 0:
            urls = download_resp_json['links'][0]['urls']
            for file_url in urls:
                files = file_url['files']

                for file in files:
                    if 'fbx' in file:
                        uri = file['fbx']
                        fbx_resp = self.session.get(uri)
                        with open(download_path + 'zip', 'wb') as f:
                            f.write(fbx_resp.content)
                            print('\nFile saved to ' + download_path + 'zip')
        # TODO: unzip video
        with ZipFile(download_path + 'zip', 'r') as f:
            f.extractall(path=download_path[:-1])

        print(download_path[:-1])
        def get_shortest_file(path):
            shortest = os.listdir(path)[0]
            print(shortest)
            for file in os.listdir(path):
                if len(file) < len(shortest):
                    print(len(file))
                    shortest = file
            return shortest
        print(download_path[:-1])
        return download_path[:-1] + "/" + get_shortest_file(download_path[:-1])
    
if __name__ == "__main__":
    deep_motion = DeepMotionHandler()
    print(deep_motion.new_job("static/videos/TableTennis.mp4"))