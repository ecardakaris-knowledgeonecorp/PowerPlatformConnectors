# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""
Method for create/update operation
"""

from paconn.common.util import ensure_file_exists, load_json_file


def format_validation_result(result):
    """
    Format a validation result returned by the service into a readable string.
    """
    if not result:
        return ''

    # Replace \r\n in the string to newlines
    result = bytes(result, 'utf-8').decode('unicode-escape')
    # Remove quotes at the beginning and end
    return result.strip('"')


def validate(powerapps_rp, settings):
    """
    Method for create/update operation
    """

    # Make sure the required files exist
    ensure_file_exists(
        file=settings.api_definition,
        file_type='API Definition')

    # Load swagger definition
    openapi_definition = load_json_file(
        filename=settings.api_definition,
        file_type='API Definition')

    # Validate Open API Definition
    result = powerapps_rp.validate_connector(
        payload=openapi_definition,
        enable_certification_rules=True)

    return format_validation_result(result)
