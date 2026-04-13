# **Requisitos Técnicos Finales: Convertidor Picolo a QLC+**

**Versión:** 3.0
**Fecha:** 24 de Mayo de 2024

## 1. Resumen del Proyecto

El objetivo es desarrollar una aplicación que automatice la conversión de archivos de shows de iluminación, generados por la función "Print" de una mesa de control **Picolo**, al formato de archivo (`.qxc`) compatible con el software **QLC+**.

La aplicación constará de dos componentes principales y desacoplados: un **Backend** (motor de conversión) que realiza la lógica de transformación y un **Frontend** (interfaz web) que permite a los usuarios interactuar con el servicio.

## 2. Arquitectura del Sistema

Se implementará una arquitectura de microservicios contenerizada, desacoplando la interfaz de usuario de la lógica de negocio para asegurar la modularidad, escalabilidad y reutilización del motor de conversión.

*   **Contenedor Backend:** Un servicio independiente que expone una API RESTful. Su única responsabilidad es recibir un archivo de texto de Picolo y devolver un archivo XML de QLC+.
*   **Contenedor Frontend:** Una aplicación web en PHP que sirve la interfaz de usuario y se comunica con la API del Backend.
*   **Orquestación:** Se utilizará **Docker Compose** para definir, construir y ejecutar ambos contenedores, gestionando la red interna para su comunicación.

### Diagrama de Arquitectura
```
[Usuario] <--> [Navegador] <--> [Contenedor Frontend (PHP/Apache)]
                                       |
                                       V (Llamada API a http://backend:PORT)
                                       |
                             [Contenedor Backend (Python/Node/etc.)]
```

## 3. Flujo de Conversión Detallado

El proceso de conversión se realizará en un único pase en el backend, siguiendo estos pasos lógicos:

### Paso 1: Pre-análisis del Fichero Picolo

1.  El backend recibe el fichero `.txt` de Picolo.
2.  Realiza una lectura completa del archivo para extraer y almacenar en memoria:
    *   **Datos de la Cue List:** Una lista ordenada de objetos, cada uno conteniendo `CueNum`, `TI` (Time In), `TO` (Time Out), `TW` (Time Wait) y `Text`.
    *   **Datos de Canales por Cue:** Un diccionario o mapa donde la clave es el `CueNum` y el valor es otro mapa de `ChannelNum` a `Nivel`.
    *   **Canal Máximo:** Durante el parseo de los canales, se debe identificar y guardar el número de canal más alto utilizado en todo el show (`max_channel_number`).

### Paso 2: Generación del XML Base y las Escenas

1.  **Crear Estructura XML:** El backend inicia la construcción de un nuevo documento XML con la estructura base de un fichero `.qxc` de QLC+.
2.  **Crear Fixture Genérico:** Se añade un único nodo `<Fixture>` al XML:
    *   **Manufacturer:** `Generic`
    *   **Model:** `Generic`
    *   **Mode:** `"[max_channel_number] Channel"` (El valor se toma del pre-análisis).
    *   **ID:** `0`
    *   **Name:** `Dimmers Picolo`
    *   **Universe:** `0`
    *   **Address:** `0`
    *   **Channels:** `max_channel_number`
3.  **Generar Escenas:** Se itera sobre los datos de canales por cue almacenados. Por cada cue:
    *   Se crea un nodo `<Function Type="Scene">` con un `ID` secuencial (empezando en `0`) y un `Name` formado por `"[CueNum] [CueText]"`.
    *   Se crea un nodo hijo `<FixtureVal ID="0">`.
    *   Se construye la cadena de valores aplicando la **lógica de conversión de niveles** (ver sección 4.2.1).
    *   Se guarda una relación entre el `CueNum` de Picolo (ej: "2.5") y el `ID` de la escena generada (ej: "2").

### Paso 3: Generación del Chaser (Cue List)

1.  Se crea un único nodo `<Function Type="Chaser">` con el siguiente `ID` disponible y un nombre (ej: "Show Convertido").
2.  Se itera sobre la lista ordenada de la Cue List almacenada en memoria.
3.  Por cada cue en la lista, se añade un nodo `<Step>` al Chaser:
    *   **Contenido del Step:** El `ID` de la escena correspondiente (obtenido de la relación guardada en el paso anterior).
    *   **Atributos de Tiempo:** Se calculan los atributos `FadeIn`, `FadeOut` y `Hold` aplicando la **lógica de mapeo de tiempos** (ver sección 4.2.2).
    *   **Atributo `Note`:** Se asigna el `Text` del cue.

