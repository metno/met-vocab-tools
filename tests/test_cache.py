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

from metvocab.cache import DataCache


@pytest.fixture(scope="function")
def tstCache(fncDir):
    """A mock instance of DataCache that redirects the config path to
    a temporary folder.
    """
    os.environ["METVOCAB_CACHEPATH"] = fncDir
    os.environ["METVOCAB_MAXAGE"] = "7"
    dtCache = DataCache()
    assert dtCache._cache_path == fncDir
    return dtCache


class MockResponse():
    """Mock response object to return from urlopen."""

    def __init__(self, status=200, data="{}"):
        self.status = status
        self.code = status
        self.data = data

    def read(self):
        return self.data


@pytest.mark.core
def testDataCache_CachePath(tstCache, monkeypatch):
    """Test the creation and/or discovery of cache_folder"""
    def mock_isdir(path):
        if path == os.path.expanduser(os.path.join("~", ".local", "share")):
            return True
        else:
            return False

    with monkeypatch.context() as mp:
        a_path = os.path.join("~", ".local", "share", "metvocab")
        e_path = os.path.expanduser(a_path)
        mp.delenv("METVOCAB_CACHEPATH")
        mp.setattr(os.path, "isdir", mock_isdir)
        mp.setattr(os, "makedirs", lambda *a, **k: None)
        tstCache._setup_cache_path()
        assert tstCache._cache_path == e_path

    with monkeypatch.context() as mp:
        mp.delenv("METVOCAB_CACHEPATH")
        mp.setattr(os.path, "isdir", lambda *a: False)
        mp.setattr(os, "makedirs", lambda *a, **k: None)
        with pytest.raises(OSError):
            tstCache._setup_cache_path()

    # Check max_age is default 7 days in seconds
    assert tstCache._max_age == 7*86400

    with monkeypatch.context() as mp:
        mp.setenv("METVOCAB_MAXAGE", "14")
        tstCache._setup_cache_path()
        assert tstCache._max_age == 14*86400

    with monkeypatch.context() as mp:
        mp.setenv("METVOCAB_MAXAGE", "0")
        tstCache._setup_cache_path()
        assert tstCache._max_age == 3600

# END Test testDataCache_CachePath


@pytest.mark.data
def testDataCache_RetrieveData(tstCache, monkeypatch, caplog):
    """Test the data retrieval function."""
    testUri = "https://vocab.met.no/mmd/Access_Constraint"

    # Test HTTPError
    with monkeypatch.context() as mp:
        def mockUrlopen(*a):
            raise urllib.error.HTTPError("url", 400, "oops!", "", "")

        mp.setattr(urllib.request, "urlopen", mockUrlopen)
        caplog.clear()
        status, data = tstCache._retrieve_data("mmd", testUri)
        assert status is False
        assert data == {}
        assert "HTTP Error 400: oops!" in caplog.text

    # Test URLError
    with monkeypatch.context() as mp:
        def mockUrlopen(*a):
            raise urllib.error.URLError("oops!")

        mp.setattr(urllib.request, "urlopen", mockUrlopen)
        caplog.clear()
        status, data = tstCache._retrieve_data("mmd", testUri)
        assert status is False
        assert data == {}
        assert "oops!" in caplog.text

    # No response
    with monkeypatch.context() as mp:
        mp.setattr(urllib.request, "urlopen", lambda *a: None)
        caplog.clear()
        status, data = tstCache._retrieve_data("mmd", testUri)
        assert status is False
        assert data == {}
        assert "No response returned from API" in caplog.text

    # Successful request
    with monkeypatch.context() as mp:
        m_data = {"test": "test"}

        def mockUrlopen(*a):
            return MockResponse(200, json.dumps(m_data))

        mp.setattr(urllib.request, "urlopen", mockUrlopen)
        status, data = tstCache._retrieve_data("mmd", testUri)
        assert status is True
        assert data == m_data
        assert tstCache.get_vocab("mmd", testUri) == data

# END Test testDataCache_RetrieveData


