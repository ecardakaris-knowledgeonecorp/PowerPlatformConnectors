# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
Update command.
"""

from paconn import _UPDATE
from paconn.common.util import display
from paconn.settings.util import load_settings_and_powerapps_rp
from paconn.operations.upsert import upsert


# pylint: disable=too-many-arguments
def update(
        environment,
        api_properties,
        api_definition,
        icon,
        script,
        connector_id,
        powerapps_url,
        powerapps_version,
        client_secret,
        settings_file):
    """
    Update command.
    """
    # Get settings and the powerapps rp
    settings, powerapps_rp = load_settings_and_powerapps_rp(
        command_context=_UPDATE,
        environment=environment,
        settings_file=settings_file,
        api_properties=api_properties,
        api_definition=api_definition,
        icon=icon,
        script=script,
        connector_id=connector_id,
        powerapps_url=powerapps_url,
        powerapps_version=powerapps_version)

    connector_id = upsert(
        powerapps_rp=powerapps_rp,
        settings=settings,
        client_secret=client_secret,
        is_update=True,
        overwrite_settings=False)

    display('{} updated successfully.'.format(connector_id))
