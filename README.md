# Market Pro 🛒

> A full-stack web application with server-rendered HTML via **Django Templates**, enhanced with **Vue 3 Composition API** (via CDN) for interactivity — containerized using Docker for rapid deployment.

---

## 📌 Project Overview

Market Pro is designed for small business or government-facing product listing and cart systems. It combines the power of:

- ✅ Django's robust backend and templating system
- ✅ Vue 3 Composition API for frontend logic (via CDN)
- ✅ Dockerized infrastructure for seamless local and production deployment

---

## 🔧 Tech Stack

| Layer       | Technology                         |
|------------|-------------------------------------|
| Frontend    | Django Templates + Vue 3 (CDN)     |
| JS Logic    | Vue 3 Composition API              |
| Backend     | Django                             |
| Database    | PostgreSQL or MySQL                |
| DevOps      | Docker, Docker Compose             |
| Auth        | Django Sessions                    |

---

## 🗂 Folder Structure

```
marketpro/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   │   ├── base.html
│   │   └── index.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🖥 Key Features

- 🛒 Product listing, cart, and checkout
- 🧠 Vue 3 reactive features (search, cart updates)
- 🔐 Auth system with session login/logout
- ⏱ Auto logout after 10 minutes of inactivity
- 🐳 Dockerized environment (`docker-compose up` and go!)
- 🔄 REST-like endpoints (optional) or classical views
- 📦 Reusable apps (Products, Users)

---

## 🐳 Quick Start with Docker

```bash
git clone https://github.com/yourusername/market-pro.git
cd market-pro
cp .env.example .env
docker-compose up --build

