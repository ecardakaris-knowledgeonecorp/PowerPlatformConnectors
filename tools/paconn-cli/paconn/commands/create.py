# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""
Create command.
"""

from paconn import _CREATE
from paconn.common.util import display
from paconn.settings.util import load_settings_and_powerapps_rp
from paconn.operations.upsert import upsert


# pylint: disable=too-many-arguments
def create(
        environment,
        api_properties,
        api_definition,
        icon,
        script,
        powerapps_url,
        powerapps_version,
        client_secret,
        settings_file,
        overwrite_settings):
    """
    Create command.
    """
    # Get settings and the powerapps rp
    settings, powerapps_rp = load_settings_and_powerapps_rp(
        command_context=_CREATE,
        environment=environment,
        settings_file=settings_file,
        api_properties=api_properties,
        api_definition=api_definition,
        icon=icon,
        script=script,
        powerapps_url=powerapps_url,
        powerapps_version=powerapps_version)

    connector_id = upsert(
        powerapps_rp=powerapps_rp,
        settings=settings,
        client_secret=client_secret,
        is_update=False,
        overwrite_settings=overwrite_settings)

    display('{} created successfully.'.format(connector_id))
