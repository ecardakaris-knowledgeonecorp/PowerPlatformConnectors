# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""
Method for create/update operation
"""

import os
import json
import urllib.parse

from knack.util import CLIError

from paconn.common.util import display, ensure_file_exists, load_json_file
from paconn.settings.util import write_settings
from paconn.apimanager.fileuploader import upload_file
from paconn.operations.validate import format_validation_result
from paconn.operations.json_keys import (
    _PROPERTIES,
    _ICON_URI,
    _SCRIPT_URI,
    _OPEN_API_DEFINITION,
    _ENVIRONMENT,
    _NAME,
    _BACKEND_SERVICE,
    _SERVICE_URL,
    _SCHEMES,
    _HOST,
    _BASE_PATH,
    _DISPLAY_NAME,
    _CONNECTION_PARAMETERS,
    _CONNECTION_PARAMETER_SET,
    _PARAMETERS,
    _VALUES,
    _TOKEN,
    _OAUTH_SETTINGS,
    _CLIENT_SECRET,
    _DESCRIPTION,
    _INFO,
    _TITLE,
    _SHARED_ACCESS_SIGNATURE
)


def _create_backendservice_url(openapi_definition):
    """
    Create a backend service URL from the Open API definition.
    """

    schemes = openapi_definition.get(_SCHEMES, [])
    scheme = next(iter(schemes), '')
    netloc = openapi_definition.get(_HOST, '')
    path = openapi_definition.get(_BASE_PATH, '')

    params = ''
    query = ''
    fragment = ''

    parts = (scheme, netloc, path, params, query, fragment)

    url = urllib.parse.urlunparse(parts)

    return url


def _add_client_secret(token_property, client_secret, is_update):
    """
    Add the OAuth2 client secret to a given token property.
    """
    if not token_property:
        return

    oauth_settings = token_property.get(_OAUTH_SETTINGS, None)
    if not oauth_settings:
        return

    if client_secret:
        oauth_settings[_CLIENT_SECRET] = client_secret
    elif not is_update:
        raise CLIError('Please provide OAuth2 client secret using the --secret argument.')


def _get_required_info_value(info, key, api_definition):
    """
    Return a required value from the info section of the Open API definition.
    """
    if key not in info:
        raise CLIError('{key} is not present in the {info} section of the API Definition file {file}.'.format(
            key=key,
            info=_INFO,
            file=api_definition))

    return info[key]


def _get_connector_id(api_registration):
    """
    Return the connector id from the api registration response.
    """
    try:
        return json.loads(api_registration)[_NAME]
    except (ValueError, KeyError, TypeError) as exception:
        raise CLIError(
            'The connector was created but the service response couldn\'t be parsed, '
            'so the settings file wasn\'t written. (Inner Error: {error})\n{response}'.format(
                error=exception,
                response=api_registration)) from exception


def upsert(powerapps_rp, settings, client_secret, is_update, overwrite_settings):
    """
    Method for create/update operation
    """

    # Make sure the required files exist
    ensure_file_exists(
        file=settings.api_properties,
        file_type='API Properties')
    ensure_file_exists(
        file=settings.api_definition,
        file_type='API Definition')

    # Open the property file
    property_definition = load_json_file(
        filename=settings.api_properties,
        file_type='API Properties')

    # Get the property object
    if _PROPERTIES not in property_definition:
        raise CLIError('{} is not present in the API Properties file {}.'.format(
            _PROPERTIES,
            settings.api_properties))

    properties = property_definition[_PROPERTIES]

    # Add secret in connection parameter
    _add_client_secret(
        token_property=properties.get(_CONNECTION_PARAMETERS, {}).get(_TOKEN, None),
        client_secret=client_secret,
        is_update=is_update)

    # Add secret in connection parameter set
    multi_auth = properties.get(_CONNECTION_PARAMETER_SET, {}).get(_VALUES, [])
    for auth in multi_auth:
        _add_client_secret(
            token_property=auth.get(_PARAMETERS, {}).get(_TOKEN),
            client_secret=client_secret,
            is_update=is_update)

    # Load swagger definition
    openapi_definition = load_json_file(
        filename=settings.api_definition,
        file_type='API Definition')

    # Append swagger
    properties[_OPEN_API_DEFINITION] = openapi_definition

    # Add backend service
    backend_service_url = _create_backendservice_url(openapi_definition)
    properties[_BACKEND_SERVICE] = {_SERVICE_URL: backend_service_url}

    # Append the environment id
    properties[_ENVIRONMENT] = {_NAME: settings.environment}

    info = openapi_definition.get(_INFO, {})

    # Add displayName only when creating a new connector
    if is_update is not True:
        properties[_DISPLAY_NAME] = _get_required_info_value(
            info=info,
            key=_TITLE,
            api_definition=settings.api_definition)

    # Add description
    properties[_DESCRIPTION] = _get_required_info_value(
        info=info,
        key=_DESCRIPTION,
        api_definition=settings.api_definition)

    # Validate Open API Definition
    validation_result = powerapps_rp.validate_connector(
        payload=openapi_definition,
        enable_certification_rules=False)

    # Surface any validation message returned by the service
    validation_message = format_validation_result(validation_result)
    if validation_message:
        display(validation_message)

    # Get the shared access signature
    response = powerapps_rp.generate_resource_storage(settings.environment)

    if _SHARED_ACCESS_SIGNATURE not in response:
        raise CLIError('{} is not present in the resource storage response.'.format(_SHARED_ACCESS_SIGNATURE))

    sas_url = response[_SHARED_ACCESS_SIGNATURE]

    # Upload the icon
    if settings.icon and os.path.exists(settings.icon):
        icon_uri = upload_file(
            sas_url=sas_url,
            file_path=settings.icon)
        properties[_ICON_URI] = icon_uri

    # Upload the script
    if settings.script and os.path.exists(settings.script):
        script_uri = upload_file(
            sas_url=sas_url,
            file_path=settings.script)
        properties[_SCRIPT_URI] = script_uri

    else:
        properties[_SCRIPT_URI] = ""

    # Update or create the connector
    if is_update is True:
        api_registration = powerapps_rp.update_connector(
            environment=settings.environment,
            connector_id=settings.connector_id,
            payload=property_definition)
        connector_id = settings.connector_id
    else:
        api_registration = powerapps_rp.create_connector(
            environment=settings.environment,
            payload=property_definition)
        connector_id = _get_connector_id(api_registration)

        # Save the settings
        settings.connector_id = connector_id
        write_settings(settings, overwrite_settings)

    return connector_id
