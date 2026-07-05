import { useEffect, useState } from 'react';
import api from '../services/api';
import RuleForm from '../components/RuleForm';
import { useRules } from '../hooks/useRules';
import type { Rule, RuleInput, RuleTestResult } from '../types/rule';
import type { WatchedLabel } from '../types/label';
import type { Folder } from '../types/folder';

export default function Rules() {
  const { rules, loading, create, update, remove, reorder, test } = useRules();
  const [labels, setLabels] = useState<WatchedLabel[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Rule | null>(null);

  useEffect(() => {
    api.get<WatchedLabel[]>('/labels').then((r) => setLabels(r.data));
    api.get<Folder[]>('/folders').then((r) => setFolders(r.data));
  }, []);

  const labelName = (id: number) => labels.find((l) => l.id === id)?.gmail_label_name ?? `#${id}`;
  const labelGmailId = (id: number) => labels.find((l) => l.id === id)?.gmail_label_id ?? '';
  const folderName = (id: number) => folders.find((f) => f.id === id)?.name ?? `#${id}`;

  const submitForm = async (input: RuleInput) => {
    if (editing) await update(editing.id, input);
    else await create(input);
    setShowForm(false);
    setEditing(null);
  };

  const move = async (index: number, dir: -1 | 1) => {
    const target = index + dir;
    if (target < 0 || target >= rules.length) return;
    const ordered = [...rules];
    [ordered[index], ordered[target]] = [ordered[target], ordered[index]];
    await reorder(ordered.map((r, i) => ({ id: r.id, priority: i })));
  };

  if (loading) return <div className="text-gray-500">Cargando…</div>;

  const canCreate = labels.length > 0 && folders.length > 0;

  return (
    <div className="max-w-3xl">
      <h1 className="mb-1 text-2xl font-bold text-gray-800">Reglas</h1>
      <p className="mb-4 text-sm text-gray-500">
        Cada regla conecta una etiqueta vigilada (y opcionalmente remitente/asunto) con una carpeta
        de Dropbox. Se evalúan por prioridad; gana la primera que coincide.
      </p>

      {!canCreate && (
        <div className="mb-4 rounded bg-yellow-50 px-3 py-2 text-sm text-yellow-800">
          Necesitas al menos una <strong>etiqueta vigilada</strong> y una <strong>carpeta</strong>{' '}
          antes de crear reglas.
        </div>
      )}

      {!showForm && (
        <button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
          disabled={!canCreate}
          className="mb-4 rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50"
        >
          + Nueva regla
        </button>
      )}

      {showForm && (
        <div className="mb-6">
          <RuleForm
            labels={labels}
            folders={folders}
            initial={editing}
            onSubmit={submitForm}
            onCancel={() => {
              setShowForm(false);
              setEditing(null);
            }}
          />
        </div>
      )}

      {rules.length === 0 ? (
        <p className="text-sm text-gray-400">Aún no hay reglas.</p>
      ) : (
        <ul className="space-y-3">
          {rules.map((r, i) => (
            <RuleRow
              key={r.id}
              rule={r}
              index={i}
              total={rules.length}
              labelName={labelName(r.source_label_id)}
              labelGmailId={labelGmailId(r.source_label_id)}
              folderName={folderName(r.dropbox_folder_id)}
              onEdit={() => {
                setEditing(r);
                setShowForm(true);
              }}
              onDelete={() => remove(r.id)}
              onToggle={() => update(r.id, { is_active: !r.is_active })}
              onMove={(dir) => move(i, dir)}
              onTest={test}
            />
          ))}
        </ul>
      )}
    </div>
  );
}

interface RowProps {
  rule: Rule;
  index: number;
  total: number;
  labelName: string;
  labelGmailId: string;
  folderName: string;
  onEdit: () => void;
  onDelete: () => void;
  onToggle: () => void;
  onMove: (dir: -1 | 1) => void;
  onTest: (
    id: number,
    email: { label_id: string; from_email: string; subject: string; has_attachments: boolean },
  ) => Promise<RuleTestResult>;
}

function RuleRow({
  rule,
  index,
  total,
  labelName,
  labelGmailId,
  folderName,
  onEdit,
  onDelete,
  onToggle,
  onMove,
  onTest,
}: RowProps) {
  const [testing, setTesting] = useState(false);
  const [from, setFrom] = useState(rule.from_email ?? '');
  const [subject, setSubject] = useState('');
  const [result, setResult] = useState<RuleTestResult | null>(null);

  const runTest = async () => {
    const res = await onTest(rule.id, {
      label_id: labelGmailId,
      from_email: from,
      subject,
      has_attachments: true,
    });
    setResult(res);
  };

  return (
    <li className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-semibold text-gray-800">{rule.name}</span>
            <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">{rule.doc_type}</span>
            {!rule.is_active && (
              <span className="rounded bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700">pausada</span>
            )}
          </div>
          <div className="mt-1 text-xs text-gray-500">
            <strong>{labelName}</strong>
            {rule.from_email ? ` · de ${rule.from_email}` : ''}
            {rule.subject_contains ? ` · asunto ~ "${rule.subject_contains}"` : ''} → 📁 {folderName}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className="flex gap-1">
            <button onClick={() => onMove(-1)} disabled={index === 0} className="rounded border border-gray-300 px-2 text-xs disabled:opacity-30">
              ↑
            </button>
            <button onClick={() => onMove(1)} disabled={index === total - 1} className="rounded border border-gray-300 px-2 text-xs disabled:opacity-30">
              ↓
            </button>
            <span className="px-1 text-xs text-gray-400">prio {rule.priority}</span>
          </div>
        </div>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        <button onClick={() => setTesting((t) => !t)} className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50">
          Probar
        </button>
        <button onClick={onEdit} className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50">
          Editar
        </button>
        <button onClick={onToggle} className="rounded border border-gray-300 px-2 py-1 text-xs text-gray-600 hover:bg-gray-50">
          {rule.is_active ? 'Pausar' : 'Activar'}
        </button>
        <button onClick={onDelete} className="rounded border border-red-300 px-2 py-1 text-xs text-red-600 hover:bg-red-50">
          Eliminar
        </button>
      </div>

      {testing && (
        <div className="mt-3 rounded border border-gray-100 bg-gray-50 p-3">
          <div className="mb-2 text-xs text-gray-500">
            Simula un correo de la etiqueta <strong>{labelName}</strong> (con adjunto):
          </div>
          <div className="flex flex-wrap gap-2">
            <input value={from} onChange={(e) => setFrom(e.target.value)} placeholder="remitente" className="rounded border border-gray-300 px-2 py-1 text-xs" />
            <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="asunto" className="rounded border border-gray-300 px-2 py-1 text-xs" />
            <button onClick={runTest} className="rounded bg-blue-600 px-3 py-1 text-xs text-white hover:bg-blue-700">
              Probar
            </button>
          </div>
          {result && (
            <div className={`mt-2 text-sm ${result.matched ? 'text-green-600' : 'text-gray-500'}`}>
              {result.matched ? '✅ Coincide con esta regla' : '✖ No coincide'}
            </div>
          )}
        </div>
      )}
    </li>
  );
}
