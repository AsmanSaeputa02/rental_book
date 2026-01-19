# Enterprise Rental SaaS - Production Grade Architecture

This repository showcases a highly scalable **Multi-tenant SaaS Application** built with **Django**, fully containerized with **Docker**, and focused on high availability and code reliability.

## 🛠️ Infrastructure & DevOps
- **Containerization:** Orchestrated with **Docker** and **Docker Compose**, including a dedicated `docker-compose.prod.yml` for production-ready deployments.
- **Web Server:** Configured **Nginx** as a reverse proxy to handle static files and secure traffic.
- **Environment Management:** Secured sensitive data using `.env.prod` and streamlined development with `.devcontainer`.
- **CI/CD Ready:** Automated workflows integrated via GitHub Actions in the `.github` directory.

## 🧪 Testing & Reliability
- **Automated Testing:** Dedicated `tests/` module with custom test cases (`create_testcase`) to ensure business logic integrity and prevent regressions.
- **Data Isolation:** Robust multi-tenancy implementation to ensure strict data separation between different organizations.

## 📂 Key Modules
- `tenants/`: Core logic for managing multiple client environments.
- `dashbord/`: Real-time analytics and monitoring dashboard.
- `user/` & `company/`: Integrated authentication and authorization systems.
- `services/`: Backend services handling core business processes.

## 🚀 Tech Stack
- **Framework:** Python, Django
- **Infrastructure:** Docker, Nginx, GitHub Actions
- **Database:** PostgreSQL/SQLite
