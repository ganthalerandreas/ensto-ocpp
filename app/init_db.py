from app.database import engine
from app.models import Base

def init_db():
    Base.metadata.create_all(bind=engine)
