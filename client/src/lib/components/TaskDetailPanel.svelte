<script lang="ts">
  import { tasksApi } from '$lib/api/tasks';
  import type { Task, TaskStatus, TaskPriority, User, TaskAttachment, TaskActivity, TaskDependencies, DependencyTask, SubTask } from '$lib/types';
  import { TASK_STATUSES, PRIORITY_CONFIG } from '$lib/types';
  import AssigneePicker from './AssigneePicker.svelte';
  import DatePicker from './DatePicker.svelte';
  import RichTextEditor from './RichTextEditor.svelte';
  import { t, dateLocale } from '$lib/i18n';
  import { get } from 'svelte/store';
  import { registerPopup, closeActivePopup, popupLeft } from '$lib/stores/popup';

  const {
    task,
    onClose,
    onUpdate,
  }: { task: Task; onClose: () => void; onUpdate: () => void } = $props();

  let title = $state(task.title);
  let description = $state(task.description);
  let status = $state<TaskStatus>(task.status);
  let priority = $state<TaskPriority>(task.priority);
  let assignee = $state<User | null>(task.assignee);
  let dueDate = $state(task.due_date ?? '');
  let saving = $state(false);
  let dirty = $state(false);
  let linkCopied = $state(false);

  function copyPermalink() {
    const url = new URL(window.location.href);
    navigator.clipboard.writeText(url.toString()).then(() => {
      linkCopied = true;
      setTimeout(() => (linkCopied = false), 2000);
    });
  }

  // Attachments
  let attachments = $state<TaskAttachment[]>([]);
  let uploading = $state(false);
  let uploadError = $state('');
  let dragOver = $state(false);
  let fileInputEl = $state<HTMLInputElement | null>(null);

  const statusCfg = $derived(TASK_STATUSES.find((s) => s.value === status)!);

  // ── Status popup ─────────────────────────────────────────────────────────
  let statusPopupOpen = $state(false);
  let statusBtnEl = $state<HTMLButtonElement | null>(null);

  // ── Priority popup ────────────────────────────────────────────────────────
  let priorityPopupOpen = $state(false);
  let priorityBtnEl = $state<HTMLButtonElement | null>(null);
  const priorityCfg = $derived(PRIORITY_CONFIG.find((p) => p.value === priority)!);

  function getPriorityPopupPos() {
    if (!priorityBtnEl) return { top: 0, left: 0 };
    const rect = priorityBtnEl.getBoundingClientRect();
    const popupH = PRIORITY_CONFIG.length * 34 + 8;
    const top = rect.bottom + 4 + popupH > window.innerHeight ? rect.top - popupH - 4 : rect.bottom + 4;
    return { top, left: popupLeft(rect.left, 160) };
  }

  function pickPriority(p: TaskPriority) {
    priorityPopupOpen = false;
    priority = p;
    dirty = true;
    quickUpdate({ priority: p });
  }

  function getStatusPopupPos() {
    if (!statusBtnEl) return { top: 0, left: 0 };
    const rect = statusBtnEl.getBoundingClientRect();
    const popupH = TASK_STATUSES.length * 34 + 8;
    const top = rect.bottom + 4 + popupH > window.innerHeight ? rect.top - popupH - 4 : rect.bottom + 4;
    return { top, left: popupLeft(rect.left, 150) };
  }

  function pickStatus(s: TaskStatus) {
    statusPopupOpen = false;
    status = s;
    dirty = true;
    quickUpdate({ status: s });
  }

  $effect(() => {
    tasksApi.listAttachments(task.id).then((a) => (attachments = a)).catch(() => {});
  });

  async function quickUpdate(data: Parameters<typeof tasksApi.update>[1]) {
    await tasksApi.update(task.id, data);
    onUpdate();
  }

  async function handleSave() {
    saving = true;
    try {
      await tasksApi.update(task.id, { title, description, status, priority, assignee_id: assignee?.id ?? null, due_date: dueDate || null });
      dirty = false;
      onUpdate();
    } finally {
      saving = false;
    }
  }

  async function handleDelete() {
    if (!confirm(get(t)('task.deleteConfirm'))) return;
    await tasksApi.delete(task.id);
    onUpdate();
    onClose();
  }

  async function uploadFiles(files: FileList | File[]) {
    const list = Array.from(files);
    if (!list.length) return;
    uploading = true;
    uploadError = '';
    try {
      for (const file of list) {
        const att = await tasksApi.uploadAttachment(task.id, file);
        attachments = [...attachments, att];
      }
    } catch (e: any) {
      const msg = e?.response?.data?.detail;
      uploadError = msg === 'File storage is not configured'
        ? 'R2가 설정되지 않았습니다. .env를 확인하세요.'
        : msg === 'File too large (max 50 MB)'
        ? '파일이 너무 큽니다 (최대 50MB).'
        : '업로드에 실패했습니다.';
    } finally {
      uploading = false;
    }
  }

  async function handleRemoveAttachment(att: TaskAttachment) {
    await tasksApi.deleteAttachment(task.id, att.id);
    attachments = attachments.filter((a) => a.id !== att.id);
  }

  function handleDrop(e: DragEvent) {
    e.preventDefault();
    dragOver = false;
    if (e.dataTransfer?.files) uploadFiles(e.dataTransfer.files);
  }

  // Activities
  let activities = $state<TaskActivity[]>([]);

  $effect(() => {
    tasksApi.listActivities(task.id).then((a) => (activities = a)).catch(() => {});
  });

  // ── Korean particle helpers ────────────────────────────────────────────────
  function kHasBatchim(ch: string): boolean {
    const c = ch.charCodeAt(0);
    if (c >= 0xAC00 && c <= 0xD7A3) return (c - 0xAC00) % 28 !== 0;
    // 숫자 받침 (한국어 읽기 기준)
    return { '0': true, '1': true, '3': true, '6': true, '7': true, '8': true }[ch] ?? false;
  }
  function kHasRieulBatchim(ch: string): boolean {
    const c = ch.charCodeAt(0);
    if (c >= 0xAC00 && c <= 0xD7A3) return (c - 0xAC00) % 28 === 8;
    return ['1', '7', '8'].includes(ch); // 일, 칠, 팔
  }
  function josa(word: string, type: 'ro' | 'i' | 'eul'): string {
    if (!word) return '';
    const last = word[word.length - 1];
    const b = kHasBatchim(last);
    const r = kHasRieulBatchim(last);
    if (type === 'ro')  return (b && !r) ? '으로' : '로';
    if (type === 'i')   return b ? '이' : '가';
    if (type === 'eul') return b ? '을' : '를';
    return '';
  }
  function subjectParticle(name: string, locale: string): string {
    return locale === 'ko-KR' ? josa(name, 'i') : '';
  }

  function getActivityText(translate: (key: any, vars?: Record<string, string>) => string, act: TaskActivity, locale: string): string {
    const d = act.data;
    const ko = locale === 'ko-KR';
    const ro  = (w: string) => ko ? josa(w, 'ro')  : '';
    const eul = (w: string) => ko ? josa(w, 'eul') : '';

    switch (act.activity_type) {
      case 'created':
        return translate('activity.created');
      case 'status_changed': {
        const from = translate(`status.${d.from}` as any);
        const to   = translate(`status.${d.to}` as any);
        return translate('activity.status_changed', { from, to, ro: ro(to) });
      }
      case 'priority_changed': {
        const from = translate(`priority.${d.from}` as any);
        const to   = translate(`priority.${d.to}` as any);
        return translate('activity.priority_changed', { from, to, ro: ro(to) });
      }
      case 'assignee_changed': {
        const toName   = d.to_name   ?? translate('activity.unassigned');
        const fromName = d.from_name ?? translate('activity.unassigned');
        if (!d.from_name) return translate('activity.assignee_set',     { to: toName,   eul: eul(toName) });
        if (!d.to_name)   return translate('activity.assignee_removed',  { from: fromName, eul: eul(fromName) });
        return translate('activity.assignee_changed', { from: fromName, to: toName, ro: ro(toName) });
      }
      case 'content_edited':
        return translate('activity.content_edited');
      case 'due_date_changed': {
        const from = d.from ?? '';
        const to   = d.to   ?? '';
        if (!d.from) return translate('activity.due_date_set',     { to, ro: ro(to) });
        if (!d.to)   return translate('activity.due_date_removed');
        return translate('activity.due_date_changed', { from, to, ro: ro(to) });
      }
      case 'project_moved': {
        const to = d.to_project ?? '';
        return translate('activity.project_moved', { from: d.from_project ?? '', to, ro: ro(to) });
      }
      default:
        return act.activity_type;
    }
  }

  function relativeTime(dateStr: string, locale: string): string {
    const diff = Date.now() - new Date(dateStr).getTime();
    const seconds = Math.floor(diff / 1000);
    const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' });
    if (seconds < 60) return rtf.format(-seconds, 'second');
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return rtf.format(-minutes, 'minute');
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return rtf.format(-hours, 'hour');
    const days = Math.floor(hours / 24);
    if (days < 30) return rtf.format(-days, 'day');
    const months = Math.floor(days / 30);
    if (months < 12) return rtf.format(-months, 'month');
    return rtf.format(-Math.floor(months / 12), 'year');
  }

  // Subtasks — initialize from task prop, keep local state for optimistic updates
  let subtasks = $state<SubTask[]>(task.subtasks ?? []);
  let newSubtaskTitle = $state('');
  let addingSubtask = $state(false);
  let subtaskInputEl = $state<HTMLInputElement | null>(null);

  async function toggleSubtask(sub: SubTask) {
    const updated = await tasksApi.updateSubtask(task.id, sub.id, { is_done: sub.status !== 'done' });
    subtasks = subtasks.map((s) => (s.id === sub.id ? updated : s));
    onUpdate();
  }

  async function addSubtask() {
    const title = newSubtaskTitle.trim();
    if (!title) return;
    const created = await tasksApi.createSubtask(task.id, { title });
    subtasks = [...subtasks, created];
    newSubtaskTitle = '';
    addingSubtask = false;
    onUpdate();
  }

  async function removeSubtask(sub: SubTask) {
    await tasksApi.deleteSubtask(task.id, sub.id);
    subtasks = subtasks.filter((s) => s.id !== sub.id);
    onUpdate();
  }

  // Dependencies
  let deps = $state<TaskDependencies>({ blocking: [], blocked: [] });
  let depSearch = $state('');
  let depResults = $state<DependencyTask[]>([]);
  let depSearching = $state(false);
  let depInputEl = $state<HTMLInputElement | null>(null);
  let showDepSearch = $state(false);

  $effect(() => {
    tasksApi.listDependencies(task.id).then((d) => (deps = d)).catch(() => {});
  });

  const DONE_STATUSES = new Set(['done', 'confirmed', 'cancelled']);

  async function searchDeps(q: string) {
    if (!q.trim()) { depResults = []; return; }
    depSearching = true;
    try {
      // Search all tasks the user can access via the tasks API
      // We'll use the project's task list — fetch from project endpoint
      const all = await tasksApi.list(task.project_id);
      const lower = q.toLowerCase();
      depResults = (all as any[])
        .filter((t: any) =>
          t.id !== task.id &&
          !deps.blocking.some((d) => d.id === t.id) &&
          (t.ref.toLowerCase().includes(lower) || t.title.toLowerCase().includes(lower))
        )
        .slice(0, 8) as DependencyTask[];
    } finally {
      depSearching = false;
    }
  }

  async function addDep(blockingId: string) {
    try {
      deps = await tasksApi.addDependency(task.id, blockingId);
      depSearch = '';
      depResults = [];
      showDepSearch = false;
    } catch (e: any) {
      const msg = e?.response?.data?.detail ?? '';
      alert(msg.includes('Circular') ? $t('dependency.circular') : msg);
    }
  }

  async function removeDep(blockingId: string) {
    await tasksApi.removeDependency(task.id, blockingId);
    deps = { ...deps, blocking: deps.blocking.filter((d) => d.id !== blockingId) };
  }

  function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }

  function fileIcon(contentType: string): string {
    if (contentType.startsWith('image/')) return '🖼️';
    if (contentType.startsWith('video/')) return '🎬';
    if (contentType.includes('pdf')) return '📄';
    if (contentType.includes('zip') || contentType.includes('compressed')) return '🗜️';
    if (contentType.includes('spreadsheet') || contentType.includes('excel')) return '📊';
    if (contentType.includes('document') || contentType.includes('word')) return '📝';
    return '📎';
  }
