# far from done
from .exceptions import *

import aiohttp
import json as jsonlib

class http():
    def __init__(self, site_baseurl, patch_baseurl=None, username=None, password=None):
        self.site_baseurl = site_baseurl
        self.patch_baseurl = patch_baseurl

        if not username==None:
            auth=(username, password)
        else:
            auth=None

        self.auth=None

    async def generate_game(self, endpoint, settings):
        for i in range(0,5):
            try:
                req = await request_json_post(
                    url=self.site_baseurl + endpoint,
                    json=settings,
                    auth=self.auth,
                    returntype='json'
                )
                return req
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
            # except aiohttp.ClientResponseError:
            #     continue
        raise alttprFailedToGenerate('failed to generate game')

    async def retrieve_game(self, hash):
        for i in range(0,5):
            try:
                if not self.patch_baseurl==None:
                    s3patch = await request_generic(
                        url=self.patch_baseurl + '/' + hash + '.json',
                        returntype='json'
                    )
                    return s3patch
                else:
                    localpatch = await request_generic(
                        url=self.site_baseurl + '/hash/' + hash,
                        returntype='json'
                    )
                    return localpatch
            except aiohttp.ClientResponseError:
                localpatch = await request_generic(
                    url=self.site_baseurl + '/hash/' + hash,
                    returntype='json'
                )
                # if localpatch.status == 404:
                #     break
                return localpatch
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
        raise alttprFailedToRetrieve('failed to retrieve game {hash}, the game is likely not found'.format(
            hash=hash
        ))

    async def retrieve_json(self, endpoint):
        req = await request_generic(
            url=self.site_baseurl + endpoint,
            auth=self.auth,
            returntype='json'
        )
        return req

    async def retrieve_url_raw_content(self, url):
        req = await request_generic(
            url=url,
            returntype='binary'
        )
        return req

async def request_generic(url, method='get', reqparams=None, data=None, header={}, auth=None, returntype='text'):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.request(method.upper(), url, params=reqparams, data=data, headers=header) as resp:
            if returntype=='text':
                return await resp.text()
            elif returntype=='json':
                return jsonlib.loads(await resp.text())
            elif returntype=='binary':
                return await resp.read()

async def request_json_post(url, json, auth=None, returntype='text'):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.post(url=url, json=json) as resp:
            if returntype=='text':
                return await resp.text()
            elif returntype=='json':
                return jsonlib.loads(await resp.text())
            elif returntype=='binary':
                return await resp.read()