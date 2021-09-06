"""
MetVocab : Package Config Test
==============================

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

from metvocab.config import Config


@pytest.mark.core
def testCoreConfig_Init(monkeypatch):
    """Test the creation and/or discovery of cache_folder"""

    # How to make this non-linux specific?
    config = Config()
    a_path = os.path.join("~", ".local", "share", "metvocab")
    assert config.cache_path == os.path.expanduser(a_path)

    # Test reading of environment variable
    os.environ["METVOCAB_CACHEPATH"] = "PATH"
    config = Config()
    assert config.cache_path == "PATH"

    with monkeypatch.context() as mp:
        mp.setattr(os.path, "isdir", lambda *a: False)
        mp.setattr(os.path, "expanduser", lambda *a: "~")
        assert config._setup_cache_path(None) == os.path.join("~", "metvocab")

# END Test testCoreConfig_Init
