import type { GmailLabelAvailable, WatchedLabel } from '../types/label';

interface Props {
  available: GmailLabelAvailable[];
  watched: WatchedLabel[];
  onToggle: (label: GmailLabelAvailable, isWatched: boolean) => void;
}

export default function LabelSelector({ available, watched, onToggle }: Props) {
  const watchedIds = new Set(watched.map((w) => w.gmail_label_id));

  if (available.length === 0) {
    return (
      <p className="text-sm text-gray-400">
        Pulsa «Sincronizar» para traer tus etiquetas de Gmail.
      </p>
    );
  }

  return (
    <ul className="divide-y divide-gray-100 rounded-lg border border-gray-200 bg-white">
      {available.map((l) => {
        const isWatched = watchedIds.has(l.gmail_label_id);
        return (
          <li key={l.gmail_label_id} className="flex items-center gap-3 px-4 py-2">
            <input
              type="checkbox"
              checked={isWatched}
              onChange={() => onToggle(l, isWatched)}
              className="h-4 w-4"
            />
            <span className="text-sm text-gray-700">{l.gmail_label_name}</span>
          </li>
        );
      })}
    </ul>
  );
}
