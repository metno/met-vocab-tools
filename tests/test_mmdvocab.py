"""
MetVocab : MMDVocab Init Test
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

import os
import json
import pytest

from metvocab.mmdvocab import MMDVocab


@pytest.mark.core
def testCoreMMDVocab_Init():
    """Test the creation initialisation of the MMDVocab class"""
    with pytest.raises(TypeError):
        lookup = MMDVocab()

    lookup = MMDVocab("mmd", "https://vocab.met.no/mmd/Access_Constraint")

    assert lookup._voc_id == "mmd"
    assert lookup._uri == "https://vocab.met.no/mmd/Access_Constraint"

# END Test testCoreMMDVocab_Init


@pytest.mark.live
def testLiveMMDVocab_InitVocab():
    """Tests initialisation of vocabulary against the live api"""
    lookup = MMDVocab("mmd", "https://vocab.met.no/mmd/Access_Constraint")

    lookup.init_vocab()
    assert lookup.is_initialised is True


# END Test testLiveMMDVocab_InitVocab


@pytest.mark.core
def testCoreMMDVocab_InitVocab(monkeypatch, filesDir):
    """Tests initialisation of vocabulary against local files"""
    json_path = os.path.join(filesDir, "Access_Constraint.json")

    with open(json_path, mode="r", encoding="utf-8") as infile:
        data = json.load(infile)
    lookup = MMDVocab("mmd", "https://vocab.met.no/mmd/Access_Constraint")
    with monkeypatch.context() as mp:
        mp.setattr(lookup._cache, "get_vocab", lambda *a: data)
        lookup.init_vocab()
        assert lookup.is_initialised

    # Check invalid json?

# END Test testCoreMMDVocab_InitVocab


@pytest.mark.core
def testCoreMMDVocab_CheckConceptValue():
    """Tests check_concept_value function in lookup class"""
    lookup = MMDVocab("mmd", "https://vocab.met.no/mmd/Access_Constraint")
    lookup._concept_values = set(["Open", "Registered users only (automated approval)"])

    assert lookup.check_concept_value("Open")
    assert not lookup.check_concept_value("Closed")
    with pytest.raises(ValueError):
        lookup.check_concept_value(["Open", "Closed"])
        lookup.check_concept_value(2)

# END Test testCoreMMDVocab_CheckConceptValue


@pytest.mark.core
def testMMDVocab_CheckIsConcept():
    """Tests check_is_concept function in lookup class"""
    lookup = MMDVocab("mmd", "https://vocab.met.no/mmd/Access_Constraint")
    assert lookup._check_is_concept("skos:Concept") is True
    assert lookup._check_is_concept(["skos:Concept", "NONE"]) is True
    assert lookup._check_is_concept("skos:Collection") is False
    assert lookup._check_is_concept(["skos:Collection", "isothes:ConceptGroup"]) is False
    assert lookup._check_is_concept(None) is False

# END Test testMMDVocab_CheckIsConcept
