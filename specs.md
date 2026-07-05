# Fracdrop — Especificaciones Técnicas

App web (**fracdrop.app**) que clasifica adjuntos de correos de Gmail y los envía a carpetas de Dropbox.

## 1. DESCRIPCIÓN GENERAL

Aplicación web que clasifica adjuntos de correos de Gmail y los envía a carpetas de Dropbox.

**Funcionamiento**:
1. El usuario selecciona qué **etiquetas de Gmail** quiere que la app vigile.
2. La app SOLO mira los correos dentro de esas etiquetas.
3. El usuario define **reglas** (ej: "si el remitente es proveedor@x.com → carpeta Dropbox A").
4. La app aplica las reglas y sube los adjuntos (facturas/albaranes) a la **carpeta de Dropbox** seleccionada en cada regla.

**Ejemplo**:
```
Correo en etiqueta "Facturas" con remitente "proveedor@ejemplo.com"
   ↓ (regla: este remitente → /Empresa/Facturas/Enero2026)
El adjunto PDF se sube a Dropbox en /Empresa/Facturas/Enero2026
```

La app NO mueve correos entre etiquetas de Gmail ni crea etiquetas. El usuario gestiona sus etiquetas/filtros directamente en Gmail; la app solo lee de las que él indique y enruta los adjuntos a Dropbox.

- **Sistema multiusuario** con autenticación.
- **Alta por invitación**: el admin invita por email; cada persona se da de alta ella misma con un enlace.
- **Automatización mediante N8N**.
- **Almacenamiento distribuido** (MariaDB, MongoDB, Redis).

---

## 2. STACK TÉCNICO

```
Frontend:        React 19 + Vite + TypeScript + TailwindCSS
Backend:         FastAPI + Python 3.11
BD Relacional:   MariaDB 10.6
BD NoSQL:        MongoDB 7.0
Cache:           Redis 7.0
Automatización:  N8N 1.x
Contenedor:      Docker + Docker Compose
Autenticación:   JWT (login app) + credenciales de servicio (Gmail App Password / Dropbox Token)
```

---

## 3. ARQUITECTURA GENERAL

```
┌─────────────────────────────────────────────────────────────┐
│                     USUARIO FINAL                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼───┐      ┌───▼────┐   ┌───▼────┐
    │React  │      │ N8N    │   │ Admin  │
    │Vite TS│      │Workflows│  │Panel   │
    └───┬───┘      └───┬────┘   └────────┘
        │             │
        └──────┬──────┘
               │
        ┌──────▼─────┐
        │  FastAPI   │
        │  Backend   │
        │ (Port 8000)│
        └──────┬─────┘
               │
    ┌──────────┼──────────┬──────────────┐
    │          │          │              │
┌───▼──┐  ┌───▼───┐  ┌───▼───┐   ┌──────▼──┐
│Maria │  │MongoDB│  │ Redis │   │ Gmail   │
│  DB  │  │       │  │       │   │ Dropbox │
└──────┘  └───────┘  └───────┘   └─────────┘
```

Flujo de datos: N8N (o un job del backend) detecta correos nuevos en las etiquetas vigiladas → pide al backend que los evalúe contra las reglas → el backend descarga los adjuntos vía Gmail API y los sube a la carpeta de Dropbox correspondiente → registra el resultado en BD.

---

## 4. ESTRUCTURA DE CARPETAS

