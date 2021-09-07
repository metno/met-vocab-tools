"""
MetVocab : Cache Class Tests
============================

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
import urllib.error
import urllib.request

from tools import writeFile

from metvocab import CONFIG
from metvocab.cache import DataCache


class MockResponse():
    """Mock response object to return from urlopen."""

    def __init__(self, status=200, data="{}"):
        self.status = status
        self.code = status
        self.data = data

    def read(self):
        return self.data


@pytest.mark.data
def testDataCache_RetrieveData(monkeypatch, caplog):
    """Test the data retrieval function."""
    dtCache = DataCache()
    testUri = "https://vocab.met.no/mmd/Access_Constraint"

    # Test HTTPError
    with monkeypatch.context() as mp:
        def mockUrlopen(*a):
            raise urllib.error.HTTPError("url", 400, "oops!", "", "")

        mp.setattr(urllib.request, "urlopen", mockUrlopen)
        caplog.clear()
        status, data = dtCache._retrieve_data("mmd", testUri)
        assert status is False
        assert data == {}
        assert "HTTP Error 400: oops!" in caplog.text

    # Test URLError
    with monkeypatch.context() as mp:
        def mockUrlopen(*a):
            raise urllib.error.URLError("oops!")

        mp.setattr(urllib.request, "urlopen", mockUrlopen)
        caplog.clear()
        status, data = dtCache._retrieve_data("mmd", testUri)
        assert status is False
        assert data == {}
        assert "oops!" in caplog.text

    # No response
    with monkeypatch.context() as mp:
        mp.setattr(urllib.request, "urlopen", lambda *a: None)
        caplog.clear()
        status, data = dtCache._retrieve_data("mmd", testUri)
        assert status is False
        assert data == {}
        assert "No response returned from API" in caplog.text

    # Successful request
    with monkeypatch.context() as mp:
        m_data = {"test": "test"}

        def mockUrlopen(*a):
            return MockResponse(200, json.dumps(m_data))

        mp.setattr(urllib.request, "urlopen", mockUrlopen)
        status, data = dtCache._retrieve_data("mmd", testUri)
        assert status is True
        assert data == m_data

# END Test testDataCache_RetrieveData


@pytest.mark.live
def testLiveCache_RetrieveData():
    """Test the data retrieval function on the actual API."""
    dtCache = DataCache()

    status, data = dtCache._retrieve_data("mmd", "https://vocab.met.no/mmd/Access_Constraint")
    assert status is True
    assert data != {}
    assert data.get("@context", None) is not None

# END Test testLiveCache_RetrieveData


@pytest.mark.data
def testDataCache_CheckCache(monkeypatch, fncDir):
    def mock_retrieve_data_succ(voc_id, uri):
        return True, {voc_id: uri}

    def mock_retrieve_data_fail(voc_id, uri):
        return False, {voc_id: uri}

    CONFIG.cache_path = fncDir
    dtCache = DataCache()

    with pytest.raises(ValueError):
        dtCache._check_cache("", "https://met.no")

    with monkeypatch.context() as mp:
        mp.setattr(dtCache, "_retrieve_data", mock_retrieve_data_succ)
        dtCache._check_cache("", "https://met.no/path1/path2")
        path = os.path.join(fncDir, "path1")
        json_path = os.path.join(path, "path2.json")
        assert os.path.isdir(path)
        assert os.path.isfile(json_path)

        with open(json_path, "r") as infile:
            assert json.load(infile) == {"": "https://met.no/path1/path2"}

    # Intentionally not removing path1/path2.json
    with monkeypatch.context() as mp:
        mp.setattr(dtCache, "_retrieve_data", mock_retrieve_data_succ)
        data = dtCache._check_cache("new_vocab", "https://met.no/path1/path2")

        # Since file is new, the file is not overwritten with vocab = new_vocab
        assert data == {"": "https://met.no/path1/path2"}

        mp.setattr(dtCache, "_check_timestamp", lambda *a: True)
        # File is now stale, so overwritten with new_vocab as voc_id
        data = dtCache._check_cache("new_vocab", "https://met.no/path1/path2")
        assert data != {"": "https://met.no/path1/path2"}
        assert data == {"new_vocab": "https://met.no/path1/path2"}

    os.unlink(json_path)

    with monkeypatch.context() as mp:
        mp.setattr(dtCache, "_retrieve_data", lambda *a: (False, {}))
        data = dtCache._check_cache("new_vocab", "https://met.no/path1/path2")
        assert data is None

# END Test testDataCache_CheckCache


@pytest.mark.data
def testDataCache_CreateCache(monkeypatch, fncDir):
    def mock_retrieve_data_succ(voc_id, uri):
        return True, {voc_id: uri}

    def mock_retrieve_data_fail(voc_id, uri):
        return False, {voc_id: uri}

    json_path = os.path.join(fncDir, "mock.json")

    dtCache = DataCache()

    # Check case where _retrieve_data is success
    with monkeypatch.context() as mp:
        mp.setattr(dtCache, "_retrieve_data", mock_retrieve_data_succ)
        status = dtCache._create_cache(fncDir, json_path, "Hello", "World")
        assert status
        assert os.path.isfile(json_path)
        with open(json_path, "r") as infile:
            assert json.load(infile) == {"Hello": "World"}

    os.unlink(json_path)
    # If _retrieve_data fails
    with monkeypatch.context() as mp:
        mp.setattr(dtCache, "_retrieve_data", mock_retrieve_data_fail)
        status = dtCache._create_cache(fncDir, json_path, "Hello", "World")
        assert not os.path.isfile(json_path)
        assert not status

# END Test testDataCache_CreateCache


@pytest.mark.data
def testDataCache_CheckTimestamp(fncDir):
    dtCache = DataCache()
    old_file = os.path.join(fncDir, "old.json")
    new_file = os.path.join(fncDir, "new.json")
    writeFile(new_file, "mockinfo")
    writeFile(old_file, "mockinfo")

    # Manually set access and modified times of old_file
    os.utime(old_file, (100, 100))

    # Check if old is older than 1 day
    assert dtCache._check_timestamp(old_file, 86400) is True
    # Check if newly created file within 1 day threshold
    assert dtCache._check_timestamp(new_file, 86400) is False

# END Test testDataCache_CheckTimestamp
