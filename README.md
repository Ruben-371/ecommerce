# 🛒 E-Commerce Lite — Microservices on DOKS

Proyecto de fin de curso: arquitectura de microservicios desplegada en **DigitalOcean Kubernetes Service (DOKS)** con CI/CD a través de GitHub Actions y Helm.

---

## Arquitectura

```
Internet
   │
   ▼
[Ingress NGINX]
   │
   ├── /api/auth, /api/users  ──► [User Service   | Node.js/Express | :3001]
   │                                       │
   │                                    MongoDB
   │
   ├── /api/v1/products       ──► [Catalog Service | Python/FastAPI  | :3002]
   │                                       │
   │                                    MongoDB
   │
   └── /api/payments          ──► [Payment Service | Go              | :3003]
                                          │
                               calls Catalog (/api/v1/products/{id})
                                          │
                                      PostgreSQL
```

## Estructura del Repositorio

```
ecommerce-lite/
├── .github/
│   └── workflows/
│       └── main.yml                  # CI/CD pipeline (GitHub Actions)
├── services/
│   ├── user-service/                 # Node.js / Express / JWT / MongoDB
│   │   ├── src/
│   │   │   ├── index.js
│   │   │   ├── db.js
│   │   │   ├── models/User.js
│   │   │   ├── routes/auth.js
│   │   │   ├── routes/users.js
│   │   │   └── middleware/errorHandler.js
│   │   ├── package.json
│   │   └── Dockerfile
│   ├── catalog-service/              # Python / FastAPI / Motor / MongoDB
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   └── database.py
│   │   │   ├── models/product.py
│   │   │   └── api/v1/products.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── payment-service/             # Go / gorilla-mux
│       ├── cmd/server/main.go
│       ├── internal/
│       │   ├── handlers/payment.go
│       │   └── middleware/middleware.go
│       ├── go.mod
│       └── Dockerfile
└── helm/
    └── ecommerce-lite/
        ├── Chart.yaml
        ├── values.yaml               # ← Configuración central
        └── templates/
            ├── user-service.yaml     # Deployment + Service + HPA
            ├── catalog-service.yaml  # Deployment + Service + HPA
            ├── payment-service.yaml  # Deployment + Service + HPA
            ├── mongodb.yaml          # StatefulSet + Headless Service
            ├── postgresql.yaml       # StatefulSet + Headless Service
            ├── ingress.yaml          # Ingress NGINX
            └── configmap.yaml        # URLs internas de servicios
```

---

## Prerrequisitos

| Herramienta | Versión mínima | Notas |
|-------------|----------------|-------|
| `doctl` | 1.100+ | CLI de DigitalOcean |
| `kubectl` | 1.28+ | Configurado con kubeconfig de DOKS |
| `helm` | 3.14+ | |
| `docker` | 24+ | |
| Node.js | 20+ | Solo local dev |
| Python | 3.12+ | Solo local dev |
| Go | 1.22+ | Solo local dev |

---

## Configuración inicial

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/ecommerce-lite.git
cd ecommerce-lite
```

### 2. Crear el clúster en DigitalOcean
```bash
doctl kubernetes cluster create ecommerce-cluster \
  --region nyc3 \
  --node-pool "name=workers;size=s-2vcpu-4gb;count=3" \
  --wait
doctl kubernetes cluster kubeconfig save ecommerce-cluster
```

### 3. Instalar Ingress NGINX en el clúster
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

### 4. (Opcional) cert-manager para TLS automático
```bash
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true
```

### 5. Crear el Container Registry en DigitalOcean
```bash
doctl registry create your-registry-name --region nyc3
```

---

## Secrets de GitHub Actions

Ve a **Settings → Secrets and Variables → Actions** y agrega:

| Secret | Descripción |
|--------|-------------|
| `DIGITALOCEAN_ACCESS_TOKEN` | Token de la API de DigitalOcean |
| `DOCR_NAME` | Nombre de tu registry (ej: `my-registry`) |
| `DOKS_CLUSTER_NAME` | Nombre del clúster de Kubernetes |
| `MONGODB_URI` | URI completa de MongoDB |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL |
| `JWT_SECRET` | Clave secreta para firmar JWT (mín. 32 chars) |

---

## Despliegue manual con Helm

```bash
# Crear namespace
kubectl create namespace production

# Crear secrets en Kubernetes
kubectl create secret generic app-secrets \
  --namespace=production \
  --from-literal=MONGODB_URI="mongodb://mongodb.production.svc.cluster.local:27017/catalog" \
  --from-literal=POSTGRES_PASSWORD="tu_password_seguro" \
  --from-literal=JWT_SECRET="tu_jwt_secret_muy_largo_y_seguro"

# Actualizar values.yaml con tu registry y dominio, luego:
helm upgrade --install ecommerce-lite ./helm/ecommerce-lite \
  --namespace production \
  --set global.imageRegistry=registry.digitalocean.com/your-registry-name \
  --wait
```

---

## API Reference

### User Service `(:3001)`

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register` | Registro de usuario |
| POST | `/api/auth/login` | Login → retorna JWT |
| GET | `/api/users/me` | Perfil del usuario autenticado |
| GET | `/api/users/validate` | Validación interna de token |

### Catalog Service `(:3002)`

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/products` | Listar productos (paginado) |
| GET | `/api/v1/products/{id}` | Detalle de un producto |
| POST | `/api/v1/products` | Crear producto |
| PATCH | `/api/v1/products/{id}` | Actualizar producto |
| DELETE | `/api/v1/products/{id}` | Eliminar producto |
| GET | `/docs` | Swagger UI (FastAPI) |

### Payment Service `(:3003)`

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/payments/process` | Procesar pago (simulado) |
| GET | `/api/payments/{id}` | Consultar transacción |

---

## Seguridad implementada

- **Contraseñas**: Hasheadas con `bcryptjs` (cost factor 12)
- **JWT**: Firmados con HS256, expiración configurable
- **Sin credenciales hardcodeadas**: Todo via `Secrets` de K8s
- **Imágenes Docker**: Ejecutan como usuario no-root
- **Helm**: Secrets inyectados desde `secretKeyRef`
- **Go binary**: Compilado estático desde `scratch` (superficie mínima de ataque)
- **HTTP headers**: Protegidos con `helmet` (Node.js)

---

## Desarrollo local

```bash
# User Service
cd services/user-service
cp .env.example .env   # configura MONGODB_URI y JWT_SECRET
npm install
npm run dev

# Catalog Service
cd services/catalog-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 3002

# Payment Service
cd services/payment-service
go run ./cmd/server
```

---

## CI/CD Flow

```
git push main
      │
      ▼
  [Test Job] ──── npm test / pytest / go test
      │
      ▼
[Build & Push] ── docker buildx + push to DOCR (tag: git SHA)
      │
      ▼
  [Deploy] ─────── helm upgrade --install → DOKS
      │
      ▼
[Verify Rollout] ─ kubectl rollout status
```