```
proyecto-clasificador-correos/
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── redis_client.py
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── invitations.py
│   │   │   │   ├── labels.py
│   │   │   │   ├── rules.py
│   │   │   │   ├── folders.py
│   │   │   │   ├── emails.py
│   │   │   │   └── integrations.py
│   │   │   └── middleware.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── invitation.py
│   │   │   ├── gmail_label.py
│   │   │   ├── rule.py
│   │   │   ├── folder.py
│   │   │   ├── email_log.py
│   │   │   └── credential_log.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── invitation.py
│   │   │   ├── label.py
│   │   │   ├── rule.py
│   │   │   ├── folder.py
│   │   │   └── email.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── invitation_service.py
│   │   │   ├── email_service.py     (envío SMTP de invitaciones)
│   │   │   ├── gmail_service.py
│   │   │   ├── dropbox_service.py
│   │   │   ├── rule_engine.py
│   │   │   └── n8n_service.py
│   │   └── utils/
│   │       ├── security.py
│   │       ├── validators.py
│   │       └── logger.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── vite-env.d.ts
│   │   ├── pages/
│   │   │   ├── Login.tsx             (Login)
│   │   │   ├── Register.tsx          (Alta con token de invitación)
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Labels.tsx          (Seleccionar etiquetas a vigilar)
│   │   │   ├── Rules.tsx           (Reglas: condición → carpeta Dropbox)
│   │   │   ├── Folders.tsx         (Carpetas de Dropbox)
│   │   │   ├── EmailLogs.tsx       (Historial de procesados)
│   │   │   ├── Profile.tsx         (Credenciales Gmail/Dropbox)
│   │   │   ├── Users.tsx           (Admin: usuarios + invitaciones)
│   │   │   └── Settings.tsx
│   │   ├── components/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── LabelSelector.tsx
│   │   │   ├── RuleForm.tsx
│   │   │   ├── DropboxFolderPicker.tsx
│   │   │   ├── EmailTable.tsx
│   │   │   ├── CredentialInput.tsx
│   │   │   └── Modals/
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useApi.ts
│   │   │   ├── useLabels.ts
│   │   │   ├── useRules.ts
│   │   │   └── useCredentials.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   └── credentials.ts
│   │   ├── types/
│   │   │   ├── user.ts
│   │   │   ├── label.ts
│   │   │   ├── rule.ts
│   │   │   ├── folder.ts
│   │   │   ├── email.ts
│   │   │   └── credential.ts
│   │   ├── styles/
│   │   │   └── globals.css
│   │   └── utils/
│   │       └── validators.ts
│
├── n8n-workflows/
│   └── process-labeled-emails.json
│
└── README.md
```

---

## 5. DOCKER COMPOSE

```yaml
version: '3.9'

services:
  mariadb:
    image: mariadb:10.6
    container_name: mariadb-correos
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mariadb_data:/var/lib/mysql
    networks:
      - correos-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  mongodb:
    image: mongo:7.0
    container_name: mongodb-correos
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
      MONGO_INITDB_DATABASE: ${MONGO_DATABASE}
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    networks:
      - correos-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      timeout: 20s
      retries: 10

  redis:
    image: redis:7-alpine
    container_name: redis-correos
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - correos-network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      timeout: 20s
      retries: 10

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: fastapi-correos
    environment:
      - DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mariadb:3306/${MYSQL_DATABASE}
      - MONGODB_URL=mongodb://${MONGO_USER}:${MONGO_PASSWORD}@mongodb:27017/${MONGO_DATABASE}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
      - SECRET_KEY=${SECRET_KEY}
      - ALGORITHM=HS256
      - ACCESS_TOKEN_EXPIRE_MINUTES=30
      - ENCRYPTION_KEY=${ENCRYPTION_KEY}
    ports:
      - "8000:8000"
    depends_on:
      mariadb:
        condition: service_healthy
      mongodb:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    networks:
      - correos-network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: react-correos
    environment:
      - VITE_API_URL=http://localhost:8000
    ports:
      - "5173:5173"
    depends_on:
      - backend
    volumes:
      - ./frontend/src:/app/src
    networks:
      - correos-network
    command: npm run dev

  n8n:
    image: n8nio/n8n
    container_name: n8n-correos
    environment:
      - DB_TYPE=mysql
      - DB_MYSQL_HOST=mariadb
      - DB_MYSQL_PORT=3306
      - DB_MYSQL_DATABASE=${N8N_DATABASE}
      - DB_MYSQL_USER=${MYSQL_USER}
      - DB_MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=0.0.0.0
      - N8N_PORT=5678
      - GENERIC_TIMEZONE=${TIMEZONE}
    ports:
      - "5678:5678"
    depends_on:
      - mariadb
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n-workflows:/workflows
    networks:
      - correos-network
    command: n8n start

volumes:
  mariadb_data:
  mongodb_data:
  redis_data:
  n8n_data:

networks:
  correos-network:
    driver: bridge
```

---

## 6. VARIABLES DE ENTORNO (.env)

