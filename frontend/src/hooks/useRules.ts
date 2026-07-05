import { useCallback, useEffect, useState } from 'react';
import api from '../services/api';
import type { Rule, RuleInput, RuleTestResult } from '../types/rule';

export function useRules() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    const { data } = await api.get<Rule[]>('/rules');
    setRules(data);
  }, []);

  const create = useCallback(
    async (input: RuleInput) => {
      await api.post('/rules', input);
      await load();
    },
    [load],
  );

  const update = useCallback(
    async (id: number, input: Partial<RuleInput>) => {
      await api.put(`/rules/${id}`, input);
      await load();
    },
    [load],
  );

  const remove = useCallback(
    async (id: number) => {
      await api.delete(`/rules/${id}`);
      await load();
    },
    [load],
  );

  const reorder = useCallback(
    async (items: { id: number; priority: number }[]) => {
      await api.post('/rules/reorder', { items });
      await load();
    },
    [load],
  );

  const test = useCallback(
    async (
      id: number,
      email: { label_id: string; from_email: string; subject: string; has_attachments: boolean },
    ): Promise<RuleTestResult> => {
      const { data } = await api.post<RuleTestResult>(`/rules/${id}/test`, email);
      return data;
    },
    [],
  );

  useEffect(() => {
    load().finally(() => setLoading(false));
  }, [load]);

  return { rules, loading, create, update, remove, reorder, test };
}
