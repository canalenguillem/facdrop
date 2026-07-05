import { useState, type FormEvent } from 'react';
import type { Rule, RuleInput } from '../types/rule';
import type { WatchedLabel } from '../types/label';
import type { Folder } from '../types/folder';

interface Props {
  labels: WatchedLabel[];
  folders: Folder[];
  initial?: Rule | null;
  onSubmit: (input: RuleInput) => Promise<void>;
  onCancel: () => void;
}

const DOC_TYPES = ['factura', 'albaran'];

export default function RuleForm({ labels, folders, initial, onSubmit, onCancel }: Props) {
  const [name, setName] = useState(initial?.name ?? '');
  const [docType, setDocType] = useState(initial?.doc_type ?? 'factura');
  const [labelId, setLabelId] = useState<number | ''>(initial?.source_label_id ?? '');
  const [folderId, setFolderId] = useState<number | ''>(initial?.dropbox_folder_id ?? '');
  const [fromEmail, setFromEmail] = useState(initial?.from_email ?? '');
  const [subject, setSubject] = useState(initial?.subject_contains ?? '');
  const [hasAttachment, setHasAttachment] = useState(initial?.has_attachment ?? true);
  const [priority, setPriority] = useState(initial?.priority ?? 0);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (labelId === '' || folderId === '') {
      setError('Elige etiqueta y carpeta destino');
      return;
    }
    setSaving(true);
    try {
      await onSubmit({
        name,
        doc_type: docType,
        source_label_id: Number(labelId),
        dropbox_folder_id: Number(folderId),
        from_email: fromEmail || null,
        subject_contains: subject || null,
        has_attachment: hasAttachment,
        is_active: initial?.is_active ?? true,
        priority: Number(priority),
      });
    } catch (err: any) {
      setError(err.response?.data?.detail ?? 'No se pudo guardar la regla');
    } finally {
      setSaving(false);
    }
  };

  const field = 'w-full rounded border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none';

  return (
    <form onSubmit={submit} className="space-y-3 rounded-lg border border-gray-200 bg-white p-5">
      <h3 className="font-semibold text-gray-800">{initial ? 'Editar regla' : 'Nueva regla'}</h3>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Nombre</label>
        <input value={name} onChange={(e) => setName(e.target.value)} required className={field} placeholder="Facturas proveedor X" />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Etiqueta vigilada</label>
          <select value={labelId} onChange={(e) => setLabelId(e.target.value ? Number(e.target.value) : '')} className={field}>
            <option value="">— elegir —</option>
            {labels.map((l) => (
              <option key={l.id} value={l.id}>
                {l.gmail_label_name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Tipo</label>
          <select value={docType} onChange={(e) => setDocType(e.target.value)} className={field}>
            {DOC_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Remitente (opcional)</label>
        <input value={fromEmail} onChange={(e) => setFromEmail(e.target.value)} className={field} placeholder="proveedor@ejemplo.com" />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Asunto contiene (opcional)</label>
        <input value={subject} onChange={(e) => setSubject(e.target.value)} className={field} placeholder="factura" />
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Carpeta de Dropbox destino</label>
        <select value={folderId} onChange={(e) => setFolderId(e.target.value ? Number(e.target.value) : '')} className={field}>
          <option value="">— elegir —</option>
          {folders.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name} ({f.dropbox_path})
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-4">
        <label className="flex items-center gap-2 text-sm text-gray-700">
          <input type="checkbox" checked={hasAttachment} onChange={(e) => setHasAttachment(e.target.checked)} />
          Requiere adjunto
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700">
          Prioridad
          <input
            type="number"
            value={priority}
            onChange={(e) => setPriority(Number(e.target.value))}
            className="w-20 rounded border border-gray-300 px-2 py-1 text-sm"
          />
        </label>
      </div>

      {error && <div className="rounded bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

      <div className="flex gap-2">
        <button type="submit" disabled={saving} className="rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50">
          {saving ? 'Guardando…' : 'Guardar regla'}
        </button>
        <button type="button" onClick={onCancel} className="rounded border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">
          Cancelar
        </button>
      </div>
    </form>
  );
}
