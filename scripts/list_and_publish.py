"""
List sites from DB and publish one using the API and admin credentials.

Usage:
  python scripts/list_and_publish.py --site-id 1
  python scripts/list_and_publish.py  # interactive

The script will:
 - Load .env into environment
 - Use ADMIN_EMAIL/ADMIN_PASSWORD to get access token
 - POST /api/sites/{SITE_ID}/publish
 - Print results and poll until the published site returns HTTP 200

"""
from __future__ import annotations
import os
import argparse
import time
import json
from typing import Optional

import requests
from dotenv import load_dotenv
from backend.database import SessionLocal, Site


load_dotenv()  # loads .env into environment

API_BASE = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')


def list_sites():
    session = SessionLocal()
    try:
        rows = session.query(Site).all()
        sites = [
            {
                'id': r.id,
                'name': r.name,
                'is_published': r.is_published,
                'github_url': r.github_url,
            }
            for r in rows
        ]
        return sites
    finally:
        session.close()


def get_token():
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        raise SystemExit('ADMIN_EMAIL and ADMIN_PASSWORD must be set in .env to auto-login')

    resp = requests.post(f"{API_BASE}/api/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD}, timeout=15)
    if resp.status_code != 200:
        raise SystemExit(f'Failed to login: {resp.status_code} {resp.text}')
    return resp.json().get('access_token')


def publish_site(site_id: int, token: str) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    # Publicación puede tardar, especialmente por la propagación de GitHub Pages. Timeout extendido.
    resp = requests.post(f"{API_BASE}/api/sites/{site_id}/publish", headers=headers, timeout=600)
    try:
        data = resp.json()
    except Exception:
        data = {'status_code': resp.status_code, 'text': resp.text}
    return {'status_code': resp.status_code, 'data': data}


def verify_url(url: str, timeout=180):
    url = url.rstrip('/') + '/'
    deadline = time.time() + timeout
    last_status = None

    while time.time() < deadline:
        try:
            r = requests.get(url, timeout=10)
            last_status = r.status_code
            if r.status_code == 200:
                return True, last_status
        except requests.RequestException as e:
            last_status = str(e)
        time.sleep(5)
    return False, last_status


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--site-id', type=int, help='Site ID to publish (if omitted, select interactively)')
    p.add_argument('--create-demo', action='store_true', help='Create a demo site (if none present)')
    p.add_argument('--async', action='store_true', dest='async_publish', help='Use async publish endpoint')
    return p.parse_args()


def main():
    args = parse_args()

    sites = list_sites()
    if not sites:
        print('No sites in the database')
        if not args.create_demo:
            print('Run with --create-demo to automatically create a demo site')
            return
        # Create a simple demo site
        from backend.database import SessionLocal, Site
        session = SessionLocal()
        try:
            demo = Site(
                name='sitio-qa-publish',
                model_type='adecuaciones',
                description='Sitio QA para publicar',
                is_published=False,
            )
            session.add(demo)
            session.commit()
            print(f'Created demo site with ID {demo.id}')
            sites = list_sites()
        finally:
            session.close()

    print('Available sites:')
    for s in sites:
        print(f"  ID: {s['id']}, name: {s['name']}, published: {s['is_published']}, url: {s['github_url']}")

    site_id = args.site_id
    if not site_id:
        try:
            site_id = int(input('Enter site_id to publish: ').strip())
        except Exception:
            raise SystemExit('Invalid site id')

    if not GITHUB_TOKEN or not GITHUB_USERNAME:
        print('WARNING: GITHUB_TOKEN or GITHUB_USERNAME not set in environment. The call will likely fail unless the backend process is launched with these variables.')

    token = get_token()
    print('Publishing site...')
    if args.async_publish:
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        resp = requests.post(f"{API_BASE}/api/sites/{site_id}/publish-async", headers=headers, timeout=15)
        print(f"Async publish response: {resp.status_code} -> {resp.text}")
        publish_result = {'status_code': resp.status_code, 'data': resp.json() if resp.text else {}}
        if resp.status_code == 200:
            # Poll for site status change
            print('Esperando la actualizacion del sitio en la DB...')
            deadline = time.time() + 600
            while time.time() < deadline:
                site_resp = requests.get(f"{API_BASE}/api/sites/{site_id}", headers={"Authorization": f"Bearer {token}"}, timeout=30)
                if site_resp.status_code == 200:
                    s = site_resp.json()
                    if s.get('is_published'):
                        pages_url = s.get('github_url')
                        if pages_url:
                            print(f"Sitio publicado: {pages_url}")
                            ok, status = verify_url(pages_url, timeout=300)
                            if ok:
                                print(f"Sitio activo: {pages_url} (HTTP 200)")
                                break
                            else:
                                print(f"Sitio publicado pero no responde 200 aun (ultimo status {status}). Esperando...")
                time.sleep(5)
    else:
        publish_result = publish_site(site_id, token)
    print(f"Publish response status: {publish_result['status_code']} -> {publish_result['data']}")

    if publish_result['status_code'] == 200:
        pages_url = publish_result['data'].get('url')
        if pages_url:
            print('Waiting for site to become available...')
            ok, last_status = verify_url(pages_url, timeout=300)
            if ok:
                print(f'Site is live: {pages_url} (HTTP 200)')
            else:
                print(f'Site did not become available after timeout (last status: {last_status})')
    else:
        print('Publish failed. Check the server logs and returned message for more details.')


if __name__ == '__main__':
    main()
