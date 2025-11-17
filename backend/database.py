from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Site(Base):
    """Modelo para los sitios web generados"""
    __tablename__ = "sites"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    model_type = Column(String(50), nullable=False)  # artesanias, cocina, etc.
    description = Column(Text)
    custom_domain = Column(String(200), nullable=True)
    github_repo = Column(String(200), nullable=True)
    github_url = Column(String(500), nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Contenido editable (JSON serializado)
    hero_title = Column(String(200))
    hero_subtitle = Column(Text)
    about_text = Column(Text)
    contact_email = Column(String(200))
    contact_phone = Column(String(50))
    contact_address = Column(Text)
    logo_url = Column(String(500))
    
    # Redes sociales
    facebook_url = Column(String(500))
    instagram_url = Column(String(500))
    tiktok_url = Column(String(500))
    whatsapp_number = Column(String(50))
    
    # Imágenes adicionales
    hero_image = Column(String(500))
    about_image = Column(String(500))
    gallery_images = Column(Text)  # JSON array de URLs
    
    # Colores y personalización
    primary_color = Column(String(20))
    secondary_color = Column(String(20))
    
    # Productos/Servicios (JSON serializado como texto)
    products_json = Column(Text)


class Visit(Base):
    """Modelo para registro de visitas"""
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, nullable=False, index=True)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    referer = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)


class Admin(Base):
    """Modelo para administradores"""
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(String(50), default="admin")  # admin, superadmin
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar base de datos y crear admin por defecto"""
    import bcrypt
    
    Base.metadata.create_all(bind=engine)
    
    # Crear admin por defecto si no existe
    db = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "admin@webcontrol.com")
        admin_exists = db.query(Admin).filter(Admin.email == admin_email).first()
        if not admin_exists:
            # Hash de la contraseña
            password = os.getenv("ADMIN_PASSWORD", "admin123")
            password_bytes = password.encode('utf-8')[:72]
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
            
            admin = Admin(
                email=admin_email,
                hashed_password=hashed_password
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin creado: {admin_email}")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("✅ Base de datos inicializada")
