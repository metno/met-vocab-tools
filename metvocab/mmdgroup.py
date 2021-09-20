"""
MetVocab : MMD Group Class
==========================

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


class MMDGroup():

    def __init__(self, voc_id, uri):

        self._voc_id = voc_id
        self._uri = uri

        self._is_initialised = False
        self._concepts = {}

        return

    ##
    #  Properties
    ##

    @property
    def is_initialised(self):
        """Return the initialised state of the class."""
        return self._is_initialised

    ##
    #  Methods
    ##

    def init_vocab(self):
        """Populate _concepts with dictionary uri: data for members of
        the given group
        """
        root_cache = DataCache()
        data = root_cache.get_vocab(self._voc_id, self._uri)
        self._concepts = {}

        for graph in data.get("graph", []):
            for member in graph.get("skos:member", []):
                if member.get("uri", None) is not None:
                    uri = member.get("uri")
                    tmp_cache = DataCache()
                    data = tmp_cache.get_vocab(self._voc_id, uri)
                    data = self._get_concept_dictionary(data, uri)

                    self._concepts.update({member.get("uri"): data})

        self._is_initialised = bool(self._concepts)

        return

    def search(self, name):
        """Searches both prefLabel (Short name) and altLabel (Long name)
        for match with given name, returns both if any match, and
        resource if resource is present
        """
        found = False
        for concept in self._concepts.values():
            found |= name == self._get_label(concept, "altLabel")
            found |= name == self._get_label(concept, "prefLabel")
            if found is True:
                Resource = self._get_resource(concept, "rdfs:seeAlso")
                return {
                    "Short_Name": self._get_label(concept, "prefLabel"),
                    "Long_Name": self._get_label(concept, "altLabel"),
                    "Resource": Resource if "wmo" in Resource else None
                }

        return {}

    ##
    #  Internal Functions
    ##

    def _get_concept_dictionary(self, data, uri):
        """Returns dictionary matching the concept itself, without
        headers
        """
        for graph in data.get("graph", []):
            if graph.get("uri", None) == uri:
                data = graph

        return data

    def _get_label(self, concept, label):
        """Helper function for search method"""
        value = concept.get(label)
        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            return value[0].get("value", None) if len(value) else None
        elif isinstance(value, dict):
            return value.get("value", None)
        return None

    def _get_resource(self, concept, label):
        """Helper function for search method"""
        value = concept.get(label)
        if isinstance(value, dict):
            return value.get("uri", "")
        elif isinstance(value, list):
            return value[0].get("uri", "") if len(value) else ""
        elif isinstance(value, str):
            return value
        return ""

# END Class MMDGroup
