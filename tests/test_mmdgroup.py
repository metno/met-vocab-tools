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

import pytest

from metvocab import MMDGroup


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
    assert group.search("Ocean and Land Colour Imager") == olci_dict
    assert group.search("MockSat") == {}

# END Test testLiveMMDGroup_Init


@pytest.mark.core
def testCoreMMDGroup_Init():
    pass

# END TEST testCoreMMDGroup_Init


@pytest.mark.core
def testCoreMMDGroup_Search():
    pass

# END TEST testCoreMMDGroup_Search
