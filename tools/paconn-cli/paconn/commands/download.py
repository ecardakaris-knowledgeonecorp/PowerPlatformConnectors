# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
Download command.
"""

from paconn import _DOWNLOAD

from paconn.common.util import display
from paconn.settings.util import load_settings_and_powerapps_rp

import paconn.operations.download


# pylint: disable=too-many-arguments
def download(
        environment,
        connector_id,
        destination,
        powerapps_url,
        powerapps_version,
        settings_file,
        overwrite):
    """
    Download command.
    """
    # Get settings and the powerapps rp
    settings, powerapps_rp = load_settings_and_powerapps_rp(
        command_context=_DOWNLOAD,
        environment=environment,
        settings_file=settings_file,
        connector_id=connector_id,
        powerapps_url=powerapps_url,
        powerapps_version=powerapps_version)

    directory = paconn.operations.download.download(
        powerapps_rp=powerapps_rp,
        settings=settings,
        destination=destination,
        overwrite=overwrite)

    display('The connector is downloaded to {}.'.format(directory))
