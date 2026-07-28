# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
"""
Save operation.
"""

import os
import json
import requests

from knack.util import CLIError
from knack.prompting import prompt_y_n

from paconn.common.util import format_json, write_file
from paconn.settings.util import write_settings, SETTINGS_FILE

from paconn.operations.json_keys import (
    _PROPERTIES,
    _API_DEFINITIONS,
    _ORIGINAL_SWAGGER_URL,
    _ICON_URI,
    _SCRIPT_URI,
    _CONNECTION_PARAMETERS,
    _CONNECTION_PARAMETER_SET,
    _ICON_BRAND_COLOR,
    _SCRIPT_OPERATIONS,
    _CAPABILITIES,
    _POLICY_TEMPLATE_INSTANCES,
    _PUBLISHER,
    _STACKOWNER
)


def _prepare_directory(destination, connector_id):
    """
    Create directory for saving a connector.
    """

    try:
        # Use the destination directory when provided
        if destination:
            if not os.path.exists(destination):
                # Create all sub-directories
                os.makedirs(destination)
        # Create a sub-directory in the current directory
        # when a destination isn't provided
        else:
            if not os.path.isdir(connector_id):
                os.mkdir(connector_id)
            destination = connector_id

        if os.path.isdir(destination):
            os.chdir(destination)
        else:
            error = 'Couldn\'t download to the desination directory {}.'
            raise CLIError(error.format(destination))
    except OSError as exception:
        error = 'Couldn\'t download to the desination directory {destination}. (Inner Error: {error})'
        raise CLIError(error.format(destination=destination, error=exception)) from exception

    return os.getcwd()


def _ensure_overwrite(settings):
    """
    Ensure the files can be overwritten, if exists
    """
    overwrite = False
    files = [settings.api_properties, settings.api_definition, settings.icon, settings.script, SETTINGS_FILE]
    existing_files = [file for file in files if os.path.exists(file)]
    if len(existing_files) > 0:
        msg = '{} file(s) exist. Do you want to overwrite?'.format(existing_files)
        overwrite = prompt_y_n(msg)
        if not overwrite:
            raise CLIError('{} files not overwritten.'.format(existing_files))

    return overwrite


def _download_content(url, content_type):
    """
    Download the content of a given URL.
    """
    try:
        response = requests.get(url, allow_redirects=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as exception:
        raise CLIError('Couldn\'t download the {content_type} from {url}. (Inner Error: {error})'.format(
            content_type=content_type,
            url=url,
            error=exception)) from exception

    return response


def download(powerapps_rp, settings, destination, overwrite):
    """
    Download operation.
    """
    # Prepare folders
    directory = _prepare_directory(
        destination=destination,
        connector_id=settings.connector_id)

    # Check if files could be overwritten
    if not overwrite:
        overwrite = _ensure_overwrite(settings)

    api_registration = powerapps_rp.get_connector(
        environment=settings.environment,
        connector_id=settings.connector_id)

    if _PROPERTIES not in api_registration:
        raise CLIError('Properties not present in the api registration information.')

    api_properties = api_registration[_PROPERTIES]

    # Property whitelist
    property_keys_whitelist = [
        _CONNECTION_PARAMETERS,
        _CONNECTION_PARAMETER_SET,
        _ICON_BRAND_COLOR,
        _SCRIPT_OPERATIONS,
        _CAPABILITIES,
        _POLICY_TEMPLATE_INSTANCES,
        _PUBLISHER,
        _STACKOWNER
    ]

    # Remove the keys that aren't present in the property JSON
    properties_present = list(
        filter(lambda prop: prop in api_properties, property_keys_whitelist)
    )

    # Only output the white listed properties that are present in the property JSON
    api_properties_selected = {_PROPERTIES: {}}
    api_properties_selected[_PROPERTIES] = {
        prop: api_properties[prop]
        for prop in properties_present
    }

    # Write the api properties
    api_prop = format_json(
        content=api_properties_selected,
        sort_keys=False)

    write_file(
        filename=settings.api_properties,
        mode='w',
        content=api_prop)

    # Write the open api definition,
    # either from swagger URL when available or from swagger property.
    if _API_DEFINITIONS in api_properties and _ORIGINAL_SWAGGER_URL in api_properties[_API_DEFINITIONS]:
        original_swagger_url = api_properties[_API_DEFINITIONS][_ORIGINAL_SWAGGER_URL]
        response = _download_content(url=original_swagger_url, content_type='API definition')
        response_string = response.content.decode('utf-8-sig')

        try:
            swagger_content = json.loads(response_string)
        except ValueError as exception:
            raise CLIError(
                'The API definition downloaded from {url} is not a valid JSON document. '
                '(Inner Error: {error})'.format(
                    url=original_swagger_url,
                    error=exception)) from exception

        swagger = format_json(
            content=swagger_content,
            sort_keys=False)

        write_file(
            filename=settings.api_definition,
            mode='w',
            content=swagger)

    # Write the icon
    if _ICON_URI in api_properties:
        icon_url = api_properties[_ICON_URI]
        response = _download_content(url=icon_url, content_type='icon')

        write_file(
            filename=settings.icon,
            mode='wb',
            content=response.content)

    # Write the script
    if _SCRIPT_URI in api_properties:
        script_url = api_properties[_SCRIPT_URI]
        response = _download_content(url=script_url, content_type='script')

        write_file(
            filename=settings.script,
            mode='wb',
            content=response.content)
    else:
        settings.script = None

    # Save the settings
    write_settings(settings, overwrite)

    return directory
