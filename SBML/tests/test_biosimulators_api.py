#!/usr/bin/env python
"""Test health status of the BioSimulators API."""

import sys

import requests

biosimulations_api_url = "https://api.biosimulations.org/health"

r = requests.get(biosimulations_api_url)
r_status = r.json()["status"]

if r_status == "ok":
    exit_status = 0
else:
    exit_status = 1

sys.exit(exit_status)
