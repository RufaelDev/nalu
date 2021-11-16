#!/usr/bin/env python
"""
   Copyright 2021 Unified Streaming

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

from os.path import abspath, dirname, join
from setuptools import setup, find_packages
from sys import path as sys_path
import pathlib
import logging

VERSION_FILE='RELEASE-VERSION'

deps = [
    "bitstring"
]

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')

try:
    version = ".".join((here / VERSION_FILE).read_text(encoding='utf-8').strip().split("-")[:2])
except FileNotFoundError:
    logging.error(f'file {VERSION_FILE} not found. Please use "make dist" to create a package')
    exit(-1)

srcdir = join(dirname(abspath(__file__)), "src/")
sys_path.insert(0, srcdir)

setup(name="nalu",
      version=version,
      description="A nalu parser, with focus on alignment with the latest standard features.",
      long_description=long_description,
      long_description_content_type='text/markdown',
      url="https://github.com/RufaelDev/nalu",
      author="Unified Streaming",
      author_email="support@unified-streaming.com",
      license="Apache 2.0",
      packages=find_packages("src"),
      package_dir={"": "src"},
      entry_points={
          "console_scripts": ["naludump=nalu.cli:__main__"]   ## will be empty at the moment intended use is library
      },
      install_requires=deps,
      test_suite="tests",
      classifiers=["Development Status :: 4 - Beta",
                   "Environment :: Console",
                   "Operating System :: POSIX",
                   "Operating System :: Microsoft :: Windows :: Windows 10",
                   "Programming Language :: Python :: 3.6",
                   "Topic :: Multimedia :: Video",
                   "Topic :: Multimedia :: Sound/Audio",
                   "Topic :: Utilities"])
