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
        """"""
        api_query = urllib.parse.urlencode({"uri": uri})
        api_call = f"{API_ROOT_URL}/{voc_id}/data?{api_query}"
        logger.debug("Making API call: %s", api_call)

        api_req = urllib.request.Request(api_call)
        api_req.add_header("user-agent", "Met-Vocab-Tools (Python script)")
        api_req.add_header("accept", "application/ld+json")

        try:
            _ = urllib.request.urlopen(api_req)
        except urllib.error.HTTPError as err:
            logger.error(str(err))
        except urllib.error.URLError as err:
            logger.error(str(err))

        return True, {}

# END Class DataCache
