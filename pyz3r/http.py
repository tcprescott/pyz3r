from .exceptions import *

import requests
import json

class http():
    def __init__(self, site_baseurl, patch_baseurl=None, username=None, password=None):
        self.site_baseurl = site_baseurl
        self.patch_baseurl = patch_baseurl

        if not username==None:
            auth=(username, password)
        else:
            auth=None

        self.auth=None

    def generate_game(self, endpoint, settings):
        for i in range(0,5):
            try:
                req = requests.post(
                    url=self.site_baseurl + endpoint,
                    json=settings,
                    auth=self.auth
                )
            except requests.exceptions.ConnectionError:
                continue
            if not req.status_code == requests.codes.ok:
                raise alttprFailedToGenerate('failed to generate game - {resp}'.format(
                    resp = req.text
                ))
            return json.loads(req.text)
        raise alttprFailedToGenerate('failed to generate game - {resp}')

    def retrieve_game(self, hash):
        for i in range(0,5):
            try:
                if not self.patch_baseurl==None:
                    s3patch = requests.get(
                        url=self.patch_baseurl + '/' + hash + '.json'
                    )
                    s3patch.raise_for_status()
                    return json.loads(s3patch.text)
                else:
                    localpatch = requests.get(
                        url=self.site_baseurl + '/hash/' + hash
                    )
                    localpatch.raise_for_status()
                    return json.loads(localpatch.text)
            except requests.exceptions.HTTPError:
                localpatch = requests.get(
                    url=self.site_baseurl + '/hash/' + hash
                )
                if localpatch.status_code == 404:
                    break
                localpatch.raise_for_status()
                return json.loads(localpatch.text)
            except requests.exceptions.ConnectionError:
                continue
        raise alttprFailedToRetrieve('failed to retrieve game {hash}, the game is likely not found'.format(
            hash=hash
        ))

    def retrieve_json(self, endpoint):
        req = requests.get(
            url=self.site_baseurl + endpoint,
            auth=self.auth
        )
        req.raise_for_status()
        return json.loads(req.text)

    def retrieve_url_raw_content(self, url):
        req = requests.get(
            url=url
        )
        req.raise_for_status()
        return req.content