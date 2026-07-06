# Guía de inicio — Fracdrop

Bienvenido/a. Fracdrop guarda automáticamente en **Dropbox** los adjuntos
(facturas, albaranes…) de los correos de **Gmail** que tú elijas. Sigue estos
pasos una sola vez y a partir de ahí funciona solo.

> ⏱️ Tardarás unos 10 minutos. Solo necesitas tu Gmail y tu Dropbox.

---

## Paso 1 · Crea tu cuenta

1. Abre el **enlace de invitación** que has recibido (algo como
   `.../register?token=...`).
2. Verás tu **email ya puesto** (no se puede cambiar).
3. Elige un **usuario** y una **contraseña** (mínimo 8 caracteres).
4. Pulsa **Crear cuenta**. Entrarás directamente.

Si el enlace dice que ha caducado, pide al administrador que te lo reenvíe.

---

## Paso 2 · Conecta tu Gmail

La app necesita una **“Contraseña de aplicación”** de Google (no tu contraseña
normal). Para generarla:

1. Activa la **Verificación en dos pasos** en https://myaccount.google.com/security
   (si no la tienes ya). Es imprescindible.
2. Ve directamente a https://myaccount.google.com/apppasswords y crea una
   contraseña de aplicación para “Correo”.
3. Google te dará **16 letras** (algo como `abcd efgh ijkl mnop`). Cópialas.

Ahora en Fracdrop:

5. Ve a **Perfil**.
6. En la tarjeta **Gmail**: escribe tu dirección de Gmail y pega la contraseña
   de aplicación.
7. Pulsa **Guardar** y luego **Probar conexión** → debe salir ✅.

---

## Paso 3 · Conecta tu Dropbox

¿No tienes cuenta de Dropbox? Créala aquí:
https://www.dropbox.com/referrals/AAC-HbKpvUuTNv4Nkqtcmlu5cTnlY5e2LFM?src=global9

Una vez la tengas, es solo un botón:

1. Ve a **Perfil**.
2. Pulsa **Conectar con Dropbox**.
3. En la ventana de Dropbox, pulsa **Permitir** para autorizar.
4. Vuelves a la app con Dropbox **conectado**.

La conexión es **permanente**: no caduca y no tendrás que volver a hacer nada.

---

## Paso 4 · En Gmail: organiza tus correos con filtros y etiquetas

Fracdrop **no crea ni mueve nada en Gmail**: solo lee de las etiquetas que le
indiques. Primero organiza tú tus correos en Gmail con **filtros**.

Crea **tantos filtros como grupos de mensajes** quieras clasificar, y que cada
filtro **aplique una etiqueta** (ej. un filtro para las facturas de un proveedor
→ etiqueta “Facturas”; otro para los albaranes → etiqueta “Albaranes”).

Cómo crear un filtro en Gmail:

1. En Gmail, ⚙️ → **Ver todos los ajustes** → pestaña **Filtros y direcciones bloqueadas**.
2. Pulsa **Crear un filtro nuevo**.
3. Define el criterio (ej. *De: proveedor@ejemplo.com*, o palabras del asunto) → **Crear filtro**.
4. Marca **Aplicar la etiqueta** y elige o crea una etiqueta (ej. “Facturas”).
5. Para etiquetar también los correos **antiguos**, marca **“Aplicar el filtro
   también a las conversaciones que cumplan estos criterios”** antes de crear el
   filtro. Si no, solo se etiquetarán los correos nuevos.
6. Repite con cada grupo de mensajes que quieras separar.

## Paso 5 · Elige qué etiquetas vigilar en Fracdrop

1. Ve a **Etiquetas**.
2. Pulsa **🔄 Sincronizar etiquetas** (trae tus etiquetas de Gmail).
3. **Marca** las que quieres que la app revise (las que creaste con los filtros).

> La app **solo lee** de esas etiquetas. Nunca mueve, borra ni cambia tus
> correos.

---

## Paso 5 · Define tus carpetas de Dropbox

1. Ve a **Carpetas**.
2. Ponle un **nombre** (ej. “Facturas 2026”).
3. En **Ruta en Dropbox**, pulsa **Explorar** y navega hasta la carpeta que ya
   usas para tus facturas; pulsa **Usar esta carpeta**. (O escribe la ruta a
   mano si quieres una nueva.)
4. Elige el **tipo** (factura / albarán / otros).
5. *(Opcional)* Marca **“Organizar por fecha”** si quieres que los archivos se
   guarden en subcarpetas por día: `.../2026/07/20/factura.pdf`.
6. Pulsa **Crear carpeta**.

---

## Paso 6 · Crea tus reglas

Una regla dice: *“los correos de esta etiqueta (de este remitente) → van a esta
carpeta”*.

1. Ve a **Reglas** → **+ Nueva regla**.
2. Elige la **etiqueta vigilada** y el **tipo** (factura/albarán).
3. *(Opcional)* Escribe el **remitente** (ej. `proveedor@ejemplo.com`) y/o un
   texto que deba tener el **asunto**.
4. Elige la **carpeta de Dropbox** destino.
5. Pulsa **Guardar regla**.

Puedes probarla con el botón **Probar** (simula un correo y te dice si coincide).
Si tienes varias reglas, se aplican por **prioridad** (ordénalas con ↑/↓).

---

## Paso 7 · ¡Listo!

- Pulsa **Procesar ahora** en **Historial** para que revise tus correos y suba
  los adjuntos a Dropbox.
- En **Historial** verás cada correo como `procesado`, `sin regla` o `error`.

A partir de aquí, cada vez que llegue un correo a una etiqueta vigilada que
cumpla una regla, su documento acabará en la carpeta de Dropbox correcta.

---

## Cosas que conviene saber

- **Solo se guardan documentos** (PDF, Word, Excel, CSV…). Las imágenes (como los
  logos de las firmas) se ignoran.
- Tus **contraseñas y tokens se guardan cifrados**; la app nunca los muestra.
- La app **nunca toca tus correos** en Gmail: solo los lee.
- Si cambias la contraseña de aplicación de Gmail o el token de Dropbox, vuelve a
  **Perfil** y actualízalos.

## Problemas frecuentes

| Síntoma | Solución |
|---|---|
| Al **Probar Gmail** falla | Revisa que usaste la *contraseña de aplicación* (16 letras), no tu contraseña normal, y que la verificación en dos pasos está activada. |
| En **Explorar** de Dropbox solo sale una carpeta rara | Tu app de Dropbox es “App folder”. Crea una nueva de tipo **Full Dropbox** (Paso 3). |
| **Probar Dropbox** falla con error de *scope* | Generaste el token antes de pulsar **Submit** en Permissions. Vuelve a **Submit** y **regenera** el token. |
| No se procesa un correo | Comprueba que su etiqueta está **vigilada**, que hay una **regla** que coincide y que el correo trae un **documento** adjunto. |