## 4. Requisitos del Backend

### 4.1. Funcionalidad Principal
*   **Parseo de Fichero Picolo:** Analizar el formato de texto plano para extraer la Cue List y los niveles de canal de cada cue.
*   **Validación de Entrada de Archivo:** Asegurar que el archivo subido sea de tipo `text/plain` y que su extensión sea `.txt`. Además, el tamaño del archivo debe ser inferior a un límite configurable (ej: 5MB) para evitar problemas de rendimiento o abusos.
*   **Generación de Fichero QLC+:** Construir un fichero XML válido (`.qxc`) siguiendo la estructura y lógica detalladas.

### 4.2. Lógica de Transformación (Reglas de Negocio)

#### 4.2.1. Conversión de Niveles de Focos
*   **Formato de Entrada (Picolo):** String.
    *   Numérico `"0"` a `"99"` (porcentaje).
    *   Especial `"FF"` (100%).
*   **Formato de Salida (QLC+):** Entero decimal (0-255).
*   **Fórmula de Conversión (Pseudocódigo):**
    ```
    if valor_picolo == "FF":
        valor_qlc = 255
    else:
        porcentaje = int(valor_picolo)
        valor_qlc = round((porcentaje / 100.0) * 255)
    ```
*   **Mapeo de Canales:** Los canales en QLC+ son 0-based.
    *   `QLC_Channel_Index = Picolo_Channel_Number - 1`

#### 4.2.2. Mapeo de Tiempos
Las unidades en Picolo son **segundos**, y en QLC+ son **milisegundos**.
*   **Fade In (Entrada):** `FadeIn_ms = float(TI_Picolo) * 1000`.
*   **Fade Out (Salida):** Se aplica lógica de crossfade. El `FadeOut` del paso `N` es el `FadeIn` del paso `N+1`.
    *   `FadeOut_ms(Paso_N) = float(TO_Picolo_del_Cue_Siguiente) * 1000`.
    *   Para el último paso, se usará su propio valor `TO`: `float(TO_Picolo_Ultimo) * 1000`.
*   **Hold (Espera):**
    *   Si `TW` es `"Manua"` -> `Hold_ms = 4294967294`.
    *   Si `TW` es numérico (ej: `"5"`) -> `Hold_ms = float(TW) * 1000`.
    *   Si `TW` es alfanumérico (ej: `"Manua4"`) -> `Hold_ms = int(parte_numerica) * 1000`.

### 4.3. API del Backend
*   **Endpoint:** `POST /api/v1/convert`
*   **Request Body:** `multipart/form-data` con un campo `file` conteniendo el `.txt` de Picolo.
*   **Response (Éxito):**
    *   **Código:** `200 OK`
    *   **Headers:** `Content-Type: application/json`
    *   **Body:** Un objeto JSON con los datos de la conversión.
        ```json
        {
          "summary": {
            "cueCount": 0,
            "channelCount": 0,
            "scenes": [
              { "id": 0, "name": "" }
            ]
          },
          "fileName": "show.qxc",
          "fileContent": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>..."
        }
        ```
*   **Response (Error):** `400 Bad Request` o `500 Internal Server Error` con un body JSON (`{"error": "mensaje descriptivo"}`).

### 4.4. Stack Tecnológico Recomendado
*   **Lenguaje:** **Python**. Es un lenguaje ideal para el parseo de texto y la manipulación de datos, que es el núcleo de la lógica de conversión.
*   **Framework API:** **FastAPI**.
    *   **Rendimiento:** Es extremadamente rápido, comparable a Node.js.
    *   **Facilidad de uso:** Reduce la cantidad de código necesario para crear una API robusta.
    *   **Documentación Automática:** Genera automáticamente una documentación interactiva de la API (con Swagger UI), lo cual es fantástico para probar el endpoint durante el desarrollo.
    *   **Validación de Datos:** Utiliza el tipado de Python para validar automáticamente las peticiones, haciendo la API más segura.

