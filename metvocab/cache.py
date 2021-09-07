"""
MetVocab : Data Cache Class
===========================

Copyright 2021 MET Norway

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
import json
import time
import logging
import urllib.parse
import urllib.error
import urllib.request

from metvocab import CONFIG

logger = logging.getLogger(__name__)

API_ROOT_URL = "https://vocab.met.no/rest/v1"


class DataCache():

    def __init__(self):
        return

    def _retrieve_data(self, voc_id, uri):
        """Make an API call and return the data as a dictionary.
        If the request is unsuccessful, return False and an empty
        dictionary.
        """
        api_query = urllib.parse.urlencode({"uri": uri})
        api_call = f"{API_ROOT_URL}/{voc_id}/data?{api_query}"
        logger.info("Making API call: %s", api_call)

        api_req = urllib.request.Request(api_call)
        api_req.add_header("user-agent", "Met-Vocab-Tools (Python script)")
        api_req.add_header("accept", "application/ld+json")

        api_resp = None
        try:
            api_resp = urllib.request.urlopen(api_req)
        except urllib.error.HTTPError as err:
            logger.error(str(err))
            return False, {}
        except urllib.error.URLError as err:
            logger.error(str(err))
            return False, {}

        if api_resp is None:
            logger.error("No response returned from API")
            return False, {}

        ret_data = api_resp.read()
        ret_code = api_resp.status if sys.hexversion >= 0x030900f0 else api_resp.code

        status = ret_code == 200
        data = json.loads(ret_data)

        return status, data

    def _check_cache(self, voc_id, uri):
        """Parses the uri to establish file-path, checks if cache exists
        and if it is below allowed caching age given in config. Falls
        back to old cache if API is unreachable. Returns None if API
        fails and no cache exists
        """
        path = urllib.parse.urlparse(uri).path
        path_list = path.split("/")

        if path_list[-1] == "":
            raise ValueError("The provided uri is missing a path: '%s'", uri)

        json_path = os.path.join(CONFIG.cache_path, *path_list[:-1])
        json_file = os.path.join(json_path, path_list[-1]+".json")

        file_exists = False

        if os.path.isfile(json_file):
            file_exists = True
            stale = self._check_timestamp(json_file, CONFIG.max_age)
            if stale:
                self._create_cache(json_path, json_file, voc_id, uri)
        else:
            file_exists = self._create_cache(json_path, json_file, voc_id, uri)

        if file_exists:
            with open(json_file, mode="r", encoding="utf-8") as infile:
                data = json.load(infile)
            return data
        else:
            return None

    def _create_cache(self, json_path, json_file, voc_id, uri):
        """Sends a request to the api, and caches the data"""
        status, data = self._retrieve_data(voc_id, uri)
        if status:
            os.makedirs(json_path, exist_ok=True)
            with open(json_file, mode="w", encoding="utf-8") as outfile:
                json.dump(data, outfile)
            return True
        return False

    def _check_timestamp(self, uri_file, max_age):
        """Checks timestamp of file, if older than max_age seconds
        returns True, if younger than max_age seconds returns False.
        """
        file_age = os.path.getmtime(uri_file)
        if (time.time() - file_age) > max_age:
            return True
        return False

# END Class DataCache
