from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import Base, engine, SessionLocal
from app.api import auth, nodes, rules
from app.models import User
from app.security import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)


def create_default_admin():
    """Create default admin user if no users exist"""
    db: Session = SessionLocal()
    try:
        # Check if any users exist
        user_count = db.query(User).count()
        if user_count == 0:
            # Create default admin user
            admin_user = User(
                username="admin",
                email="admin@iptables-easy.local",
                password_hash=get_password_hash("changeme"),
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✓ Default admin account created: username=admin, password=changeme")
    except Exception as e:
        print(f"Error creating default admin account: {e}")
        db.rollback()
    finally:
        db.close()


# Create default admin on startup
create_default_admin()

app = FastAPI(
    title="iptables-easy Backend",
    description="API for managing distributed iptables firewall rules",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(nodes.router)
app.include_router(rules.router)


@app.get("/")
def read_root():
    return {"message": "iptables-easy API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
