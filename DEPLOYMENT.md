# Guía de Despliegue

## 🚀 Despliegue en Producción

### Opción 1: Servidor VPS (Ubuntu/Debian)

#### 1. Preparar el servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install python3 python3-pip python3-venv nginx -y
```

#### 2. Clonar y configurar

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/control-sitios.git
cd control-sitios

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar .env
nano .env
```

#### 3. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/control-sitios
```

Agregar:

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /ruta/al/proyecto/frontend/static;
    }
}
```

```bash
# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/control-sitios /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. Configurar como servicio

```bash
sudo nano /etc/systemd/system/control-sitios.service
```

Agregar:

```ini
[Unit]
Description=Control de Sitios
After=network.target

[Service]
User=tu-usuario
WorkingDirectory=/ruta/al/proyecto/backend
Environment="PATH=/ruta/al/proyecto/venv/bin"
ExecStart=/ruta/al/proyecto/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
# Iniciar servicio
sudo systemctl daemon-reload
sudo systemctl start control-sitios
sudo systemctl enable control-sitios
```

### Opción 2: Docker

#### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./db.sqlite3:/app/backend/db.sqlite3
    env_file:
      - .env
    restart: unless-stopped
```

Ejecutar:

```bash
docker-compose up -d
```

### Opción 3: Heroku

```bash
# Instalar Heroku CLI
heroku login

# Crear app
heroku create mi-control-sitios

# Configurar variables de entorno
heroku config:set SECRET_KEY=tu-clave-secreta
heroku config:set GITHUB_TOKEN=tu-token
heroku config:set GITHUB_USERNAME=tu-usuario

# Crear Procfile
echo "web: cd backend && uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git push heroku main
```

### Opción 4: Railway

1. Conecta tu repositorio en railway.app
2. Configura las variables de entorno
3. Railway detectará automáticamente FastAPI y desplegará

## 🔒 SSL/HTTPS

### Con Certbot (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com
```

## 📊 Monitoreo

### Logs

```bash
# Ver logs del servicio
sudo journalctl -u control-sitios -f

# Ver logs de Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 🔄 Actualizaciones

```bash
cd /ruta/al/proyecto
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart control-sitios
```

## 🛡️ Seguridad

1. **Cambiar credenciales por defecto**
2. **Usar HTTPS siempre**
3. **Configurar firewall**:
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw enable
   ```
4. **Backups regulares de la base de datos**:
   ```bash
   cp db.sqlite3 db.sqlite3.backup-$(date +%Y%m%d)
   ```

## 📞 Soporte

Para problemas o dudas, abre un issue en GitHub.
