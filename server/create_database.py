from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Float, DateTime, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash  # Add this import

# Create a base class for declarative models
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(500))  # Add this line
    score = Column(Float, default=0.0)
    under_investigation = Column(Boolean, default=False)
    under_surveillance = Column(Boolean, default=False)
    role = Column(String(50), default='user')

    messages = relationship('Message', back_populates='user')
    identity = relationship('Identity', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Define the Message model
class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(DateTime, default=datetime.now)
    message = Column(String(2048), nullable=False)
    score = Column(Float, default=0.0)
    flagged = Column(Boolean, default=False)
    flagged_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship('User', back_populates='messages')

# Define the Identity model
class Identity(Base):
    __tablename__ = 'identities'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True)
    physical_address = Column(String(200))
    social_security_number = Column(String(25), unique=True)
    date_of_birth = Column(Date)
    gender = Column(String(10))
    ethnicity = Column(String(50))
    language = Column(String(50))
    user = relationship('User', back_populates='identity')

# Create the database engine
engine = create_engine('mysql+pymysql://root:root@localhost:3306/bigbrother')

# Function to recreate the database
def recreate_database():
    # Drop all tables
    Base.metadata.drop_all(engine)
    print("Existing tables dropped.")

    # Create all tables
    Base.metadata.create_all(engine)
    print("New tables created.")

# Function to create a base dataset
def create_base_dataset():
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create users
    users = [
        User(username="john_doe", score=75.0, under_investigation=False, under_surveillance=False, role="user"),
        User(username="jane_smith", score=80.0, under_investigation=True, under_surveillance=False, role="user"),
        User(username="bob_johnson", score=70.0, under_investigation=False, under_surveillance=True, role="administrator"),
        User(username="alice_williams", score=85.0, under_investigation=False, under_surveillance=False, role="operator"),
        User(username="charlie_brown", score=65.0, under_investigation=True, under_surveillance=True, role="user"),
    ]
    
    # Set passwords for users
    for user in users:
        user.set_password(f"123456")  # Add this line
    
    session.add_all(users)
    session.commit()

    # Create identities
    identities = [
        Identity(user_id=1, first_name="John", last_name="Doe", email="john@example.com", physical_address="123 Main St", social_security_number="123-45-6789", date_of_birth=datetime(1980, 1, 1), gender="Male", ethnicity="Caucasian", language="English"),
        Identity(user_id=2, first_name="Jane", last_name="Smith", email="jane@example.com", physical_address="456 Elm St", social_security_number="234-56-7890", date_of_birth=datetime(1985, 5, 15), gender="Female", ethnicity="African American", language="English"),
        Identity(user_id=3, first_name="Bob", last_name="Johnson", email="bob@example.com", physical_address="789 Oak St", social_security_number="345-67-8901", date_of_birth=datetime(1990, 10, 30), gender="Male", ethnicity="Hispanic", language="Spanish"),
        Identity(user_id=4, first_name="Alice", last_name="Williams", email="alice@example.com", physical_address="101 Pine St", social_security_number="456-78-9012", date_of_birth=datetime(1988, 7, 20), gender="Female", ethnicity="Asian", language="Mandarin"),
        Identity(user_id=5, first_name="Charlie", last_name="Brown", email="charlie@example.com", physical_address="202 Maple St", social_security_number="567-89-0123", date_of_birth=datetime(1995, 3, 10), gender="Non-binary", ethnicity="Mixed", language="French"),
    ]
    session.add_all(identities)
    session.commit()

    print("Base dataset created successfully.")
    session.close()

if __name__ == "__main__":
    recreate_database()
    create_base_dataset()
    print("Database recreated and base dataset added successfully.")