```env
# MYSQL
MYSQL_ROOT_PASSWORD=root_secure_password_123
MYSQL_DATABASE=clasificador_correos
MYSQL_USER=correos_user
MYSQL_PASSWORD=correos_password_secure

# MONGODB
MONGO_USER=mongo_admin
MONGO_PASSWORD=mongo_password_secure
MONGO_DATABASE=clasificador_correos

# REDIS
REDIS_PASSWORD=redis_password_secure

# BACKEND
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Encriptación de credenciales (clave Fernet, 32 bytes base64)
ENCRYPTION_KEY=your-fernet-encryption-key

# Admin inicial (se crea en el primer arranque si no existe)
ADMIN_EMAIL=admin@fracdrop.app
ADMIN_PASSWORD=change_this_on_first_login

# URL pública de la app (para construir los enlaces de invitación)
APP_PUBLIC_URL=https://fracdrop.app

# SMTP para enviar los emails de invitación
SMTP_HOST=smtp.tuservidor.com
SMTP_PORT=587
SMTP_USER=no-reply@fracdrop.app
SMTP_PASSWORD=smtp_password_secure
SMTP_FROM=Fracdrop <no-reply@fracdrop.app>

# Caducidad de la invitación (días)
INVITATION_EXPIRE_DAYS=7

# N8N
N8N_USER=admin
N8N_PASSWORD=n8n_password_secure
N8N_DATABASE=n8n_db

# TIMEZONE
TIMEZONE=Europe/Madrid

# FRONTEND
VITE_API_URL=http://localhost:8000
```

---

## 7. MODELOS DE BASE DE DATOS

### 7.1 MariaDB (SQLAlchemy)

```python
# user.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String(20), default="user")   # 'admin' | 'user'

    # Credenciales Gmail (guardadas en el perfil, encriptadas)
    gmail_app_password = Column(String(500), nullable=True)   # Encriptado
    gmail_user_email = Column(String(255), nullable=True)
    gmail_connected = Column(Boolean, default=False)
    gmail_connected_at = Column(DateTime, nullable=True)
    gmail_last_tested = Column(DateTime, nullable=True)
    gmail_test_status = Column(String(50), nullable=True)     # 'success' | 'failed'

    # Credenciales Dropbox (guardadas en el perfil, encriptadas)
    dropbox_access_token = Column(String(500), nullable=True) # Encriptado
    dropbox_connected = Column(Boolean, default=False)
    dropbox_connected_at = Column(DateTime, nullable=True)
    dropbox_last_tested = Column(DateTime, nullable=True)
    dropbox_test_status = Column(String(50), nullable=True)   # 'success' | 'failed'

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    gmail_labels = relationship("GmailLabel", back_populates="user")
    rules = relationship("Rule", back_populates="user")
    folders = relationship("Folder", back_populates="user")
    email_logs = relationship("EmailLog", back_populates="user")
    credential_logs = relationship("CredentialLog", back_populates="user")


# invitation.py — Invitaciones para alta de usuarios
class Invitation(Base):
    __tablename__ = "invitations"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), index=True)          # A quién se invita
    token = Column(String(255), unique=True, index=True)  # Token único del enlace
    role = Column(String(20), default="user")        # Rol que tendrá al aceptar
    invited_by = Column(Integer, ForeignKey("users.id"))  # Admin que invita
    status = Column(String(20), default="pending")   # 'pending' | 'accepted' | 'revoked' | 'expired'
    expires_at = Column(DateTime)                    # Caduca (ej: 7 días)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    inviter = relationship("User", foreign_keys=[invited_by])


# gmail_label.py — Etiquetas de Gmail que la app vigila (solo lectura)
class GmailLabel(Base):
    __tablename__ = "gmail_labels"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gmail_label_id = Column(String(255), index=True)   # ID real de la etiqueta en Gmail
    gmail_label_name = Column(String(255))             # Ej: "Facturas", "Albaranes"
    is_active = Column(Boolean, default=True)          # Si la app la vigila o no
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="gmail_labels")


# folder.py — Carpetas de Dropbox donde se guardan los adjuntos
class Folder(Base):
    __tablename__ = "folders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))                # Nombre amigable (ej: "Facturas Enero 2026")
    dropbox_path = Column(String(500))        # Ruta en Dropbox (ej: /Empresa/Facturas/Enero2026)
    doc_type = Column(String(50))             # 'factura' | 'albaran' | 'otros'
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="folders")


# rule.py — Regla: condición (etiqueta + remitente/asunto) → carpeta Dropbox
class Rule(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255), index=True)
    doc_type = Column(String(50))             # 'factura' | 'albaran'

    # Condiciones (qué correos coinciden)
    source_label_id = Column(Integer, ForeignKey("gmail_labels.id"))  # En qué etiqueta busca
    from_email = Column(String(255), nullable=True)        # Remitente (ej: proveedor@x.com)
    subject_contains = Column(String(255), nullable=True)  # Texto que debe contener el asunto
    has_attachment = Column(Boolean, default=True)         # Requiere adjunto

    # Destino: carpeta de Dropbox
    dropbox_folder_id = Column(Integer, ForeignKey("folders.id"))

    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)     # Orden de evaluación (menor = antes)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="rules")
    source_label = relationship("GmailLabel")
    dropbox_folder = relationship("Folder")


# email_log.py — Historial de cada correo procesado
class EmailLog(Base):
    __tablename__ = "email_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    gmail_message_id = Column(String(255), unique=True, index=True)
    from_email = Column(String(255))
    subject = Column(String(500))
    source_label = Column(String(255))        # Etiqueta de Gmail donde estaba el correo
    doc_type = Column(String(50))             # 'factura' | 'albaran' | 'ignorado'
    rule_applied_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    status = Column(String(50))               # 'procesado' | 'sin_regla' | 'error'
    error_message = Column(Text, nullable=True)
    dropbox_folder_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    dropbox_file_path = Column(String(500), nullable=True)  # Ruta final en Dropbox
    processed_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="email_logs")


# credential_log.py — Auditoría de credenciales
class CredentialLog(Base):
    __tablename__ = "credential_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    service = Column(String(50))              # 'gmail' | 'dropbox'
    action = Column(String(50))              # 'added' | 'updated' | 'removed' | 'tested'
    test_result = Column(String(50), nullable=True)  # 'success' | 'failed'
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="credential_logs")
```

