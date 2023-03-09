#!/usr/bin/env python3

import os


class Base:
    """A base class for implementing tests."""

    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
