from sqlalchemy import Column, String, Float, UUID
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from geoalchemy2 import Geometry
from app.db.database import Base
import uuid

class Product(Base):
    __tablename__ = "products"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False) 