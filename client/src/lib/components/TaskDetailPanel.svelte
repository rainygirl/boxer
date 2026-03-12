<script lang="ts">
  import { tasksApi } from '$lib/api/tasks';
  import type { Task, TaskStatus, TaskPriority, User, TaskAttachment } from '$lib/types';
  import { TASK_STATUSES, PRIORITY_CONFIG } from '$lib/types';
  import AssigneePicker from './AssigneePicker.svelte';
  import { t, dateLocale } from '$lib/i18n';
  import { get } from 'svelte/store';

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
  let saving = $state(false);
  let dirty = $state(false);

  // Attachments
  let attachments = $state<TaskAttachment[]>([]);
  let uploading = $state(false);
  let uploadError = $state('');
  let dragOver = $state(false);
  let fileInputEl = $state<HTMLInputElement | null>(null);

  const statusCfg = $derived(TASK_STATUSES.find((s) => s.value === status)!);

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
      await tasksApi.update(task.id, { title, description, status, priority, assignee_id: assignee?.id ?? null });
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

<svelte:window onkeydown={(e) => e.key === 'Escape' && onClose()} />

<div class="fixed inset-0 z-50 flex">
  <div class="flex-1 bg-black/20" onclick={onClose}></div>
  <div class="w-[480px] bg-white dark:bg-slate-900 h-full shadow-2xl flex flex-col overflow-hidden border-l border-slate-200 dark:border-slate-700">
    <!-- Header -->
    <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-700">
      <span class="text-xs font-semibold px-2 py-0.5 rounded-full {statusCfg.color} {statusCfg.bg}">
        {$t(`status.${statusCfg.value}` as any)}
      </span>
      <div class="flex items-center gap-2">
        <button
          onclick={handleDelete}
          class="text-xs text-slate-400 hover:text-red-500 transition-colors px-2 py-1 rounded hover:bg-red-50 dark:hover:bg-red-500/10"
        >{$t('task.delete')}</button>
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
        class="w-full text-lg font-semibold text-slate-800 dark:text-slate-100 bg-transparent border-0 resize-none focus:outline-none focus:ring-2 focus:ring-brand-500 rounded-lg p-1 -ml-1"
      ></textarea>

      <div class="grid grid-cols-2 gap-3">
        <div>
          <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">{$t('task.status')}</label>
          <select
            bind:value={status}
            onchange={(e) => { quickUpdate({ status: e.currentTarget.value as TaskStatus }); }}
            class="w-full text-sm px-2.5 py-1.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            {#each TASK_STATUSES as s}
              <option value={s.value}>{$t(`status.${s.value}` as any)}</option>
            {/each}
          </select>
        </div>
        <div>
          <label class="block text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">{$t('task.priority')}</label>
          <select
            bind:value={priority}
            onchange={(e) => { quickUpdate({ priority: e.currentTarget.value as TaskPriority }); }}
            class="w-full text-sm px-2.5 py-1.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            {#each PRIORITY_CONFIG as p}
              <option value={p.value}>{p.icon} {$t(`priority.${p.value}` as any)}</option>
            {/each}
          </select>
        </div>
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
        <textarea
          bind:value={description}
          oninput={() => (dirty = true)}
          rows="6"
          placeholder={$t('task.descriptionEditPlaceholder')}
          class="w-full text-sm text-slate-700 dark:text-slate-200 px-3 py-2.5 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none placeholder:text-slate-400 dark:placeholder:text-slate-600"
        ></textarea>
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

      <div class="pt-2 border-t border-slate-100 dark:border-slate-700 space-y-1">
        <p class="text-xs text-slate-400 dark:text-slate-500">
          {$t('task.createdBy')} {task.created_by.name} · {new Date(task.created_at).toLocaleDateString($dateLocale)}
        </p>
        <p class="text-xs text-slate-400 dark:text-slate-500">{$t('task.updatedAt')} {new Date(task.updated_at).toLocaleDateString($dateLocale)}</p>
      </div>
    </div>

    {#if dirty}
      <div class="px-6 py-4 border-t border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
        <button
          onclick={handleSave}
          disabled={saving}
          class="w-full py-2 bg-brand-500 hover:bg-brand-600 text-white text-sm font-medium rounded-lg transition-colors disabled:opacity-50"
        >
          {saving ? $t('task.saving') : $t('task.saveChanges')}
        </button>
      </div>
    {/if}
  </div>
</div>
