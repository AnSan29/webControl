from jinja2 import Template
import json
import os
from pathlib import Path

class TemplateEngine:
    """Motor de plantillas para generar sitios"""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent.parent / "templates_base"
    
    def load_template(self, model_type: str, filename: str = "index.html") -> str:
        """Cargar plantilla desde archivo"""
        template_path = self.templates_dir / model_type / filename
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template no encontrado: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render_template(self, template_content: str, context: dict) -> str:
        """Renderizar plantilla con contexto"""
        template = Template(template_content)
        return template.render(**context)
    
    def generate_site(self, model_type: str, site_data: dict) -> dict:
        """
        Generar sitio completo
        
        Args:
            model_type: Tipo de modelo (artesanias, cocina, etc.)
            site_data: Datos del sitio (nombre, descripción, etc.)
        
        Returns:
            Dict con archivos generados {path: content}
        """
        files = {}
        
        # Cargar configuración del modelo
        models_config_path = Path(__file__).parent.parent / "models.json"
        with open(models_config_path, 'r', encoding='utf-8') as f:
            models_config = json.load(f)
        
        model_config = next((m for m in models_config["models"] if m["id"] == model_type), None)
        if not model_config:
            raise ValueError(f"Modelo no encontrado: {model_type}")
        
        # Preparar contexto para las plantillas
        context = {
            "site_name": site_data.get("name", "Mi Negocio"),
            "site_description": site_data.get("description", ""),
            "hero_title": site_data.get("hero_title", site_data.get("name", "Mi Negocio")),
            "hero_subtitle": site_data.get("hero_subtitle", "Bienvenido a nuestro sitio"),
            "hero_image": site_data.get("hero_image", ""),
            "about_text": site_data.get("about_text", "Sobre nosotros..."),
            "about_image": site_data.get("about_image", ""),
            "contact_email": site_data.get("contact_email", ""),
            "contact_phone": site_data.get("contact_phone", ""),
            "contact_address": site_data.get("contact_address", ""),
            "whatsapp_number": site_data.get("whatsapp_number", ""),
            "facebook_url": site_data.get("facebook_url", ""),
            "instagram_url": site_data.get("instagram_url", ""),
            "tiktok_url": site_data.get("tiktok_url", ""),
            "logo_url": site_data.get("logo_url", ""),
            "primary_color": site_data.get("primary_color", model_config["palette"]["primary"]),
            "secondary_color": site_data.get("secondary_color", model_config["palette"]["secondary"]),
            "palette": model_config["palette"],
            "model_icon": model_config["icon"],
            "products": json.loads(site_data.get("products_json", "[]")),
            "gallery_images": json.loads(site_data.get("gallery_images", "[]")),
            "current_year": 2025
        }
        
        # Generar index.html
        try:
            index_template = self.load_template(model_type, "index.html")
            files["index.html"] = self.render_template(index_template, context)
        except FileNotFoundError:
            # Si no existe plantilla específica, usar genérica
            files["index.html"] = self.generate_generic_template(context, model_config)
        
        # Generar CSS personalizado
        files["styles.css"] = self.generate_css(model_config["palette"])
        
        # Generar tracking script
        files["tracking.js"] = self.generate_tracking_script(site_data.get("id"))
        
        return files
    
    def generate_generic_template(self, context: dict, model_config: dict) -> str:
        """Generar plantilla HTML genérica"""
        template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{{{ site_name }}}}</title>
    <meta name="description" content="{{{{ site_description }}}}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <!-- Header -->
    <header class="header">
        <div class="container">
            <div class="logo">
                {{% if logo_url %}}
                <img src="{{{{ logo_url }}}}" alt="{{{{ site_name }}}}">
                {{% else %}}
                <span class="icon">{model_config['icon']}</span>
                {{% endif %}}
                <h1>{{{{ site_name }}}}</h1>
            </div>
            <nav>
                <a href="#inicio">Inicio</a>
                <a href="#nosotros">Nosotros</a>
                <a href="#productos">Productos</a>
                <a href="#contacto">Contacto</a>
            </nav>
        </div>
    </header>

    <!-- Hero Section -->
    <section id="inicio" class="hero">
        <div class="container">
            <h2>{{{{ hero_title }}}}</h2>
            <p>{{{{ hero_subtitle }}}}</p>
            <a href="#contacto" class="btn">Contáctanos</a>
        </div>
    </section>

    <!-- About Section -->
    <section id="nosotros" class="about">
        <div class="container">
            <h2>Sobre Nosotros</h2>
            <p>{{{{ about_text }}}}</p>
        </div>
    </section>

    <!-- Products Section -->
    <section id="productos" class="products">
        <div class="container">
            <h2>Nuestros Productos</h2>
            <div class="products-grid">
                {{% for product in products %}}
                <div class="product-card">
                    {{% if product.image %}}
                    <img src="{{{{ product.image }}}}" alt="{{{{ product.name }}}}">
                    {{% endif %}}
                    <h3>{{{{ product.name }}}}</h3>
                    <p>{{{{ product.description }}}}</p>
                    {{% if product.price %}}
                    <span class="price">${{{{ product.price }}}}</span>
                    {{% endif %}}
                </div>
                {{% endfor %}}
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contacto" class="contact">
        <div class="container">
            <h2>Contáctanos</h2>
            <div class="contact-info">
                {{% if contact_email %}}
                <p>📧 {{{{ contact_email }}}}</p>
                {{% endif %}}
                {{% if contact_phone %}}
                <p>📱 {{{{ contact_phone }}}}</p>
                {{% endif %}}
                {{% if contact_address %}}
                <p>📍 {{{{ contact_address }}}}</p>
                {{% endif %}}
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <p>&copy; {{{{ current_year }}}} {{{{ site_name }}}}. Todos los derechos reservados.</p>
        </div>
    </footer>

    <script src="tracking.js"></script>
