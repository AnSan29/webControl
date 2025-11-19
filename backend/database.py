from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
from pathlib import Path
import os
import re

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "db.sqlite3"
DEFAULT_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Role(Base):
    """Roles fijos del sistema (superadmin, admin, owner)."""
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
    cname_record = Column(String(200), nullable=True)
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

    owner_user = relationship("User", back_populates="site", uselist=False)


class Visit(Base):
    """Modelo para registro de visitas"""
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, nullable=False, index=True)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    referer = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)


class User(Base):
    """Usuarios del sistema con rol fijo y asignación opcional a un sitio."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    plain_password = Column(String(255), nullable=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    site_id = Column(Integer, ForeignKey("sites.id"), nullable=True, unique=True)
    is_active = Column(Boolean, default=True)
    activated_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    site = relationship("Site", back_populates="owner_user")


def get_db():
    """Dependency para obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Inicializar base de datos, roles fijos y superadmin."""
    import bcrypt

    Base.metadata.create_all(bind=engine)
    ensure_user_audit_columns()
    ensure_site_dns_columns()

    db = SessionLocal()
    try:
        seed_roles(db)
        seed_superadmin_user(db, bcrypt)
    finally:
        db.close()


def seed_roles(db):
    """Crear los 3 roles fijos del sistema si faltan."""
    default_roles = [
        ("superadmin", "Acceso total al sistema, crea sitios y gestiona usuarios"),
        ("admin", "Rol reservado para futuras delegaciones administrativas"),
        ("owner", "Dueño del sitio generado, solo puede editar su espacio"),
    ]

    for name, description in default_roles:
        exists = db.query(Role).filter(Role.name == name).first()
        if exists:
            continue
        role = Role(name=name, description=description)
        db.add(role)
        print(f"✅ Rol creado: {name}")
    db.commit()


def _unique_username(db, base_username: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", base_username.lower()).strip("-") or "usuario"
    username = base
    counter = 1
    while db.query(User).filter(User.username == username).first():
        counter += 1
        username = f"{base}-{counter}"
    return username


def seed_superadmin_user(db, bcrypt_module):
    """Crear superadmin por defecto si no existe."""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@webcontrol.com")
    default_username = os.getenv("ADMIN_USERNAME", "superadmin")
    plain_password = os.getenv("ADMIN_PASSWORD", "admin123")
    superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
    if superadmin_role is None:
        print("⚠️  No se encontró rol superadmin; omitiendo creación de usuario")
        return

    user = db.query(User).filter(User.email == admin_email).first()
    if user:
        if not user.plain_password:
            user.plain_password = plain_password
            db.commit()
        return

    password_bytes = plain_password.encode("utf-8")[:72]
    salt = bcrypt_module.gensalt()
    hashed_password = bcrypt_module.hashpw(password_bytes, salt).decode("utf-8")
    username = _unique_username(db, default_username or admin_email.split("@")[0])
    new_user = User(
        username=username,
        email=admin_email,
        hashed_password=hashed_password,
        plain_password=plain_password,
        role_id=superadmin_role.id,
        is_active=True,
        activated_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    print(f"✅ Superadmin creado: {admin_email}")


def ensure_user_audit_columns():
    """Garantiza que la tabla users tenga las columnas de activación/expiración."""
    if engine.dialect.name != "sqlite":
        return

    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(users)"))
        existing = {row[1] for row in result}
        statements = []
        if "activated_at" not in existing:
            statements.append("ALTER TABLE users ADD COLUMN activated_at DATETIME")
        if "expires_at" not in existing:
            statements.append("ALTER TABLE users ADD COLUMN expires_at DATETIME")
        for statement in statements:
            conn.execute(text(statement))
        if statements:
            conn.commit()


def ensure_site_dns_columns():
    """Garantiza que la tabla sites tenga los campos necesarios para DNS personalizado."""
    if engine.dialect.name != "sqlite":
        return

    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(sites)"))
        existing = {row[1] for row in result}
        statements = []
        if "cname_record" not in existing:
            statements.append("ALTER TABLE sites ADD COLUMN cname_record VARCHAR(200)")
        for statement in statements:
            conn.execute(text(statement))
        if statements:
            conn.commit()


if __name__ == "__main__":
    init_db()
    print("✅ Base de datos inicializada")
