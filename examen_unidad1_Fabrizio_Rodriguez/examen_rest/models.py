from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Laptop(Base):
    __tablename__ = "laptops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    marca = Column(String(50), nullable=False)
    modelo = Column(String(50), nullable=False)
    ram_gb = Column(Integer, nullable=False)
    disponible = Column(Boolean, default=True)