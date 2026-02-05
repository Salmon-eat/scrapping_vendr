from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, Float, Text, JSON
from app2.db import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    category = Column(String)
    price = Column(Float)
    rating = Column(Integer)
    stock_availability = Column(String)
    image_url = Column(Text)
    description = Column(Text)
    product_information = Column(JSON)


@dataclass
class BookData:
    title: str
    category: str
    price: float
    rating: int
    stock_availability: str
    image_url: str
    description: str
    product_information: dict
