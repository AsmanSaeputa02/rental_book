# Multi-tenant Rental Management System (Enterprise Grade)

This repository showcases a complex **Multi-tenant SaaS Architecture** built with **Django and Docker**. It is designed for scalability, featuring isolated data environments for multiple clients within a single application instance.

## 🏗️ Core Architecture & Features
- **Multi-tenancy:** Engineered using a tenant-based architecture to manage separate client data (Schools/Companies) efficiently.
- **Containerization (Docker):** Full environment orchestration using `Dockerfile` and `docker-compose` for both development and production (`docker-compose.prod.yml`).
- **Web Server & Reverse Proxy:** Configured **Nginx** for serving static files and handling requests securely.
- **Infrastructure as Code:** Includes `.devcontainer` for standardized development environments and GitHub Actions for automated workflows.
- **Monitoring Dashboard:** Integrated dashboard logic for real-time data visualization.

## 🛠️ Tech Stack
- **Backend:** Python, Django
- **DevOps:** Docker, Docker Compose, Nginx
- **Environment Management:** Python-dotenv (`.env.prod`)
- **CI/CD:** GitHub Actions

## 📂 Key Modules
- `tenants/`: Logic for tenant identification and data isolation.
- `dashbord/`: Visualization of rental metrics and system status.
- `rental/` & `book/`: Core business logic for asset and inventory management.
- `docker/`: Custom configurations for Nginx and service containers.
