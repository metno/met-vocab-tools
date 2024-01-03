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
import warnings

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
            found |= self._search_altLabel(concept, "altLabel", name)
            found |= name == self._get_label(concept, "prefLabel")
            found |= name == self._get_label(concept, "uri")
            found |= self._search_resource(concept, "exactMatch", name)

            if found is True:
                return {
                    "Short_Name": self._get_label(concept, "prefLabel"),
                    "short_name": self._get_label(concept, "prefLabel"),
                    "Long_Name": self._get_altLabel(concept, "altLabel"),
                    "long_name": self._get_altLabel(concept, "altLabel"),
                    "Resource": self._get_resource(concept, "uri"),
                    "resource": self._get_resource(concept, "uri")
                }

        warnings.warn("Short_Name, Long_Name and Resource dict keys "
                      "are deprecated, and will be removed in v2.0 of"
                      " met-vocab-tools.")

        return {}

    def search_lowercase(self, name):
        """Searches both prefLabel (Short name) and altLabel (Long name)
        for match with given name, but searches with lowercase letters.
        returns both prefLabel and altLabel if any is found, and resource
        if resource is present
        """
        name = name.lower()
        found = False
        for concept in self._concepts.values():
            found |= self._search_altLabel_lowercase(concept, "altLabel", name)
            found |= name == self._get_label_lowercase(concept, "prefLabel")
            if found is True:
                return {
                    "Short_Name": self._get_label(concept, "prefLabel"),
                    "short_name": self._get_label(concept, "prefLabel"),
                    "Long_Name": self._get_altLabel(concept, "altLabel"),
                    "long_name": self._get_altLabel(concept, "altLabel"),
                    "Resource": self._get_resource(concept, "uri"),
                    "resource": self._get_resource(concept, "uri")
                }

        warnings.warn("Short_Name, Long_Name and Resource dict keys "
                      "are deprecated, and will be removed in v2.0 of"
                      " met-vocab-tools.")

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
        if isinstance(concept, dict):
            value = concept.get(label)
        else:
            return None

        if isinstance(value, str):
            return value
        elif isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], dict):
                return value[0].get("value", None)
        elif isinstance(value, dict):
            return value.get("value", None)

        return None

    def _search_altLabel(self, concept, label, name):
        """Helper function for search method"""
        if isinstance(concept, dict):
            values = concept.get(label)
        else:
            return False

        if isinstance(values, str):
            return values == name
        elif isinstance(values, list):
            if len(values) > 0 and isinstance(values[0], dict):
                for value in values:
                    if value.get("value", None) == name:
                        return True
                return False
        elif isinstance(values, dict):
            return values.get("value", None) == name

        return False

    def _search_altLabel_lowercase(self, concept, label, name):
        """Helper function for search method """
        if isinstance(concept, dict):
            values = concept.get(label)
        else:
            return False

        if isinstance(values, str):
            return values.lower() == name
        elif isinstance(values, list):
            if len(values) > 0 and isinstance(values[0], dict):
                for value in values:
                    altlabel = value.get("value", None)
                    if isinstance(altlabel, str) and altlabel.lower() == name:
                        return True
        elif isinstance(values, dict):
            altlabel = values.get("value", None)
            return isinstance(altlabel, str) and altlabel.lower() == name

        return False

    def _get_altLabel(self, concept, label):
        """Helper function for search method"""
        if isinstance(concept, dict):
            values = concept.get(label)
        else:
            return None

        if isinstance(values, str):
            return values
        elif isinstance(values, list):
            # Fetches the value in last index for altLabel if its a list
            if len(values) > 0 and isinstance(values[0], dict):
                return values[len(values)-1].get("value", None)

        elif isinstance(values, dict):
            return values.get("value", None)

        return None

    def _get_label_lowercase(self, concept, label):
        """Wrapper function around _get_label to not call
        lower() on non-str instances
        """
        value = self._get_label(concept, label)
        if isinstance(value, str):
            return value.lower()
        return None

    def _get_resource(self, concept, label):
        """Helper function for search method"""
        if isinstance(concept, dict):
            value = concept.get(label)
        else:
            return ""

        if isinstance(value, dict):
            return value.get("uri", "")
        elif isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], dict):
                return value[0].get("uri", "")
        elif isinstance(value, str):
            return value

        return ""

    def _search_resource(self, concept, label, uri):
        """Helper function for search method"""
        if isinstance(concept, dict):
            values = concept.get(label)
        else:
            return False

        if isinstance(values, dict):
            return values.get("uri", "") == uri
        elif isinstance(values, list):
            if len(values) > 0 and isinstance(values[0], dict):
                for value in values:
                    if (value.get("uri", "") == uri):
                        return True
        elif isinstance(values, str):
            return values == uri

        return False
# END Class MMDGroup
