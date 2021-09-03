"""
MetVocab : Main Package Init
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

__package__ = "metvocab"
__version__ = "0.1"

import os
import logging

CACHE_PATH = os.environ.get("METVOCAB_CACHEPATH", None)


def _init_logging(log_obj):
    """Call to initialise logging."""
    # Read environment variables
    want_level = os.environ.get("METVOCAB_LOGLEVEL", "INFO")
    log_file = os.environ.get("METVOCAB_LOGFILE", None)
    
    # Determine log level and format
    if hasattr(logging, want_level):
        log_level = getattr(logging, want_level)
    else:
        print("Invalid logging level '%s' in environment variable METVOCAB_LOGLEVEL" % want_level)
        log_level = logging.INFO

    if log_level < logging.INFO:
        msg_format = "[{asctime:}] {name:>28}:{lineno:<4d} {levelname:8s} {message:}"
    else:
        msg_format = "{levelname:8s} {message:}"

    log_format = logging.Formatter(fmt=msg_format, style="{")
    log_obj.setLevel(log_level)

    # Create stream handlers
    h_stdout = logging.StreamHandler()
    h_stdout.setLevel(log_level)
    h_stdout.setFormatter(log_format)
    log_obj.addHandler(h_stdout)

    if log_file is not None:
        h_file = logging.FileHandler(log_file, encoding="utf-8")
        h_file.setLevel(log_level)
        h_file.setFormatter(log_format)
        log_obj.addHandler(h_file)

    return


def setup_cache_path(cache_path):
    
    path_tries = [
        os.path.join("~", ".local", "share"),
        os.path.join("~", "Library", "Application Support"),
    ]
    
    for a_path in path_tries:
        a_path = os.path.expanduser(a_path)
        if os.path.isdir(a_path):
            cache_path = a_path
            break

    if cache_path is None:
        cache_path = os.path.expanduser("~")

    return cache_path


# Logging Setup
logger = logging.getLogger(__name__)
_init_logging(logger)

# Cache path setup
if CACHE_PATH is None:
    CACHE_PATH = setup_cache_path(CACHE_PATH)
if CACHE_PATH is None:
    raise OSError("Was not allowed to create cache folder")
