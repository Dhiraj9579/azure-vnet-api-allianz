"""
Azure client for creating VNets and subnet metadata.
"""
from azure.identity import ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.core.exceptions import AzureError
from typing import Optional, Dict, List
import logging

from src.config import settings

logger = logging.getLogger(__name__)


class AzureVNetClient:
    """Client for managing Azure VNets and subnets."""

    def __init__(self):
        try:
            if not all([settings.AZURE_TENANT_ID, settings.AZURE_CLIENT_ID, settings.AZURE_CLIENT_SECRET]):
                logger.warning("Azure credentials not fully configured. Some features may not work.")
                self.credential = None
                self.network_client = None
                return

            self.credential = ClientSecretCredential(
                tenant_id=settings.AZURE_TENANT_ID,
                client_id=settings.AZURE_CLIENT_ID,
                client_secret=settings.AZURE_CLIENT_SECRET
            )
            self.network_client = NetworkManagementClient(
                credential=self.credential,
                subscription_id=settings.AZURE_SUBSCRIPTION_ID
            )
            logger.info("Azure Network Management Client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Azure client: {str(e)}")
            self.credential = None
            self.network_client = None

    def create_vnet(
        self,
        resource_group: str,
        vnet_name: str,
        location: str,
        address_space: str,
        subnets: Optional[List[Dict]] = None
    ) -> Dict:
        """Create a Virtual Network in Azure."""
        if not self.network_client:
            logger.warning("Azure client not initialized. Returning mock data.")
            return self._mock_vnet_response(vnet_name, location, address_space, subnets)

        try:
            vnet_params = {
                "location": location,
                "address_space": {"address_prefixes": [address_space]}
            }

            if subnets:
                vnet_params["subnets"] = [
                    {
                        "name": subnet["name"],
                        "address_prefix": subnet["address_prefix"]
                    }
                    for subnet in subnets
                ]

            vnet = self.network_client.virtual_networks.begin_create_or_update(
                resource_group_name=resource_group,
                virtual_network_name=vnet_name,
                parameters=vnet_params
            ).result()

            logger.info(f"VNet {vnet_name} created successfully")

            return {
                "id": vnet.id,
                "name": vnet.name,
                "location": vnet.location,
                "address_space": vnet.address_space.address_prefixes[0] if vnet.address_space.address_prefixes else None,
                "resource_id": vnet.id,
                "provisioning_state": vnet.provisioning_state,
                "subnets": [
                    {
                        "name": subnet.name,
                        "address_prefix": subnet.address_prefix,
                        "resource_id": subnet.id
                    }
                    for subnet in (vnet.subnets or [])
                ]
            }
        except AzureError as e:
            logger.error(f"Azure error creating VNet: {str(e)}")
            raise Exception(f"Failed to create VNet: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating VNet: {str(e)}")
            raise

    @staticmethod
    def _mock_vnet_response(vnet_name: str, location: str, address_space: str, subnets: Optional[List[Dict]]) -> Dict:
        """Return mock VNet response for testing."""
        return {
            "id": f"/subscriptions/mock-sub/resourceGroups/mock-rg/providers/Microsoft.Network/virtualNetworks/{vnet_name}",
            "name": vnet_name,
            "location": location,
            "address_space": address_space,
            "resource_id": f"/subscriptions/mock-sub/resourceGroups/mock-rg/providers/Microsoft.Network/virtualNetworks/{vnet_name}",
            "provisioning_state": "Succeeded",
            "subnets": [
                {
                    "name": subnet["name"],
                    "address_prefix": subnet["address_prefix"],
                    "resource_id": f"/subscriptions/mock-sub/resourceGroups/mock-rg/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/{subnet['name']}"
                }
                for subnet in (subnets or [])
            ]
        }


_azure_client: Optional[AzureVNetClient] = None


def get_azure_client() -> AzureVNetClient:
    """Get or create Azure client instance."""
    global _azure_client
    if _azure_client is None:
        _azure_client = AzureVNetClient()
    return _azure_client
