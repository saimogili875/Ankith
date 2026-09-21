# Adept Eduverse PWA

Mobile-first Progressive Web App for [@adepteduverse](https://youtube.com/@adepteduverse) YouTube channel. Organizes JEE Advanced Mathematics videos by chapter and topic.

## Tech Stack
- **Frontend**: Next.js (App Router), TypeScript, Tailwind CSS, TanStack Query, next-pwa
- **Backend**: Python 3.12, Django 5, Django REST Framework, SimpleJWT, django-allauth, django-cors-headers, django-filter, drf-spectacular
- **Database**: PostgreSQL with GIN Full-Text Search
- **Storage**: Cloudflare R2 via django-storages (S3 API)
- **Local Dev**: Docker Compose

## Quick Start (Local Development)

1. **Environment Setup**:
   Copy environment templates and update with your credentials:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env.local
   ```

2. **Docker Compose**:
   ```bash
   docker compose up --build
   ```

3. **Run Video Export (Phase 0)**:
   ```bash
   ./backend/venv/bin/python backend/manage.py export_videos
   ```

4. **Run Tests**:
   ```bash
   ./backend/venv/bin/pytest backend/
   ```
