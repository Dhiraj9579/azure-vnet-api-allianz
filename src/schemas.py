"""
API Request/Response schemas
"""
from typing import List, Optional
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class SubnetCreate:
    """Schema for subnet creation"""
    name: str
    address_prefix: str


@dataclass
class SubnetResponse:
    """Schema for subnet response"""
    id: str
    name: str
    address_prefix: str
    vnet_id: str
    resource_id: str
    created_at: datetime
    status: str


@dataclass
class VNetCreate:
    """Schema for VNET creation"""
    name: str
    location: str
    address_space: str
    subnets: List[SubnetCreate] = field(default_factory=list)


@dataclass
class VNetResponse:
    """Schema for VNET response"""
    id: str
    name: str
    location: str
    address_space: str
    resource_id: str
    created_at: datetime
    status: str
    subnets: List[SubnetResponse] = field(default_factory=list)


@dataclass
class VNetDetailResponse:
    """Detailed VNET response with all metadata"""
    id: str
    name: str
    location: str
    address_space: str
    resource_id: str
    resource_group: str
    subscription_id: str
    created_at: datetime
    updated_at: Optional[datetime]
    status: str
    provisioning_state: str
    subnets: List[SubnetResponse] = field(default_factory=list)
    tags: Optional[dict] = None


@dataclass
class VNetListResponse:
    """Schema for listing VNETs"""
    count: int
    vnets: List[VNetResponse]


@dataclass
class ErrorResponse:
    """Schema for error responses"""
    detail: str
    code: Optional[str] = None


@dataclass
class HealthResponse:
    """Health check response"""
    status: str
    version: str

