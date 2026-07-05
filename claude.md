# CLAUDE.md — Fracdrop

Guía para trabajar en este proyecto. Lee también `docs/ESPECIFICACIONES.md` (fuente de verdad completa).

## Qué es Fracdrop

App web **multiusuario** (**fracdrop.app**) que clasifica adjuntos de correos de Gmail y los sube a **Dropbox**.

**Principio central (no romper nunca):**
- La app **SOLO lee** de las etiquetas de Gmail que el usuario marca como vigiladas.
- Los adjuntos (facturas / albaranes) se suben a una **carpeta de Dropbox** según **reglas** definidas por el usuario (normalmente por remitente).
- La app **NUNCA** mueve, borra ni crea etiquetas ni correos en Gmail. Gmail es solo lectura.
- Toda la lógica de procesamiento (leer Gmail, aplicar reglas, subir a Dropbox) vive en el **backend**. N8N solo dispara.

## Altas: solo por invitación

- **No hay registro abierto.**
- Existe un admin semilla (`admin@fracdrop.app`) creado en el primer arranque desde `ADMIN_EMAIL` / `ADMIN_PASSWORD`.
- El admin da de alta gente **enviando un enlace de invitación** por email. Cada persona (ej. Rufo) se registra ella misma con ese enlace (`/register?token=...`).
- Token de un solo uso, con caducidad (`INVITATION_EXPIRE_DAYS`). El email queda fijado por la invitación. `POST /api/auth/register` exige token válido o devuelve 403.

## Stack

- Backend: **FastAPI** + Python 3.11
- Frontend: **React 19 + Vite + TypeScript + TailwindCSS**
- BD relacional: **MariaDB 10.6** (usuarios, invitaciones, etiquetas, reglas, carpetas, logs)
- BD NoSQL: **MongoDB 7.0** (metadatos de adjuntos, preferencias)
- Cache: **Redis 7.0**
- Automatización: **N8N** (disparador programado)
- Envío de emails de invitación: **SMTP** (config en `.env`)
- Todo en **Docker Compose**

## Arrancar

```bash
cp .env.example .env      # rellenar secretos (incl. ADMIN_*, SMTP_*, APP_PUBLIC_URL)
docker-compose build
docker-compose up -d
# backend  → http://localhost:8000  (docs en /docs)
# frontend → http://localhost:5173
# n8n      → http://localhost:5678
```

## Modelo de datos (resumen)

En MariaDB, tablas clave:
- `users` — credenciales **encriptadas** (Gmail App Password, Dropbox Access Token) + `role` (admin/user).
- `invitations` — email, token único, status (pending/accepted/revoked/expired), expires_at, invited_by.
- `gmail_labels` — etiquetas que la app vigila (solo lectura).
- `folders` — carpetas de **Dropbox** destino (ruta + doc_type).
- `rules` — condición (`source_label_id` + `from_email` / `subject_contains`) → `dropbox_folder_id`. Con `doc_type` (factura/albaran) y `priority`.
- `email_logs` — historial: `procesado` / `sin_regla` / `error`.
- `credential_logs` — auditoría de credenciales.

Detalle completo de columnas en `docs/ESPECIFICACIONES.md` §7.

## Flujo de procesamiento

1. N8N llama cada X min a `POST /api/emails/process`.
2. El backend recorre las etiquetas vigiladas del usuario.
3. Por cada correo con adjunto → `RuleEngine` busca la primera regla que coincide (por prioridad).
4. Si coincide: descarga adjuntos vía Gmail API → sube a la carpeta Dropbox de la regla → registra `procesado`.
5. Si no coincide: registra `sin_regla`. No se toca el correo.

## Convenciones

- **Idioma del dominio**: usar `factura` y `albaran` (no "invoice"/"baran"). "Albaranes" = albaranes de proveedor (ej. Bongrup).
- **Credenciales**: encriptar SIEMPRE con Fernet antes de guardar. El frontend nunca recibe la credencial en claro, solo el estado (`connected` true/false).
- **Auth**: JWT para la app (expira 30 min). Header `Authorization: Bearer <token>` en todo `/api/` salvo `/api/auth/*` y `GET /api/auth/invite/{token}`.
- **Endpoints**: agrupados por router en `backend/app/api/routes/` (auth, users, invitations, labels, rules, folders, emails, integrations).
- **El motor de reglas es único**: vive en `backend/app/services/rule_engine.py`. No dupliques lógica de clasificación en N8N ni en el frontend.

## Cómo pedir tareas (orden sugerido)

Implementar por fases, referenciando secciones de la spec:
1. Estructura Docker + `.env` (spec §5, §6).
2. Modelos SQLAlchemy + MongoDB (spec §7).
3. Auth + admin semilla + invitaciones + registro por token (spec §8.1, §8.2, §9).
4. Encriptación de credenciales y perfil (spec §8.3, §13).
5. Endpoints de etiquetas y reglas (spec §8.4, §8.5).
6. Servicios Gmail / Dropbox + RuleEngine (spec §11).
7. Endpoint de procesado + workflow N8N (spec §10).
8. Frontend: Login/Register → Perfil → Etiquetas → Carpetas → Reglas → Logs → Users/Invitaciones (spec §12).

## Cosas que NO hacer

- No abrir el registro: toda alta pasa por invitación con token válido.
- No permitir cambiar el email en el formulario de registro (viene fijado por la invitación).
- No mover ni etiquetar correos en Gmail.
- No exponer credenciales al frontend.
- No poner la lógica de clasificación en N8N.
- No usar "invoice"/"baran" en el código; usar `factura`/`albaran`.
- No inventar campos fuera de los definidos en la spec sin marcarlo.