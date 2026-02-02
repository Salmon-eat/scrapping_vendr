from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    product_name: str
    category: str
    low_price: Optional[int]
    median_price: Optional[int]
    high_price: Optional[int]
    description: str
