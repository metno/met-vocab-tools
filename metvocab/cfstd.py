"""
MetVocab : CF Standard Vocabulary Class
=======================================

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
import sys
import time
import logging

from lxml import etree

logger = logging.getLogger(__name__)

PKG_PATH = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))


class CFStandard():

    def __init__(self):

        self._standard_names = set()
        self._is_initialised = False

        # Meta Data
        self._cf_version_number = "Unknown"
        self._cf_last_modified = "Unknown"

        return

    ##
    #  Properties
    ##

    @property
    def is_initialised(self):
        """Return the initialised state of the class."""
        return self._is_initialised

    @property
    def cf_version(self):
        """Return the version number of the CF data."""
        return self._cf_version_number

    @property
    def cf_modified(self):
        """Return the modified date of the CF data."""
        return self._cf_last_modified

    ##
    #  Methods
    ##

    def init_vocab(self):
        """Initialise vocabulary class by loading the data from vocab
        file. The vocab file is downloaded in XML format from:
        https://cfconventions.org/standard-names.html
        """
        self._standard_names = set()
        self._is_initialised = False

        start_time = time.time()

        cf_file = os.path.join(PKG_PATH, "data", "cf-standard-name-table.xml")
        cf_xml = etree.parse(cf_file)
        cf_root = cf_xml.getroot()
        if cf_root.tag != "standard_name_table":
            raise LookupError("The CF Standards file does not contain the correct root tag")

        for cf_elem in cf_root:
            if cf_elem.tag == "entry":
                cf_id = cf_elem.attrib.get("id", None)
                if cf_id is not None:
                    self._standard_names.add(cf_id)
            elif cf_elem.tag == "version_number":
                self._cf_version_number = cf_elem.text
            elif cf_elem.tag == "last_modified":
                self._cf_last_modified = cf_elem.text

        logger.debug("Parsing CF Standards file took %.3f ms", (time.time() - start_time)*1000)

        self._is_initialised = len(self._standard_names) > 0

        return

    def check_standard_name(self, value):
        """Look up a value in the list of standard names."""
        if isinstance(value, str):
            return value in self._standard_names
        return False

# END Class CFStandard
