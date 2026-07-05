import { useCallback, useEffect, useState } from 'react';
import api from '../services/api';
import type { GmailLabelAvailable, WatchedLabel } from '../types/label';

export function useLabels() {
  const [watched, setWatched] = useState<WatchedLabel[]>([]);
  const [available, setAvailable] = useState<GmailLabelAvailable[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  const loadWatched = useCallback(async () => {
    const { data } = await api.get<WatchedLabel[]>('/labels');
    setWatched(data);
  }, []);

  const sync = useCallback(async () => {
    setSyncing(true);
    try {
      const { data } = await api.post<GmailLabelAvailable[]>('/labels/gmail/sync');
      setAvailable(data);
    } finally {
      setSyncing(false);
    }
  }, []);

  const watch = useCallback(
    async (label: GmailLabelAvailable) => {
      await api.post('/labels', {
        gmail_label_id: label.gmail_label_id,
        gmail_label_name: label.gmail_label_name,
      });
      await loadWatched();
    },
    [loadWatched],
  );

  const unwatch = useCallback(
    async (id: number) => {
      await api.delete(`/labels/${id}`);
      await loadWatched();
    },
    [loadWatched],
  );

  const toggle = useCallback(
    async (id: number) => {
      await api.put(`/labels/${id}/toggle`);
      await loadWatched();
    },
    [loadWatched],
  );

  useEffect(() => {
    loadWatched().finally(() => setLoading(false));
  }, [loadWatched]);

  return { watched, available, loading, syncing, sync, watch, unwatch, toggle };
}
