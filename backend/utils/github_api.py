from github import Github, GithubException
import os
import json
import time
from typing import Optional

class GitHubPublisher:
    """Utilidad para publicar sitios en GitHub Pages"""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.username = os.getenv("GITHUB_USERNAME")
        
        # Validar configuración
        if not self.token or not self.username or self.token == "" or self.username == "":
            raise ValueError(
                "⚠️ GITHUB_TOKEN y GITHUB_USERNAME no están configurados.\n\n"
                "Para publicar sitios en GitHub Pages necesitas:\n"
                "1. Obtener un token de GitHub en: https://github.com/settings/tokens\n"
                "2. Configurar las variables en el archivo .env:\n"
                "   GITHUB_TOKEN=tu_token_aqui\n"
                "   GITHUB_USERNAME=tu_usuario_github\n\n"
                "Sin esto, puedes crear sitios pero NO publicarlos."
            )
        
        try:
            self.github = Github(self.token)
            self.user = self.github.get_user()
            # Verificar que el token sea válido
            self.user.login
        except Exception as e:
            raise ValueError(
                f"❌ Error al conectar con GitHub: {str(e)}\n\n"
                "Verifica que:\n"
                "1. Tu GITHUB_TOKEN sea válido\n"
                "2. El token tenga permisos: repo, workflow, write:packages\n"
                "3. Tu GITHUB_USERNAME sea correcto\n\n"
                "Genera un nuevo token en: https://github.com/settings/tokens"
            )
    
    def create_repository(self, repo_name: str, description: str = "") -> dict:
        """Crear repositorio en GitHub o usar existente"""
        try:
            # Primero intentar obtener el repositorio existente
            repo = self.user.get_repo(repo_name)
            # El repositorio ya existe, devolverlo
            return {
                "success": True,
                "repo_name": repo.name,
                "repo_url": repo.html_url,
                "clone_url": repo.clone_url,
                "already_exists": True
            }
        except GithubException as e:
            # Si el error es 404 (Not Found), el repo no existe, intentar crearlo
            if e.status == 404:
                try:
                    repo = self.user.create_repo(
                        name=repo_name,
                        description=description,
                        auto_init=False,  # No crear README automático para evitar conflictos
                        private=False
                    )
                    
                    # Esperar más tiempo para que GitHub propague el repositorio
                    print(f"⏳ Repositorio creado, esperando propagación en GitHub (10 segundos)...")
                    time.sleep(10)
                    
                    # Verificar que el repositorio esté realmente disponible
                    max_retries = 8
                    retry_delay = 3
                    for i in range(max_retries):
                        try:
                            repo = self.user.get_repo(repo_name)
                            print(f"✅ Repositorio {repo_name} verificado y disponible")
                            break
                        except GithubException:
                            if i < max_retries - 1:
                                print(f"⏳ Reintentando verificación ({i+1}/{max_retries}) en {retry_delay}s...")
                                time.sleep(retry_delay)
                            else:
                                print(f"⚠️ Verificación no exitosa, pero continuando...")
                    
                    return {
                        "success": True,
                        "repo_name": repo.name,
                        "repo_url": repo.html_url,
                        "clone_url": repo.clone_url,
                        "already_exists": False
                    }
                except GithubException as create_error:
                    # Si falla al crear, verificar si es porque ya existe
                    error_msg = str(create_error)
                    if "already exists" in error_msg.lower() or create_error.status == 422:
                        # El repo existe, intentar obtenerlo de nuevo
                        print(f"ℹ️ El repositorio {repo_name} ya existe, obteniendo referencia...")
                        time.sleep(2)  # Pequeña espera antes de intentar obtenerlo
                        try:
                            repo = self.user.get_repo(repo_name)
                            return {
                                "success": True,
                                "repo_name": repo.name,
                                "repo_url": repo.html_url,
                                "clone_url": repo.clone_url,
                                "already_exists": True
                            }
                        except Exception as get_error:
                            return {
                                "success": False,
                                "error": f"El repositorio parece existir pero no se puede acceder: {str(get_error)}"
                            }
                    return {
                        "success": False,
                        "error": error_msg
                    }
            else:
                # Otro tipo de error al obtener el repo
                return {
                    "success": False,
                    "error": str(e)
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def upload_file(self, repo_name: str, file_path: str, content: str, commit_message: str = "Update file"):
        """Subir o actualizar archivo en repositorio"""
        try:
            repo = self.user.get_repo(repo_name)
            
            # Intentar obtener el archivo existente
            try:
                file = repo.get_contents(file_path)
                repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=file.sha,
                    branch="main"
                )
            except GithubException:
                # El archivo no existe, crearlo
                repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch="main"
                )
            
            return {"success": True}
        except GithubException as e:
            return {"success": False, "error": str(e)}
    
    def upload_binary_file(self, repo_name: str, file_path: str, file_content: bytes, commit_message: str = "Upload image"):
        """Subir archivo binario (imagen) al repositorio sin doble codificación."""
        try:
            repo = self.user.get_repo(repo_name)
            
            # Intentar obtener el archivo existente
            try:
                file = repo.get_contents(file_path)
                repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=file_content,
                    sha=file.sha,
                    branch="main"
                )
            except GithubException:
                # El archivo no existe, crearlo
                repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=file_content,
                    branch="main"
                )
            
            return {"success": True}
        except GithubException as e:
            return {"success": False, "error": str(e)}
    
    def upload_multiple_files(self, repo_name: str, files: dict, commit_message: str = "Update site"):
        """
        Subir múltiples archivos
        files: dict con estructura {"path/to/file.html": "contenido", ...}
        """
        try:
            # Intentar obtener el repo con más reintentos y mayor espera
            repo = None
            max_retries = 6
            retry_delay = 5
            
            print(f"🔍 Buscando repositorio {repo_name}...")
            for i in range(max_retries):
                try:
                    repo = self.user.get_repo(repo_name)
                    print(f"✅ Repositorio encontrado")
                    break
                except GithubException as e:
                    if e.status == 404 and i < max_retries - 1:
                        print(f"⏳ Repositorio aún no visible en GitHub API, reintentando en {retry_delay}s... ({i+1}/{max_retries})")
                        time.sleep(retry_delay)
                    else:
                        raise
            
            if not repo:
                return {"success": False, "error": f"No se pudo acceder al repositorio {repo_name}"}
            
            print(f"📦 Subiendo {len(files)} archivos al repositorio...")
            
            # Verificar si el repo tiene commits (para saber si existe la rama main)
            has_commits = False
            try:
                repo.get_branch("main")
                has_commits = True
                print("✓ Repositorio tiene rama main existente")
            except:
                print("ℹ️ Repositorio vacío, creando primera estructura")
            
            for file_path, content in files.items():
                try:
                    if has_commits:
                        # El repo tiene commits, intentar actualizar o crear
                        try:
                            file = repo.get_contents(file_path)
                            repo.update_file(
                                path=file_path,
                                message=commit_message,
                                content=content,
                                sha=file.sha,
                                branch="main"
                            )
                            print(f"  ✓ Actualizado: {file_path}")
                        except GithubException:
                            # El archivo no existe, crearlo
                            repo.create_file(
                                path=file_path,
                                message=commit_message,
                                content=content,
                                branch="main"
                            )
                            print(f"  ✓ Creado: {file_path}")
                    else:
                        # Repo sin commits, crear archivo (esto creará la rama main)
                        repo.create_file(
                            path=file_path,
                            message=commit_message,
                            content=content,
                            branch="main"
                        )
                        print(f"  ✓ Creado: {file_path}")
                        has_commits = True  # Ahora ya tiene commits
                except Exception as e:
                    print(f"  ✗ Error en {file_path}: {str(e)}")
                    raise
            
            print(f"✅ Todos los archivos subidos correctamente")
            return {"success": True}
        except GithubException as e:
            error_msg = f"Error de GitHub: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def enable_github_pages(self, repo_name: str, branch: str = "main", path: str = "/") -> dict:
        """Habilitar GitHub Pages en el repositorio"""
        try:
            repo = self.user.get_repo(repo_name)
            
            # Usar la API de GitHub para habilitar Pages
            # Necesitamos hacer una petición POST a la API de Pages
            try:
                # Intentar obtener la configuración de Pages existente
                pages = repo.get_pages_build()
            except:
                # Si no existe, crear la configuración de Pages
                # Usamos la API REST directamente
                import requests
                headers = {
                    "Authorization": f"token {self.token}",
                    "Accept": "application/vnd.github.v3+json"
                }
                
                # Habilitar GitHub Pages
                pages_config = {
                    "source": {
                        "branch": branch,
                        "path": path
                    }
                }
                
                response = requests.post(
                    f"https://api.github.com/repos/{self.username}/{repo_name}/pages",
                    headers=headers,
                    json=pages_config
                )
                
                # Si ya está habilitado, intentar actualizarlo
                if response.status_code == 409:
                    response = requests.put(
                        f"https://api.github.com/repos/{self.username}/{repo_name}/pages",
                        headers=headers,
                        json=pages_config
                    )
            
            pages_url = f"https://{self.username}.github.io/{repo_name}/"
            
            return {
                "success": True,
                "pages_url": pages_url
            }
        except Exception as e:
            # Si hay error, intentar de todos modos devolver la URL
            pages_url = f"https://{self.username}.github.io/{repo_name}/"
            return {
                "success": True,
                "pages_url": pages_url,
                "warning": f"Pages URL generada, pero puede requerir configuración manual: {str(e)}"
            }
    
    def create_cname(self, repo_name: str, custom_domain: str) -> dict:
        """Crear archivo CNAME para dominio personalizado"""
        try:
            result = self.upload_file(
                repo_name=repo_name,
                file_path="CNAME",
                content=custom_domain,
                commit_message="Add custom domain"
            )
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def publish_site(self, repo_name: str, site_files: dict, custom_domain: Optional[str] = None) -> dict:
        """
        Publicar sitio completo en GitHub Pages
        
        Args:
            repo_name: Nombre del repositorio
            site_files: Dict con archivos {path: content}
            custom_domain: Dominio personalizado opcional
        """
        try:
            # Subir archivos del sitio
            result = self.upload_multiple_files(repo_name, site_files, "Publish site")
            
            if not result["success"]:
                return result
            
            # Subir imágenes locales desde uploads/
            from pathlib import Path
            uploads_dir = Path(__file__).parent.parent.parent / "uploads"
            if uploads_dir.exists():
                for image_file in uploads_dir.glob("*"):
                    if image_file.is_file() and image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']:
                        try:
                            with open(image_file, 'rb') as f:
                                image_content = f.read()
                            
                            # Subir imagen al repo en carpeta images/
                            self.upload_binary_file(
                                repo_name=repo_name,
                                file_path=f"images/{image_file.name}",
                                file_content=image_content,
                                commit_message=f"Upload image {image_file.name}"
                            )
                        except Exception as e:
                            print(f"Warning: Could not upload image {image_file.name}: {e}")
            
            # Si hay dominio personalizado, crear CNAME
            if custom_domain:
                cname_result = self.create_cname(repo_name, custom_domain)
                if not cname_result["success"]:
                    return cname_result
            
            # Habilitar GitHub Pages
            pages_result = self.enable_github_pages(repo_name)
            
            return pages_result
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_repository(self, repo_name: str) -> dict:
        """Eliminar repositorio"""
        try:
            repo = self.user.get_repo(repo_name)
            repo.delete()
            return {"success": True}
        except GithubException as e:
            return {"success": False, "error": str(e)}


def test_github_connection():
    """Probar conexión con GitHub"""
    try:
        publisher = GitHubPublisher()
        user = publisher.user
        print(f"✅ Conectado como: {user.login}")
        print(f"📊 Repositorios: {user.public_repos}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    test_github_connection()
