<p align="center">
  <img src="logo.png" width="180" alt="VisorXM">
</p>

<h1 align="center">VisorXM</h1>

<p align="center">
  <b>Consulta, visualiza y descarga información pública de XM de forma sencilla.</b>
</p>

<p align="center">
  Una interfaz amigable para acceder a datos de XM / Sinergox sin necesidad de trabajar directamente con endpoints, códigos de variables o llamadas a la API.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit">
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-0078D6?logo=windows&logoColor=white" alt="Windows">
</p>

---

## ⚡ ¿Qué es VisorXM?

**VisorXM** es una herramienta desarrollada para facilitar la consulta y descarga de información pública del mercado eléctrico colombiano disponible a través de **XM / Sinergox**.

El objetivo es simple:

> **Encontrar el dato → seleccionar el período → consultar → descargar.**

VisorXM oculta gran parte de la complejidad técnica asociada al uso directo de la API y permite trabajar con la información desde una interfaz gráfica sencilla.

Está pensado para estudiantes, investigadores, ingenieros, analistas y cualquier persona que necesite utilizar información de XM sin tener que construir consultas programáticamente.

---

## 🚀 Funcionalidades

- 🔎 Búsqueda de variables disponibles en XM.
- 📂 Organización de información por categorías.
- 📅 Selección sencilla de períodos de consulta.
- ⚙️ Gestión automática de los parámetros técnicos de la API.
- 🔄 División automática de consultas cuando el rango de fechas supera los límites del servicio.
- 📊 Vista previa de los datos obtenidos.
- 📈 Visualización rápida de series de tiempo.
- 🎛️ Filtros sobre la información consultada.
- 📥 Exportación a **Excel**.
- 📄 Exportación a **CSV**.
- 📝 Generación de metadatos de la consulta.
- ♻️ Caché de consultas para evitar solicitudes innecesarias.
- 🛡️ Manejo de errores y reintentos ante fallos temporales de conexión.
- 🖥️ Instalación automática mediante entorno virtual.

---

## 💡 ¿Por qué VisorXM?

XM dispone de una gran cantidad de información pública de enorme utilidad para el análisis del sistema eléctrico colombiano.

Sin embargo, trabajar directamente con las interfaces programáticas puede requerir conocer previamente:

- códigos de variables;
- entidades;
- granularidades;
- estructuras de respuesta;
- límites de consulta;
- procesamiento posterior de los datos.

VisorXM busca convertir ese proceso en una experiencia mucho más directa.

```text
XM / Sinergox
      │
      ▼
   VisorXM
      │
      ├── Buscar información
      ├── Seleccionar período
      ├── Consultar
      ├── Visualizar
      └── Descargar
              │
              ├── Excel
              └── CSV
```

---

# 🖥️ Instalación rápida

VisorXM está preparado para que un usuario en Windows pueda ejecutarlo sin configurar manualmente un entorno de desarrollo.

## Opción recomendada

### 1. Descargar el proyecto

Descarga el repositorio como ZIP:

**Code → Download ZIP**

Luego descomprime completamente el archivo.

### 2. Ejecutar VisorXM

Haz doble clic en:

```text
VisorXM.bat
```

Eso es todo.

---

## 🔧 Primera ejecución

Durante la primera ejecución, VisorXM configura automáticamente el entorno necesario.

El instalador:

1. Busca una instalación compatible de Python.
2. Si Python no está disponible, intenta instalar Python 3.12 mediante `winget`.
3. Crea un entorno virtual local:

```text
.venv
```

4. Actualiza `pip`.
5. Instala las dependencias indicadas en:

```text
requirements.txt
```

6. Verifica el entorno.
7. Inicia VisorXM.
8. Abre automáticamente la aplicación en el navegador.

La primera instalación puede tardar algunos minutos dependiendo de la conexión a Internet.

---

## ▶️ Ejecuciones posteriores

Después de la primera configuración solo debes volver a ejecutar:

```text
VisorXM.bat
```

VisorXM reutilizará el entorno virtual existente y abrirá directamente la aplicación.

No es necesario volver a instalar las dependencias.

---

# 📊 Uso de VisorXM

El flujo principal está diseñado para ser sencillo:

### 1 — Buscar información

Busca la variable o información que necesitas consultar.

Por ejemplo:

```text
Demanda
Generación
Precio de bolsa
Disponibilidad
Aportes
Embalses
```

### 2 — Seleccionar la variable

VisorXM muestra información básica de la variable seleccionada y gestiona internamente los parámetros técnicos necesarios.

### 3 — Seleccionar período

Define:

```text
Fecha inicial
Fecha final
```

### 4 — Consultar

VisorXM realiza las solicitudes necesarias a XM.

