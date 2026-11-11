# Flask Kickoff

# 1\. Principios

Usaremos como referencia:

- [The Twelve-Factor App](https://12factor.net/)  
- [15-Factor Apps — IBM](https://developer.ibm.com/articles/15-factor-applications/)  
- [Flask Documentation](https://flask.palletsprojects.com/en/stable/)

---

# 2\. Stack

```
Python
   uv              → proyecto y dependencias
   Flask           → HTTP / web framework
   Jinja2          → HTML server-side
   SQLAlchemy      → ORM / acceso a DB
   Alembic         → migraciones
   pytest          → tests
   Ruff            → lint + formatting
```

&nbsp;

Base de datos:

```
Development → SQLite
Production  → PostgreSQL
```

&nbsp;

La aplicación no debería depender de una base de datos específica.

---

# 3\. Estructura inicial

Propuesta:

```text
flask-kickoff/
|-- pyproject.toml
|-- uv.lock
|-- README.md
|-- .gitignore
|-- .env.example
|
|-- src/
|   `-- myapp/
|       |-- __init__.py
|       |-- config.py
|       |-- extensions.py
|       |
|       |-- models/
|       |   |-- __init__.py
|       |   `-- user.py
|       |
|       |-- api/
|       |   |-- __init__.py
|       |   `-- health.py
|       |
|       |-- web/
|       |   |-- __init__.py
|       |   `-- users.py
|       |
|       |-- services/
|       |   `-- ...
|       |
|       |-- templates/
|       |   |-- base.html
|       |   `-- users/
|       |       |-- index.html
|       |       `-- detail.html
|       |
|       `-- static/
|           |-- css/
|           |   `-- app.css
|           `-- js/
|               `-- app.js
|
|-- migrations/
|   |-- versions/
|   |-- env.py
|   `-- alembic.ini
|
`-- tests/
    |-- conftest.py
    |-- test_health.py
    `-- test_users.py
```

&nbsp;

---

# 4\. Crear el proyecto con uv

**uv** es un gestor de proyectos y dependencias para Python. Permite crear un proyecto, agregar dependencias y ejecutar comandos de forma reproducible. Ref: [https\://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

Crear un proyecto:

```sh
uv init
```

&nbsp;

Agregar Flask:

Flask es un microframework web para Python. Permite crear aplicaciones web y APIs de forma sencilla. Ref: [https\://flask.palletsprojects.com/en/stable/](https://flask.palletsprojects.com/en/stable/)

```sh
uv add flask
```

&nbsp;

Agregar SQLAlchemy:

SQLAlchemy es un ORM para Python que permite interactuar con bases de datos de forma orientada a objetos. Ref: [https\://www\.sqlalchemy.org/](https://www.sqlalchemy.org/)

```sh
uv add sqlalchemy
```

&nbsp;

Agregar Alembic:

Alembic es una herramienta de migraciones para SQLAlchemy. Permite versionar y aplicar cambios en la estructura de la base de datos. Ref: [https\://alembic.sqlalchemy.org/](https://alembic.sqlalchemy.org/)

```sh
uv add alembic
```

&nbsp;

Dependencias de desarrollo:

ruff es un linter y formateador para Python. Permite mantener un estilo de código consistente y detectar errores comunes. Ref: [https\://docs.astral.sh/ruff/](https://docs.astral.sh/ruff/)

```sh
uv add --dev pytest ruff
```

&nbsp;

Sincronizar: syncroniza las dependencias del proyecto según lo definido en `pyproject.toml` y `uv.lock`.

```sh
uv sync
```

&nbsp;

Ejecutar comandos:

```sh
uv run pytest
uv run ruff check .
uv run ruff format .
```

&nbsp;

Importante: `pyproject.toml` y `uv.lock` deben estar versionados en Git. Esto permite que cualquier persona pueda clonar el proyecto y tener exactamente las mismas dependencias. `.venv/` no debe estar versionado.

---

# 5\. Application Factory

`src/myapp/__init__.py`:

```py
from flask import Flask

from myapp.config import Config
from myapp.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)

    from myapp.api.health import health_bp
    from myapp.web.users import users_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(users_bp)

    return app
```

&nbsp;

La idea es poder crear diferentes aplicaciones:

```
development
testing
production
```

&nbsp;

sin modificar el código de la aplicación.

---

# 6\. Configuración

`src/myapp/config.py`:

```py
import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///app.db",
    )
```

&nbsp;

`.env.example`:

```dotenv
APP_ENV=development
SECRET_KEY=change-me
DATABASE_URL=sqlite:///app.db
```

&nbsp;

Nunca guardar secretos reales en Git.

---

# 7\. SQLAlchemy

Una forma simple de integrar SQLAlchemy es mediante una extensión compartida.

`src/myapp/extensions.py`:

```py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
```

&nbsp;

En ese caso agregar:

```sh
uv add flask-sqlalchemy
```

&nbsp;

Esto permite tener un estilo similar al que muchos alumnos conocen de ActiveRecord:

```py
class User(db.Model):
    ...
```

&nbsp;

---

# 8\. Modelo

`src/myapp/models/user.py`:

```py
from myapp.extensions import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f"<User {self.email}>"
```

&nbsp;

Y:

`src/myapp/models/__init__.py`:

```py
from myapp.models.user import User

__all__ = ["User"]
```

&nbsp;

Conceptualmente:

```
ActiveRecord / Rails       Flask / SQLAlchemy

User < ActiveRecord        class User(db.Model)

User.find(1)               db.session.get(User, 1)

User.all                   db.session.scalars(
                               db.select(User)
                           ).all()

user.save                  db.session.add(user)
                           db.session.commit()

user.destroy               db.session.delete(user)
                           db.session.commit()
```

&nbsp;

SQLAlchemy es un ORM potente, pero su API no es una copia de ActiveRecord.

---

# 9\. Migraciones con Alembic

No queremos crear la base de datos manualmente.

La estructura debería evolucionar mediante migraciones:

```
Model
  ↓
migration
  ↓
database
```

&nbsp;

Inicializar Alembic:

```sh
uv run alembic init migrations
```

&nbsp;

Después configurar `migrations/env.py` para que Alembic conozca el metadata de nuestros modelos.

La idea conceptual es:

```sh
uv run alembic revision --autogenerate -m "create users"
```

&nbsp;

Revisar la migración generada.

Luego:

```sh
uv run alembic upgrade head
```

&nbsp;

Para volver atrás:

```sh
uv run alembic downgrade -1
```

&nbsp;

Regla importante:

> Una migración es parte del código del proyecto y debe estar versionada en Git.

No se debe modificar manualmente la estructura de la DB de producción y después intentar sincronizar el código.

---

# 10\. HTML: Flask \+ Jinja2

Flask utiliza Jinja2 para generar HTML server-side.

Por ejemplo:

```py
from flask import Blueprint, render_template

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.get("/")
def index():
    users = ...

    return render_template(
        "users/index.html",
        users=users,
    )
```

&nbsp;

Template:

`templates/users/index.html`

```html
{% extends "base.html" %}

{% block content %}
<h1>Users</h1>

<ul>
  {% for user in users %}
    <li>
      {{ user.name }} — {{ user.email }}
    </li>
  {% endfor %}
</ul>
{% endblock %}
```

&nbsp;

Esto permite enseñar una arquitectura web clásica:

```
Browser
   ↓
HTTP GET
   ↓
Flask route
   ↓
Service / ORM
   ↓
Database
   ↓
Python objects
   ↓
Jinja2
   ↓
HTML
   ↓
Browser
```

&nbsp;

---

# 11\. Template base

`templates/base.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <title>{% block title %}My App{% endblock %}</title>

  <link
    rel="stylesheet"
    href="{{ url_for('static', filename='css/app.css') }}"
  >
</head>

<body>

<header>
  <nav>
    <a href="{{ url_for('users.index') }}">Users</a>
  </nav>
</header>

<main>
  {% block content %}{% endblock %}
</main>

<script
  src="{{ url_for('static', filename='js/app.js') }}"
></script>

</body>
</html>
```

&nbsp;

Esto introduce otro concepto importante:

```
layout
   ↓
templates
   ↓
HTML
```

&nbsp;

Los alumnos pueden reutilizar el layout sin duplicar HTML.

---

# 12\. API y HTML pueden convivir

No hace falta elegir entre una API y HTML.

El mismo proyecto puede tener:

```
/api/users
```

&nbsp;

para clientes programáticos y:

```
/users
```

&nbsp;

para humanos.

Por ejemplo:

```
Browser
   ↓
GET /users
   ↓
HTML/Jinja

Mobile app / JavaScript / external client
   ↓
GET /api/users
   ↓
JSON
```

&nbsp;

Esto es muy útil pedagógicamente porque permite comparar:

```
HTML
vs
JSON
```

&nbsp;

y:

```
Server-side rendering
vs
API
```

&nbsp;

sin tener que introducir React/Vue/etc. desde el comienzo.

---

# 13\. CRUD

Una primera iteración podría implementar:

```
GET    /users
GET    /users/<id>
GET    /users/new
POST   /users
GET    /users/<id>/edit
POST   /users/<id>
POST   /users/<id>/delete
```

&nbsp;

Y posteriormente:

```
GET    /api/users
GET    /api/users/<id>
POST   /api/users
PATCH  /api/users/<id>
DELETE /api/users/<id>
```

&nbsp;

Esto permite enseñar REST y comparar una aplicación web tradicional con una API.

---

# 14\. Formularios HTML

Inicialmente se puede trabajar directamente con Flask:

```html
<form method="post">

  <label>
    Name
    <input
      type="text"
      name="name"
      required
    >
  </label>

  <label>
    Email
    <input
      type="email"
      name="email"
      required
    >
  </label>

  <button type="submit">
    Create user
  </button>

</form>
```

&nbsp;

Después se puede incorporar Flask-WTF si se quiere profundizar en:

- validación  
- CSRF  
- formularios reutilizables

No lo agregaría al kickoff inicial. Es mejor que los alumnos primero entiendan HTTP forms y después una librería que los abstraiga.

---

# 15\. CSS y JavaScript

Mantenerlo simple:

```
static/
|-- css/
|   `-- app.css
`-- js/
    `-- app.js
```

&nbsp;

Al principio no hace falta introducir un frontend framework.

El objetivo es que los alumnos entiendan:

```
HTML
CSS
JavaScript
HTTP
Flask
Database
```

&nbsp;

antes de agregar React, Vue, etc.

---

# 16\. Testing

Instalar:

```sh
uv add --dev pytest
```

&nbsp;

`tests/conftest.py`:

```py
import pytest

from myapp import create_app


@pytest.fixture
def app():
    app = create_app()

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    return app


@pytest.fixture
def client(app):
    return app.test_client()
```

&nbsp;

Test:

```py
def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}
```

&nbsp;

Y luego tests de persistencia:

```py
def test_create_user(client):
    response = client.post(
        "/users",
        data={
            "name": "Ada Lovelace",
            "email": "ada@example.com",
        },
    )

    assert response.status_code == 302
```

&nbsp;

---

# 17\. Health endpoint

`src/myapp/api/health.py`:

```py
from flask import Blueprint

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return {"status": "ok"}
```

&nbsp;

Test:

```py
def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}
```

&nbsp;

Este endpoint también será útil más adelante para Docker, CI y deployment.

---

# 18\. Ruff

Ejecutar:

```sh
uv run ruff check .
```

&nbsp;

Y:

```sh
uv run ruff format .
```

&nbsp;

La idea es que el proyecto tenga una definición automática de calidad:

```
pytest
+
ruff
```

&nbsp;

Antes de hacer un pull request.

---

# 19\. GitHub Actions

Una primera CI puede ejecutar:

```
checkout
   ↓
install uv
   ↓
uv sync
   ↓
ruff check
   ↓
pytest
```

&nbsp;

Ejemplo:

```yaml
name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6

      - name: Install dependencies
        run: uv sync --locked

      - name: Lint
        run: uv run ruff check .

      - name: Test
        run: uv run pytest
```

&nbsp;

La idea pedagógica es que GitHub pueda responder:

> "¿Este cambio sigue funcionando?"

sin que una persona tenga que ejecutar los tests manualmente.

---

# 20\. Development vs Production

Development:

```sh
uv run flask --app myapp run --debug
```

&nbsp;

Production:

```sh
uv add gunicorn
```

&nbsp;

y:

```sh
uv run gunicorn "myapp:create_app()"
```

&nbsp;

El servidor de desarrollo de Flask no debe confundirse con un servidor de producción.

Esto permite enseñar:

```
Application
   !=
Development server
```

&nbsp;

---

# 21\. Port binding

La aplicación debería poder recibir el puerto desde el entorno:

```
PORT=5000
```

&nbsp;

La plataforma puede decidir:

```
PORT=8080
```

&nbsp;

sin modificar el código.

Esto conecta directamente con el concepto de port binding de 12-Factor.

---

# 22\. Logging

Evitar:

```py
print("User created")
```

&nbsp;

Preferir:

```py
import logging

logger = logging.getLogger(__name__)

logger.info("User created")
```

&nbsp;

Más adelante se puede enseñar logging estructurado y telemetry.

---

# 23\. Qué NO agregar al kickoff

No empezaría con:

- Docker  
- Kubernetes  
- microservicios  
- React  
- Celery  
- Redis  
- Kafka  
- OAuth  
- JWT  
- Kubernetes  
- AWS/GCP  
- observability stack completo

No porque sean malas tecnologías, sino porque agregan complejidad antes de que los alumnos hayan entendido los fundamentos.

El proyecto debe ser pequeño.

---

# 24\. Evolución sugerida del curso

## Kickoff

```
Git
uv
Flask
Application Factory
Blueprints
Jinja2
HTML
CSS
pytest
Ruff
README
.env
```

&nbsp;

## Iteración 1 — Web

```
Routes
HTTP
HTML
Forms
Jinja
CRUD
```

&nbsp;

## Iteración 2 — Database

```
SQLAlchemy
Models
Relationships
Alembic
Migrations
PostgreSQL
```

&nbsp;

## Iteración 3 — API

```
JSON
REST
HTTP status codes
API design
```

&nbsp;

## Iteración 4 — Software Engineering

```
Service layer
Validation
Error handling
Testing
Mocking
Integration tests
```

&nbsp;

## Iteración 5 — Security

```
Authentication
Authorization
CSRF
Secrets
Input validation
```

&nbsp;

## Iteración 6 — Deployment

```
Docker
WSGI
Environment variables
CI/CD
Cloud deployment
```

&nbsp;

## Iteración 7 — Operations

```
Logging
Metrics
Telemetry
Health checks
```

&nbsp;

---

# 25\. Relación con 12-Factor

| Concepto | Cómo aparece en el proyecto |
| :---- | :---- |
| Codebase | Git repository |
| Dependencies | `pyproject.toml` \+ `uv.lock` |
| Config | environment variables |
| Backing services | database |
| Build/release/run | CI/deployment |
| Processes | Flask/Gunicorn processes |
| Port binding | `$PORT` |
| Concurrency | múltiples workers |
| Disposability | startup/shutdown rápido |
| Dev/prod parity | SQLite/PostgreSQL \+ misma aplicación |
| Logs | logging/stdout |
| Admin processes | migrations/scripts |

&nbsp;

No es necesario implementar todos estos conceptos en la primera clase.

---

# 26\. Relación con 15-Factor

Los conceptos adicionales pueden aparecer posteriormente:

```
API First
   ↓
REST API

Telemetry
   ↓
logs + metrics + tracing

Authentication & Authorization
   ↓
users + roles + permissions
```

&nbsp;

La idea es que los alumnos vean que estas prácticas no son recetas aisladas, sino respuestas a problemas concretos de sistemas reales.

---

# 27\. Definición de "funciona"

El kickoff debería permitir ejecutar:

```sh
git clone <repository>

cd flask-kickoff

uv sync

uv run pytest

uv run ruff check .

uv run flask --app myapp run
```

&nbsp;

Luego:

```sh
curl http://localhost:5000/health
```

&nbsp;

Resultado:

```json
{
  "status": "ok"
}
```

&nbsp;

Y desde el browser:

```
http://localhost:5000/users
```

&nbsp;

debería mostrar una página HTML generada por Jinja.

---

# 28\. Primera milestone para los alumnos

La primera entrega puede ser:

### "Kickoff funcionando"

Debe incluir:

- [ x ] Repository GitHub  
- [ x ] `pyproject.toml`  
- [ x ] `uv.lock`  
- [ x ] Flask  
- [ x ] Application Factory  
- [ ] Blueprint  
- [ ] `/health`  
- [ ] HTML con Jinja  
- [ ] CSS  
- [ ] SQLAlchemy  
- [ ] User model  
- [ ] Alembic  
- [ ] Primera migration  
- [ ] pytest  
- [ ] Ruff  
- [ ] README  
- [ ] `.env.example`  
- [ ] No secrets committed

---

# 29\. Segunda milestone

### "CRUD completo"

Los alumnos deberían implementar:

```
Create
Read
Update
Delete
```

&nbsp;

para una entidad de dominio.

Por ejemplo:

```
Project
Task
Book
Movie
Product
Student
Course
```

&nbsp;

La entidad concreta puede variar entre grupos.

---

# 30\. Tercera milestone

### "API"

Agregar una API JSON:

```
GET    /api/projects
GET    /api/projects/<id>
POST   /api/projects
PATCH  /api/projects/<id>
DELETE /api/projects/<id>
```

&nbsp;

Y tests para cada endpoint.

---

# 31\. Regla arquitectónica principal

No enseñar:

> "Siempre hay que crear esta carpeta."

Enseñar:

> "Cada decisión arquitectónica debe resolver un problema."

Por ejemplo:

```
¿Por qué Blueprints?
→ modularización.

¿Por qué Application Factory?
→ configuración y testing.

¿Por qué Alembic?
→ evolución reproducible de la DB.

¿Por qué uv.lock?
→ reproducibilidad.

¿Por qué environment variables?
→ separar configuración del código.

¿Por qué pytest?
→ feedback automático.

¿Por qué CI?
→ detectar problemas antes de integrar.
```

&nbsp;

Esta forma de enseñar probablemente sea más valiosa que memorizar una estructura de carpetas.

---

# 32\. Resultado final esperado

Al terminar varias iteraciones, el alumno debería poder mirar el proyecto y entender:

```
                    GitHub
                       |
                 Git / CI
                       |
                       v
                Flask Application
                       |
          +------------+------------+
          |            |            |
       Web/Jinja      API        Services
          |            |            |
          +------------+------------+
                       |
                   SQLAlchemy
                       |
                       v
                   PostgreSQL
                       |
                   Alembic
                       |
                  Migrations
```

&nbsp;

Y, sobre todo, debería poder explicar por qué cada componente existe.

---

# Referencias

- Flask: [https\://flask.palletsprojects.com/en/stable/](https://flask.palletsprojects.com/en/stable/)  
- Flask Application Factories: [https\://flask.palletsprojects.com/en/stable/patterns/appfactories/](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)  
- Flask Blueprints: [https\://flask.palletsprojects.com/en/stable/blueprints/](https://flask.palletsprojects.com/en/stable/blueprints/)  
- Flask Templates: [https\://flask.palletsprojects.com/en/stable/templating/](https://flask.palletsprojects.com/en/stable/templating/)  
- SQLAlchemy: [https\://www\.sqlalchemy.org/](https://www.sqlalchemy.org/)  
- Alembic: [https\://alembic.sqlalchemy.org/](https://alembic.sqlalchemy.org/)  
- uv: [https\://docs.astral.sh/uv/](https://docs.astral.sh/uv/)  
- pytest: [https\://docs.pytest.org/](https://docs.pytest.org/)  
- Ruff: [https\://docs.astral.sh/ruff/](https://docs.astral.sh/ruff/)  
- Twelve-Factor App: [https\://12factor.net/](https://12factor.net/)  
- IBM 15-Factor Apps: [https\://developer.ibm.com/articles/15-factor-applications/](https://developer.ibm.com/articles/15-factor-applications/)
