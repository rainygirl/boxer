<script lang="ts">
  import { t, dateLocale } from '$lib/i18n';
  import type { Task, User } from '$lib/types';
  import { TASK_STATUSES, PRIORITY_CONFIG } from '$lib/types';

  const { tasks, onSelectTask }: { tasks: Task[]; onSelectTask?: (t: Task) => void } = $props();

  const STATUS_COLORS: Record<string, string> = {
    backlog: '#94a3b8',
    todo: '#3b82f6',
    in_progress: '#f59e0b',
    done: '#22c55e',
    confirmed: '#a855f7',
    cancelled: '#f87171',
  };

  // ── Card 0: Recent Issues ─────────────────────────────────────────────
  const recentIssues = $derived(
    [...tasks].sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()).slice(0, 5)
  );

  // ── Card 0b: Upcoming Due Dates ───────────────────────────────────────
  const today = new Date(new Date().toDateString());
  const in7 = new Date(today); in7.setDate(in7.getDate() + 7);

  const upcomingDue = $derived(
    tasks
      .filter((t) => t.due_date && !['done', 'confirmed', 'cancelled'].includes(t.status))
      .map((t) => ({ ...t, dueMs: new Date(t.due_date! + 'T00:00:00').getTime() }))
      .sort((a, b) => a.dueMs - b.dueMs)
      .slice(0, 5)
  );

  // ── Card 1: Cycle Time ───────────────────────────────────────────────
  const cycleTime = $derived.by(() => {
    const doneTasks = tasks.filter((t) => t.status === 'done' || t.status === 'confirmed');
    if (doneTasks.length === 0) return null;

    const totalMs = doneTasks.reduce((sum, task) => {
      return sum + Math.max(0, new Date(task.updated_at).getTime() - new Date(task.created_at).getTime());
    }, 0);

    const avgHours = totalMs / doneTasks.length / (1000 * 60 * 60);
    return { avgHours, count: doneTasks.length };
  });

  // ── Card 2: Status Distribution ──────────────────────────────────────
  const statusDist = $derived.by(() => {
    const counts: Record<string, number> = {};
    for (const task of tasks) counts[task.status] = (counts[task.status] ?? 0) + 1;
    const total = tasks.length || 1;
    return TASK_STATUSES
      .map((s) => ({ ...s, count: counts[s.value] ?? 0 }))
      .filter((s) => s.count > 0)
      .map((s) => ({ ...s, pct: (s.count / total) * 100 }));
  });

  // ── Card 3: By Assignee (with user object for avatar) ─────────────────
  const byAssignee = $derived.by(() => {
    const map = new Map<string, { count: number; user: User | null }>();
    for (const task of tasks) {
      const key = task.assignee ? String(task.assignee.id) : '__unassigned__';
      const existing = map.get(key);
      if (existing) existing.count++;
      else map.set(key, { count: 1, user: task.assignee ?? null });
    }
    const sorted = [...map.values()].sort((a, b) => b.count - a.count);
    const max = sorted[0]?.count ?? 1;
    return { rows: sorted, max };
  });

  // ── Card 4 & 5: Daily helpers ────────────────────────────────────────
  function getLast30Days(): string[] {
    const days: string[] = [];
    const now = new Date();
    for (let i = 29; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(d.getDate() - i);
      days.push(d.toISOString().slice(0, 10));
    }
    return days;
  }

  const last30 = getLast30Days();

  const dailyProgress = $derived.by(() => {
    const byDay: Record<string, { ip: number; done: number; conf: number }> = {};
    for (const day of last30) byDay[day] = { ip: 0, done: 0, conf: 0 };
    for (const task of tasks) {
      const day = task.updated_at.slice(0, 10);
      if (!byDay[day]) continue;
      if (task.status === 'in_progress') byDay[day].ip++;
      else if (task.status === 'done') byDay[day].done++;
      else if (task.status === 'confirmed') byDay[day].conf++;
    }
    const rows = last30.map((day) => ({ day, ...byDay[day] }));
    const maxV = Math.max(...rows.map((r) => r.ip + r.done + r.conf), 1);
    return { rows, maxV };
  });

  const dailyCreated = $derived.by(() => {
    const byDay: Record<string, number> = {};
    for (const day of last30) byDay[day] = 0;
    for (const task of tasks) {
      const day = task.created_at.slice(0, 10);
      if (day in byDay) byDay[day]++;
    }
    const rows = last30.map((day) => ({ day, count: byDay[day] }));
    const maxV = Math.max(...rows.map((r) => r.count), 1);
    return { rows, maxV };
  });

  // ── SVG constants ─────────────────────────────────────────────────────
  const PAD_L = 28, PAD_R = 8, PAD_T = 8, PAD_B = 32;
  const SVG_W = 520, SVG_H = 140;
  const CHART_H = SVG_H - PAD_T - PAD_B;
  const slotW = (SVG_W - PAD_L - PAD_R) / 30;
  const BAR_W = Math.max(4, slotW * 0.7);
  const Y_BOTTOM = PAD_T + CHART_H;

  function barX(i: number) { return PAD_L + i * slotW + (slotW - BAR_W) / 2; }

  function gridTicks(maxV: number): number[] {
    const step = Math.ceil(maxV / 4) || 1;
    const ticks: number[] = [];
    for (let v = step; v <= maxV; v += step) ticks.push(v);
    return ticks.slice(0, 4);
  }

  function fmtMMDD(dateStr: string) { return dateStr.slice(5); }

  function fmtDue(dateStr: string) {
    const [y, m, d] = dateStr.split('-').map(Number);
    return new Date(y, m - 1, d).toLocaleDateString($dateLocale, { month: 'short', day: 'numeric' });
  }