Si el rango supera el máximo admitido por una consulta individual, la aplicación divide automáticamente el período y posteriormente consolida los resultados.

### 5 — Revisar y filtrar

Puedes revisar los datos obtenidos antes de descargarlos.

### 6 — Descargar

Los resultados pueden exportarse como:

```text
.xlsx
.csv
```

---

# 📁 Exportación a Excel

Los archivos Excel generados por VisorXM incluyen una hoja principal con la información consultada y una hoja adicional de metadatos.

Ejemplo:

```text
Consulta_VisorXM.xlsx

├── Datos
└── Metadatos
```

Los metadatos permiten conservar información como:

```text
Variable consultada
Código de la variable
Entidad
Fecha inicial
Fecha final
Fecha de consulta
Fuente
```

Esto facilita la trazabilidad de los datos utilizados posteriormente en análisis, informes o investigaciones.

---

# 🗂️ Estructura del proyecto

```text
VisorXM/
│
├── VisorXM.bat
│
├── REINSTALAR_DEPENDENCIAS.bat
│
├── app.py
│
├── Consulta_API_XM.xlsm
│
├── logo.png
│
├── requirements.txt
│
├── README.md
│
├── LEEME_PRIMERO.txt
│
└── scripts/
    └── bootstrap.ps1
```

### `VisorXM.bat`

Archivo principal de inicio de la aplicación.

### `app.py`

Aplicación principal desarrollada con Streamlit.

### `Consulta_API_XM.xlsm`

Catálogo utilizado por VisorXM para organizar y consultar las variables disponibles.

### `requirements.txt`

Dependencias necesarias para ejecutar la aplicación.

### `bootstrap.ps1`

Script encargado de crear el entorno, verificar Python, instalar dependencias y ejecutar la aplicación.

### `REINSTALAR_DEPENDENCIAS.bat`

Permite reconstruir las dependencias si el entorno local presenta algún problema.

---

# 🧰 Tecnologías

VisorXM utiliza principalmente:

```text
Python
Streamlit
Pandas
OpenPyXL
PyDataXM
Requests
aiohttp
```

La aplicación utiliza un entorno virtual independiente para evitar interferir con otras instalaciones de Python existentes en el computador.

---

# 🌐 Requisitos

Para ejecutar VisorXM se recomienda:

```text
Windows 10 o Windows 11
Conexión a Internet
Navegador web moderno
```

No es necesario instalar manualmente las librerías de Python.

En equipos que no tengan Python instalado, VisorXM intentará configurar automáticamente una versión compatible mediante Windows Package Manager (`winget`).

---

# 🛠️ Solución de problemas

Si VisorXM deja de iniciar correctamente, ejecuta:

```text
REINSTALAR_DEPENDENCIAS.bat
```

Esto reconstruirá el entorno de dependencias.

Cuando sea necesario realizar diagnóstico, el proceso de instalación puede generar:

```text
VisorXM_instalacion.log
```

con información técnica sobre el proceso de configuración.

---

# 🗺️ Roadmap

VisorXM continúa en desarrollo.

Algunas funcionalidades previstas para próximas versiones incluyen:

- consultas rápidas especializadas;
- favoritos y consultas recientes;
- búsqueda inteligente de variables;
- descarga de múltiples variables;
- mayor número de visualizaciones;
- indicadores automáticos;
- comparación entre períodos;
- clasificación mejorada de variables;
- procesamiento automático de unidades;
- módulos especializados de demanda, generación, precios e hidrología.

---

# 📡 Fuente de información

VisorXM utiliza información pública disponible a través de los servicios de:

**XM S.A. E.S.P. / Sinergox**

La disponibilidad, estructura y actualización de los datos dependen de los servicios proporcionados por dichas plataformas.

---

# ⚠️ Aviso

**VisorXM es una herramienta independiente.**

No es un producto oficial de XM S.A. E.S.P. ni existe afiliación, patrocinio o respaldo oficial por parte de XM.

La herramienta únicamente busca facilitar el acceso, consulta, procesamiento y descarga de información pública disponible a través de sus servicios.

El usuario es responsable de verificar la información utilizada para análisis, publicaciones, investigaciones o procesos de toma de decisiones.

---

# 👨‍💻 Autor

```text
╭────────────────────────────────────────────╮
│                                            │
│               @queenergia                  │
│                                            │
│     Ing. Juan E. Rodríguez Villada         │
│             VisorXM · 2026                 │
│                                            │
╰────────────────────────────────────────────╯
```

Desarrollado en Colombia 🇨🇴 para facilitar el acceso y análisis de información del sector eléctrico.

---

<p align="center">
  <b>VisorXM</b><br>
  Datos de energía más fáciles de consultar.
</p>
