# proyecto-is
Taller Ingenieria de Software I (2026).

# Proyecto Ingeniería de Software I (3385) | 2026

| N.º | Nombre y apellido | DNI |
|:---:|---|:---:|
| 1 | Gastón Nicolás López | 47.463.500 |
| 2 | Juan Manuel Martin | 47.911.017 |
| 3 | Juan Cruz Uva Britos | 47.363.325 |

### 1. Idea del proyecto

La idea de este proyecto nace del sitio web de predicciones *PolyMarket*, donde un usuario o un LLM realiza una publicación en forma de pregunta sobre un hecho de la vida real, y otros usuarios compran y venden 'acciones' de cada respuesta basadas en la probabilidad de que eso ocurra (o no), esto provoca que el precio de las mismas vaya oscilando hasta la fecha límite de la pregunta, cuando se confirma cuál es la respuesta correcta y ganan los que compraron 'acciones' de esa respuesta. Algunos ejemplos pueden ser: ¿Alcanzará Bitcoin los 200.000 dólares antes de finales de 2026?, ¿Quién gana las elecciones de Brasil?, entre otros.

### 2. Justificación de la aplicación del patrón de diseño

1. **Patrón *Strategy* (Comportamiento):**
* **Problema que resuelve:** Nuestro sistema necesita generar contenido de manera automática y verificar fuentes usando distintos proveedores de inteligencia artificial conocidos (`Gemini`, `Claude`, `LocalLLM`), evitando que la clase principal de contexto quede fuertemente conectada a una implementación específica, situación que podria generar problemas.
* **Aplicación en el diseño:** Se implementó una interfaz común `StrategyLLM` que define los contratos operativos (`createQuestion()`, `checkSource()`), permitiendo que la clase `LLM` delegue dinámicamente la ejecución en distintas instancias de strategy de manera simple e intercambiable.

---

### 3. Ejecución del proyecto

#### Requisitos previos
- [uv](https://docs.astral.sh/uv/) (gestor de entornos y dependencias de Python)
- Python >= 3.14

#### Instalación y sincronización de dependencias
Clonar el repositorio y sincronizar el entorno virtual con:

```sh
uv sync
```

#### Variables de entorno
Copiar el archivo de ejemplo y ajustar las variables si es necesario (nunca subir `.env` al repositorio):

```sh
cp .env.example .env
```

#### Migraciones de base de datos (Alembic)
Para aplicar las migraciones existentes a la base de datos:

```sh
uv run alembic -c migrations/alembic.ini upgrade head
```

Para generar una nueva migración luego de modificar modelos:

```sh
uv run alembic -c migrations/alembic.ini revision --autogenerate -m "descripcion del cambio"
```

Para revertir la última migración aplicada:

```sh
uv run alembic -c migrations/alembic.ini downgrade -1
```

#### Ejecutar el servidor de desarrollo
Iniciar la aplicación Flask:

```sh
uv run flask --app myapp run
```

La aplicación estará disponible en `http://localhost:5000`:
- **Health check (JSON):** `http://localhost:5000/health`
- **CRUD de Preguntas:** `http://localhost:5000/questions`
- **Página de usuarios (HTML):** `http://localhost:5000/users`

#### Rutas del CRUD de Preguntas (`/questions`)

| Método HTTP | Ruta | Descripción / Acción |
| :--- | :--- | :--- |
| `GET` | `/questions/` | Muestra el listado de todas las preguntas creadas. |
| `GET` | `/questions/new` | Muestra el formulario para crear una nueva pregunta. |
| `POST` | `/questions` | Procesa y almacena una nueva pregunta. |
| `GET` | `/questions/<question_id>` | Muestra el detalle de una pregunta específica (incluyendo respuestas, estado, etiquetas, etc.). |
| `GET` | `/questions/<question_id>/edit` | Muestra el formulario para editar una pregunta existente. |
| `POST` | `/questions/<question_id>` | Procesa la actualización de una pregunta existente. |
| `POST` | `/questions/<question_id>/delete` | Elimina una pregunta existente. |

#### Cargar las categorías iniciales
Con la base de datos ya creada (migraciones aplicadas), cargar las categorías predefinidas:

```sh
uv run flask --app myapp seed-categories
```

El comando es idempotente: si se ejecuta más de una vez no crea categorías duplicadas. La lista está en `src/myapp/services/categories.py`.

Para correr en modo debug:

```sh
uv run flask --app myapp run --debug
```

#### Tests y calidad de código
- **Ejecutar tests con pytest:**
  ```sh
  uv run pytest
  ```
- **Verificar formato y linter con Ruff:**
  ```sh
  uv run ruff check .
  uv run ruff format .
  ```
