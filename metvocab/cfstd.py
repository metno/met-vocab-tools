"""
MetVocab : CF Standard Vocabulary Class
=======================================

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

import lxml


class CFStandard():

    def __init__(self):

        self._standard_names = set()
        self._is_initialised = False

        return

    @property
    def is_initialised(self):
        """Read the initialised state of the class."""
        return self._is_initialised

    def init_vocab(self):
        """Initialise vocabulary class by loading the data from vocab
        file. The vocab file is downloaded in XML format from:
        https://cfconventions.org/standard-names.html
        """
        self._standard_names = set()

        self._is_initialised = len(self._concept_values) > 0

        return

    def check_standard_name(self, value):
        """Look up a value in the list of standard names."""
        if isinstance(value, str):
            return value in self._standard_names
        return False

# END Class CFStandard
