<script lang="ts">
  import { invalidate } from '$app/navigation';
  import { projectsApi } from '$lib/api/projects';
  import type { Project } from '$lib/types';

  const { project, onClose, onOpenMembers }: { project: Project; onClose: () => void; onOpenMembers: () => void } = $props();

  let name = $state(project.name);
  let key = $state(project.key);
  let keyError = $state('');
  let nameError = $state('');
  let saving = $state(false);
  let saved = $state(false);

  function validateKey(v: string): string {
    if (!v) return '키를 입력해주세요';
    if (!/^[A-Z]{1,5}$/.test(v)) return '영문 대문자만, 최대 5자';
    return '';
  }

  function onKeyInput() {
    key = key.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 5);
    keyError = validateKey(key);
    saved = false;
  }

  function onNameInput() {
    nameError = name.trim() ? '' : '프로젝트명을 입력해주세요';
    saved = false;
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    nameError = name.trim() ? '' : '프로젝트명을 입력해주세요';
    keyError = validateKey(key);
    if (nameError || keyError) return;

    const unchanged = name.trim() === project.name && key === project.key;
    if (unchanged) { onClose(); return; }

    saving = true;
    try {
      await projectsApi.update(project.id, { name: name.trim(), key });
      await invalidate('app:projects');
      saved = true;
      setTimeout(onClose, 600);
    } catch (err: any) {
      const detail = err?.response?.data?.detail ?? '저장에 실패했습니다';
      // key-related errors go to keyError, others to nameError
      if (typeof detail === 'string' && detail.toLowerCase().includes('key')) {
        keyError = detail;
      } else {
        nameError = detail;
      }
    } finally {
      saving = false;
    }
  }
</script>

<svelte:window onkeydown={(e) => e.key === 'Escape' && onClose()} />

<div class="fixed inset-0 z-50 flex items-center justify-center">
  <div class="absolute inset-0 bg-black/30" onclick={onClose}></div>
  <div class="relative bg-white dark:bg-slate-900 rounded-2xl shadow-2xl w-full max-w-sm mx-4">
    <form onsubmit={handleSubmit}>
      <div class="flex items-center justify-between px-6 pt-5 pb-0">
        <h2 class="text-base font-semibold text-slate-800 dark:text-slate-100">프로젝트 설정</h2>
        <button type="button" onclick={onClose} class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 w-7 h-7 flex items-center justify-center rounded hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">✕</button>
      </div>
      <div class="p-6 space-y-4">

        <!-- 프로젝트명 -->
        <div>
          <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">
            프로젝트명
          </label>
          <input
            autofocus
            type="text"
            bind:value={name}
            oninput={onNameInput}
            placeholder="프로젝트 이름"
            class="w-full text-sm px-3 py-2 border rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100
                   placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500
                   {nameError ? 'border-red-400' : 'border-slate-200 dark:border-slate-600'}"
          />
          {#if nameError}
            <p class="mt-1 text-xs text-red-500">{nameError}</p>
          {/if}
        </div>

        <!-- 프로젝트 키 -->
        <div>
          <label class="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1.5">
            프로젝트 키 <span class="font-normal text-slate-400">(태스크 번호 접두사)</span>
          </label>
          <div class="flex items-center gap-3">
            <input
              type="text"
              bind:value={key}
              oninput={onKeyInput}
              maxlength="5"
              placeholder="예: PROJ"
              class="w-28 text-sm px-3 py-2 border rounded-lg bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100
                     placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500 font-mono uppercase tracking-widest
                     {keyError ? 'border-red-400' : 'border-slate-200 dark:border-slate-600'}"
            />
            <span class="text-xs text-slate-400 font-mono">{key || '??'}-1, {key || '??'}-2 …</span>
          </div>
          {#if keyError}
            <p class="mt-1 text-xs text-red-500">{keyError}</p>
          {/if}
        </div>
      </div>

      <div class="flex items-center justify-between px-6 py-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-100 dark:border-slate-700 rounded-b-2xl">
        <button
          type="button"
          onclick={() => { onClose(); onOpenMembers(); }}
          class="text-[12px] text-slate-400 dark:text-slate-500 hover:text-brand-500 dark:hover:text-brand-400 underline underline-offset-2 transition-colors"
        >멤버 관리</button>
        <div class="flex items-center gap-2">
        <button
          type="submit"
          disabled={!!keyError || !!nameError || saving || saved}
          class="px-4 py-2 text-sm font-medium rounded-lg transition-colors
                 {saved
                   ? 'bg-green-500 text-white'
                   : 'bg-brand-500 hover:bg-brand-600 text-white disabled:opacity-50'}"
        >
          {saved ? '저장됨 ✓' : saving ? '저장 중…' : '저장'}
        </button>
        </div>
      </div>
    </form>
  </div>
</div>
