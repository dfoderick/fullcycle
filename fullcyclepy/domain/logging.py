'''logging classes'''
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

#Create table minerlog(minerlogid int primary key
#minerid varchar(50),
##minername varchar(50), createdate datetime,
##action varchar(255));

class MinerLog(Base):
    __tablename__ = 'minerlog'
    minerlogid = Column(Integer, primary_key=True)
    minerid = Column(String, nullable=False)
    minername = Column(String)
    #, default=func.now()
    createdate = Column(DateTime)
    action = Column(String)
