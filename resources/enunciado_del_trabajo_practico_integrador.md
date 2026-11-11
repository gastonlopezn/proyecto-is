# Trabajo Práctico: Diseño de Modelo Conceptual (UML)

## Plataforma Collaborativa de Preguntas y Respuestas (Q\&A)

### Objetivo

Diseñar el modelo de clases conceptual (UML) para una plataforma de preguntas y respuestas destinada a estudiantes universitarios, aplicando principios de diseño orientado a objetos y patrones de diseño para garantizar la extensibilidad y el desacoplamiento del sistema.

---

### Requerimientos Funcionales

1. **Usuarios y Autenticación**

   - El sistema debe permitir el registro de usuarios humanos mediante correo electrónico y contraseña.  
   - Existirán distintos tipos o roles de usuarios (por ejemplo: `Admin` y `Usuario general`).  
2. **Preguntas**

   - Los usuarios pueden realizar preguntas indicando un título, un cuerpo detallado (texto enriquecido) y una fecha de publicación.  
   - Cada pregunta debe estar asociada obligatoriamente a **una sola categoría** (por ejemplo: *Python*, *Flask*, *Base de Datos*).  
   - Cada pregunta puede incluir **múltiples etiquetas** (*tags*).  
3. **Respuestas y Autoría**

   - Una pregunta puede recibir múltiples respuestas.  
   - Cada respuesta cuenta con un cuerpo, una fecha de publicación, un indicador de si fue marcada como "respuesta aceptada" por el autor de la pregunta y la identificación del emisor/autor que la generó.  
   - El autor de una respuesta puede ser tanto un usuario registrado como un agente/sistema de respuesta automática.  
4. **Votaciones (Opcional)**

   - Tanto las preguntas como las respuestas pueden recibir votos positivos o negativos por parte de los usuarios registrados para calcular una puntuación o reputación.  
5. **Agente de Respuestas Automáticas mediante LLM**

   - El sistema debe ser capaz de generar respuestas automáticas asistidas por IA para preguntas que incluyan una etiqueta específica (por ejemplo: `#ia-help`) o que permanezcan sin responder durante un tiempo determinado.

---

### Requisitos de Diseño de Software (Patrones y Arquitectura)

- **Abstracción y Creación de Autoría:** Se debe diseñar una estructura de clases flexible (utilizando **Polimorfismo** y opcionalmente un patrón creacional como **Factory Method**) que abstraiga el concepto de "Autor". Esto debe permitir atribuir las respuestas tanto a usuarios humanos como a agentes de IA de manera homogénea, evitando duplicar lógica o generar acoplamiento rígido en la entidad `Response`.

- **Patrón Strategy:** Para la generación de contenido automático, el diseño en UML debe aplicar el patrón **Strategy**. Esto asegurará que la integración con diferentes proveedores de LLM (*OpenAI*, *Gemini*, *modelos locales*, etc.) sea intercambiable y esté completamente desacoplada de la lógica principal del dominio.

---

### Entregables

- Diagrama de clases completo en notación UML estándar.  
- Justificación breve de la aplicación de los patrones de diseño seleccionados (*Strategy* y *Abstracción/Factory de Autoría*).