import enum
import string
from datetime import datetime

from sqlalchemy import String, Column, DateTime, Float, Enum

from context.base import Base


class AssetType(enum.Enum):
    CURRENCY = 'Currency'


class Asset(Base):
    __tablename__ = 'assets'

    type = Column(Enum(AssetType))
    name = Column(String, primary_key=True)
    price_usd = Column(Float)
    last_price_update_datetime = Column(DateTime)

    def __init__(self, type: AssetType,  name: string, price_usd: float, last_price_update_datetime: datetime):
        self.type = type
        self.name = name
        self.price_usd = price_usd
        self.last_price_update_datetime = last_price_update_datetime
