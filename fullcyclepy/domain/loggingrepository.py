
#from sqlalchemy.sql import select
from domain.logging import MinerLog

def getminerlog(session):
    return session.query(MinerLog)