### 7.2 MongoDB (PyMongo)

```javascript
// Metadatos de adjuntos subidos a Dropbox
db.createCollection("email_attachments", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      properties: {
        user_id: { bsonType: "int" },
        gmail_message_id: { bsonType: "string" },
        attachments: {
          bsonType: "array",
          items: {
            bsonType: "object",
            properties: {
              filename: { bsonType: "string" },
              mime_type: { bsonType: "string" },
              size: { bsonType: "int" },
              dropbox_path: { bsonType: "string" }
            }
          }
        },
        created_at: { bsonType: "date" }
      }
    }
  }
})

// Preferencias de usuario
db.createCollection("user_preferences")
```

---

## 8. ENDPOINTS API (FastAPI)

### 8.1 Autenticación

```
POST   /api/auth/login              - Login (devuelve JWT)
POST   /api/auth/refresh            - Refrescar token
POST   /api/auth/logout             - Logout
GET    /api/auth/invite/{token}     - (Público) Validar token de invitación
POST   /api/auth/register           - (Público) Alta con token de invitación
```

> No hay registro abierto: `POST /api/auth/register` exige un `token` de invitación válido. Sin invitación no se puede crear cuenta.

### 8.2 Invitaciones (solo admin)

```
GET    /api/invitations             - Listar invitaciones enviadas
POST   /api/invitations             - Crear invitación y enviar email con el enlace
DELETE /api/invitations/{id}        - Revocar invitación pendiente
POST   /api/invitations/{id}/resend - Reenviar el email de invitación
```

### 8.3 Usuarios y Perfil (credenciales)

```
GET    /api/users/me                          - Datos del usuario actual
PUT    /api/users/me                          - Actualizar perfil
GET    /api/users/me/credentials              - Estado de credenciales
PUT    /api/users/me/credentials/gmail        - Guardar/Actualizar Gmail App Password
PUT    /api/users/me/credentials/dropbox      - Guardar/Actualizar Dropbox Access Token
POST   /api/users/me/credentials/test/gmail   - Probar conexión Gmail
POST   /api/users/me/credentials/test/dropbox - Probar conexión Dropbox
DELETE /api/users/me/credentials/gmail        - Eliminar credencial Gmail
DELETE /api/users/me/credentials/dropbox      - Eliminar credencial Dropbox
GET    /api/users                             - Listar usuarios (admin)
PUT    /api/users/{id}                        - Actualizar usuario (admin): activar/desactivar, rol
DELETE /api/users/{id}                        - Eliminar usuario (admin)
```

> El admin ya NO crea usuarios con contraseña a mano: da de alta gente vía invitación (§8.2). El endpoint `PUT /api/users/{id}` sirve para gestionar los ya existentes.

### 8.4 Etiquetas de Gmail (que la app vigila)

```
POST   /api/labels/gmail/sync       - Traer las etiquetas reales de la cuenta de Gmail
GET    /api/labels/gmail/available  - Listar todas las etiquetas de Gmail del usuario
GET    /api/labels                  - Listar etiquetas que la app vigila
POST   /api/labels                  - Activar una etiqueta para vigilar
DELETE /api/labels/{id}             - Dejar de vigilar una etiqueta
PUT    /api/labels/{id}/toggle      - Activar/Desactivar vigilancia
```

### 8.5 Reglas (condición → carpeta Dropbox)

