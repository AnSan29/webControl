from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from pathlib import Path
import os

try:  # pragma: no cover - falla solo si bcrypt no está instalado
    import bcrypt  # type: ignore
except ImportError:  # pragma: no cover
    bcrypt = None

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "db.sqlite3"
DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Role(Base):
    """Modelo de roles para control de permisos"""
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    users = relationship("User", back_populates="role", cascade="all, delete", passive_deletes=True)


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

    owner_user = relationship(
        "User",
        back_populates="owned_site",
        uselist=False,
        foreign_keys="[User.site_id]",
    )
    collaborators = relationship(
        "SiteAssignment",
        back_populates="site",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class User(Base):
    """Modelo de usuarios finales con roles"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    owned_site = relationship(
        "Site",
        back_populates="owner_user",
        foreign_keys=[site_id],
        post_update=True,
    )
    site_assignments = relationship(
        "SiteAssignment",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SiteAssignment(Base):
    """Asignaciones explícitas de usuarios a sitios (ej. editores)."""
    __tablename__ = "site_assignments"
    __table_args__ = (
        UniqueConstraint("site_id", "user_id", name="uq_site_user_assignment"),
    )

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    permission = Column(String(50), default="editor")
    created_at = Column(DateTime, default=datetime.utcnow)

    site = relationship("Site", back_populates="collaborators")
    user = relationship("User", back_populates="site_assignments")


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
    if bcrypt is None:
        raise RuntimeError("El paquete bcrypt es requerido para inicializar la base de datos.")
    Base.metadata.create_all(bind=engine)
    
    # Crear admin por defecto si no existe
    db = SessionLocal()
    try:
        seed_roles(db)
        seed_default_admin_user(db)
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


def seed_roles(db):
    """Crear roles base si no existen."""
    default_roles = [
        ("admin", "Acceso total al sistema y a todos los sitios"),
        ("owner", "Dueño del sitio generado, controla solo su espacio"),
        ("editor", "Puede editar sitios asignados por un admin"),
        ("user", "Acceso básico al panel con permisos limitados"),
    ]

    for name, description in default_roles:
        exists = db.query(Role).filter(Role.name == name).first()
        if exists:
            continue
        role = Role(name=name, description=description)
        db.add(role)
        print(f"✅ Rol creado: {name}")
    db.commit()


def seed_default_admin_user(db):
    """Crear un usuario administrador en la nueva tabla users si no existe."""
    if bcrypt is None:
        raise RuntimeError("El paquete bcrypt es requerido para crear usuarios.")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@webcontrol.com")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin123")

    existing_user = db.query(User).filter(User.email == admin_email).first()
    if existing_user:
        return

    admin_role = db.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        return

    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    user = User(
        username=admin_username,
        email=admin_email,
        hashed_password=hashed_password,
        role_id=admin_role.id,
        is_active=True,
    )
    db.add(user)
    db.commit()
    print(f"✅ Usuario admin creado: {admin_email}")


if __name__ == "__main__":
    init_db()
    print("✅ Base de datos inicializada")
