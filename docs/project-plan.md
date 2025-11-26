# Plan de Proyecto: Conversor de Shows Picolo a QLC+

## Objetivo

Este proyecto busca resolver la conversión manual y propensa a errores de archivos de shows de iluminación de mesas Picolo al formato de QLC+. La solución es una aplicación web que automatiza este proceso. Se desarrollará con una arquitectura desacoplada, utilizando un backend en Python con FastAPI para la lógica de conversión y un frontend interactivo en JavaScript (Vue.js/React) para la interfaz de usuario. Todo el sistema será orquestado y desplegado mediante contenedores Docker.

## Hitos y Tareas

### 1. Fase Inicial: Configuración del Entorno

- [ ] Inicializar el repositorio Git.
- [ ] Crear la estructura de directorios (`backend/`, `frontend/`).
- [ ] Configurar el archivo `docker-compose.yml` inicial para los servicios `backend` y `frontend`.
- [ ] Crear un `Dockerfile` base para el servicio de backend (Python).
- [ ] Crear un `Dockerfile` base para el servicio de frontend (Node/Nginx).

### 2. Fase de Desarrollo: Backend (Motor de Conversión)

-   **2.1. Parseo de Fichero Picolo**
    -   [ ] Implementar la lectura y análisis del fichero `.txt`.
    -   [ ] Crear modelos de datos para almacenar la Cue List y los datos de canales.
    -   [ ] Implementar la lógica para identificar el número de canal más alto.
    -   [ ] Implementar la validación del archivo de entrada (tipo, extensión `.txt` y tamaño máximo configurable a través de una **variable de entorno**).
-   **2.2. Lógica de Conversión**
    -   [ ] Implementar la función de conversión de niveles de foco (Picolo a QLC+ 0-255).
    -   [ ] Implementar la función de mapeo de tiempos (`TI`, `TO`, `TW` a `FadeIn`, `FadeOut`, `Hold`).
-   **2.3. Generación de XML (QLC+)**
    -   [ ] Crear la estructura base del documento XML `.qxc`.
    -   [ ] Implementar la generación del Fixture genérico.
    -   [ ] Implementar la generación de las Escenas a partir de los datos parseados.
    -   [ ] Implementar la generación del Chaser que contiene todos los pasos (cues).

### 3. Fase de Desarrollo: API Backend

-   [ ] Configurar la aplicación base de FastAPI.
-   [ ] Crear el endpoint `POST /api/v1/convert`.
-   [ ] Implementar la subida de archivos (`multipart/form-data`).
-   [ ] Integrar el motor de conversión con el endpoint de la API.
-   [ ] Construir la respuesta JSON (`summary`, `fileName`, `fileContent`).
-   [ ] Implementar el manejo de errores y las respuestas JSON correspondientes.

### 4. Fase de Desarrollo: Frontend (Interfaz de Usuario)

-   [ ] Inicializar el proyecto (Vue.js o React).
-   [ ] Diseñar y maquetar la interfaz principal (área de subida, botones, área de resultados).
-   [ ] Implementar el formulario para la subida del fichero.
-   [ ] Implementar validación de archivo en el cliente (extensión `.txt`, tamaño) para feedback inmediato.
-   [ ] Implementar **validación en el servidor del Frontend** (tipo, extensión `.txt`, tamaño) tras la subida del usuario y antes de reenviar al Backend.
-   [ ] Desarrollar el servicio para comunicarse con la API del backend.
-   [ ] Implementar el estado de carga (animación/spinner) durante la conversión.
-   [ ] Implementar la visualización del resumen de la conversión (`cueCount`, `channelCount`).
-   [ ] Implementar el botón de descarga que genera el fichero `.qxc` a partir del `fileContent`.
-   [ ] Implementar la visualización de mensajes de error provenientes de la API.

### 5. Fase de Pruebas

-   **5.1. Pruebas Unitarias (Backend):** Deberán crearse y ejecutarse de forma concurrente con el desarrollo de cada función o componente nuevo para asegurar su correcto funcionamiento desde el inicio.
    -   [ ] Crear pruebas para la conversión de niveles (casos `FF`, `99`, `0`, etc.).
    -   [ ] Crear pruebas para el mapeo de tiempos (casos `Manua`, numérico, alfanumérico).
    -   [ ] Crear pruebas para las funciones clave del parseo.
-   **5.2. Pruebas de Integración (API)**
    -   [ ] Probar el endpoint `/api/v1/convert` con ficheros `.txt` válidos (utilizando los recursos de prueba disponibles).
    -   [ ] Probar el endpoint con ficheros mal formados o inválidos para verificar los errores.

### 6. Fase de Despliegue

-   [ ] Finalizar el `Dockerfile` del backend para producción (con Gunicorn).
-   [ ] Finalizar el `Dockerfile` del frontend para producción (build de assets estáticos y Nginx).
-   [ ] Configurar `docker-compose.yml` para el entorno de producción.
-   [ ] Configurar los volúmenes de Docker para persistir logs.

## Preguntas Clave a Responder

1.  **Manejo de Grandes Archivos:** Este riesgo se mitigará mediante la validación en el backend. El tamaño máximo de archivo será configurable a través de una variable de entorno para prevenir que archivos excesivamente grandes lleguen a procesarse y afecten el rendimiento del navegador.
2.  **Compatibilidad QLC+:** ¿Hay alguna versión específica de QLC+ con la que se deba garantizar la compatibilidad del fichero `.qxc` generado?
