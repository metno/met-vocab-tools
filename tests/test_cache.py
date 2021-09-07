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

import json
import pytest
import urllib.error
import urllib.request

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
