"""
MetVocab : MMD Group Class Tests
================================

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
import pytest

from tools import readJson
from metvocab.cache import DataCache
from metvocab.mmdgroup import MMDGroup


@pytest.mark.live
def testLiveMMDGroup_Init():
    """Tests initialisation of group against api at vocab.met.no"""
    group = MMDGroup("mmd", "https://vocab.met.no/mmd/Platform")
    assert group.is_initialised is False

    group.init_vocab()
    assert group.is_initialised is True

    group = MMDGroup("mmd", "https://vocab.met.no/mmd/NotAGroup")
    group.init_vocab()
    assert group.is_initialised is False

# END Test testLiveMMDGroup_Init


@pytest.mark.live
def testLiveMMDGroup_Search():
    """Tests search in group against api at vocab.met.no"""
    group = MMDGroup("mmd", "https://vocab.met.no/mmd/Instrument")
    group.init_vocab()

    modis_dict = {
        "Short_Name": "MODIS",
        "short_name": "MODIS",
        "Long_Name": "Moderate-resolution Imaging Spectro-radiometer",
        "long_name": "Moderate-resolution Imaging Spectro-radiometer",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/modis",
        "resource": "https://www.wmo-sat.info/oscar/instruments/view/modis"
    }
    olci_dict = {
        "Short_Name": "OLCI",
        "short_name": "OLCI",
        "Long_Name": "Ocean and Land Colour Imager",
        "long_name": "Ocean and Land Colour Imager",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/olci",
        "resource": "https://www.wmo-sat.info/oscar/instruments/view/olci"
    }

    assert group.search("MODIS") == modis_dict
    assert group.search("MODIS") != olci_dict

    assert group.search("Ocean and Land Colour Imager") == olci_dict
    assert group.search("Ocean and Land Colour Imager") != modis_dict

    assert group.search("MockSat") == {}
    assert group.search("MockSat") != modis_dict
    assert group.search("MockSat") != olci_dict

# END Test testLiveMMDGroup_Init


@pytest.mark.core
def testCoreMMDGroup_Init(filesDir, monkeypatch):
    """Tests initialisation of group against local files"""
    data = readJson(os.path.join(filesDir, "Instrument.json"))

    def mock_get_vocab(self, voc_id, uri):
        if uri == "https://vocab.met.no/mmd/Instrument":
            return data
        return {}

    with monkeypatch.context() as mp:
        mp.setattr(DataCache, "get_vocab", mock_get_vocab)
        group = MMDGroup("mmd", "https://vocab.met.no/mmd/Instrument")
        assert group.is_initialised is False

        group.init_vocab()
        assert group.is_initialised is True

        group = MMDGroup("mmd", "https://vocab.met.no/mmd/NotAGroup")
        group.init_vocab()
        assert group.is_initialised is False

# END Test testCoreMMDGroup_Init


@pytest.mark.core
def testCoreMMDGroup_Search(filesDir):
    """Tests search in group against local files """
    group_data = readJson(os.path.join(filesDir, "Instrument.json"))
    modis_data = readJson(os.path.join(filesDir, "Instrument", "MODIS.json"))
    olci_data = readJson(os.path.join(filesDir, "Instrument", "OLCI.json"))

    def mock_get_vocab(self, voc_id, uri):
        if uri == "https://vocab.met.no/mmd/Instrument":
            return group_data
        elif uri == "https://vocab.met.no/mmd/Instrument/MODIS":
            return modis_data
        elif uri == "https://vocab.met.no/mmd/Instrument/OLCI":
            return olci_data
        return {}

    group = MMDGroup("mmd", "https://vocab.met.no/mmd/Instrument")
    group.init_vocab()

    modis_dict = {
        "Short_Name": "MODIS",
        "short_name": "MODIS",
        "Long_Name": "Moderate-resolution Imaging Spectro-radiometer",
        "long_name": "Moderate-resolution Imaging Spectro-radiometer",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/modis",
        "resource": "https://www.wmo-sat.info/oscar/instruments/view/modis"
    }
    olci_dict = {
        "Short_Name": "OLCI",
        "short_name": "OLCI",
        "Long_Name": "Ocean and Land Colour Imager",
        "long_name": "Ocean and Land Colour Imager",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/olci",
        "resource": "https://www.wmo-sat.info/oscar/instruments/view/olci"
    }

    assert group.search("MODIS") == modis_dict
    assert group.search("MODIS") != olci_dict

    assert group.search("Ocean and Land Colour Imager") == olci_dict
    assert group.search("Ocean and Land Colour Imager") != modis_dict

    assert group.search("MockSat") == {}
    assert group.search("MockSat") != modis_dict
    assert group.search("MockSat") != olci_dict

# END Test testCoreMMDGroup_Search


@pytest.mark.core
def testCoreMMDGroup_SearchLowercase(filesDir):
    """Tests search in group against local files """
    group_data = readJson(os.path.join(filesDir, "Instrument.json"))
    modis_data = readJson(os.path.join(filesDir, "Instrument", "MODIS.json"))
    olci_data = readJson(os.path.join(filesDir, "Instrument", "OLCI.json"))

    def mock_get_vocab(self, voc_id, uri):
        if uri == "https://vocab.met.no/mmd/Instrument":
            return group_data
        elif uri == "https://vocab.met.no/mmd/Instrument/MODIS":
            return modis_data
        elif uri == "https://vocab.met.no/mmd/Instrument/OLCI":
            return olci_data
        return {}

    group = MMDGroup("mmd", "https://vocab.met.no/mmd/Instrument")
    group.init_vocab()

    modis_dict = {
        "Short_Name": "MODIS",
        "short_name": "MODIS",
        "Long_Name": "Moderate-resolution Imaging Spectro-radiometer",
        "long_name": "Moderate-resolution Imaging Spectro-radiometer",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/modis",
        "resource": "https://www.wmo-sat.info/oscar/instruments/view/modis"
    }
    olci_dict = {
        "Short_Name": "OLCI",
        "short_name": "OLCI",
        "Long_Name": "Ocean and Land Colour Imager",
        "long_name": "Ocean and Land Colour Imager",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/olci",
        "resource": "https://www.wmo-sat.info/oscar/instruments/view/olci"
    }

    assert group.search_lowercase("MODIS") == modis_dict
    assert group.search_lowercase("MODIS") != olci_dict

    assert group.search_lowercase("MoDiS") == modis_dict
    assert group.search_lowercase("MoDiS") != olci_dict

    assert group.search_lowercase("Ocean and Land Colour Imager") == olci_dict
    assert group.search_lowercase("Ocean and Land Colour Imager") != modis_dict

    assert group.search_lowercase("ocean and land colour imager") == olci_dict
    assert group.search_lowercase("ocean and land colour imager") != modis_dict

    assert group.search_lowercase("mocksat") == {}
    assert group.search_lowercase("mocksat") != modis_dict
    assert group.search_lowercase("mocksat") != olci_dict

# END Test testCoreMMDGroup_SearchLowercase


@pytest.mark.core
def testCoreMMDGroup_GetLabel(monkeypatch):
    """Test helper function for getting labels"""
    with monkeypatch.context() as mp:
        mp.setattr(DataCache, "get_vocab", lambda *a: {})
        group = MMDGroup("mmd", "https://vocab.met.no/mmd/Platform")

    concept = {"label": "value"}
    concept_with_dict = {"label": {"value": "inner_value"}}
    concept_with_list = {"label": [{"value": "name0"}, {"value": "name1"}]}
    concept_with_empty_list = {"label": []}
    invalid_concept = {"resource": 123}

    assert group._get_label("NotADict", "label") is None

    assert group._get_label(concept, "label") == "value"
    assert group._get_label(concept, "value") is None

    assert group._get_label(concept_with_dict, "label") == "inner_value"
    assert group._get_label(concept_with_dict, "value") is None

    assert group._get_label(invalid_concept, "resource") is None

    assert group._get_label(concept_with_empty_list, "label") is None

    assert group._get_label(concept_with_list, "label") == "name0"
    assert group._get_label(concept_with_list, "value") is None

# END Test testCoreMMDGroup_GetLabel


@pytest.mark.core
def testCoreMMDGroup_GetLabelLowercase(monkeypatch):
    """Test wrapper function for getting lowercase labels"""
    with monkeypatch.context() as mp:
        mp.setattr(DataCache, "get_vocab", lambda *a: {})
        group = MMDGroup("mmd", "https://vocab.met.no/mmd/Platform")

    concept = {"label": "value", "label_but_big": "VaLuE"}

    # Check for cases with no label results
    with monkeypatch.context() as mp:
        mp.setattr(group, "_get_label", lambda *a: None)
        assert group._get_label_lowercase(concept, "label") is None

    # Check for cases with label results
    assert group._get_label_lowercase(concept, "label") == "value"
    assert group._get_label_lowercase(concept, "label_but_big") == "value"

# END Test testCoreMMDGroup_GetLabelLowercase


@pytest.mark.core
def testCoreMMDGroup_GetResource(monkeypatch):
    """Test helper function for getting resources"""
    with monkeypatch.context() as mp:
        mp.setattr(DataCache, "get_vocab", lambda *a: {})
        group = MMDGroup("mmd", "https://vocab.met.no/mmd/Platform")

    concept_dict = {"resource": "https://vocab.met.no"}
    concept_with_list = {"resource": [{"uri": "https://vocab.met.no"}, {"uri": "wmo.com"}]}
    concept_with_dict = {"resource": {"uri": "https://vocab.met.no"}}
    invalid_concept = {"resource": 123}
    concept_with_empty_list = {"resource": []}

    assert group._get_resource("NotADict", "label") == ""

    assert group._get_resource(concept_dict, "resource") == "https://vocab.met.no"
    assert group._get_resource(concept_dict, "resource") != "SomethingElse"

    assert group._get_resource(concept_with_list, "resource") == "https://vocab.met.no"
    assert group._get_resource(concept_with_list, "resource") != "SomethingElse"

    assert group._get_resource(concept_with_dict, "resource") == "https://vocab.met.no"
    assert group._get_resource(concept_with_dict, "resource") != "SomethingElse"

    assert group._get_resource(invalid_concept, "resource") == ""

    assert group._get_resource(concept_with_empty_list, "resource") == ""

    assert group._get_resource({"resource": ["hello"]}, "resource") == ""

# END Test testCoreMMDGroup_GetResource