```
GET    /api/rules            - Listar reglas del usuario
POST   /api/rules            - Crear regla
GET    /api/rules/{id}       - Obtener una regla
PUT    /api/rules/{id}       - Actualizar regla
DELETE /api/rules/{id}       - Eliminar regla
POST   /api/rules/{id}/test  - Probar regla contra un correo de ejemplo
POST   /api/rules/reorder    - Reordenar prioridad
```


### 8.6 Carpetas de Dropbox

```
GET    /api/folders                - Listar carpetas configuradas
POST   /api/folders                - Crear carpeta (define ruta de Dropbox)
PUT    /api/folders/{id}           - Actualizar carpeta
DELETE /api/folders/{id}           - Eliminar carpeta
GET    /api/folders/dropbox/browse - Navegar carpetas existentes en Dropbox
```

### 8.7 Correos

```
GET    /api/emails                 - Historial de correos procesados
GET    /api/emails/{id}            - Detalle de un correo
POST   /api/emails/process         - Procesar correos pendientes de las etiquetas vigiladas
POST   /api/emails/{id}/reprocess  - Reprocesar un correo concreto
GET    /api/emails/stats           - Estadísticas
```

### 8.8 Integraciones

```
GET    /api/integrations/status         - Estado de Gmail / Dropbox / N8N
GET    /api/integrations/n8n/workflows  - Listar workflows N8N
POST   /api/integrations/n8n/trigger    - Ejecutar workflow manualmente
```

---

## 9. ALTA DE USUARIOS POR INVITACIÓN

No hay registro abierto. Solo el **admin** (`admin@fracdrop.app`) puede dar de alta a gente, y lo hace enviando un **enlace de invitación**. Cada persona se registra ella misma con ese enlace.

### 9.1 Admin inicial (semilla)

En el primer arranque, el backend crea el admin si no existe, usando `ADMIN_EMAIL` y `ADMIN_PASSWORD` del `.env`:

```python
# Al iniciar la app (startup event)
def seed_admin(db):
    if not db.query(User).filter_by(email=settings.ADMIN_EMAIL).first():
        db.add(User(
            email=settings.ADMIN_EMAIL,
            username="admin",
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_admin=True,
            role="admin",
            is_active=True,
        ))
        db.commit()
```

Se recomienda que el admin cambie su contraseña en el primer login.

### 9.2 Flujo de invitación (ej: dar de alta a Rufo)

```
1. Admin entra en "Usuarios" → "Invitar" e introduce: rufo@empresa.com
2. Backend:
   - Crea fila en `invitations` (email, token único, status 'pending',
     expires_at = ahora + INVITATION_EXPIRE_DAYS).
   - Envía email a rufo@empresa.com con el enlace:
     https://fracdrop.app/register?token=<TOKEN>
3. Rufo abre el enlace.
   - El frontend llama a GET /api/auth/invite/<TOKEN> para validar.
   - Si es válido: muestra formulario con su email ya fijado; Rufo elige
     username y contraseña.
   - Si caducó/ya usado/revocado: muestra error.
4. Rufo envía el formulario → POST /api/auth/register { token, username, password }
   - Backend valida el token de nuevo, crea el User (role 'user'),
     marca la invitación como 'accepted' (accepted_at = ahora).
   - Devuelve JWT: Rufo entra directamente.
5. Rufo ya dentro configura sus credenciales de Gmail/Dropbox, etiquetas y reglas.
```

### 9.3 Reglas de seguridad de la invitación

- El **token** es aleatorio y de un solo uso (ej: `secrets.token_urlsafe(32)`).
- Caduca según `INVITATION_EXPIRE_DAYS` (por defecto 7 días).
- El email de la cuenta queda **fijado** por la invitación: Rufo no puede cambiarlo en el formulario (evita que una invitación sirva para registrar otro correo).
- `POST /api/auth/register` **siempre** exige token válido; sin él, 403.
- El admin puede **revocar** (`DELETE /api/invitations/{id}`) mientras esté `pending`, o **reenviar** el email.
- Una invitación `accepted` no puede reutilizarse.

### 9.4 Endpoint de registro (esquema)

```python
@router.post("/auth/register")
def register(data: RegisterInvite, db: Session):
    inv = db.query(Invitation).filter_by(token=data.token, status="pending").first()
    if not inv or inv.expires_at < datetime.utcnow():
        raise HTTPException(403, "Invitación inválida o caducada")

    if db.query(User).filter_by(email=inv.email).first():
        raise HTTPException(409, "Ese email ya tiene cuenta")

    user = User(
        email=inv.email,                 # fijado por la invitación
        username=data.username,
        hashed_password=hash_password(data.password),
        role=inv.role,
        is_admin=(inv.role == "admin"),
        is_active=True,
    )
    db.add(user)
    inv.status = "accepted"
    inv.accepted_at = datetime.utcnow()
    db.commit()
    return {"access_token": create_jwt(user), "token_type": "bearer"}
```