## 5. Requisitos del Frontend

### 5.1. Interfaz y Flujo de Usuario
1.  El usuario ve una página con un formulario para subir un archivo y un botón "Convertir".
2.  Al seleccionar el archivo y hacer clic, se muestra una animación de carga.
3.  La aplicación envía el archivo a la API del backend.
4.  **En caso de éxito:**
    *   La animación de carga desaparece.
    *   Se muestra en pantalla un resumen de la conversión: "Conversión exitosa: Se detectaron **X** cues y **Y** canales."
    *   Opcionalmente, se puede mostrar una tabla con la lista de escenas generadas.
    *   Aparece un botón "Descargar Archivo .qxc". Al hacer clic, el frontend genera y descarga el archivo utilizando los datos recibidos de la API.
5.  **En caso de error:** Se muestra un mensaje de error claro y comprensible.

### 5.2. Tecnologías

El frontend se desarrollará con un stack interactivo para una experiencia de usuario mejorada.

#### 5.2.1. Stack Interactivo Recomendado
*   **Framework:** **Vue.js** o **React**.
*   **Descripción:** Para implementar funcionalidades dinámicas como la previsualización de resultados sin recargar la página, se utilizará un framework de JavaScript moderno. Esto permite crear una Single Page Application (SPA) que ofrece una experiencia de usuario mucho más fluida y rápida.
*   **Servidor:** El frontend será un conjunto de archivos estáticos (HTML, CSS, JS) que pueden ser servidos por un servidor web ligero como **Nginx**.

## 6. Requisitos de Despliegue (Docker)

El proyecto se desplegará utilizando Docker y Docker Compose.

### 6.1. Estructura de Directorios Recomendada
```
/proyecto-conversor/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   └── src/
└── frontend/
    ├── Dockerfile
    └── src/
```

### 6.2. Contenedor Backend
*   **`Dockerfile`:** Definirá una imagen ligera (ej: `python:3.10-slim`) que instale dependencias, copie el código y ejecute un servidor de API (ej: Gunicorn).
*   **Red:** Será accesible dentro de la red de Docker por su nombre de servicio (ej: `backend`).

### 6.3. Contenedor Frontend
*   **`Dockerfile`:** Definirá una imagen de servidor web con PHP (ej: `php:8.1-apache`), copiando el código fuente y asegurando que las extensiones necesarias (ej: `curl`) estén instaladas.
*   **Red:** Se comunicará con el backend a través de su nombre de servicio (ej: `http://backend:5000/api/v1/convert`).

### 6.4. Orquestación (`docker-compose.yml`)
*   Definirá los servicios `backend` y `frontend`.
*   Mapeará el puerto del `frontend` (ej: `80`) a un puerto de la máquina host (ej: `8080`) para el acceso público: `ports: - "8080:80"`.
*   Utilizará volúmenes para el desarrollo local, permitiendo la recarga de código sin reconstruir las imágenes.
*   Definirá volúmenes para persistir los archivos de log generados por ambos servicios.

## 7. Requisitos No Funcionales

### 7.1. Pruebas (Testing)
*   **Pruebas Unitarias (Backend):** Deberán cubrir todas las funciones de lógica de negocio, especialmente:
    *   La función de conversión de niveles, con casos de prueba para `"FF"`, `"99"`, `"50"` y `"0"`.
    *   La función de cálculo de tiempos de `Hold`.
    *   Las funciones de parseo de las diferentes secciones del fichero Picolo.
*   **Pruebas de API/Integración (Backend):** Probar el endpoint `/api/v1/convert` con un fichero válido y verificar que el XML de salida es correcto. Probar con ficheros inválidos para asegurar respuestas de error adecuadas.

### 7.2. Logging
*   Ambos servicios, `frontend` y `backend`, deben generar logs.
*   Los logs deben registrar eventos de éxito (petición recibida, conversión completada) y de error (fichero inválido, error interno).
*   **Importante:** No se deben guardar los ficheros subidos por los usuarios ni los ficheros generados. El logging es solo para telemetría y depuración.

### 7.3. Modularidad
La estricta separación entre el frontend y el backend es un requisito clave para permitir que el motor de conversión sea reutilizado en el futuro por otras aplicaciones (ej: una aplicación de escritorio nativa).