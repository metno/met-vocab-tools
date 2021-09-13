"""
MetVocab : Lookup Init Test
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

from metvocab.lookup import Lookup


@pytest.mark.core
def testCoreLookup_Init():
    """Test the creation initialisation of the Lookup class"""
    with pytest.raises(TypeError):
        lookup = Lookup()

    lookup = Lookup("mmd", "https://vocab.met.no/mmd/Access_Constraint")

    assert lookup._voc_id == "mmd"
    assert lookup._uri == "https://vocab.met.no/mmd/Access_Constraint"

# END Test testCoreLookup_Init


@pytest.mark.live
def testLiveLookup_InitVocab():
    """
    """
    lookup = Lookup("mmd", "https://vocab.met.no/mmd/Access_Constraint")

    lookup.init_vocab()
    assert lookup.is_initialised is True


# END Test testLiveLookup_InitVocab


@pytest.mark.core
def testCoreLookup_InitVocab(monkeypatch, filesDir):
    """
    """
    json_path = os.path.join(filesDir, "Access_Constraint.json")

    with open(json_path, mode="r", encoding="utf-8") as infile:
        data = json.load(infile)
    lookup = Lookup("mmd", "https://vocab.met.no/mmd/Access_Constraint")
    with monkeypatch.context() as mp:
        mp.setattr(lookup._cache, "get_vocab", lambda *a: data)
        lookup.init_vocab()
        assert lookup.is_initialised

    # Check invalid json?

# END Test testCoreLookup_InitVocab


@pytest.mark.core
def testCoreLookup_CheckConceptValue():
    """
    """
    lookup = Lookup("mmd", "https://vocab.met.no/mmd/Access_Constraint")
    lookup._concept_values = set(["Open", "Registered users only (automated approval)"])

    assert lookup.check_concept_value("Open")
    assert not lookup.check_concept_value("Closed")
    with pytest.raises(ValueError):
        lookup.check_concept_value(["Open", "Closed"])
        lookup.check_concept_value(2)

# END Test testCoreLookup_CheckConceptValue


@pytest.mark.core
def testLookup_CheckIsConcept():
    """
    """
    lookup = Lookup("mmd", "https://vocab.met.no/mmd/Access_Constraint")
    assert lookup._check_is_concept("skos:Concept") is True
    assert lookup._check_is_concept(["skos:Concept", "NONE"]) is True
    assert lookup._check_is_concept("skos:Collection") is False
    assert lookup._check_is_concept(["skos:Collection", "isothes:ConceptGroup"]) is False
    assert lookup._check_is_concept(None) is False

# END Test testLookup_CheckIsConcept
