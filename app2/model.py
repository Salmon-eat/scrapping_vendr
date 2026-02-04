from sqlalchemy import Column, Integer, String, Float, Text, JSON
from db import Base

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
