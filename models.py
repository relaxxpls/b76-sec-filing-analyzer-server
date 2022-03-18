from unicodedata import category
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime

from database import Base


class Company(Base):
    __tablename__ = "company"

    cik = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    sic = Column(String)
    state_incorp = Column(String)
    ticker = Column(String) # multiple ticker separated by ,
    mailing_addr = Column(String)
    category = Column(String)

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
