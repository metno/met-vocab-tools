"""
MetVocab : Config
=================

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
import logging

logger = logging.getLogger(__name__)


class Config:

    def __init__(self):
        cache_path = os.environ.get("METVOCAB_CACHEPATH", None)

        # Cache path setup
        if cache_path is None:
            cache_path = self._setup_cache_path(cache_path)

        self.cache_path = os.path.abspath(os.path.expanduser(cache_path))
        os.makedirs(self.cache_path, exist_ok=True)
        logger.debug("Cache path is %s", self.cache_path)

        # Must be given as day or hour?
        max_age = os.environ.get("METVOCAB_CACHEDAYS", None)
        if max_age is None:
            # 7 days
            max_age = 7
        # Convert to seconds internally
        self.max_age = max_age*24*60*60

        return

    def _setup_cache_path(self, cache_path):
        """Tries to find path for cache folder"""
        path_tries = [
            os.path.join("~", ".local", "share"),  # Linux
            os.path.join("~", "Library", "Application Support"),  # macOS
        ]

        for a_path in path_tries:
            a_path = os.path.expanduser(a_path)
            if os.path.isdir(a_path):
                cache_path = a_path
                break

        if cache_path is None:
            cache_path = os.path.join(os.path.expanduser("~"))

        return os.path.join(cache_path, "metvocab")