@pytest.mark.live
def testLiveCache_RetrieveData(tstCache, tmpDir):
    """Test the data retrieval function on the actual API."""
    status, data = tstCache._retrieve_data("mmd", "https://vocab.met.no/mmd/Access_Constraint")
    assert status is True
    assert data != {}
    assert data.get("@context", None) is not None

    savePath = os.path.join(tmpDir, "Access_Constraint.json")
    with open(savePath, mode="w", encoding="utf-8") as outFile:
        json.dump(data, outFile, indent=2)

# END Test testLiveCache_RetrieveData


@pytest.mark.data
def testDataCache_GetData(tstCache, monkeypatch, fncDir):
    """Test the data caching when data retrieval succeds, fails and
    tests for cases where cache exists, both when old and not old
    """
    def mock_retrieve_data_succ(voc_id, uri):
        return True, {voc_id: uri}

    with pytest.raises(ValueError):
        tstCache._get_data("", "https://met.no")

    with monkeypatch.context() as mp:
        mp.setattr(tstCache, "_retrieve_data", mock_retrieve_data_succ)
        tstCache._get_data("", "https://met.no/path1/path2")
        path = os.path.join(fncDir, "path1")
        json_path = os.path.join(path, "path2.json")
        assert os.path.isdir(path)
        assert os.path.isfile(json_path)

        with open(json_path, mode="r", encoding="utf-8") as infile:
            assert json.load(infile) == {"": "https://met.no/path1/path2"}

    # Intentionally not removing path1/path2.json
    with monkeypatch.context() as mp:
        mp.setattr(tstCache, "_retrieve_data", mock_retrieve_data_succ)
        data = tstCache._get_data("new_vocab", "https://met.no/path1/path2")

        # Since file is new, the file is not overwritten with vocab = new_vocab
        assert data == {"": "https://met.no/path1/path2"}

        mp.setattr(tstCache, "_check_timestamp", lambda *a: True)
        # File is now stale, so overwritten with new_vocab as voc_id
        data = tstCache._get_data("new_vocab", "https://met.no/path1/path2")
        assert data != {"": "https://met.no/path1/path2"}
        assert data == {"new_vocab": "https://met.no/path1/path2"}

    os.unlink(json_path)

    with monkeypatch.context() as mp:
        mp.setattr(tstCache, "_retrieve_data", lambda *a: (False, {}))
        data = tstCache._get_data("new_vocab", "https://met.no/path1/path2")
        assert data is None

# END Test testDataCache_GetData


@pytest.mark.data
def testDataCache_CreateCache(tstCache, monkeypatch, fncDir):
    """Tests the creation of cache, and behavior when data retrieval
    fails.
    """
    def mock_retrieve_data_succ(voc_id, uri):
        return True, {voc_id: uri}

    def mock_retrieve_data_fail(voc_id, uri):
        return False, {voc_id: uri}

    json_path = os.path.join(fncDir, "mock.json")

    # Check case where _retrieve_data is success
    with monkeypatch.context() as mp:
        mp.setattr(tstCache, "_retrieve_data", mock_retrieve_data_succ)
        status = tstCache._create_cache(fncDir, json_path, "Hello", "World")
        assert status
        assert os.path.isfile(json_path)
        with open(json_path, mode="r", encoding="utf-8") as infile:
            assert json.load(infile) == {"Hello": "World"}

    os.unlink(json_path)
    # If _retrieve_data fails
    with monkeypatch.context() as mp:
        mp.setattr(tstCache, "_retrieve_data", mock_retrieve_data_fail)
        status = tstCache._create_cache(fncDir, json_path, "Hello", "World")
        assert not os.path.isfile(json_path)
        assert not status

# END Test testDataCache_CreateCache


@pytest.mark.data
def testDataCache_CheckTimestamp(tstCache, fncDir):
    """Tests _check_timestamp method in Cache class when file is fresh
    and when file is stale"""
    old_file = os.path.join(fncDir, "old.json")
    new_file = os.path.join(fncDir, "new.json")
    writeFile(new_file, "mockinfo")
    writeFile(old_file, "mockinfo")

    # Manually set access and modified times of old_file
    os.utime(old_file, (100, 100))

    # Check if old is older than 1 day
    assert tstCache._check_timestamp(old_file, 86400) is True
    # Check if newly created file within 1 day threshold
    assert tstCache._check_timestamp(new_file, 86400) is False

# END Test testDataCache_CheckTimestamp
