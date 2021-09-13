"""
MetVocab : Lookup Class
=======================

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

from metvocab.cache import DataCache


class Lookup():

    def __init__(self, voc_id, uri):
        self._voc_id = voc_id
        self._uri = uri
        self._cache = DataCache()
        self._data = None
        self._is_initialised = False
        self._concept_values = set()

    def init_vocab(self):
        """
        """
        self._data = self._cache.get_vocab(self._voc_id, self._uri)

        self._concept_values = set()
        for graph in self._data.get("graph", []):
            if self._check_is_concept(graph.get("type", None)):
                prefLabel = graph.get("prefLabel", None)
                if prefLabel is not None:
                    value = prefLabel.get("value", None)
                    if value is not None:
                        self._concept_values.add(value)

        self._is_initialised = len(self._concept_values) > 0

    def check_concept_value(self, value):
        """
        """
        if not isinstance(value, str):
            raise ValueError("Attribute 'value' must be a string")
        return value in self._concept_values

    def status(self):
        """
        """
        pass

    ##
    #  Internal Functions
    ##

    def _check_is_concept(self, value):
        """
        """
        if isinstance(value, list):
            return "skos:Concept" in value
        elif isinstance(value, str):
            return "skos:Concept" == value
        return False

# END Class Lookup
