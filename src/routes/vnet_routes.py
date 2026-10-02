"""
Routes for VNet creation and read operations.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from src.database import (
    get_db, create_vnet, get_all_vnets, get_vnet_by_id, get_vnet_by_name,
    create_subnet
)
from src.azure_client import get_azure_client
from src.schemas import VNetCreate, VNetDetailResponse, VNetListResponse, ErrorResponse
from src.models import ResourceStatus, Subnet
from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
azure_client = get_azure_client()


@router.post(
    "",
    response_model=VNetDetailResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}
)
def create_vnet_endpoint(
    vnet: VNetCreate,
    db: Session = Depends(get_db)
):
    """Create a VNet and save it with all subnet metadata."""
    try:
        existing_vnet = get_vnet_by_name(db, vnet.name)
        if existing_vnet:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"VNet with name '{vnet.name}' already exists"
            )

        logger.info(f"Creating VNet {vnet.name} in Azure region {vnet.location}")
        azure_vnet = azure_client.create_vnet(
            resource_group=settings.AZURE_RESOURCE_GROUP,
            vnet_name=vnet.name,
            location=vnet.location,
            address_space=vnet.address_space,
            subnets=vnet.subnets if vnet.subnets else None
        )

        vnet_data = {
            "name": vnet.name,
            "location": vnet.location,
            "address_space": vnet.address_space,
            "resource_id": azure_vnet["resource_id"],
            "resource_group": settings.AZURE_RESOURCE_GROUP,
            "subscription_id": settings.AZURE_SUBSCRIPTION_ID,
            "status": ResourceStatus.SUCCEEDED,
            "provisioning_state": azure_vnet.get("provisioning_state", "Succeeded")
        }

        db_vnet = create_vnet(db, vnet_data)

        subnet_records = []
        for subnet in azure_vnet.get("subnets", []):
            subnet_data = {
                "name": subnet["name"],
                "address_prefix": subnet["address_prefix"],
                "vnet_id": db_vnet.id,
                "resource_id": subnet.get("resource_id", ""),
                "status": ResourceStatus.SUCCEEDED,
                "provisioning_state": "Succeeded"
            }
            subnet_record = create_subnet(db, subnet_data)
            subnet_records.append(subnet_record)

        db.commit()

        logger.info(f"VNet {vnet.name} created successfully with ID {db_vnet.id}")

        return {
            "id": db_vnet.id,
            "name": db_vnet.name,
            "location": db_vnet.location,
            "address_space": db_vnet.address_space,
            "resource_id": db_vnet.resource_id,
            "resource_group": db_vnet.resource_group,
            "subscription_id": db_vnet.subscription_id,
            "created_at": db_vnet.created_at,
            "updated_at": db_vnet.updated_at,
            "status": db_vnet.status,
            "provisioning_state": db_vnet.provisioning_state,
            "subnets": subnet_records
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating VNet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create VNet: {str(e)}"
        )


@router.get(
    "",
    response_model=VNetListResponse,
    status_code=status.HTTP_200_OK
)
def list_vnets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all created VNets."""
    try:
        vnets = get_all_vnets(db, skip=skip, limit=limit)

        return {
            "count": len(vnets),
            "vnets": [
                {
                    "id": vnet.id,
                    "name": vnet.name,
                    "location": vnet.location,
                    "address_space": vnet.address_space,
                    "resource_id": vnet.resource_id,
                    "resource_group": vnet.resource_group,
                    "subscription_id": vnet.subscription_id,
                    "created_at": vnet.created_at,
                    "updated_at": vnet.updated_at,
                    "status": vnet.status,
                    "provisioning_state": vnet.provisioning_state
                }
                for vnet in vnets
            ]
        }
    except Exception as e:
        logger.error(f"Error listing VNets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list VNets"
        )


@router.get(
    "/{vnet_id}",
    response_model=VNetDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={404: {"model": ErrorResponse}}
)
def get_vnet_endpoint(
    vnet_id: str,
    db: Session = Depends(get_db)
):
    """Fetch a single VNet and its subnet records."""
    try:
        vnet = get_vnet_by_id(db, vnet_id)

        if not vnet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"VNet with ID '{vnet_id}' not found"
            )

        subnets = db.query(Subnet).filter(Subnet.vnet_id == vnet_id).all()

        return {
            "id": vnet.id,
            "name": vnet.name,
            "location": vnet.location,
            "address_space": vnet.address_space,
            "resource_id": vnet.resource_id,
            "resource_group": vnet.resource_group,
            "subscription_id": vnet.subscription_id,
            "created_at": vnet.created_at,
            "updated_at": vnet.updated_at,
            "status": vnet.status,
            "provisioning_state": vnet.provisioning_state,
            "subnets": subnets
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting VNet: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get VNet"
        )
