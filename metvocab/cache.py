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

import sys
import json
import logging
import urllib.request
import urllib.parse
import urllib.error

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

# END Class DataCache