### 9.5 Pantallas frontend nuevas

- **`/register?token=...`** (pública): valida el token y muestra el formulario de alta (email fijo + username + contraseña).
- **Users.tsx** (admin): lista de usuarios + botón "Invitar" (pide email) + lista de invitaciones pendientes con acciones **Reenviar** / **Revocar**.

---

## 10. FLUJO COMPLETO (paso a paso)

### 9.1 Configuración inicial del usuario

```
1. El usuario se registra e inicia sesión en la app.
2. En "Mi Perfil" introduce:
   - Gmail App Password (su cuenta de Gmail)
   - Dropbox Access Token
   La app verifica ambas conexiones y las guarda encriptadas.
3. En "Etiquetas":
   - Pulsa "Sincronizar" → la app trae todas sus etiquetas de Gmail.
   - Marca las etiquetas que quiere que la app vigile
     (ej: "Facturas", "Albaranes").
4. En "Carpetas de Dropbox":
   - Define las carpetas destino
     (ej: /Empresa/Facturas/Enero2026, /Empresa/Albaranes).
5. En "Reglas":
   - Crea reglas que conectan una condición con una carpeta de Dropbox.
```

### 9.2 Ejemplo de reglas

```
Regla 1
  Etiqueta vigilada: "Facturas"
  Remitente:         proveedor@ejemplo.com
  Tipo:              factura
  → Carpeta Dropbox: /Empresa/Facturas/Enero2026

Regla 2
  Etiqueta vigilada: "Albaranes"
  Remitente:         bongrup@ejemplo.com
  Tipo:              albaran
  → Carpeta Dropbox: /Empresa/Albaranes/Bongrup
```

### 9.3 Procesamiento automático

```
1. N8N (o un job programado) revisa periódicamente las etiquetas vigiladas.
2. Por cada correo nuevo con adjunto:
   a. Llama a POST /api/emails/process.
   b. El backend evalúa el correo contra las reglas del usuario (por prioridad).
   c. Si una regla coincide:
      - Descarga el/los adjunto(s) vía Gmail API.
      - Los sube a la carpeta de Dropbox de esa regla.
      - Registra en email_logs (status: 'procesado').
   d. Si ninguna regla coincide:
      - Registra en email_logs (status: 'sin_regla'). No se hace nada más.
3. El correo permanece en Gmail tal cual (la app no mueve ni borra correos).
```

### 9.4 Workflow N8N (process-labeled-emails.json)

```json
{
  "name": "Procesar Correos de Etiquetas Vigiladas",
  "nodes": [
    {
      "name": "Cron cada 15 min",
      "type": "n8n-nodes-base.cron",
      "config": { "triggerInterval": "minutes", "value": 15 }
    },
    {
      "name": "Procesar pendientes (por usuario)",
      "type": "n8n-nodes-base.httpRequest",
      "config": {
        "url": "http://backend:8000/api/emails/process",
        "method": "POST",
        "authentication": "headerAuth",
        "note": "El backend recorre las etiquetas vigiladas, aplica reglas y sube a Dropbox"
      }
    }
  ]
}
```

> Nota: la lógica pesada (leer Gmail, aplicar reglas, subir a Dropbox) vive en el backend. N8N solo actúa como disparador programado, de modo que el motor de reglas es único y testeable.

---

## 11. MOTOR DE REGLAS (RuleEngine)

```python
class RuleEngine:
    def find_matching_rule(self, email: dict, rules: list) -> dict | None:
        """
        Evalúa un correo contra las reglas activas del usuario, por prioridad.
        Devuelve la primera regla que coincide, o None.
        `email` ya viene con la etiqueta de Gmail en la que se encontró.
        """
        for rule in sorted(rules, key=lambda r: r.priority):
            if not rule.is_active:
                continue
            if self._matches(email, rule):
                return rule
        return None

    def _matches(self, email: dict, rule) -> bool:
        # 1. La etiqueta de origen debe coincidir
        if email["label_id"] != rule.source_label.gmail_label_id:
            return False
        # 2. Remitente (si la regla lo define)
        if rule.from_email and rule.from_email.lower() not in email["from"].lower():
            return False
        # 3. Asunto contiene (si la regla lo define)
        if rule.subject_contains and rule.subject_contains.lower() not in email["subject"].lower():
            return False
        # 4. Requiere adjunto
        if rule.has_attachment and not email["has_attachments"]:
            return False
        return True
```

