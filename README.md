# 📡CRM de Ventas B2B con Analítica e Inteligencia Artificial | Somos Telser

> Plataforma web desarrollada para digitalizar, centralizar y optimizar la gestión comercial de ventas B2B en el sector de telecomunicaciones mediante analítica de datos, automatización de procesos y visualización interactiva.

---

## 1. 📊 Información General del Sistema
* Nombre del modelo: Proyecto: CRM de Ventas B2B con Analítica de Datos e Inteligencia Artificial
* Tipo de sistema: CRM Web con arquitectura orientada a SaaS
* Autor: Kely Jhojana Hincapié Zapata
* Versión: v1.0
* Lenguaje: Python
* Dataset utilizado: `crm_sistema_maestro.csv` (Gestión centralizada de contratos B2B)
* Despliegue: Streamlit Community Cloud
* Demo en vivo: [Enlace a tu aplicación aquí](#)

## 2. 🎯 Resumen Ejecutivo
El sistema permite a los asesores registrar y actualizar contratos, mientras que el administrador supervisa el rendimiento global. Integra analítica visual interactiva (Dashboards) y un asistente de ofertas automatizado, optimizando el seguimiento comercial, reduciendo errores manuales y facilitando la toma de decisiones basada en datos.

## 3. 📈 Objetivo
Desarrollar un CRM web para la gestión integral de ventas B2B en el sector de telecomunicaciones, que centralice el registro y seguimiento de contratos, automatice procesos comerciales y proporcione analítica de datos en tiempo real mediante indicadores y dashboards interactivos. La plataforma busca mejorar la productividad de los asesores, facilitar la supervisión administrativa y apoyar la toma de decisiones basada en datos.

## 4. 💡 Problema y Contexto
### 4.1. Problema Identificado
En muchas organizaciones del sector telecomunicaciones, la gestión comercial continúa realizándose mediante hojas de cálculo y procesos manuales, lo que ocasiona:
> Falta de trazabilidad de los contratos.
> Dificultad para realizar seguimiento comercial.
> Información dispersa entre diferentes asesores.
> Escasa visibilidad del desempeño comercial.
> Retrasos en la generación de reportes gerenciales.

Este proyecto centraliza toda la operación en una única plataforma web.

### 4.2 Justificación del Uso de Analítica e IA
La implementación de analítica de datos en tiempo real permite transformar registros planos en indicadores de rendimiento (KPIs) procesables. Esto, sumado al asistente de búsqueda y automatización de flujos, permite escalar la operación de forma inteligente frente a sistemas manuales tradicionales.

## 5. 🤖 Analítica de Datos e Inteligencia Artificial
La plataforma incorpora herramientas analíticas que permiten transformar la información comercial en indicadores útiles para la toma de decisiones.

Entre sus funcionalidades se encuentran:

> Dashboard interactivo de indicadores (KPIs).
> Análisis de ventas por estado.
> Seguimiento del desempeño por asesor.
> Comparativo entre portafolios Fijo y Móvil.
> Detección de oportunidades de cross-selling.
> Asistente inteligente de búsqueda de ofertas y planes comerciales.

## 6. ⚙️ Arquitectura del Sistema
Registro de ventas
        │
        ▼
Procesamiento de datos (Pandas)
        │
        ▼
Motor de negocio
        │
        ├── Dashboard Analítico (Plotly)
        ├── Gestión CRM
        ├── Reportes
        └── Notificaciones Telegram

## 7. 🗂️ Datos y Variables
> Estado del contrato
> Portafolio (Fijo / Móvil)
> Tipo de servicio
> Plan contratado
> Cantidad de líneas
> Valor del contrato
> Asesor responsable
> Departamento
> Municipio
> Cliente
> Representante legal
> Fecha de seguimiento

## 8. 🛠️ Tecnologías
> Frontend y Backend: Streamlit y Python
> Procesamiento de Datos:Pandas
> Visualización Analítica: Plotly Express / Graph Objects
> Alertas y Notificaciones: Integración con API REST de Telegram
> Despliegue: Streamlit Community Cloud
> CSV como almacenamiento de datos, en preparación para proximo almacemiento es SQlite

## 9 🚀 Funcionalidades
> Inicio de sesión por roles.
> Gestión independiente para Administrador y Asesor.
> Registro de contratos B2B.
> Actualización del estado comercial.
> Seguimiento de clientes.
> Calculadora automática de planes móviles.
> Consulta rápida de ofertas.
> Dashboard gerencial.
> Exportación de información en CSV.
> Notificaciones automáticas mediante Telegram.

## 10. 📈 Valor generado
La plataforma permite:
> Centralizar la gestión comercial.
> Reducir tiempos de registro y seguimiento.
> Minimizar errores manuales.
> Facilitar la supervisión de la operación.
> Obtener indicadores en tiempo real.
> Mejorar la toma de decisiones basada en datos.

## 11. 🔒 Seguridad
El sistema implementa autenticación mediante roles de usuario (Administrador y Asesor), restringiendo el acceso a la información según el perfil autorizado y protegiendo la información comercial.

## 12 ⚖️ Ética, Privacidad y Uso Responsable
Este proyecto fue desarrollado siguiendo principios de uso responsable de la información y buenas prácticas en el tratamiento de datos comerciales.

> Control de acceso: La plataforma implementa autenticación basada en roles (Administrador y Asesor), limitando el acceso a la información según los permisos asignados.
Confidencialidad: Los datos de clientes y contratos se utilizan exclusivamente para la gestión comercial y el seguimiento de ventas.
> Protección de la información: El sistema restringe la visualización de información sensible y evita la exposición de indicadores globales a usuarios no autorizados.
> Analítica responsable: Los indicadores y visualizaciones apoyan la toma de decisiones comerciales sin generar decisiones automatizadas sobre los clientes.
> Escalabilidad en seguridad: La arquitectura está preparada para incorporar mecanismos adicionales de protección, como bases de datos seguras, cifrado de credenciales y almacenamiento robusto en futuras versiones.

## 13. Manual de uso
1. Inicio de sesión
Ingresar con las credenciales asignadas. El sistema habilita automáticamente las funcionalidades según el rol.

2. Registro de ventas
Registrar la información del cliente, seleccionar el portafolio, el plan comercial y guardar el contrato.

3. Seguimiento
Actualizar el estado del contrato, registrar observaciones y enviar automáticamente la notificación mediante Telegram.

4. Dashboard
El administrador puede consultar indicadores, analizar el desempeño comercial, aplicar filtros y exportar la información.

📌 Próximas mejoras
> Migración de CSV a SQLite/PostgreSQL.
> Gestión documental integrada.
> Agenda comercial con recordatorios.
> Predicción de probabilidad de cierre mediante Machine Learning.
> Predicción de riesgo de cancelación.
> Integración con modelos de Inteligencia Artificial para asistencia comercial.