</body>
</html>"""
        
        return self.render_template(template, context)
    
    def generate_css(self, palette: dict) -> str:
        """Generar CSS con paleta de colores"""
        return f"""/* Reset y Variables */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

:root {{
    --primary: {palette['primary']};
    --secondary: {palette['secondary']};
    --accent: {palette['accent']};
    --neutral: {palette['neutral']};
    --text: #333;
    --bg: #fff;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--text);
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header */
.header {{
    background: var(--primary);
    color: white;
    padding: 1rem 0;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}}

.header .container {{
    display: flex;
    justify-content: space-between;
    align-items: center;
}}

.logo {{
    display: flex;
    align-items: center;
    gap: 1rem;
}}

.logo .icon {{
    font-size: 2rem;
}}

.logo h1 {{
    font-size: 1.5rem;
}}

.header nav {{
    display: flex;
    gap: 2rem;
}}

.header nav a {{
    color: white;
    text-decoration: none;
    transition: opacity 0.3s;
}}

.header nav a:hover {{
    opacity: 0.8;
}}

/* Hero */
.hero {{
    background: linear-gradient(135deg, var(--primary), var(--secondary));
    color: white;
    padding: 5rem 0;
    text-align: center;
}}

.hero h2 {{
    font-size: 3rem;
    margin-bottom: 1rem;
}}

.hero p {{
    font-size: 1.5rem;
    margin-bottom: 2rem;
}}

.btn {{
    display: inline-block;
    background: white;
    color: var(--primary);
    padding: 1rem 2rem;
    text-decoration: none;
    border-radius: 5px;
    font-weight: bold;
    transition: transform 0.3s;
}}

.btn:hover {{
    transform: translateY(-2px);
}}

/* Sections */
section {{
    padding: 4rem 0;
}}

section h2 {{
    text-align: center;
    font-size: 2.5rem;
    margin-bottom: 2rem;
    color: var(--primary);
}}

/* About */
.about {{
    background: var(--neutral);
}}

.about p {{
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
    font-size: 1.1rem;
}}

/* Products */
.products-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}}

.product-card {{
    background: white;
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.3s;
}}

.product-card:hover {{
    transform: translateY(-5px);
}}

.product-card img {{
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 5px;
    margin-bottom: 1rem;
}}

.product-card h3 {{
    color: var(--primary);
    margin-bottom: 0.5rem;
}}

.product-card .price {{
    display: block;
    font-size: 1.5rem;
    font-weight: bold;
    color: var(--secondary);
    margin-top: 1rem;
}}

/* Contact */
.contact {{
    background: var(--accent);
}}

.contact-info {{
    text-align: center;
    font-size: 1.2rem;
}}

.contact-info p {{
    margin: 1rem 0;
}}

/* Gallery */
.gallery {{
    background: var(--neutral);
}}

.gallery-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
    margin-top: 2rem;
}}

.gallery-item {{
    position: relative;
    overflow: hidden;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.3s;
    background: white;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 250px;
    font-size: 3rem;
}}

.gallery-item:hover {{
    transform: translateY(-5px);
}}

.gallery-item img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}}

/* Footer */
.footer {{
    background: var(--primary);
    color: white;
    text-align: center;
    padding: 2rem 0;
}}

.footer .social-links {{
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
}}

.footer .social-links a {{
    color: white;
    transition: transform 0.3s, opacity 0.3s;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
}}

.footer .social-links a:hover {{
    transform: translateY(-3px);
    opacity: 0.8;
    background: rgba(255,255,255,0.2);
}}

/* WhatsApp Floating Button */
.whatsapp-float {{
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: #25D366;
    color: white;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(37, 211, 102, 0.4);
    z-index: 1000;
    transition: all 0.3s ease;
    text-decoration: none;
}}

.whatsapp-float:hover {{
    transform: scale(1.1);
    box-shadow: 0 6px 20px rgba(37, 211, 102, 0.6);
}}

.whatsapp-float svg {{
    width: 32px;
    height: 32px;
}}

/* Responsive */
@media (max-width: 768px) {{
    .header .container {{
        flex-direction: column;
        gap: 1rem;
    }}
    
    .hero h2 {{
        font-size: 2rem;
    }}
    
    .hero p {{
        font-size: 1.2rem;
    }}
    
    .whatsapp-float {{
        width: 50px;
        height: 50px;
        bottom: 15px;
        right: 15px;
    }}
    
    .whatsapp-float svg {{
        width: 28px;
        height: 28px;
    }}
}}
"""
    
    def generate_tracking_script(self, site_id: int) -> str:
        """Generar script de tracking de visitas"""
        return f"""// Simple tracking script
(function() {{
    // Registrar visita
    const trackingData = {{
        site_id: {site_id},
        timestamp: new Date().toISOString(),
        referrer: document.referrer,
        userAgent: navigator.userAgent
    }};
    
    // Enviar a backend (ajustar URL según deployment)
    fetch('https://tu-backend.com/api/stats/' + {site_id} + '/visit', {{
        method: 'POST',
        headers: {{
            'Content-Type': 'application/json'
        }},
        body: JSON.stringify(trackingData)
    }}).catch(err => console.log('Tracking error:', err));
}})();
"""
