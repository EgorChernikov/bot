import enum
import string

from sqlalchemy import Column, BigInteger, Float, DateTime, Enum, String, ForeignKey, Integer

from context.base import Base


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger)
    datetime = Column(DateTime)
    asset_name = Column(String, ForeignKey('assets.name'))
    amount = Column(Float)

    def __init__(self, user_id, datetime: datetime, asset_name: string, amount: float):
        self.user_id = user_id
        self.datetime = datetime
        self.asset_name = asset_name
        self.amount = amount
