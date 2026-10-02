"""
Database initialization and operations
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from src.config import settings
from src.models import Base, VNet, Subnet

logger = logging.getLogger(__name__)

# Database engine and session factory
if settings.DATABASE_URL.startswith("sqlite"):
    # For SQLite, use check_same_thread=False to allow multi-threaded access
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # For other databases (PostgreSQL, MySQL, etc.)
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Database operations
def create_vnet(session: Session, vnet_data: dict) -> VNet:
    """Create a new VNet"""
    vnet = VNet(**vnet_data)
    session.add(vnet)
    session.flush()
    return vnet


def get_vnet_by_id(session: Session, vnet_id: str) -> VNet:
    """Get VNet by ID"""
    return session.query(VNet).filter(VNet.id == vnet_id).first()


def get_vnet_by_name(session: Session, name: str) -> VNet:
    """Get VNet by name"""
    return session.query(VNet).filter(VNet.name == name).first()


def get_all_vnets(session: Session, skip: int = 0, limit: int = 100):
    """Get all VNets with pagination"""
    return session.query(VNet).offset(skip).limit(limit).all()


def create_subnet(session: Session, subnet_data: dict) -> Subnet:
    """Create a new subnet"""
    subnet = Subnet(**subnet_data)
    session.add(subnet)
    session.flush()
    return subnet


def get_subnet_by_id(session: Session, subnet_id: str) -> Subnet:
    """Get subnet by ID"""
    return session.query(Subnet).filter(Subnet.id == subnet_id).first()


def get_subnets_by_vnet(session: Session, vnet_id: str):
    """Get all subnets for a VNet"""
    return session.query(Subnet).filter(Subnet.vnet_id == vnet_id).all()