Servicio de procesamiento (resumen):

```python
async def process_email(email, user, rules):
    rule = RuleEngine().find_matching_rule(email, rules)
    if not rule:
        log(email, status="sin_regla")
        return

    attachments = gmail_service.download_attachments(user, email["id"])
    for att in attachments:
        path = f"{rule.dropbox_folder.dropbox_path}/{att.filename}"
        dropbox_service.upload(user, path, att.content)

    log(email, status="procesado", rule=rule, dropbox_path=rule.dropbox_folder.dropbox_path)
```

---

## 12. FRONTEND — PANTALLAS CLAVE

### 11.1 Etiquetas (Labels.tsx)

```typescript
// Sincroniza etiquetas de Gmail y permite marcar cuáles vigilar
export default function Labels() {
  const api = useApi();
  const [available, setAvailable] = useState<GmailLabel[]>([]);
  const [watched, setWatched] = useState<number[]>([]);

  const sync = async () => {
    const res = await api.post('/api/labels/gmail/sync');
    setAvailable(res.data.labels);
  };

  const toggleWatch = async (label: GmailLabel) => {
    if (watched.includes(label.id)) {
      await api.delete(`/api/labels/${label.id}`);
    } else {
      await api.post('/api/labels', {
        gmail_label_id: label.gmail_label_id,
        gmail_label_name: label.name,
      });
    }
    // refrescar lista vigilada...
  };

  return (
    <div>
      <h1>Etiquetas de Gmail a vigilar</h1>
      <button onClick={sync}>🔄 Sincronizar etiquetas</button>
      <ul>
        {available.map(l => (
          <li key={l.id}>
            <input
              type="checkbox"
              checked={watched.includes(l.id)}
              onChange={() => toggleWatch(l)}
            />
            {l.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### 11.2 Reglas (RuleForm.tsx)

```typescript
// Una regla conecta: etiqueta + (remitente/asunto) → carpeta de Dropbox
<RuleForm>
  <Select label="Etiqueta vigilada" options={watchedLabels} bind="source_label_id" />
  <Select label="Tipo de documento" options={['factura', 'albaran']} bind="doc_type" />
  <Input  label="Remitente (opcional)" placeholder="proveedor@ejemplo.com" bind="from_email" />
  <Input  label="Asunto contiene (opcional)" placeholder="factura" bind="subject_contains" />
  <DropboxFolderPicker label="Carpeta de Dropbox destino" bind="dropbox_folder_id" />
  <button>Guardar regla</button>
</RuleForm>
```

### 11.3 Carpetas de Dropbox (Folders.tsx)

```typescript
// El usuario define la ruta de Dropbox donde irán los adjuntos
<FolderForm>
  <Input label="Nombre" placeholder="Facturas Enero 2026" bind="name" />
  <DropboxFolderPicker label="Ruta en Dropbox" bind="dropbox_path" />
  <Select label="Tipo" options={['factura', 'albaran', 'otros']} bind="doc_type" />
  <button>Crear carpeta</button>
</FolderForm>
```

### 11.4 Perfil / Credenciales (CredentialInput.tsx)

```typescript
<CredentialInput
  service="gmail"
  label="Gmail App Password"
  placeholder="Contraseña de aplicación de Google (16 caracteres)"
  connected={gmailConnected}
  onSave={saveGmailPassword}
  onTest={testGmail}
  onRemove={removeGmail}
/>

<CredentialInput
  service="dropbox"
  label="Dropbox Access Token"
  placeholder="Token de acceso de Dropbox"
  connected={dropboxConnected}
  onSave={saveDropboxToken}
  onTest={testDropbox}
  onRemove={removeDropbox}
/>
```

---

## 13. SEGURIDAD

### 12.1 Login y JWT

```
1. Registro/login → MariaDB, contraseña con hash (bcrypt).
2. Login devuelve JWT (expira en 30 min) + refresh token.
3. Toda llamada a /api/ requiere el JWT en el header Authorization.
```

### 12.2 Encriptación de credenciales de servicio

```python
# app/utils/security.py
from cryptography.fernet import Fernet

