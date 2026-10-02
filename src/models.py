"""
Database models using SQLAlchemy
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class ResourceStatus(str, enum.Enum):
    """Status of Azure resources"""
    CREATING = "creating"
    SUCCEEDED = "succeeded"
    UPDATING = "updating"
    DELETING = "deleting"
    FAILED = "failed"
    DELETED = "deleted"


class VNet(Base):
    """Virtual Network model"""
    __tablename__ = "vnets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(80), unique=True, nullable=False, index=True)
    location = Column(String(50), nullable=False)
    address_space = Column(String(20), nullable=False)
    resource_id = Column(String(500), unique=True)
    resource_group = Column(String(90), nullable=False)
    subscription_id = Column(String(36), nullable=False)
    status = Column(SQLEnum(ResourceStatus), default=ResourceStatus.CREATING)
    provisioning_state = Column(String(50), default="Creating")
    tags = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subnets = relationship("Subnet", back_populates="vnet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VNet(id={self.id}, name={self.name}, location={self.location})>"


class Subnet(Base):
    """Subnet model"""
    __tablename__ = "subnets"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(80), nullable=False, index=True)
    address_prefix = Column(String(20), nullable=False)
    vnet_id = Column(String(36), ForeignKey("vnets.id"), nullable=False)
    resource_id = Column(String(500), unique=True)
    status = Column(SQLEnum(ResourceStatus), default=ResourceStatus.CREATING)
    provisioning_state = Column(String(50), default="Creating")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vnet = relationship("VNet", back_populates="subnets")
    
    def __repr__(self):
        return f"<Subnet(id={self.id}, name={self.name}, vnet_id={self.vnet_id})>"
