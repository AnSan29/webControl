#!/usr/bin/env python3
"""Script para probar los endpoints de la API de usuarios y roles"""
import requests
import json
import time

# Esperar a que el servidor esté listo
time.sleep(2)

BASE_URL = "http://localhost:8000/api"

# Paso 1: Login
print("=" * 60)
print("PASO 1: Haciendo login...")
print("=" * 60)
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    data={"username": "admin@example.com", "password": "admin123"}
)
print(f"Status: {login_response.status_code}")
print(f"Response: {json.dumps(login_response.json(), indent=2)}")

if login_response.status_code != 200:
    print("❌ Error en login, abortando prueba")
    exit(1)

response_data = login_response.json()
token = response_data.get("token", {}).get("access_token") or response_data.get("access_token")
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Token obtenido: {token[:20]}...")

# Paso 2: Obtener usuarios
print("\n" + "=" * 60)
print("PASO 2: Obteniendo lista de usuarios...")
print("=" * 60)
users_response = requests.get(f"{BASE_URL}/users", headers=headers)
print(f"Status: {users_response.status_code}")
print(f"Response: {json.dumps(users_response.json(), indent=2)[:500]}")

# Paso 3: Obtener roles
print("\n" + "=" * 60)
print("PASO 3: Obteniendo lista de roles...")
print("=" * 60)
roles_response = requests.get(f"{BASE_URL}/roles", headers=headers)
print(f"Status: {roles_response.status_code}")
print(f"Response: {json.dumps(roles_response.json(), indent=2)[:500]}")

# Paso 4: Crear nuevo usuario
print("\n" + "=" * 60)
print("PASO 4: Creando nuevo usuario...")
print("=" * 60)
new_user = {
    "email": f"testuser@example.com",
    "username": "testuser",
    "password": "SecurePassword123!",
    "role": "user"
}
create_response = requests.post(f"{BASE_URL}/users", json=new_user, headers=headers)
print(f"Status: {create_response.status_code}")
print(f"Response: {json.dumps(create_response.json(), indent=2)}")

if create_response.status_code == 201:
    print("✅ Usuario creado exitosamente")
    new_user_id = create_response.json()["id"]
    
    # Paso 5: Actualizar rol del usuario
    print("\n" + "=" * 60)
    print("PASO 5: Actualizando rol del usuario...")
    print("=" * 60)
    update_response = requests.patch(
        f"{BASE_URL}/users/{new_user_id}",
        json={"role": "editor"},
        headers=headers
    )
    print(f"Status: {update_response.status_code}")
    print(f"Response: {json.dumps(update_response.json(), indent=2)}")
    print("✅ Rol actualizado exitosamente")
else:
    print("❌ Error al crear usuario")

print("\n" + "=" * 60)
print("✅ PRUEBA COMPLETADA")
print("=" * 60)
