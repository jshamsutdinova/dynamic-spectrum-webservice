#!/usr/bin/env python3
""" The class for Dynamic Spectrum exceptions """


class CannotDownloadFile(Exception):
    code = "CANNOTDOWNLOADFILE"


class AmaterasFileIsNotExists(Exception):
    code = "AMATERASFILEISNOTEXISTS"


class OrfeesFileIsNotExists(Exception):
    code = "ORFEESFILEISNOTEXISTS"


class CannotCreateDirectory(Exception):
    code = "CANNOTCREATEDIRECTORY"
