# (C) Copyright 2021-2022 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from .pycentral_error import PycentralError


class UnsupportedCapabilityError(PycentralError):
    """
    Exception class for an PYCENTRAL Unsupported Capability Error.
    """

    base_msg = "UNSUPPORTED CAPABILITY"
