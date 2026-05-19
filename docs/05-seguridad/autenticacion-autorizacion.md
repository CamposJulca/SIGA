# Autenticación y Autorización

| Campo        | Valor                                                                       |
|--------------|------------------------------------------------------------------------------|
| Versión      | 1.0                                                                          |
| Fecha        | 2026-05-13                                                                   |
| Fuente       | Arquitectura §9 (Seguridad); Documentación Técnica §14                        |
| Responsable  | Seguridad / TI                                                                |
| Estado       | **Borrador — cobertura BAJA**, ver `gaps.md` Top 10 #2                        |

---

> ⚠️ ALERTA DE SEGURIDAD: las fuentes reconocen explícitamente que la configuración por defecto **es insuficiente para producción**. Sin endurecimiento, cualquier cliente con acceso a la red interna puede invocar todos los endpoints. Esta sección documenta el estado actual y deja PENDIENTE el modelo objetivo.

## 1. Estado actual (lo que está implementado)

| Superficie         | Estado                                                                                      |
|--------------------|---------------------------------------------------------------------------------------------|
| Autenticación DRF   | Configurada con `SessionAuthentication` y `BasicAuthentication`.                            |
| Permisos por defecto | `AllowAny`. Cualquiera con acceso a la red puede invocar todos los endpoints.               |
| Sesiones           | Cookie de sesión Django estándar; sólo aplica si el usuario realmente se autentica vía admin. |
| Admin Django       | Disponible en `/admin/`. Requiere superusuario creado vía `createsuperuser`.                 |

### Autoría operativa

`UploadView` reconoce dos formas de capturar el `usuario_carga`:

1. Si hay una sesión autenticada, se usa el `username` del request.
2. Si no, se acepta el campo `usuario` del formulario; si no se envía, se registra `anonimo`.

Esta es **trazabilidad funcional**, no autenticación criptográfica.

## 2. Recomendaciones que sí están en las fuentes

De `siga/ARQUITECTURA_SOFTWARE.md` §9:

- Cambiar permisos por defecto a **autenticación obligatoria** si SIGA queda expuesto fuera de red controlada.
- Limitar tamaño de subida en proxy / webserver.
- Validar extensión y MIME de archivos cargados si se requiere hardening.
- Proteger `storage/landing` y `prepagada.db` con backups y permisos del sistema.

## 3. Modelo objetivo (a definir)

> ⚠️ PENDIENTE: el esquema productivo debe ser definido por el equipo de seguridad antes del despliegue a producción.

### Preguntas a resolver

| Decisión                                       | Opciones tentativas                                                                |
|------------------------------------------------|-------------------------------------------------------------------------------------|
| ¿SSO corporativo o local?                       | OIDC / SAML / cuentas locales Django.                                                |
| ¿Qué autoridad de identidad?                    | Azure AD / Google Workspace / Keycloak / `PENDIENTE`.                                |
| ¿Roles esperados?                               | Mínimo: Analista, Responsable de prepagada, Contabilidad, Tributaria, Admin.          |
| ¿Permisos por endpoint?                         | Granularidad endpoint vs módulo.                                                      |
| ¿Tokens para clientes no humanos?               | DRF TokenAuth, JWT o API Keys de Django.                                              |
| ¿MFA?                                            | Obligatorio para admin; opcional para usuarios.                                       |
| ¿Auditoría de acciones críticas?                | Mantener log inmutable (creación/edición de política, cálculo de planilla, borrado de pensionados). |
| ¿Aislamiento red?                                | Sólo accesible desde VPN/Intranet o expuesto con WAF.                                  |

### Modelo de roles propuesto (esqueleto)

| Rol                         | Permisos esperados                                                                                   |
|-----------------------------|-------------------------------------------------------------------------------------------------------|
| **Analista de Gestión Humana** | `POST /upload/`, `GET` de archivos, beneficios, novedades, dashboard.                                  |
| **Responsable de prepagada**    | Todo lo de Analista + CRUD de política, pensionados, auxilio externo + cálculo de planilla.            |
| **Contabilidad**                | `GET` de planillas, causación, exportaciones. Sin escritura.                                            |
| **Tributaria**                  | `GET` de planillas y apoyo gravable.                                                                    |
| **Admin Django**                | Acceso completo.                                                                                         |
| **Cliente sistema (portal)**    | Token o sesión segura para invocar la API en nombre de un usuario.                                       |

## 4. Riesgos derivados del estado actual

| Riesgo                                                  | Severidad sin mitigar                                            |
|----------------------------------------------------------|-------------------------------------------------------------------|
| Cualquier cliente con red invoca `POST /upload/`        | Alta — puede subir Excel y mezclar/corromper datos.                |
| Cualquier cliente con red invoca `POST /planilla/calcular/` | Alta — genera planillas no autorizadas.                            |
| Sin autoría real de quien crea/edita políticas           | Alta — afecta confianza tributaria/contable.                       |
| `usuario_carga` puede ser inyectado en el form           | Media — útil para auditar pero no certifica identidad.             |
| Admin Django en `/admin/` sin segundo factor              | Media — credenciales únicas son únicos punto de control.            |

## 5. Plan mínimo de endurecimiento sugerido

> ⚠️ PENDIENTE: plan formal a redactar por seguridad.

1. Habilitar **autenticación obligatoria** en DRF (cambiar `DEFAULT_PERMISSION_CLASSES` a `IsAuthenticated`).
2. Definir el proveedor de identidad y migrar al esquema productivo.
3. Implementar roles y permisos por vista (DRF `permission_classes`).
4. Forzar `DEBUG=0` y `SECRET_KEY` único en producción.
5. Forzar TLS y proxy reverso.
6. Auditoría inmutable de operaciones críticas (política, planilla, pensionados).
7. MFA para admin y para Responsable de prepagada.

---

**Fuente:** `siga/ARQUITECTURA_SOFTWARE.md` (§9 Seguridad), `siga/DOCUMENTACION_TECNICA.md` (§14 Consideraciones).
