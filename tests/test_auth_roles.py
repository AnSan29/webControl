import os
from pathlib import Path
import sys
from datetime import datetime

# Fuerza una base de datos SQLite aislada para los tests ANTES de importar la app
TEST_DB_PATH = Path(__file__).resolve().parent / "test_db.sqlite3"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient

from backend.main import app, DEFAULT_CNAME_TARGET
from backend.database import (
    Base,
    engine,
    seed_roles,
    SessionLocal,
    Role,
    User,
    Site,
    get_db,
)
from backend.auth import hash_password


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clean_database():
    """Resetea las tablas y semillas obligatorias antes de cada prueba."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seed_roles(session)
    session.close()
    yield
    session = SessionLocal()
    session.close()


@pytest.fixture
def client():
    return TestClient(app)


def create_superadmin(email="root@webcontrol.test", password="Admin!123"):
    session = SessionLocal()
    role = session.query(Role).filter(Role.name == "superadmin").first()
    user = User(
        username="root",
        email=email,
        hashed_password=hash_password(password),
        plain_password=password,
        role_id=role.id,
        is_active=True,
        activated_at=datetime.utcnow(),
    )
    session.add(user)
    session.commit()
    session.close()
    return {"email": email, "password": password}


def login(client: TestClient, username: str, password: str):
    response = client.post(
        "/api/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    return data["access_token"], data["user"]


def auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_superadmin_can_login_and_receive_jwt(client):
    creds = create_superadmin()
    token, user = login(client, creds["email"], creds["password"])
    assert token
    assert user["role"] == "superadmin"
    assert user["email"] == creds["email"]


def test_site_creation_auto_generates_owner_account(client):
    creds = create_superadmin()
    token, _ = login(client, creds["email"], creds["password"])

    response = client.post(
        "/api/sites",
        headers=auth_header(token),
        json={
            "name": "Panaderia Test",
            "model_type": "cocina",
            "description": "Sitio temporal",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["owner"]["role"] == "owner"
    assert payload["owner"]["temporary_password"]

    session = SessionLocal()
    owner_user = (
        session.query(User)
        .filter(User.email == payload["owner"]["email"])
        .first()
    )
    assert owner_user is not None
    assert owner_user.site_id == payload["id"]
    session.close()


def test_owner_only_sees_their_site_and_is_blocked_elsewhere(client):
    creds = create_superadmin()
    token, _ = login(client, creds["email"], creds["password"])

    first_site = client.post(
        "/api/sites",
        headers=auth_header(token),
        json={"name": "Sitio Uno", "model_type": "cocina"},
    ).json()
    owner_creds = first_site["owner"]

    second_site = client.post(
        "/api/sites",
        headers=auth_header(token),
        json={"name": "Sitio Dos", "model_type": "cocina"},
    ).json()

    owner_token, _ = login(
        client, owner_creds["email"], owner_creds["temporary_password"]
    )

    list_response = client.get("/api/sites", headers=auth_header(owner_token))
    assert list_response.status_code == 200
    sites = list_response.json()
    assert len(sites) == 1
    assert sites[0]["id"] == first_site["id"]

    own_site_response = client.get(
        f"/api/sites/{first_site['id']}", headers=auth_header(owner_token)
    )
    assert own_site_response.status_code == 200

    forbidden_response = client.get(
        f"/api/sites/{second_site['id']}", headers=auth_header(owner_token)
    )
    assert forbidden_response.status_code == 403


def test_roles_endpoint_requires_superadmin(client):
    creds = create_superadmin()
    super_token, _ = login(client, creds["email"], creds["password"])

    response = client.get("/api/roles", headers=auth_header(super_token))
    assert response.status_code == 200, response.text
    payload = response.json()
    assert isinstance(payload, list)
    role_names = {role["name"] for role in payload}
    assert {"superadmin", "admin", "owner"}.issubset(role_names)

    site_payload = client.post(
        "/api/sites",
        headers=auth_header(super_token),
        json={"name": "Sitio Roles", "model_type": "cocina"},
    ).json()

    owner_creds = site_payload["owner"]
    owner_token, _ = login(
        client,
        owner_creds["email"],
        owner_creds["temporary_password"],
    )

    forbidden = client.get("/api/roles", headers=auth_header(owner_token))
    assert forbidden.status_code == 403


def test_superadmin_can_replace_site_owner_during_user_creation(client):
    creds = create_superadmin()
    token, _ = login(client, creds["email"], creds["password"])

    site_payload = client.post(
        "/api/sites",
        headers=auth_header(token),
        json={"name": "Sitio Owner", "model_type": "cocina"},
    ).json()

    new_owner_payload = {
        "username": "owner.reemplazo",
        "email": "owner.reemplazo@example.com",
        "role": "owner",
        "password": "NuevaClave123",
        "is_active": True,
        "site_id": site_payload["id"],
    }

    response = client.post(
        "/api/users",
        headers=auth_header(token),
        json=new_owner_payload,
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["site_id"] == site_payload["id"]
    assert payload["username"] == new_owner_payload["username"]
    assert payload["email"] == new_owner_payload["email"]

    session = SessionLocal()
    owners = session.query(User).filter(User.site_id == site_payload["id"]).all()
    session.close()
    assert len(owners) == 1
    assert owners[0].email == new_owner_payload["email"]


def test_custom_cname_is_persisted_and_visible(client):
    creds = create_superadmin()
    token, _ = login(client, creds["email"], creds["password"])

    custom_domain = "tienda.example.com"
    custom_cname = "custom-pages.github.test"
    response = client.post(
        "/api/sites",
        headers=auth_header(token),
        json={
            "name": "Sitio con CNAME",
            "model_type": "cocina",
            "custom_domain": custom_domain,
            "cname_record": custom_cname,
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["cname_record"] == custom_cname

    session = SessionLocal()
    site_in_db = session.query(Site).filter(Site.id == payload["id"]).first()
    session.close()
    assert site_in_db is not None
    assert site_in_db.custom_domain == custom_domain
    assert site_in_db.cname_record == custom_cname

    owner_token, _ = login(
        client,
        payload["owner"]["email"],
        payload["owner"]["temporary_password"],
    )
    site_response = client.get(
        f"/api/sites/{payload['id']}",
        headers=auth_header(owner_token),
    )
    assert site_response.status_code == 200, site_response.text
    site_payload = site_response.json()
    assert site_payload["custom_domain"] == custom_domain
    assert site_payload["cname_record"] == custom_cname


def test_cname_defaults_when_not_provided(client):
    creds = create_superadmin()
    token, _ = login(client, creds["email"], creds["password"])

    response = client.post(
        "/api/sites",
        headers=auth_header(token),
        json={
            "name": "Sitio sin CNAME",
            "model_type": "cocina",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["cname_record"] == DEFAULT_CNAME_TARGET

    owner_token, _ = login(
        client,
        payload["owner"]["email"],
        payload["owner"]["temporary_password"],
    )
    site_response = client.get(
        f"/api/sites/{payload['id']}",
        headers=auth_header(owner_token),
    )
    assert site_response.status_code == 200
    assert site_response.json()["cname_record"] == DEFAULT_CNAME_TARGET