class CredentialEncryptor:
    def __init__(self, encryption_key: str):
        self.cipher = Fernet(encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()
```

- El Gmail App Password y el Dropbox Access Token se guardan **encriptados** (Fernet) en la tabla `users`.
- El frontend nunca recibe la credencial desencriptada; solo el estado (conectado / no conectado).
- Cada alta, cambio, prueba o borrado queda registrado en `credential_logs`.

### 12.3 Middleware JWT

```python
@app.middleware("http")
async def check_jwt_token(request: Request, call_next):
    if request.url.path.startswith("/api/") and not request.url.path.startswith("/api/auth/"):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return JSONResponse(status_code=401, content={"detail": "No token"})
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            request.state.user_id = payload.get("sub")
        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})
    return await call_next(request)
```

---

## 14. GUÍA: OBTENER CREDENCIALES

### 13.1 Gmail App Password

```
1. https://myaccount.google.com/security
2. Activar verificación en dos pasos.
3. "Contraseñas de aplicaciones" → generar una para "Correo".
4. Copiar los 16 caracteres y pegarlos en la app.
```

### 13.2 Dropbox Access Token

```
1. https://www.dropbox.com/developers/apps
2. Crear app → "Scoped access" → "Full Dropbox".
3. En "Permissions" activar: files.content.write, files.content.read.
4. En "Settings" → generar "Access Token" y pegarlo en la app.
```

---

## 15. DEPLOYMENT

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f backend

# Stop
docker-compose down

# Reset total (¡borra volúmenes!)
docker-compose down -v
```

Variables a cambiar en producción: `SECRET_KEY`, `ENCRYPTION_KEY`, todas las contraseñas de BD/Redis/N8N y `VITE_API_URL`.

---

## 16. FUNCIONALIDADES PRINCIPALES

### Requisito 1 — Vigilar solo las etiquetas elegidas
- ✓ El usuario sincroniza sus etiquetas de Gmail.
- ✓ Marca cuáles quiere que la app procese.
- ✓ La app ignora todo lo que esté fuera de esas etiquetas.

### Requisito 2 — Reglas por remitente/asunto
- ✓ Cada regla: etiqueta + remitente/asunto → carpeta de Dropbox.
- ✓ Soporta facturas y albaranes (campo doc_type).
- ✓ Prioridad configurable entre reglas.

### Requisito 3 — Envío a carpetas de Dropbox
- ✓ Los adjuntos se suben a la carpeta de Dropbox de la regla.
- ✓ El usuario define rutas (ej. carpeta distinta cada mes).
- ✓ La app no mueve ni borra correos en Gmail.

### Requisito 4 — Multiusuario con alta por invitación
- ✓ Cada usuario tiene sus credenciales, etiquetas, carpetas y reglas.
- ✓ Credenciales encriptadas en su perfil.
- ✓ Admin inicial semilla (admin@fracdrop.app) creado en el primer arranque.
- ✓ Sin registro abierto: el admin invita por email y cada persona se da de alta con un enlace.
- ✓ Invitaciones con token de un solo uso y caducidad; revocables y reenviables.
- ✓ Panel admin (roles admin/user).

### Requisito 5 — Automatización N8N
- ✓ Disparador programado (cada X minutos).
- ✓ El motor de reglas vive en el backend (único y testeable).
- ✓ Historial completo en email_logs.

---

## 17. TESTING

```bash
# Backend
pytest backend/tests/
pytest --cov=app backend/tests/

# Frontend
npm test
```

Casos clave a cubrir: motor de reglas (coincidencia por etiqueta/remitente/asunto/prioridad), encriptación/desencriptación de credenciales, subida a Dropbox, y registro en email_logs (procesado / sin_regla / error).

---

## 18. NOTAS IMPORTANTES

1. La app **solo lee** de las etiquetas que el usuario marca; no crea ni mueve etiquetas.
2. El destino de los adjuntos es **siempre Dropbox**, según la carpeta de la regla.
3. Credenciales (Gmail App Password / Dropbox Token) **encriptadas con Fernet** en el perfil.
4. El frontend nunca ve las credenciales en claro.
5. El motor de reglas se ejecuta en el backend; N8N solo dispara.
6. Cada correo procesado queda trazado en email_logs.

---

## 19. PRÓXIMAS FASES (Opcional)

- [ ] Carpeta mensual automática (crear ruta /Facturas/{YYYY-MM} sola).
- [ ] Detección de duplicados de factura.
- [ ] Notificaciones (email / WebSocket) al procesar.
- [ ] OCR para leer importe/fecha de la factura.
- [ ] Dashboard con gráficos y exportación (PDF/Excel).

---

**Fecha**: Junio 2026
**Versión**: 2.1 — Etiquetas vigiladas + reglas → Dropbox, con alta de usuarios por invitación (Fracdrop)