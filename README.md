# Utamu Wetu Backend 

**A Scalable GraphQL API for Modern E-Commerce**

**Utamu Wetu Backend** is a production-ready, containerized service designed to power a high-performance frontend. Built with **Django** and **Graphene**, it offers a flexible GraphQL schema, robust JWT authentication, and seamless integration with cloud services for media and database management.

---

## 🏗 System Architecture

The project follows a decoupled, modular architecture to ensure high maintainability:

* **API Layer:** GraphQL (Graphene-Django) for efficient, single-endpoint data fetching.
* **Database:** PostgreSQL (managed via **Supabase**) for relational data integrity.
* **Media Management:** **Cloudinary** integration for optimized image hosting.
* **Security:** **JWT (JSON Web Tokens)** for stateless authentication.
* **Environment:** **Dockerized** workflow for parity between development and production.

---

## 🚀 Getting Started

### Prerequisites

* **Docker** & **Docker Compose**
* **Python 3.11+** (if running outside Docker)
* **Supabase Account** (for PostgreSQL hosting)

### Installation & Setup

1. **Clone the Repository**
```bash
git clone https://github.com/vitroyfix/utamu-wetu-backend.git
cd utamu-wetu-backend

```


2. **Configure Environment Variables**
Create a `.env` file in the root directory and populate it with your credentials:
```env
DEBUG=True
SECRET_KEY=your_django_secret_key
DATABASE_URL=postgres://postgres:[PASSWORD]@[HOST]:5432/postgres
CLOUDINARY_URL=cloudinary://[API_KEY]:[API_SECRET]@[CLOUD_NAME]

```


3. **Launch via Docker**
```bash
docker-compose up --build

```


*The server will be accessible at `http://localhost:8000/graphql/`.*

---

## 🛠 Project Structure

```text
├── apps/
│   ├── users/          # Custom User models & JWT Logic
│   ├── store/          # Product, Category, & Inventory Management
│   └── orders/         # Transactional logic & Order tracking
├── core/
│   ├── settings.py     # Production & Dev configurations
│   ├── schema.py       # Global GraphQL Schema entry point
│   └── urls.py         # Root URL routing
├── docker-compose.yml  # Orchestration for App and DB
├── Dockerfile          # Container specification
└── requirements.txt    # Python dependencies

```

---

## 📡 API Overview (GraphQL)

This backend utilizes a single endpoint: `/graphql/`. You can use the built-in **GraphiQL** interface in debug mode to explore the schema.

### Sample Query: Fetch Store Catalog

```graphql
query {
  allProducts {
    id
    name
    price
    category {
      name
    }
    image
  }
}

```

### Sample Mutation: User Login

```graphql
mutation {
  tokenAuth(username: "peter", password: "password123") {
    token
    payload
  }
}

```

---

##  Deployment

The repository is pre-configured for deployment on **Render** or **Heroku**:

* **Static Files:** Managed via `WhiteNoise`.
* **Database Migrations:** Run automatically via the entrypoint script or manually:
```bash
docker-compose exec web python manage.py migrate

```



---

##  License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

**Would you like me to include a detailed "Contribution Guide" or the specific SQL setup for your Supabase instance?**
