"""
MetVocab : MMD Vocabulary Class Tests
=====================================

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
import json
import pytest

from metvocab.cache import DataCache
from metvocab.mmdgroup import MMDGroup


@pytest.mark.live
def testLiveMMDGroup_Init():
    group = MMDGroup("mmd", "https://vocab.met.no/mmd/Platform")
    assert len(group._concepts) > 0
    group = MMDGroup("mmd", "https://vocab.met.no/mmd/NotAGroup")
    assert len(group._concepts) == 0

# END Test testLiveMMDGroup_Init


@pytest.mark.live
def testLiveMMDGroup_Search():
    group = MMDGroup("mmd", "https://vocab.met.no/mmd/Instrument")

    modis_dict = {
        "Short_Name": "MODIS",
        "Long_Name": "Moderate-resolution Imaging Spectro-radiometer",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/modis"
    }
    olci_dict = {
        "Short_Name": "OLCI",
        "Long_Name": "Ocean and Land Colour Imager",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/olci"
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
    """Tests initialisation of vocabulary against local files"""

    json_path = os.path.join(filesDir, "Instrument.json")

    with open(json_path, mode="r", encoding="utf-8") as infile:
        data = json.load(infile)

    def mock_get_vocab(self, voc_id, uri):
        if uri == "https://vocab.met.no/mmd/Instrument":
            return data
        return {}

    with monkeypatch.context() as mp:
        mp.setattr(DataCache, "get_vocab", mock_get_vocab)
        group = MMDGroup("mmd", "https://vocab.met.no/mmd/Instrument")
        assert len(group._concepts) > 0
        group = MMDGroup("mmd", "https://vocab.met.no/mmd/NotAGroup")
        assert len(group._concepts) == 0

# END TEST testCoreMMDGroup_Init


@pytest.mark.core
def testCoreMMDGroup_Search(filesDir):
    """Tests search of vocabulary against local files"""

    json_group_path = os.path.join(filesDir, "Instrument.json")
    json_modis_path = os.path.join(filesDir, "Instrument", "MODIS.json")
    json_olci_path = os.path.join(filesDir, "Instrument", "OLCI.json")

    with open(json_group_path, mode="r", encoding="utf-8") as infile:
        group_data = json.load(infile)
    with open(json_modis_path, mode="r", encoding="utf-8") as infile:
        modis_data = json.load(infile)
    with open(json_olci_path, mode="r", encoding="utf-8") as infile:
        olci_data = json.load(infile)

    def mock_get_vocab(self, voc_id, uri):
        if uri == "https://vocab.met.no/mmd/Instrument":
            return group_data
        elif uri == "https://vocab.met.no/mmd/Instrument/MODIS":
            return modis_data
        elif uri == "https://vocab.met.no/mmd/Instrument/OLCI":
            return olci_data
        return {}

    group = MMDGroup("mmd", "https://vocab.met.no/mmd/Instrument")

    modis_dict = {
        "Short_Name": "MODIS",
        "Long_Name": "Moderate-resolution Imaging Spectro-radiometer",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/modis"
    }
    olci_dict = {
        "Short_Name": "OLCI",
        "Long_Name": "Ocean and Land Colour Imager",
        "Resource": "https://www.wmo-sat.info/oscar/instruments/view/olci"
    }

    assert group.search("MODIS") == modis_dict
    assert group.search("MODIS") != olci_dict

    assert group.search("Ocean and Land Colour Imager") == olci_dict
    assert group.search("Ocean and Land Colour Imager") != modis_dict

    assert group.search("MockSat") == {}
    assert group.search("MockSat") != modis_dict
    assert group.search("MockSat") != olci_dict


# END TEST testCoreMMDGroup_Search

def testCoreMMDGroup_GetLabel(monkeypatch):
    with monkeypatch.context() as mp:
        mp.setattr(DataCache, "get_vocab", lambda *a : {})
        group = MMDGroup("mmd", "https://vocab.met.no/mmd/Platform")

    concept = {"label": "value"}
    concept_with_dict = {"label": {"value": "inner_value"}}

    assert group._get_label(concept, "label") == "value"
    assert group._get_label(concept, "value") is None

    assert group._get_label(concept_with_dict, "label") == "inner_value"
    assert group._get_label(concept_with_dict, "value") is None



# END TEST testCoreMMDGroup_GetLabel


def testCoreMMDGroup_GetResource(monkeypatch):
    with monkeypatch.context() as mp:
        mp.setattr(DataCache, "get_vocab", lambda *a : {})
        group = MMDGroup("mmd", "https://vocab.met.no/mmd/Platform")

    concept_dict = {"resource": "https://vocab.met.no"}
    concept_with_list = {"resource": [{"uri": "https://vocab.met.no"}, {"uri": "wmo.com"}]}
    concept_with_dict = {"resource": {"uri": "https://vocab.met.no"}}
    invalid_concept = {"resource": 123}


    assert group._get_resource(concept_dict, "resource") == "https://vocab.met.no"
    assert group._get_resource(concept_dict, "resource") != "SomethingElse"

    assert group._get_resource(concept_with_list, "resource") == "https://vocab.met.no"
    assert group._get_resource(concept_with_list, "resource") != "SomethingElse"

    assert group._get_resource(concept_with_dict, "resource") == "https://vocab.met.no"
    assert group._get_resource(concept_with_dict, "resource") != "SomethingElse"

    assert group._get_resource(invalid_concept, "resource") == ""
# END TEST testCoreMMDGroup_GetResource
