# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

"""
PowerApps RP manager
"""

import json
from urllib.parse import urljoin


class PowerAppsRP:
    """
    PowerAppsRP manager.
    """

    def __init__(self, api_manager):
        self.api_manager = api_manager
        self.rp_headers = {'x-ms-origin': 'paconn-cli'}

    @staticmethod
    def _get_filter_query(environment):
        return {'$filter': 'environment eq \'{}\''.format(environment)}

    # pylint: disable=too-many-arguments
    def _request(self, verb, path, query=None, payload=None, send_rp_headers=True):
        """
        Send a request to the given API path.
        """
        endpoint = self.api_manager.construct_url(
            path=path,
            query=query)

        return self.api_manager.request(
            verb=verb,
            endpoint=endpoint,
            payload=payload,
            headers=self.rp_headers if send_rp_headers else None)

    def get_connector(self, environment, connector_id):
        """
        Returns API registration JSON for a given connector.
        """
        response = self._request(
            verb='GET',
            path=urljoin('apis/', connector_id),
            query=PowerAppsRP._get_filter_query(environment))

        return response.json()

    def create_connector(self, environment, payload):
        """
        Creates a new custom connector.
        """
        response = self._request(
            verb='POST',
            path='apis',
            query=PowerAppsRP._get_filter_query(environment),
            payload=payload)

        return response.text

    def update_connector(self, environment, connector_id, payload):
        """
        Updates a custom connector.
        """
        response = self._request(
            verb='PATCH',
            path=urljoin('apis/', connector_id),
            query=PowerAppsRP._get_filter_query(environment),
            payload=payload)

        return response.text

    def get_all_connectors(self, environment):
        """
        Returns all connectors.
        """
        response = self._request(
            verb='GET',
            path='apis',
            query=PowerAppsRP._get_filter_query(environment))

        return response.json()

    def validate_connector(self, payload, enable_certification_rules):
        """
        Validates a custom connector.
        """
        query = None
        if enable_certification_rules:
            query = {'enableConnectorCertificationRules': 'true'}

        response = self._request(
            verb='POST',
            path=self.api_manager.add_object_id('validateApiSwagger'),
            query=query,
            payload=payload)

        return response.text

    def generate_resource_storage(self, environment):
        """
        Generates a resource storage
        """
        response = self._request(
            verb='POST',
            path=self.api_manager.add_object_id('generateResourceStorage'),
            payload={'environment': {'name': environment}},
            send_rp_headers=False)

        return json.loads(response.text)