</script>

<svelte:window
  onkeydown={(e) => e.key === 'Escape' && onClose()}
  onclick={() => closeActivePopup()}
/>

<div class="fixed inset-0 z-50 flex">
  <div class="hidden md:block md:flex-1 bg-black/60" onclick={onClose}></div>
  <div class="w-full md:w-[480px] bg-white dark:bg-slate-900 h-full shadow-2xl flex flex-col overflow-hidden border-l border-slate-200 dark:border-slate-700 select-none">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-700">
      <span class="text-xs font-mono text-slate-400 dark:text-slate-500">{task.ref}</span>
      <div class="flex items-center gap-1">
        <button
          onclick={copyPermalink}
          title="링크 복사"
          class="text-slate-300 dark:text-slate-600 hover:text-slate-500 dark:hover:text-slate-400 w-7 h-7 flex items-center justify-center rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          {#if linkCopied}
            <span class="text-xs text-green-500">✓</span>
          {:else}
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          {/if}
        </button>
        <button
          onclick={onClose}
          class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 w-7 h-7 flex items-center justify-center rounded hover:bg-slate-100 dark:hover:bg-slate-800"
        >✕</button>
      </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-y-auto p-6 space-y-4 scrollbar-thin">
      <textarea
        autofocus
        bind:value={title}
        oninput={() => (dirty = true)}
        rows="2"
        placeholder={$t('task.titleEditPlaceholder')}
        class="w-full text-lg font-semibold text-slate-800 dark:text-slate-100 bg-transparent border-0 resize-none focus:outline-none focus:ring-2 focus:ring-brand-500 rounded-lg p-1 -ml-1 select-text"
      ></textarea>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">{$t('task.status')}</label>
          <button
            bind:this={statusBtnEl}
            onclick={(e) => { e.stopPropagation(); if (statusPopupOpen) { statusPopupOpen = false; closeActivePopup(); } else { statusPopupOpen = true; priorityPopupOpen = false; registerPopup(() => { statusPopupOpen = false; }); } }}
            class="flex items-center gap-2 w-full px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 cursor-pointer hover:border-slate-300 dark:hover:border-slate-500 transition-colors"
          >
            <span class="text-xs font-medium px-2 py-0.5 rounded-full {statusCfg.color} {statusCfg.bg}">
              {$t(`status.${status}` as any)}
            </span>
            <svg class="w-3 h-3 text-slate-400 ml-auto shrink-0" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="1,1 5,5 9,1"/>
            </svg>
          </button>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">{$t('task.priority')}</label>
          <button
            bind:this={priorityBtnEl}
            onclick={(e) => { e.stopPropagation(); if (priorityPopupOpen) { priorityPopupOpen = false; closeActivePopup(); } else { priorityPopupOpen = true; statusPopupOpen = false; registerPopup(() => { priorityPopupOpen = false; }); } }}
            class="flex items-center gap-2 w-full px-2.5 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 cursor-pointer hover:border-slate-300 dark:hover:border-slate-500 transition-colors"
          >
            <span class="text-base leading-none">{priorityCfg.icon}</span>
            <span class="text-sm text-slate-700 dark:text-slate-200">{$t(`priority.${priority}` as any)}</span>
            <svg class="w-3 h-3 text-slate-400 ml-auto shrink-0" viewBox="0 0 10 6" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="1,1 5,5 9,1"/>
            </svg>
          </button>
        </div>
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">{$t('task.dueDate')}</label>
        <DatePicker
          value={dueDate}
          placeholder={$t('task.dueDate')}
          onChange={(v) => {
            dueDate = v;
            dirty = true;
            quickUpdate({ due_date: v || null });
          }}
        />
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">{$t('task.assignee')}</label>
        <AssigneePicker
          value={assignee}
          onChange={(u) => { assignee = u; dirty = true; }}
        />
      </div>

      <div>
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">{$t('task.description')}</label>
        <div class="px-3 py-2.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus-within:ring-2 focus-within:ring-brand-500 focus-within:border-transparent min-h-[120px]">
          <RichTextEditor
            value={description}
            onChange={(html) => { description = html; dirty = true; }}
          />
        </div>
      </div>

      <!-- Attachments -->
      <div>
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-2">{$t('attachment.label')}</label>

        <!-- Drop zone -->
        <div
          role="button"
          tabindex="0"
          onclick={() => fileInputEl?.click()}
          onkeydown={(e) => e.key === 'Enter' && fileInputEl?.click()}
          ondragover={(e) => { e.preventDefault(); dragOver = true; }}
          ondragleave={() => (dragOver = false)}
          ondrop={handleDrop}
          class="border-2 border-dashed rounded-lg px-4 py-5 text-center cursor-pointer transition-colors {dragOver
            ? 'border-brand-400 bg-brand-50 dark:bg-brand-500/10'
            : 'border-slate-200 dark:border-slate-700 hover:border-brand-300 dark:hover:border-brand-600 hover:bg-slate-50 dark:hover:bg-slate-800/50'}"
        >
          {#if uploading}
            <p class="text-sm text-slate-400 dark:text-slate-500 animate-pulse">{$t('attachment.uploading')}</p>
          {:else}
            <p class="text-sm text-slate-400 dark:text-slate-500">{$t('attachment.dropHint')}</p>
            <p class="text-xs text-slate-300 dark:text-slate-600 mt-0.5">{$t('attachment.maxSize')}</p>
          {/if}
        </div>
        <input
          bind:this={fileInputEl}
          type="file"
          multiple
          class="hidden"
          onchange={(e) => { const f = (e.currentTarget as HTMLInputElement).files; if (f) uploadFiles(f); }}
        />

        {#if uploadError}
          <p class="text-xs text-red-500 mt-1">{uploadError}</p>
        {/if}

        <!-- File list -->
        {#if attachments.length > 0}
          <!-- 이미지 썸네일 그리드 -->
          {@const images = attachments.filter((a) => a.content_type.startsWith('image/'))}
          {@const others = attachments.filter((a) => !a.content_type.startsWith('image/'))}

          {#if images.length > 0}
            <div class="mt-2 grid grid-cols-3 gap-1.5">
              {#each images as att (att.id)}
                <div class="relative group aspect-square rounded-lg overflow-hidden bg-slate-100 dark:bg-slate-800">
                  <a href={att.url} target="_blank" rel="noopener noreferrer">
                    <img
                      src={att.url}
                      alt={att.filename}
                      class="w-full h-full object-cover hover:opacity-90 transition-opacity"
                    />
                  </a>
                  <button
                    onclick={() => handleRemoveAttachment(att)}
                    class="absolute top-1 right-1 opacity-0 group-hover:opacity-100 w-5 h-5 rounded-full bg-black/50 text-white text-[10px] flex items-center justify-center transition-all hover:bg-red-500"
                  >✕</button>
                </div>
              {/each}
            </div>
          {/if}

          <!-- 일반 파일 목록 -->
          {#if others.length > 0}
            <ul class="mt-2 space-y-1">
              {#each others as att (att.id)}
                <li class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 group">
                  <span class="text-base shrink-0">{fileIcon(att.content_type)}</span>
                  <a
                    href={att.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="flex-1 min-w-0"
                  >
                    <p class="text-sm text-slate-700 dark:text-slate-200 truncate hover:text-brand-600 dark:hover:text-brand-400 transition-colors">{att.filename}</p>
                    <p class="text-xs text-slate-400 dark:text-slate-500">{formatSize(att.size)}</p>
                  </a>
                  <button
                    onclick={() => handleRemoveAttachment(att)}
                    class="opacity-0 group-hover:opacity-100 text-slate-300 dark:text-slate-600 hover:text-red-400 transition-all shrink-0"
                  >✕</button>
                </li>
              {/each}
            </ul>
          {/if}
        {/if}
      </div>

      <!-- Subtasks -->
      <div>
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-2">
          {$t('subtask.title')}
          {#if subtasks.length > 0}
            <span class="ml-1 font-normal text-slate-300 dark:text-slate-600">
              ({subtasks.filter((s) => s.status === 'done').length}/{subtasks.length})
            </span>
          {/if}
        </label>

        {#if subtasks.length > 0}
          <div class="h-1 rounded-full bg-slate-100 dark:bg-slate-700 mb-3 overflow-hidden">
            <div
              class="h-full rounded-full bg-green-500 transition-all duration-300"
              style="width: {(subtasks.filter((s) => s.status === 'done').length / subtasks.length * 100).toFixed(0)}%"
            ></div>
          </div>

          <div class="space-y-0.5">
            {#each subtasks as sub (sub.id)}
              <div class="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 group transition-colors">
                <input
                  type="checkbox"
                  checked={sub.status === 'done'}
                  onchange={() => toggleSubtask(sub)}
                  class="w-4 h-4 rounded border-slate-300 dark:border-slate-600 text-brand-500 focus:ring-brand-500 shrink-0 cursor-pointer"
                />
                <span class="text-[10px] font-mono text-slate-300 dark:text-slate-600 shrink-0">{sub.ref}</span>
                <span class="flex-1 text-sm text-slate-700 dark:text-slate-200 {sub.status === 'done' ? 'line-through text-slate-400 dark:text-slate-500' : ''} truncate">
                  {sub.title}
                </span>
                {#if sub.assignee}
                  <div class="w-5 h-5 rounded-full overflow-hidden shrink-0" title={sub.assignee.name}>
                    {#if sub.assignee.avatar_url}
                      <img src={sub.assignee.avatar_url} class="w-full h-full object-cover" alt="" />
                    {:else}
                      <div class="w-full h-full bg-brand-400 text-white text-[9px] flex items-center justify-center">
                        {sub.assignee.name[0]}
                      </div>
                    {/if}
                  </div>
                {/if}
                <button
                  onclick={() => removeSubtask(sub)}
                  class="opacity-0 group-hover:opacity-100 text-slate-300 dark:text-slate-600 hover:text-red-400 transition-all text-xs leading-none shrink-0"
                >✕</button>
              </div>
            {/each}
          </div>
        {/if}

        {#if addingSubtask}
          <div class="flex items-center gap-2 mt-2">
            <input
              bind:this={subtaskInputEl}
              bind:value={newSubtaskTitle}
              placeholder={$t('subtask.placeholder')}
              onkeydown={(e) => {
                if (e.key === 'Enter') addSubtask();
                if (e.key === 'Escape') { addingSubtask = false; newSubtaskTitle = ''; }
              }}
              class="flex-1 text-sm px-2.5 py-1.5 bg-white dark:bg-slate-800 border border-brand-400 dark:border-brand-500 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-800 dark:text-slate-100 placeholder:text-slate-400"
            />
            <button onclick={addSubtask} class="text-xs px-2.5 py-1.5 bg-brand-500 hover:bg-brand-600 text-white rounded-lg transition-colors">{$t('subtask.add')}</button>
            <button onclick={() => { addingSubtask = false; newSubtaskTitle = ''; }} class="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors">{$t('common.cancel')}</button>
          </div>
        {:else}
          <button
            onclick={() => { addingSubtask = true; setTimeout(() => subtaskInputEl?.focus(), 0); }}
            class="mt-1 flex items-center gap-1.5 text-xs text-slate-400 dark:text-slate-500 hover:text-brand-600 dark:hover:text-brand-400 transition-colors"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
            </svg>
            {$t('subtask.addButton')}
          </button>
        {/if}
      </div>

      <!-- Dependencies -->
      <div class="mt-4 pt-4 border-t border-slate-100/60 dark:border-slate-700/40">
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-2">{$t('dependency.title')}</label>

        <!-- Blocked by (먼저 해결되어야 하는 이슈) -->
        {#if deps.blocking.length > 0}
          <div class="mb-2">
            <p class="text-[11px] text-slate-400 dark:text-slate-500 mb-1.5 flex items-center gap-1">
              <svg class="w-3 h-3 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"/>
              </svg>
              {$t('dependency.blocking')}
            </p>
            <div class="space-y-1">
              {#each deps.blocking as dep (dep.id)}
                {@const done = DONE_STATUSES.has(dep.status)}
                {@const statusCfgDep = TASK_STATUSES.find((s) => s.value === dep.status)!}
                <div class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg {done ? 'bg-green-50 dark:bg-green-900/10 border border-green-200 dark:border-green-800/40' : 'bg-amber-50 dark:bg-amber-900/10 border border-amber-200 dark:border-amber-800/40'}">
                  {#if done}
                    <svg class="w-3.5 h-3.5 shrink-0 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>
                    </svg>
                  {:else}
                    <svg class="w-3.5 h-3.5 shrink-0 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z"/>
                    </svg>
                  {/if}
                  <span class="text-[11px] font-mono text-slate-400 dark:text-slate-500 shrink-0">{dep.ref}</span>
                  <span class="text-xs text-slate-700 dark:text-slate-200 truncate flex-1">{dep.title}</span>
                  <span class="text-[10px] font-medium px-1.5 py-0.5 rounded-full shrink-0 {statusCfgDep.color} {statusCfgDep.bg}">
                    {$t(`status.${dep.status}` as any)}
                  </span>
                  <button onclick={() => removeDep(dep.id)} class="shrink-0 text-slate-300 dark:text-slate-600 hover:text-red-400 transition-colors text-xs leading-none">✕</button>
                </div>
              {/each}
            </div>
            {#if deps.blocking.some((d) => !DONE_STATUSES.has(d.status))}
              <p class="text-[11px] text-amber-600 dark:text-amber-400 mt-1.5 flex items-center gap-1">
                <svg class="w-3 h-3 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495ZM10 5a.75.75 0 0 1 .75.75v3.5a.75.75 0 0 1-1.5 0v-3.5A.75.75 0 0 1 10 5Zm0 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clip-rule="evenodd"/>
                </svg>
                {$t('dependency.waitingFor', { ref: deps.blocking.filter((d) => !DONE_STATUSES.has(d.status)).map((d) => d.ref).join(', ') })}
              </p>
            {/if}
          </div>
        {/if}

        <!-- Blocking (이 이슈를 기다리는 이슈) -->
        {#if deps.blocked.length > 0}
          <div class="mb-2">
            <p class="text-[11px] text-slate-400 dark:text-slate-500 mb-1.5">{$t('dependency.blocked')}</p>
            <div class="space-y-1">
              {#each deps.blocked as dep (dep.id)}
                {@const statusCfgDep = TASK_STATUSES.find((s) => s.value === dep.status)!}
                <div class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                  <span class="text-[11px] font-mono text-slate-400 dark:text-slate-500 shrink-0">{dep.ref}</span>
                  <span class="text-xs text-slate-700 dark:text-slate-200 truncate flex-1">{dep.title}</span>
                  <span class="text-[10px] font-medium px-1.5 py-0.5 rounded-full shrink-0 {statusCfgDep.color} {statusCfgDep.bg}">
                    {$t(`status.${dep.status}` as any)}
                  </span>
                </div>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Add dependency -->
        {#if showDepSearch}
          <div class="relative">
            <input
              bind:this={depInputEl}
              bind:value={depSearch}
              oninput={() => searchDeps(depSearch)}
              onkeydown={(e) => e.key === 'Escape' && (showDepSearch = false)}
              placeholder={$t('dependency.search')}
              class="w-full text-sm px-3 py-1.5 border border-brand-400 dark:border-brand-500 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
            {#if depResults.length > 0}
              <div class="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg z-10 overflow-hidden">
                {#each depResults as r (r.id)}
                  {@const statusCfgR = TASK_STATUSES.find((s) => s.value === r.status)!}
                  <button
                    onclick={() => addDep(r.id)}
                    class="w-full flex items-center gap-2 px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-left"
                  >
                    <span class="text-[11px] font-mono text-slate-400 shrink-0">{r.ref}</span>
                    <span class="text-sm text-slate-700 dark:text-slate-200 truncate flex-1">{r.title}</span>
                    <span class="text-[10px] px-1.5 py-0.5 rounded-full shrink-0 {statusCfgR.color} {statusCfgR.bg}">{$t(`status.${r.status}` as any)}</span>
                  </button>
                {/each}
              </div>
            {:else if depSearch && !depSearching}
              <div class="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg z-10 px-3 py-2 text-sm text-slate-400 dark:text-slate-500">
                {$t('dependency.noResults')}
              </div>
            {/if}
          </div>
        {:else}
          <button
            onclick={() => { showDepSearch = true; setTimeout(() => depInputEl?.focus(), 0); }}
            class="flex items-center gap-1.5 text-xs text-slate-400 dark:text-slate-500 hover:text-brand-600 dark:hover:text-brand-400 transition-colors mt-1"
          >
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/>
            </svg>
            {$t('dependency.add')}
          </button>
        {/if}
      </div>

      <!-- Activity History -->
      <div class="mt-4 pt-4 border-t border-slate-100/60 dark:border-slate-700/40">
        <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-3">{$t('activity.title')}</label>
        {#if activities.length === 0}
          <p class="text-xs text-slate-300 dark:text-slate-600 py-1">—</p>
        {:else}
          <div class="space-y-3">
            {#each activities as act (act.id)}
              <div class="flex gap-2 items-start">
                {#if act.user?.avatar_url}
                  <img src={act.user.avatar_url} alt={act.user.name} class="w-5 h-5 rounded-full shrink-0 mt-0.5 object-cover" />
                {:else if act.user}
                  <div class="w-5 h-5 rounded-full shrink-0 mt-0.5 bg-brand-500 flex items-center justify-center text-[9px] font-bold text-white">
                    {act.user.name.charAt(0).toUpperCase()}
                  </div>
                {:else}
                  <div class="w-5 h-5 rounded-full shrink-0 mt-0.5 bg-slate-200 dark:bg-slate-700"></div>
                {/if}
                <div class="flex-1 min-w-0">
                  <p class="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                    {#if act.user}<span class="font-medium">{act.user.name}</span>{subjectParticle(act.user.name, $dateLocale)}{' '}{/if}{getActivityText($t, act, $dateLocale)}</p>
                  <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">{relativeTime(act.created_at, $dateLocale)}</p>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <div class="space-y-1">
        <p class="text-xs text-slate-400 dark:text-slate-500">
          {$t('task.createdBy')} {task.created_by.name} · {new Date(task.created_at).toLocaleDateString($dateLocale)}
        </p>
        <p class="text-xs text-slate-400 dark:text-slate-500">{$t('task.updatedAt')} {new Date(task.updated_at).toLocaleDateString($dateLocale)}</p>
      </div>

      <!-- Save / Delete — 스크롤 영역 안에 두어 설명이 가려지지 않게 함 -->
      <div class="pt-2 space-y-2">
        {#if dirty}
          <button
            onclick={handleSave}
            disabled={saving}
            class="w-full py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
          >
            {saving ? $t('task.saving') : $t('task.saveChanges')}
          </button>
        {/if}
        <div class="flex justify-end pb-2">
          <button
            onclick={handleDelete}
            class="flex items-center gap-1 text-[12px] text-slate-400 dark:text-slate-500 hover:text-red-400 dark:hover:text-red-400 transition-colors"
          >
            <svg class="w-3 h-3 shrink-0" viewBox="0 0 14 14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M2 3.5h10M5 3.5V2.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 .5.5v1M5.5 6v4.5M8.5 6v4.5M3 3.5l.7 7.5a.5.5 0 0 0 .5.5h5.6a.5.5 0 0 0 .5-.5L11 3.5"/>
            </svg>
            {$t('task.delete')}
          </button>
        </div>
      </div>
    </div>
  </div>
</div>

{#if statusPopupOpen}
  {@const pos = getStatusPopupPos()}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {pos.top}px; left: {pos.left}px;"
    class="z-[300] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden min-w-[160px] py-1"
  >
    {#each TASK_STATUSES as s}
      <button
        onclick={() => pickStatus(s.value)}
        class="w-full flex items-center gap-2 px-3 py-2 text-xs transition-colors hover:bg-slate-50 dark:hover:bg-slate-700 {status === s.value ? 'bg-slate-50 dark:bg-slate-700' : ''}"
      >
        <span class="inline-block px-2 py-0.5 rounded-full font-medium {s.color} {s.bg}">
          {$t(`status.${s.value}` as any)}
        </span>
      </button>
    {/each}
  </div>
{/if}

{#if priorityPopupOpen}
  {@const pos = getPriorityPopupPos()}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {pos.top}px; left: {pos.left}px;"
    class="z-[300] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg overflow-hidden min-w-[150px] py-1"
  >
    {#each PRIORITY_CONFIG as p}
      <button
        onclick={() => pickPriority(p.value)}
        class="w-full flex items-center gap-2 px-3 py-2 text-sm transition-colors hover:bg-slate-50 dark:hover:bg-slate-700 {priority === p.value ? 'bg-slate-50 dark:bg-slate-700' : ''}"
      >
        <span class="text-base leading-none">{p.icon}</span>
        <span class="text-slate-700 dark:text-slate-200">{$t(`priority.${p.value}` as any)}</span>
      </button>
    {/each}
  </div>
{/if}
