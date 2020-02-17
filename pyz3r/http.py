# far from done
from . import exceptions

import aiohttp
import json


class site():
    def __init__(
            self,
            site_baseurl,
            patch_baseurl=None,
            username=None,
            password=None):
        self.site_baseurl = site_baseurl
        self.patch_baseurl = patch_baseurl

        self.auth = aiohttp.BasicAuth(login=username, password=password) if username else None

    async def generate_game(self, endpoint, settings):
        for i in range(0, 5):
            try:
                req = await request_json_post(
                    url=self.site_baseurl + endpoint,
                    data=settings,
                    auth=self.auth,
                    returntype='json'
                )
                return req
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
            # except aiohttp.ClientResponseError:
            #     continue
        raise exceptions.alttprFailedToGenerate('failed to generate game')

    async def retrieve_game(self, hash_id):
        for i in range(0, 5):
            try:
                if self.patch_baseurl is not None:
                    s3patch = await request_generic(
                        url=self.patch_baseurl + '/' + hash_id + '.json',
                        returntype='json'
                    )
                    return s3patch
                else:
                    localpatch = await request_generic(
                        url=self.site_baseurl + '/hash/' + hash_id,
                        auth=self.auth,
                        returntype='json'
                    )
                    return localpatch
            except aiohttp.ClientResponseError:
                localpatch = await request_generic(
                    url=self.site_baseurl + '/hash/' + hash_id,
                    auth=self.auth,
                    returntype='json'
                )
                # if localpatch.status == 404:
                #     break
                return localpatch
            except aiohttp.client_exceptions.ServerDisconnectedError:
                continue
        raise exceptions.alttprFailedToRetrieve(
            'failed to retrieve game {hash}, the game is likely not found'.format(
                hash=hash_id))

    async def retrieve_json(self, endpoint, useauth=True):
        if useauth:
            auth = self.auth
        else:
            auth = None

        req = await request_generic(
            url=self.site_baseurl + endpoint,
            auth=auth,
            returntype='json'
        )
        return req

    async def retrieve_url_raw_content(self, url, useauth=True):
        if useauth:
            auth = self.auth
        else:
            auth = None

        req = await request_generic(
            url=url,
            auth=auth,
            returntype='binary'
        )
        return req


async def request_generic(url, method='get', reqparams=None, data=None, header=None, auth=None, returntype='text'):
    async with aiohttp.ClientSession(auth=None, raise_for_status=True) as session:
        async with session.request(method.upper(), url, params=reqparams, data=data, headers=header, auth=auth) as resp:
            if returntype == 'text':
                return await resp.text()
            elif returntype == 'json':
                return json.loads(await resp.text())
            elif returntype == 'binary':
                return await resp.read()

async def request_json_put(url, data, auth=None, returntype='text'):
    async with aiohttp.ClientSession(auth=auth, raise_for_status=True) as session:
        async with session.put(url=url, json=data, auth=auth) as resp:
            if returntype == 'text':
                return await resp.text()
            elif returntype == 'json':
                return json.loads(await resp.text())
            elif returntype == 'binary':
                return await resp.read()

async def request_json_post(url, data, auth=None, returntype='text'):
    async with aiohttp.ClientSession(auth=auth, raise_for_status=True) as session:
        async with session.post(url=url, json=data, auth=auth) as resp:
            if returntype == 'text':
                return await resp.text()
            elif returntype == 'json':
                return json.loads(await resp.text())
            elif returntype == 'binary':
                return await resp.read()
