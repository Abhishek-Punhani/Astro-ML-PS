from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Define the base class
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password =Column("password", String(255), nullable=False)

    

    def __repr__(self):
        return f'<User {self.username}>'

# Function to create all tables defined in the models
def create_tables(engine):
    Base.metadata.create_all(engine)
