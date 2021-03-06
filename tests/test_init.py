"""
MetVocab : Package Init Test
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
import pytest
import logging

import metvocab

from tools import readFile


@pytest.mark.core
def testCoreInit_Init():
    """Test the package initialisation."""
    assert metvocab.__version__ != ""
    assert metvocab.__package__ == "metvocab"

# END Test testCoreInit_Init


@pytest.mark.core
def testCoreInit_Logger(tmpDir):
    """Test the logger initialisation."""
    os.environ["METVOCAB_LOGLEVEL"] = "DEBUG"
    logger = logging.getLogger(__name__)
    metvocab._init_logging(logger)
    assert logger.getEffectiveLevel() == logging.DEBUG

    os.environ["METVOCAB_LOGLEVEL"] = "INVALID"
    logger = logging.getLogger(__name__)
    metvocab._init_logging(logger)
    assert logger.getEffectiveLevel() == logging.INFO

    # Test log file
    logFile = os.path.join(tmpDir, "test.log")
    if os.path.isfile(logFile):
        os.unlink(logFile)

    os.environ["METVOCAB_LOGLEVEL"] = "DEBUG"
    os.environ["METVOCAB_LOGFILE"] = logFile
    logger = logging.getLogger(__name__)
    metvocab._init_logging(logger)
    assert os.path.isfile(logFile)
    logger.debug("Some log message")
    assert readFile(logFile).strip().endswith("Some log message")

# END Test testCoreInit_Logger
