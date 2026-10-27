# proyecto-is
Taller Ingenieria de Software I (2026).

# Proyecto Ingeniería de Software I (3385) | 2026

| N.º | Nombre y apellido | DNI |
|:---:|---|:---:|
| 1 | Gastón Nicolás López | 47.463.500 |
| 2 | Juan Manuel Martin | 47.911.017 |
| 3 | Juan Cruz Uva Britos | 47.363.325 |

### 1. Idea del proyecto

La idea de este proyecto nace del sitio web de predicciones *PolyMarket*, donde un usuario realiza una publicación de un posible hecho en la vida real, y otros usuarios compran y venden acciones basadas en la probabilidad de que eso ocurra (o no). Algunos ejemplos pueden ser: ¿Alcanzará Bitcoin los 200.000 dólares antes de finales de 2026?, ¿Quién gana las elecciones de Brasil?, entre otros.

### 2. Justificación de la aplicación del patrón de diseño

1. **Patrón *Strategy* (Comportamiento):**
* **Problema que resuelve:** Nuestro sistema necesita generar contenido de manera automática y verificar fuentes usando distintos proveedores de inteligencia artificial conocidos (`Gemini`, `Claude`, `LocalLLM`), evitando que la clase principal de contexto quede fuertemente conectada a una implementación específica, situación que podria generar problemas.
* **Aplicación en el diseño:** Se implementó una interfaz común `StrategyLLM` que define los contratos operativos (`createQuestion()`, `checkSource()`), permitiendo que la clase `LLM` delegue dinámicamente la ejecución en distintas instancias de strategy de manera simple e intercambiable.