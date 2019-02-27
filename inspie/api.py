import requests
import json
import hashlib
import math
import time
import copy
from requests_toolbelt import MultipartEncoder
from moviepy.editor import VideoFileClip
from .utils import generate_UUID, generate_signature, generate_device_id, get_image_size
from .config import API_URL, USER_AGENT, EXPERIMENTS, DEVICE_SETTINTS

# Turn off InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class InspieAPI(object):
    """
    # username            # Instagram username
    # password            # Instagram password
    # uuid                # UUID
    # device_id           # Device ID
    # username_id         # Username ID
    # token               # _csrftoken
    # is_logged_in        # Session status
    # rank_token          # Rank token
    """

    API_URL = API_URL
    USER_AGENT = USER_AGENT
    EXPERIMENTS = EXPERIMENTS
    DEVICE_SETTINTS = DEVICE_SETTINTS

    def __init__(self, username, password):
        m = hashlib.md5()
        m.update(username.encode('utf-8') + password.encode('utf-8'))
        self.device_id = generate_device_id(m.hexdigest())
        self.is_logged_in = False
        self.last_response = None
        self.s = requests.Session()
        self.username = username
        self.password = password
        self.uuid = generate_UUID(True)
        self.login()

    def login(self, force=False):
        if (not self.is_logged_in or force):
            if (self.send_request('si/fetch_headers/?challenge_type=signup&guid={}'.format(generate_UUID(False)),
                                  None,
                                  True)):

                data = {'phone_id': generate_UUID(True),
                        '_csrftoken': self.last_response.cookies['csrftoken'],
                        'username': self.username,
                        'guid': self.uuid,
                        'device_id': self.device_id,
                        'password': self.password,
                        'login_attempt_count': '0'}

                if (self.send_request('accounts/login/',
                                      generate_signature(json.dumps(data)),
                                      True)):
                    self.is_logged_in = True if self.last_json.get("logged_in_user") else False
                    self.username_id = self.last_json["logged_in_user"]["pk"]
                    self.rank_token = "%s_%s" % (self.username_id, self.uuid)
                    self.token = self.last_response.cookies["csrftoken"]

                    self.sync_features()
                    self.auto_complete_user_list()
                    self.timeline_feed()
                    print("Login success!\n")
                    return True

    def sync_features(self):
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           'id': self.username_id,
                           '_csrftoken': self.token,
                           'experiments': self.EXPERIMENTS})
        return self.send_request('qe/sync/', generate_signature(data))

    def auto_complete_user_list(self):
        return self.send_request('friendships/autocomplete_user_list/')

    def timeline_feed(self):
        return self.send_request('feed/timeline/')

    def send_request(self, endpoint, post=None, login=False):
        verify = False  # don't show request warning

        if (not self.is_logged_in and not login):
            raise Exception("Not logged in!\n")

        self.s.headers.update({'Connection': 'close',
                               'Accept': '*/*',
                               'Content-type': 'application/x-www-form-urlencoded; charset=utf-8',
                               'Cookie2': '$Version=1',
                               'Accept-Language': 'en-US',
                               'User-Agent': self.USER_AGENT})

        if (post is not None):
            response = self.s.post(self.API_URL + endpoint, data=post, verify=verify)
        else:
            response = self.s.get(self.API_URL + endpoint, verify=verify)

        self.last_response = response
        self.last_json = response.json()

        if response.status_code == 200:
            return True
        else:
            print("Request return " + str(response.status_code) + " error!")
            print(self.last_json)
            return False

    def media_configure(self, upload_id, photo, caption=''):
        (w, h) = get_image_size(photo)
        data = json.dumps({'_csrftoken': self.token,
                           'media_folder': 'Instagram',
                           'source_type': 4,
                           '_uid': self.username_id,
                           '_uuid': self.uuid,
                           'caption': caption,
                           'upload_id': upload_id,
                           'device': self.DEVICE_SETTINTS,
                           'edits': {
                               'crop_original_size': [w * 1.0, h * 1.0],
                               'crop_center': [0.0, 0.0],
                               'crop_zoom': 1.0
                           },
                           'extra': {
                               'source_width': w,
                               'source_height': h
                           }})
        return self.send_request('media/configure/?', generate_signature(data))

    def video_configure(self, upload_id, video, thumbnail, caption=''):
        clip = VideoFileClip(video)
        self.upload_photo(photo=thumbnail, caption=caption, upload_id=upload_id)
        data = json.dumps({
            'upload_id': upload_id,
            'source_type': 3,
            'poster_frame_index': 0,
            'length': 0.00,
            'audio_muted': False,
            'filter_type': 0,
            'video_result': 'deprecated',
            'clips': {
                'length': clip.duration,
                'source_type': '3',
                'camera_position': 'back',
            },
            'extra': {
                'source_width': clip.size[0],
                'source_height': clip.size[1],
            },
            'device': self.DEVICE_SETTINTS,
            '_csrftoken': self.token,
            '_uuid': self.uuid,
            '_uid': self.username_id,
            'caption': caption,
        })
        return self.send_request('media/configure/?video=1', generate_signature(data))

    def upload_photo(self, photo, caption=None, upload_id=None, is_sidecar=None):
        if upload_id is None:
            upload_id = str(int(time.time() * 1000))
        data = {'upload_id': upload_id,
                '_uuid': self.uuid,
                '_csrftoken': self.token,
                'image_compression': '{"lib_name":"jt","lib_version":"1.3.0","quality":"87"}',
                'photo': ('pending_media_{}.jpg'.format(upload_id),
                          open(photo, 'rb'),
                          'application/octet-stream', {'Content-Transfer-Encoding': 'binary'})}
        if is_sidecar:
            data['is_sidecar'] = '1'
        m = MultipartEncoder(data, boundary=self.uuid)
        self.s.headers.update({'X-IG-Capabilities': '3Q4=',
                               'X-IG-Connection-Type': 'WIFI',
                               'Cookie2': '$Version=1',
                               'Accept-Language': 'en-US',
                               'Accept-Encoding': 'gzip, deflate',
                               'Content-type': m.content_type,
                               'Connection': 'close',
                               'User-Agent': self.USER_AGENT})
        response = self.s.post(self.API_URL + "upload/photo/", data=m.to_string())
        if response.status_code == 200:
            if self.media_configure(upload_id, photo, caption):
                self.expose()
                print(self.last_json.get("status"))
                return True
        return False

    def upload_Video(self, video, thumbnail, caption=None, upload_id=None, is_sidecar=None):
        if upload_id is None:
            upload_id = str(int(time.time() * 1000))
        data = {'upload_id': upload_id,
                '_csrftoken': self.token,
                'media_type': '2',
                '_uuid': self.uuid}
        if is_sidecar:
            data['is_sidecar'] = '1'
        m = MultipartEncoder(data, boundary=self.uuid)
        self.s.headers.update({'X-IG-Capabilities': '3Q4=',
                               'X-IG-Connection-Type': 'WIFI',
                               'Host': 'i.instagram.com',
                               'Cookie2': '$Version=1',
                               'Accept-Language': 'en-US',
                               'Accept-Encoding': 'gzip, deflate',
                               'Content-type': m.content_type,
                               'Connection': 'keep-alive',
                               'User-Agent': self.USER_AGENT})
        response = self.s.post(self.API_URL + "upload/video/", data=m.to_string())
        if response.status_code == 200:
            body = json.loads(response.text)
            upload_url = body['video_upload_urls'][3]['url']
            upload_job = body['video_upload_urls'][3]['job']

            video_data = open(video, 'rb').read()
            request_size = int(math.floor(len(video_data) / 4))
            last_request_extra = (len(video_data) - (request_size * 3))

            headers = copy.deepcopy(self.s.headers)
            self.s.headers.update({'X-IG-Capabilities': '3Q4=',
                                   'X-IG-Connection-Type': 'WIFI',
                                   'Cookie2': '$Version=1',
                                   'Accept-Language': 'en-US',
                                   'Accept-Encoding': 'gzip, deflate',
                                   'Content-type': 'application/octet-stream',
                                   'Session-ID': upload_id,
                                   'Connection': 'keep-alive',
                                   'Content-Disposition': 'attachment; filename="video.mov"',
                                   'job': upload_job,
                                   'Host': 'upload.instagram.com',
                                   'User-Agent': self.USER_AGENT})
            for i in range(0, 4):
                start = i * request_size
                if i == 3:
                    end = i * request_size + last_request_extra
                else:
                    end = (i + 1) * request_size
                length = last_request_extra if i == 3 else request_size
                content_range = "bytes {start}-{end}/{lenVideo}".format(start=start, end=(end - 1),
                                                                        lenVideo=len(video_data)).encode('utf-8')

                self.s.headers.update({'Content-Length': str(end - start),
                                       'Content-Range': content_range, })
                response = self.s.post(upload_url, data=video_data[start:start + length])
            self.s.headers = headers

            if response.status_code == 200:
                if self.video_configure(upload_id, video, thumbnail, caption):
                    self.expose()
                    return True
        return False

    def delete_media(self, media_id, media_type=1):
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           '_csrftoken': self.token,
                           'media_type': media_type,
                           'media_id': media_id})
        return self.send_request('media/' + str(media_id) + '/delete/', generate_signature(data))

    def expose(self):
        data = json.dumps({'_uuid': self.uuid,
                           '_uid': self.username_id,
                           'id': self.username_id,
                           '_csrftoken': self.token,
                           'experiment': 'ig_android_profile_contextual_feed'})
        return self.send_request('qe/expose/', generate_signature(data))