</script>

<div class="flex-1 overflow-auto bg-slate-50 dark:bg-slate-950 p-4 md:p-6">
  <div class="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-4">

    <!-- Card: Recent Issues (full width) -->
    <div class="md:col-span-3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
        {$t('report.recentIssues')}
      </div>
      {#if recentIssues.length === 0}
        <p class="text-sm text-slate-400 dark:text-slate-500">{$t('report.noData')}</p>
      {:else}
        <div class="flex flex-col divide-y divide-slate-100 dark:divide-slate-800">
          {#each recentIssues as task}
            {@const statusCfg = TASK_STATUSES.find((s) => s.value === task.status)!}
            {@const priCfg = PRIORITY_CONFIG.find((p) => p.value === task.priority)!}
            <button
              onclick={() => onSelectTask?.(task)}
              class="flex items-center gap-3 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-lg px-1 -mx-1 transition-colors group"
            >
              <span class="text-[11px] font-mono text-slate-400 dark:text-slate-500 shrink-0 w-14 truncate">{task.ref}</span>
              <span class="text-sm text-slate-700 dark:text-slate-200 flex-1 truncate group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">{task.title}</span>
              <span class="text-xs shrink-0">{priCfg.icon}</span>
              <span class="text-[11px] px-1.5 py-0.5 rounded-full font-medium shrink-0 {statusCfg.color} {statusCfg.bg}">
                {$t(`status.${task.status}` as any)}
              </span>
              {#if task.assignee}
                {#if task.assignee.avatar_url}
                  <img src={task.assignee.avatar_url} class="w-5 h-5 rounded-full shrink-0" alt={task.assignee.name} />
                {:else}
                  <div class="w-5 h-5 rounded-full bg-brand-400 text-white text-xs flex items-center justify-center font-medium shrink-0">
                    {task.assignee.name[0]}
                  </div>
                {/if}
              {:else}
                <div class="w-5 h-5 rounded-full border border-dashed border-slate-300 dark:border-slate-600 shrink-0"></div>
              {/if}
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Card: Upcoming Due Dates (full width) -->
    {#if upcomingDue.length > 0}
      <div class="md:col-span-3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
        <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3">
          {$t('report.upcomingDue')}
        </div>
        <div class="flex flex-col divide-y divide-slate-100 dark:divide-slate-800">
          {#each upcomingDue as task}
            {@const isOverdue = task.dueMs < today.getTime()}
            {@const statusCfg = TASK_STATUSES.find((s) => s.value === task.status)!}
            <button
              onclick={() => onSelectTask?.(task)}
              class="flex items-center gap-3 py-2 text-left hover:bg-slate-50 dark:hover:bg-slate-800/50 rounded-lg px-1 -mx-1 transition-colors group"
            >
              <span class="text-[11px] font-medium shrink-0 w-16 {isOverdue ? 'text-red-500 dark:text-red-400' : 'text-slate-400 dark:text-slate-500'}">
                {fmtDue(task.due_date!)}
              </span>
              <span class="text-sm text-slate-700 dark:text-slate-200 flex-1 truncate group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">{task.title}</span>
              <span class="text-[11px] px-1.5 py-0.5 rounded-full font-medium shrink-0 {statusCfg.color} {statusCfg.bg}">
                {$t(`status.${task.status}` as any)}
              </span>
              {#if task.assignee}
                {#if task.assignee.avatar_url}
                  <img src={task.assignee.avatar_url} class="w-5 h-5 rounded-full shrink-0" alt={task.assignee.name} />
                {:else}
                  <div class="w-5 h-5 rounded-full bg-brand-400 text-white text-xs flex items-center justify-center font-medium shrink-0">
                    {task.assignee.name[0]}
                  </div>
                {/if}
              {:else}
                <div class="w-5 h-5 rounded-full border border-dashed border-slate-300 dark:border-slate-600 shrink-0"></div>
              {/if}
            </button>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Card 1: Cycle Time -->
    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-4">
        {$t('report.cycleTime')}
      </div>
      {#if cycleTime}
        {@const h = cycleTime.avgHours}
        {@const display = h < 1
          ? `${Math.round(h * 60)}${$t('time.minutes')}`
          : h < 24
            ? `${h.toFixed(1)}${$t('time.hours')}`
            : `${(h / 24).toFixed(1)}${$t('time.days')}`}
        <div class="flex flex-col gap-1">
          <span class="text-4xl font-bold text-slate-800 dark:text-slate-100 leading-none">{display}</span>
          <span class="text-xs text-slate-400 dark:text-slate-500 mt-2">{$t('report.cycleTimeSub')} · {$t('report.cycleTimeCount', { count: cycleTime.count })}</span>
        </div>
      {:else}
        <p class="text-sm text-slate-400 dark:text-slate-500">{$t('report.noData')}</p>
      {/if}
    </div>

    <!-- Card 2: Status Distribution -->
    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-4">
        {$t('report.statusDist')}
      </div>
      {#if statusDist.length === 0}
        <p class="text-sm text-slate-400 dark:text-slate-500">{$t('report.noData')}</p>
      {:else}
        <div class="flex flex-col gap-2">
          {#each statusDist as s}
            <div class="flex items-center gap-2">
              <span class="text-xs text-slate-500 dark:text-slate-400 w-20 shrink-0">{$t(`status.${s.value}` as any)}</span>
              <div class="flex-1 bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                <div class="h-full rounded-full" style="width: {s.pct}%; background-color: {STATUS_COLORS[s.value]};"></div>
              </div>
              <span class="text-xs text-slate-500 dark:text-slate-400 w-6 text-right shrink-0">{s.count}</span>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Card 3: By Assignee (with avatar) -->
    <div class="bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-4">
        {$t('report.byAssignee')}
      </div>
      {#if byAssignee.rows.length === 0}
        <p class="text-sm text-slate-400 dark:text-slate-500">{$t('report.noData')}</p>
      {:else}
        <div class="flex flex-col gap-2">
          {#each byAssignee.rows as { count, user }}
            {@const pct = (count / byAssignee.max) * 100}
            <div class="flex items-center gap-2">
              {#if user}
                {#if user.avatar_url}
                  <img src={user.avatar_url} class="w-5 h-5 rounded-full shrink-0" alt={user.name} />
                {:else}
                  <div class="w-5 h-5 rounded-full bg-brand-400 text-white text-xs flex items-center justify-center font-medium shrink-0">
                    {user.name[0]}
                  </div>
                {/if}
              {:else}
                <div class="w-5 h-5 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-slate-400 text-xs shrink-0">?</div>
              {/if}
              <span class="text-xs text-slate-500 dark:text-slate-400 w-20 shrink-0 truncate">
                {user ? user.name : $t('report.unassigned')}
              </span>
              <div class="flex-1 bg-slate-100 dark:bg-slate-800 rounded-full h-2 overflow-hidden">
                <div class="h-full rounded-full bg-indigo-500" style="width: {pct}%;"></div>
              </div>
              <span class="text-xs text-slate-500 dark:text-slate-400 w-6 text-right shrink-0">{count}</span>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Card 4: Daily Progress (stacked bar SVG) -->
    <div class="md:col-span-3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="mb-3">
        <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">
          {$t('report.dailyProgress')}
        </div>
        <!-- Legend below title, wrapping -->
        <div class="flex items-center gap-2.5 flex-wrap mt-1">
          <div class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full inline-block shrink-0" style="background:#f59e0b"></span>
            <span class="text-xs text-slate-500 dark:text-slate-400">{$t('status.in_progress' as any)}</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full inline-block shrink-0" style="background:#22c55e"></span>
            <span class="text-xs text-slate-500 dark:text-slate-400">{$t('status.done' as any)}</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full inline-block shrink-0" style="background:#a855f7"></span>
            <span class="text-xs text-slate-500 dark:text-slate-400">{$t('status.confirmed' as any)}</span>
          </div>
        </div>
      </div>

      <svg viewBox="0 0 {SVG_W} {SVG_H}" class="w-full">
        {#each gridTicks(dailyProgress.maxV) as tick}
          {@const gy = PAD_T + CHART_H * (1 - tick / dailyProgress.maxV)}
          <line x1={PAD_L} y1={gy} x2={SVG_W - PAD_R} y2={gy} stroke-width="0.5" stroke-dasharray="3,2" class="stroke-slate-200 dark:stroke-slate-700" />
          <text x={PAD_L - 4} y={gy + 3} text-anchor="end" font-size="8" class="fill-slate-400 dark:fill-slate-500">{tick}</text>
        {/each}
        <line x1={PAD_L} y1={Y_BOTTOM} x2={SVG_W - PAD_R} y2={Y_BOTTOM} stroke-width="0.5" class="stroke-slate-300 dark:stroke-slate-600" />

        {#each dailyProgress.rows as row, i}
          {@const x = barX(i)}
          {@const h_ip = CHART_H * (row.ip / dailyProgress.maxV)}
          {@const h_done = CHART_H * (row.done / dailyProgress.maxV)}
          {@const h_conf = CHART_H * (row.conf / dailyProgress.maxV)}
          {#if h_ip > 0}<rect x={x} y={Y_BOTTOM - h_ip} width={BAR_W} height={h_ip} fill="#f59e0b" rx="1" />{/if}
          {#if h_done > 0}<rect x={x} y={Y_BOTTOM - h_ip - h_done} width={BAR_W} height={h_done} fill="#22c55e" rx="1" />{/if}
          {#if h_conf > 0}<rect x={x} y={Y_BOTTOM - h_ip - h_done - h_conf} width={BAR_W} height={h_conf} fill="#a855f7" rx="1" />{/if}
          {#if i % 5 === 0}
            <text x={x + BAR_W / 2} y={Y_BOTTOM + 12} text-anchor="middle" font-size="8" class="fill-slate-400 dark:fill-slate-500">{fmtMMDD(row.day)}</text>
          {/if}
        {/each}
      </svg>
      <p class="text-xs text-slate-400 dark:text-slate-500 mt-2">{$t('report.progressNote')}</p>
    </div>

    <!-- Card 5: Daily Created -->
    <div class="md:col-span-3 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-700 p-5">
      <div class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-4">
        {$t('report.dailyCreated')}
      </div>
      <svg viewBox="0 0 {SVG_W} {SVG_H}" class="w-full">
        {#each gridTicks(dailyCreated.maxV) as tick}
          {@const gy = PAD_T + CHART_H * (1 - tick / dailyCreated.maxV)}
          <line x1={PAD_L} y1={gy} x2={SVG_W - PAD_R} y2={gy} stroke-width="0.5" stroke-dasharray="3,2" class="stroke-slate-200 dark:stroke-slate-700" />
          <text x={PAD_L - 4} y={gy + 3} text-anchor="end" font-size="8" class="fill-slate-400 dark:fill-slate-500">{tick}</text>
        {/each}
        <line x1={PAD_L} y1={Y_BOTTOM} x2={SVG_W - PAD_R} y2={Y_BOTTOM} stroke-width="0.5" class="stroke-slate-300 dark:stroke-slate-600" />
        {#each dailyCreated.rows as row, i}
          {@const x = barX(i)}
          {@const h = CHART_H * (row.count / dailyCreated.maxV)}
          {#if h > 0}<rect x={x} y={Y_BOTTOM - h} width={BAR_W} height={h} fill="#6366f1" rx="1" />{/if}
          {#if i % 5 === 0}
            <text x={x + BAR_W / 2} y={Y_BOTTOM + 12} text-anchor="middle" font-size="8" class="fill-slate-400 dark:fill-slate-500">{fmtMMDD(row.day)}</text>
          {/if}
        {/each}
      </svg>
    </div>

  </div>
</div>
