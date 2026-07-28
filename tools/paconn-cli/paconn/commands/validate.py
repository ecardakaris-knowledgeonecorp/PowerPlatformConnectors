# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
Validate command.
"""

from paconn import _VALIDATE

from paconn.common.util import display
from paconn.settings.util import load_settings_and_powerapps_rp

import paconn.operations.validate


def validate(
        api_definition,
        powerapps_url,
        powerapps_version,
        settings_file):
    """
    Validate command.
    """
    # Get settings and the powerapps rp
    settings, powerapps_rp = load_settings_and_powerapps_rp(
        command_context=_VALIDATE,
        settings_file=settings_file,
        api_definition=api_definition,
        powerapps_url=powerapps_url,
        powerapps_version=powerapps_version)

    result = paconn.operations.validate.validate(
        powerapps_rp=powerapps_rp,
        settings=settings)

    if result:
        display(result)
    else:
        display('{} validated successfully.'.format(settings.api_definition))
