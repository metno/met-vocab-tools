"""
MetVocab : CF Standards Vocabulary Class Tests
==============================================

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

import metvocab.cfstd

from tools import writeFile
from metvocab import CFStandard


@pytest.mark.core
def testCoreCFStandard_Init():
    """Test the instantiation of the CFStandard class"""
    cfstd = CFStandard()

    assert cfstd.is_initialised is False

# END Test testCoreCFStandard_Init


@pytest.mark.core
def testCoreCFStandard_InitVocab(monkeypatch, fncDir):
    """Tests initialisation of vocabulary"""

    cfstd = CFStandard()

    # No XML File
    with monkeypatch.context() as mp:
        mp.setattr(metvocab.cfstd, "PKG_PATH", fncDir)
        with pytest.raises(OSError):
            cfstd.init_vocab()
        assert cfstd.is_initialised is False

    # Mock XML File
    os.mkdir(os.path.join(fncDir, "data"))
    mockFile = os.path.join(fncDir, "data", "cf-standard-name-table.xml")
    writeFile(mockFile, (
        "<?xml version=\"1.0\"?>\n"
        "<whatever>\n"
        "<entry id=\"stuff\"/>\n"
        "</whatever>"
    ))

    with monkeypatch.context() as mp:
        mp.setattr(metvocab.cfstd, "PKG_PATH", fncDir)
        with pytest.raises(LookupError):
            cfstd.init_vocab()
        assert cfstd.is_initialised is False

    # Successful Init
    cfstd.init_vocab()
    assert cfstd.is_initialised is True
    assert cfstd.cf_version != "Unknown"
    assert cfstd.cf_modified != "Unknown"
    assert len(cfstd._standard_names) > 0

# END Test testCoreCFStandard_InitVocab


@pytest.mark.core
def testCoreCFStandard_CheckStandardName():
    """Tests checking standard name from vocabulary"""

    cfstd = CFStandard()
    cfstd.init_vocab()
    assert cfstd.is_initialised is True

    # Invalid Names
    assert cfstd.check_standard_name("something_i_made_up") is False
    assert cfstd.check_standard_name(12345) is False
    assert cfstd.check_standard_name(None) is False

    # Valid Standard Names
    assert cfstd.check_standard_name("aerodynamic_particle_diameter") is True
    assert cfstd.check_standard_name("atmosphere_mole_content_of_water_vapor") is True
    assert cfstd.check_standard_name("atmosphere_momentum_diffusivity") is True
    assert cfstd.check_standard_name("mass_concentration_of_ammonia_in_air") is True
    assert cfstd.check_standard_name("mole_fraction_of_isoprene_in_air") is True

    # Check Aliases
    assert cfstd.check_standard_name("mass_fraction_of_o3_in_air", include_alias=False) is False
    assert cfstd.check_standard_name("mass_fraction_of_o3_in_air", include_alias=True) is True
    assert cfstd.check_standard_name("swell_wave_period", include_alias=False) is False
    assert cfstd.check_standard_name("swell_wave_period", include_alias=True) is True
    assert cfstd.check_standard_name("longwave_radiance", include_alias=False) is False
    assert cfstd.check_standard_name("longwave_radiance", include_alias=True) is True

# END Test testCoreCFStandard_CheckStandardName
