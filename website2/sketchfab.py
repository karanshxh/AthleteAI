import json
import time
import requests
import os

class SketchfabHandler():

    SKETCHFAB_API_URL = 'https://api.sketchfab.com/v3'
    MAX_RETRIES = 50
    MAX_ERRORS = 10
    RETRY_TIMEOUT = 5  # seconds

    def __init__(self):
        with open("static/sketchfab_credentials.txt") as f:
            self.API_TOKEN = f.readline()

    def _get_request_payload(self, data=None, files=None):
        """Helper method that returns the authentication token and proper content type depending on
        whether or not we use JSON payload."""
        data = data or {}
        files = files or {}
        headers = {'Authorization': f'Token {self.API_TOKEN}'}

        return {'data': data, 'files': files, 'headers': headers}
    
    def upload(self, model_file):
        model_endpoint = f'{self.SKETCHFAB_API_URL}/models'

        data = {
            'name': os.path.basename(model_file),
            'background': '{"color": "#2F4858"}',
            'isPublished': True,  # Model will be on draft instead of published,
            'isInspectable': True,  # Allow 2D view in model inspector
        }

        print("Uploading...")

        with open(model_file, 'rb') as file_:
            files = {'modelFile': file_}
            payload = self._get_request_payload(data=data, files=files)

            try:
                response = requests.post(model_endpoint, **payload)
            except Exception as exc:
                print(f'An error occured: {exc}')
                return

        if response.status_code != requests.codes.created:
            print(f'Upload failed with error: {response.json()}')
            return

        # Should be https://api.sketchfab.com/v3/models/XXXX
        model_url = response.headers['Location']
        print('Upload successful. Your model is being processed.')
        print(f'Once the processing is done, the model will be available at: {model_url}')

        return model_url

    def poll_processing_status(self, model_url):
        """GET the model endpoint to check the processing status."""
        errors = 0
        retry = 0

        print('Start polling processing status for model')

        while (retry < self.MAX_RETRIES) and (errors < self.MAX_ERRORS):
            print(f'Try polling processing status (attempt #{retry})...')

            payload = self._get_request_payload()

            try:
                response = requests.get(model_url, **payload)
            except Exception as exc:
                print(f'Try failed with error {exc}')
                errors += 1
                retry += 1
                continue

            result = response.json()

            if response.status_code != requests.codes.ok:
                print(f'Upload failed with error: {result["error"]}')
                errors += 1
                retry += 1
                continue

            processing_status = result['status']['processing']

            if processing_status == 'PENDING':
                print(f'Your model is in the processing queue. Will retry in {self.RETRY_TIMEOUT} seconds')
                retry += 1
                time.sleep(self.RETRY_TIMEOUT)
                continue
            elif processing_status == 'PROCESSING':
                print(f'Your model is still being processed. Will retry in {self.RETRY_TIMEOUT} seconds')
                retry += 1
                time.sleep(self.RETRY_TIMEOUT)
                continue
            elif processing_status == 'FAILED':
                print(f'Processing failed: {result["error"]}')
                return False
            elif processing_status == 'SUCCEEDED':
                print(f'Processing successful. Check your model here: {model_url}')
                return True

            retry += 1

        print('Stopped polling after too many retries or too many errors')
        return False

        
if __name__ == "__main__":
    handler = SketchfabHandler()
    handler.upload("static/deep_motion_vids/TableTennis/TableTennis_Adult_Male_Alt.fbx")