import type { ReactNode } from 'react';

function Section({ n, title, children }: { n: number; title: string; children: ReactNode }) {
  return (
    <section className="mb-8">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-gray-800">
        <span className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-600 text-sm text-white">
          {n}
        </span>
        {title}
      </h2>
      <div className="ml-9 space-y-2 text-sm text-gray-700">{children}</div>
    </section>
  );
}

function Warn({ children }: { children: ReactNode }) {
  return (
    <div className="rounded border border-yellow-300 bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
      {children}
    </div>
  );
}

function Ext({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="font-medium text-blue-600 underline hover:text-blue-800"
    >
      {children}
    </a>
  );
}

export default function Help() {
  return (
    <div className="max-w-3xl">
      <h1 className="mb-1 text-2xl font-bold text-gray-800">Ayuda · Primeros pasos</h1>
      <p className="mb-8 text-sm text-gray-500">
        Fracdrop guarda en Dropbox los adjuntos (facturas, albaranes…) de los correos de Gmail que
        tú elijas. Configúralo una vez siguiendo estos pasos y funcionará solo.
      </p>

      <Section n={1} title="En Gmail: organiza tus correos con filtros y etiquetas">
        <p>
          Fracdrop <strong>no crea ni mueve nada en Gmail</strong>: solo lee de las etiquetas que le
          indiques. Por eso, primero organiza tú tus correos en Gmail con <strong>filtros</strong>.
        </p>
        <p>
          Crea <strong>tantos filtros como grupos de mensajes</strong> quieras clasificar, y cada
          filtro que <strong>aplique una etiqueta</strong>. Por ejemplo: un filtro para las facturas
          de un proveedor → etiqueta «Facturas»; otro para los albaranes → etiqueta «Albaranes».
        </p>
        <p className="font-medium text-gray-800">Cómo crear un filtro en Gmail:</p>
        <ol className="list-decimal space-y-1 pl-5">
          <li>En Gmail, ⚙️ → <strong>Ver todos los ajustes</strong> → pestaña <strong>Filtros y direcciones bloqueadas</strong>.</li>
          <li>Pulsa <strong>Crear un filtro nuevo</strong>.</li>
          <li>Define el criterio (p. ej. <em>De: proveedor@ejemplo.com</em>, o palabras del asunto) → <strong>Crear filtro</strong>.</li>
          <li>Marca <strong>Aplicar la etiqueta</strong> y elige o crea una etiqueta (ej. «Facturas»).</li>
          <li>Repite con cada grupo de mensajes que quieras separar.</li>
        </ol>
        <p className="text-gray-500">
          Resultado: cada correo entrante queda con su etiqueta. Fracdrop vigilará esas etiquetas.
        </p>
      </Section>

      <Section n={2} title="Crea tu cuenta">
        <p>Abre el enlace de invitación que has recibido. Tu email ya viene fijado; elige usuario y contraseña, y pulsa <strong>Crear cuenta</strong>.</p>
      </Section>

      <Section n={3} title="Conecta tu Gmail">
        <p>La app necesita una <strong>Contraseña de aplicación</strong> de Google (no tu contraseña normal):</p>
        <ol className="list-decimal space-y-1 pl-5">
          <li>Activa la <strong>Verificación en dos pasos</strong> en <Ext href="https://myaccount.google.com/security">myaccount.google.com/security</Ext> (si aún no la tienes). Es imprescindible.</li>
          <li>Ve a <Ext href="https://myaccount.google.com/apppasswords">myaccount.google.com/apppasswords</Ext> y crea una contraseña de aplicación para «Correo». Copia las 16 letras.</li>
          <li>En <strong>Perfil → Gmail</strong>: pon tu dirección y pega la contraseña → <strong>Guardar</strong> → <strong>Probar conexión</strong> (debe salir ✅).</li>
        </ol>
      </Section>

      <Section n={4} title="Conecta tu Dropbox">
        <Warn>Este paso tiene truco. Léelo con calma.</Warn>
        <p>Necesitas un <strong>token</strong> de una app de Dropbox de tipo <strong>Full Dropbox</strong>:</p>
        <ol className="list-decimal space-y-1 pl-5">
          <li>Entra en <Ext href="https://www.dropbox.com/developers/apps/create">dropbox.com/developers/apps/create</Ext>.</li>
          <li><strong>Choose an API:</strong> Scoped access.</li>
          <li><strong>Type of access:</strong> <strong>Full Dropbox</strong> (⚠️ NO «App folder», o solo verá una carpeta suya).</li>
          <li>Nombre cualquiera → <strong>Create app</strong>.</li>
          <li>Pestaña <strong>Permissions</strong>: marca <code>files.metadata.read</code>, <code>files.content.read</code> y <code>files.content.write</code>, y pulsa <strong>Submit</strong>.</li>
          <li>Recarga la página: si las casillas siguen marcadas, se guardó.</li>
          <li><strong>Después</strong>, pestaña <strong>Settings</strong> → <strong>Generate access token</strong>. Copia el token.</li>
          <li>En <strong>Perfil → Dropbox</strong>: pega el token → <strong>Guardar</strong> → <strong>Probar conexión</strong> (✅).</li>
        </ol>
        <Warn>El orden importa: primero <strong>Submit</strong> de los permisos, y <strong>después</strong> generar el token. Si lo generas antes, no tendrá permisos.</Warn>
      </Section>

      <Section n={5} title="Elige qué etiquetas vigilar">
        <p>En <strong>Etiquetas</strong>, pulsa <strong>🔄 Sincronizar</strong> y marca las etiquetas de Gmail que quieres que la app revise (las que creaste con los filtros del paso 1).</p>
      </Section>

      <Section n={6} title="Define tus carpetas de Dropbox">
        <p>En <strong>Carpetas</strong>, dale un nombre y usa <strong>Explorar</strong> para elegir una carpeta de Dropbox que ya tengas (o escribe una ruta nueva). Opcional: marca <strong>Organizar por fecha</strong> para guardar en subcarpetas <code>AAAA/MM/DD</code>.</p>
      </Section>

      <Section n={7} title="Crea tus reglas">
        <p>En <strong>Reglas</strong>, cada regla conecta una etiqueta (y opcionalmente remitente/asunto) con una carpeta de Dropbox. Usa <strong>Probar</strong> para comprobarla. Si tienes varias, ordénalas por prioridad con ↑/↓.</p>
      </Section>

      <Section n={8} title="¡Listo!">
        <p>En <strong>Historial</strong>, pulsa <strong>Procesar ahora</strong>. Verás cada correo como <em>procesado</em>, <em>sin regla</em> o <em>error</em>, y los documentos aparecerán en tu Dropbox.</p>
      </Section>

      <div className="mt-6 rounded-lg border border-gray-200 bg-white p-4 text-sm text-gray-600">
        <p className="mb-2 font-semibold text-gray-800">Bueno saber</p>
        <ul className="list-disc space-y-1 pl-5">
          <li>Solo se guardan <strong>documentos</strong> (PDF, Word, Excel, CSV…). Las imágenes (logos de firma) se ignoran.</li>
          <li>Tus contraseñas y tokens se guardan <strong>cifrados</strong>; la app nunca los muestra.</li>
          <li>La app <strong>nunca toca tus correos</strong> en Gmail: solo los lee.</li>
        </ul>
      </div>
    </div>
  );
}
