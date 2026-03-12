<script lang="ts">
  const { value = '', onChange }: { value?: string; onChange: (v: string) => void } = $props();

  let editorEl = $state<HTMLDivElement | null>(null);
  let linkPopup = $state<{ anchor: HTMLAnchorElement; top: number; left: number } | null>(null);
  let linkHref = $state('');
  let linkInputEl = $state<HTMLInputElement | null>(null);

  let isComposing = false;
  let pendingEnter = false;
  let skipNextEnter = false;

  const BLOCK_TAGS = new Set(['P', 'H2', 'H3', 'H4', 'H5']);
  const HEADING_MAP: Record<string, string> = { '#': 'h2', '##': 'h3', '###': 'h4', '####': 'h5' };

  // ── Init ─────────────────────────────────────────────────────────────────
  $effect(() => {
    if (!editorEl || editorEl.dataset.init) return;
    editorEl.dataset.init = '1';
    editorEl.innerHTML = initHtml(value);
  });

  function initHtml(v: string): string {
    if (!v?.trim()) return '<p><br></p>';
    if (v.trimStart().startsWith('<')) return sanitizeHtml(v);
    return v.split('\n')
      .map(l => l.trim())
      .filter(Boolean)
      .map(l => `<p>${l.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>`)
      .join('') || '<p><br></p>';
  }

  // ── DOM helpers ───────────────────────────────────────────────────────────
  function getBlock(node: Node | null): HTMLElement | null {
    let n: Node | null = node;
    while (n && n !== editorEl) {
      if (n instanceof HTMLElement && BLOCK_TAGS.has(n.tagName)) return n;
      n = n.parentNode;
    }
    return null;
  }

  function setCursorAtEnd(el: HTMLElement) {
    const r = document.createRange();
    r.selectNodeContents(el);
    r.collapse(false);
    const s = window.getSelection();
    s?.removeAllRanges();
    s?.addRange(r);
  }

  function setCursorAtStart(el: HTMLElement) {
    const r = document.createRange();
    r.setStart(el, 0);
    r.collapse(true);
    const s = window.getSelection();
    s?.removeAllRanges();
    s?.addRange(r);
  }

  // ── Sanitize ──────────────────────────────────────────────────────────────
  function sanitizeHtml(html: string): string {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    const out = document.createElement('div');
    for (const child of Array.from(tmp.childNodes)) {
      if (child.nodeType === Node.TEXT_NODE) {
        const text = (child.textContent || '').trim();
        if (text) {
          const p = document.createElement('p');
          p.textContent = text;
          out.appendChild(p);
        }
      } else if (child instanceof HTMLElement) {
        if (BLOCK_TAGS.has(child.tagName)) {
          const el = document.createElement(child.tagName.toLowerCase()) as HTMLElement;
          el.innerHTML = sanitizeInline(child.innerHTML);
          out.appendChild(el);
        } else {
          const inner = sanitizeInline((child as HTMLElement).textContent || '');
          if (inner.trim()) {
            const p = document.createElement('p');
            p.innerHTML = inner;
            out.appendChild(p);
          }
        }
      }
    }
    if (!out.children.length) out.innerHTML = '<p><br></p>';
    return out.innerHTML;
  }

  function sanitizeInline(html: string): string {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    function walk(node: Node): string {
      if (node.nodeType === Node.TEXT_NODE) return node.textContent || '';
      if (node instanceof HTMLElement) {
        const children = Array.from(node.childNodes).map(walk).join('');
        const tag = node.tagName;
        if (tag === 'B' || tag === 'STRONG') return `<b>${children}</b>`;
        if (tag === 'A') {
          const href = (node.getAttribute('href') || '').replace(/"/g, '&quot;');
          return `<a href="${href}" target="_blank" rel="noopener noreferrer">${children}</a>`;
        }
        if (tag === 'BR') return '<br>';
        return children;
      }
      return '';
    }
    return Array.from(tmp.childNodes).map(walk).join('');
  }

  function normalizeBlocks() {
    if (!editorEl) return;
    for (const child of Array.from(editorEl.childNodes)) {
      if (child.nodeType === Node.TEXT_NODE) {
        if ((child.textContent || '').trim()) {
          const p = document.createElement('p');
          editorEl.insertBefore(p, child);
          p.appendChild(child);
        } else {
          editorEl.removeChild(child);
        }
      } else if (child instanceof HTMLElement && !BLOCK_TAGS.has(child.tagName)) {
        const p = document.createElement('p');
        p.innerHTML = child.innerHTML;
        child.replaceWith(p);
      }
    }
    for (const block of Array.from(editorEl.children)) {
      cleanBlockInlines(block as HTMLElement);
    }
    if (!editorEl.children.length) editorEl.innerHTML = '<p><br></p>';
  }

  function cleanBlockInlines(block: HTMLElement) {
    for (const nested of Array.from(block.querySelectorAll(Array.from(BLOCK_TAGS).map(t => t.toLowerCase()).join(',')))) {
      const parent = nested.parentNode!;
      while (nested.firstChild) parent.insertBefore(nested.firstChild, nested);
      parent.removeChild(nested);
    }
    function walk(node: Node) {
      for (const child of Array.from(node.childNodes)) {
        if (child.nodeType === Node.TEXT_NODE) continue;
        if (child instanceof HTMLElement) {
          const tag = child.tagName;
          if (tag === 'B' || tag === 'A' || tag === 'BR') { walk(child); continue; }
          const parent = child.parentNode!;
          while (child.firstChild) parent.insertBefore(child.firstChild, child);
          parent.removeChild(child);
        }
      }
    }
    walk(block);
  }

  function emit() {
    if (!editorEl) return;
    onChange(sanitizeHtml(editorEl.innerHTML));
  }

  // ── Heading shortcut (# + Space) ─────────────────────────────────────────
  function tryHeadingShortcut(block: HTMLElement): boolean {
    const text = (block.textContent || '').trimStart();
    const tag = HEADING_MAP[text];
    if (!tag) return false;
    const el = document.createElement(tag);
    el.innerHTML = '<br>';
    block.replaceWith(el);
    setCursorAtEnd(el);
    return true;
  }

  // ── Bold shortcut (**text**) ──────────────────────────────────────────────
  function tryBoldShortcut(block: HTMLElement): boolean {
    const html = block.innerHTML;
    if (!/\*\*(.+?)\*\*/.test(html)) return false;
    const CURSOR = '\x00C\x00';
    const replaced = html.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
    const lastClose = replaced.lastIndexOf('</b>');
    const marked = lastClose !== -1
      ? replaced.slice(0, lastClose + 4) + CURSOR + replaced.slice(lastClose + 4)
      : replaced + CURSOR;
    block.innerHTML = marked;
    const walker = document.createTreeWalker(block, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const tn = walker.currentNode as Text;
      const idx = (tn.textContent || '').indexOf(CURSOR);
      if (idx !== -1) {
        tn.textContent = tn.textContent!.replace(CURSOR, '');
        const r = document.createRange();
        r.setStart(tn, idx);
        r.collapse(true);
        window.getSelection()?.removeAllRanges();
        window.getSelection()?.addRange(r);
        return true;
      }
    }
    setCursorAtEnd(block);
    return true;
  }

  // ── Enter: split block (from CMS pattern) ────────────────────────────────
  function doEnterSplit() {
    const sel = window.getSelection();
    if (!sel?.rangeCount) return;
    const range = sel.getRangeAt(0);
    const block = getBlock(range.startContainer);
    if (!block) return;

    const newP = document.createElement('p');

    if (block.tagName === 'P') {
      const afterRange = document.createRange();
      afterRange.setStart(range.startContainer, range.startOffset);
      if (block.lastChild) afterRange.setEndAfter(block.lastChild);
      else afterRange.setEnd(block, block.childNodes.length);
      const frag = afterRange.extractContents();
      newP.appendChild(frag);
      if (!newP.textContent?.trim()) newP.innerHTML = '<br>';
      if (!block.textContent?.trim()) block.innerHTML = '<br>';
    } else {
      // Heading → exit to p
      newP.innerHTML = '<br>';
    }

    block.after(newP);
    setCursorAtStart(newP);
    emit();
  }

  // ── Keyboard ──────────────────────────────────────────────────────────────
  function handleKeydown(e: KeyboardEvent) {
    if (isComposing) return;

    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      triggerLinkEdit();
      return;
    }

    const sel = window.getSelection();
    if (!sel?.rangeCount) return;
    const range = sel.getRangeAt(0);
    const block = getBlock(range.startContainer);

    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (e.isComposing) { pendingEnter = true; return; }
      if (skipNextEnter) { skipNextEnter = false; return; }
      doEnterSplit();
      return;
    }

    if (e.key === ' ' && block) {
      if (tryHeadingShortcut(block)) {
        e.preventDefault();
        emit();
        return;
      }
    }

    if (e.key === 'Backspace' && block && range.collapsed) {
      // Start of heading → convert to p
      if (block.tagName !== 'P') {
        const before = document.createRange();
        before.setStart(block, 0);
        before.setEnd(range.startContainer, range.startOffset);
        if (before.toString().length === 0) {
          e.preventDefault();
          const p = document.createElement('p');
          p.innerHTML = block.innerHTML;
          block.replaceWith(p);
          setCursorAtStart(p);
          emit();
          return;
        }
      }
      // Empty block, prev exists → remove
      const isEmpty = block.innerHTML === '' || block.innerHTML === '<br>';
      if (isEmpty && block.previousElementSibling) {
        e.preventDefault();
        const prev = block.previousElementSibling as HTMLElement;
        setCursorAtEnd(prev);
        block.remove();
        emit();
        return;
      }
    }
  }

  function handleInput() {
    if (isComposing) return;
    const sel = window.getSelection();
    if (sel?.rangeCount) {
      const block = getBlock(sel.getRangeAt(0).startContainer);
      if (block) tryBoldShortcut(block);
    }
    normalizeBlocks();
    emit();
  }

  function handlePaste(e: ClipboardEvent) {
    e.preventDefault();
    const text = e.clipboardData?.getData('text/plain') || '';
    if (!text) return;
    const sel = window.getSelection();
    if (!sel?.rangeCount) return;
    const range = sel.getRangeAt(0);
    range.deleteContents();
    const lines = text.split(/\r?\n/);
    const frag = document.createDocumentFragment();
    for (let i = 0; i < lines.length; i++) {
      if (i > 0) frag.appendChild(document.createElement('br'));
      frag.appendChild(document.createTextNode(lines[i]));
    }
    range.insertNode(frag);
    range.collapse(false);
    sel.removeAllRanges();
    sel.addRange(range);
    setTimeout(() => { normalizeBlocks(); emit(); }, 0);
  }

  // ── Links ─────────────────────────────────────────────────────────────────
  function triggerLinkEdit() {
    const sel = window.getSelection();
    if (!sel?.rangeCount) return;
    let node: Node | null = sel.getRangeAt(0).startContainer;
    while (node && node !== editorEl) {
      if (node instanceof HTMLAnchorElement) { showLinkPopup(node); return; }
      node = node.parentNode;
    }
    if (!sel.isCollapsed) {
      document.execCommand('createLink', false, 'https://');
      // Find newly created anchor
      let a: HTMLAnchorElement | null = null;
      const anc = sel.anchorNode?.parentElement;
      if (anc?.tagName === 'A') a = anc as HTMLAnchorElement;
      else a = editorEl?.querySelector('a[href="https://"]') as HTMLAnchorElement | null;
      if (a) { a.target = '_blank'; a.rel = 'noopener noreferrer'; showLinkPopup(a); }
    }
  }

  function handleEditorClick(e: MouseEvent) {
    const a = (e.target as HTMLElement).closest?.('a') as HTMLAnchorElement | null;
    if (a && editorEl?.contains(a)) {
      e.preventDefault();
      showLinkPopup(a);
    } else {
      closeLinkPopup();
    }
  }

  function showLinkPopup(anchor: HTMLAnchorElement) {
    const rect = anchor.getBoundingClientRect();
    const left = Math.min(rect.left, window.innerWidth - 268);
    linkHref = anchor.getAttribute('href') || '';
    linkPopup = { anchor, top: rect.bottom + 6, left };
    setTimeout(() => linkInputEl?.select(), 0);
  }

  function closeLinkPopup() { linkPopup = null; linkHref = ''; }

  function applyLink() {
    if (!linkPopup) return;
    const { anchor } = linkPopup;
    const url = linkHref.trim();
    if (url) {
      anchor.href = url;
      anchor.target = '_blank';
      anchor.rel = 'noopener noreferrer';
    } else {
      const parent = anchor.parentNode!;
      while (anchor.firstChild) parent.insertBefore(anchor.firstChild, anchor);
      parent.removeChild(anchor);
    }
    closeLinkPopup();
    emit();
  }
</script>

<svelte:window onclick={() => closeLinkPopup()} />

<div class="rich-editor relative" onclick={(e) => e.stopPropagation()}>
  <div
    bind:this={editorEl}
    contenteditable="true"
    class="min-h-[120px] focus:outline-none"
    onkeydown={handleKeydown}
    oninput={handleInput}
    onclick={handleEditorClick}
    onpaste={handlePaste}
    oncompositionstart={() => (isComposing = true)}
    oncompositionend={() => {
      isComposing = false;
      if (pendingEnter) {
        pendingEnter = false;
        skipNextEnter = true;
        setTimeout(doEnterSplit, 0);
      }
      handleInput();
    }}
  ></div>
</div>

{#if linkPopup}
  {@const popup = linkPopup}
  <div
    onclick={(e) => e.stopPropagation()}
    style="position: fixed; top: {popup.top}px; left: {popup.left}px;"
    class="z-[300] bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl shadow-lg p-2 flex items-center gap-1.5 w-[260px]"
  >
    <input
      bind:this={linkInputEl}
      bind:value={linkHref}
      placeholder="https://..."
      onkeydown={(e) => {
        if (e.key === 'Enter') { e.preventDefault(); applyLink(); }
        if (e.key === 'Escape') { e.preventDefault(); closeLinkPopup(); }
      }}
      class="flex-1 min-w-0 text-xs px-2 py-1.5 bg-slate-50 dark:bg-slate-700 rounded-lg text-slate-700 dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-500"
    />
    <button
      onclick={() => popup.anchor.href && window.open(popup.anchor.href, '_blank', 'noopener noreferrer')}
      title="새 탭에서 열기"
      class="shrink-0 text-slate-400 hover:text-brand-500 w-6 h-6 flex items-center justify-center rounded text-xs hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
    >↗</button>
    <button
      onclick={() => { linkHref = ''; applyLink(); }}
      title="링크 제거"
      class="shrink-0 text-slate-400 hover:text-red-500 w-6 h-6 flex items-center justify-center rounded text-xs hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
    >✕</button>
    <button
      onclick={applyLink}
      class="shrink-0 text-xs bg-brand-500 hover:bg-brand-600 text-white px-2 py-1 rounded-lg transition-colors"
    >확인</button>
  </div>
{/if}

<style>
  .rich-editor :global(p) {
    font-size: 0.875rem;
    line-height: 1.65;
    margin: 0 0 0.2rem;
    min-height: 1.4em;
  }
  .rich-editor :global(h2) {
    font-size: 1.2rem;
    font-weight: 700;
    line-height: 1.3;
    margin: 0.75rem 0 0.25rem;
  }
  .rich-editor :global(h3) {
    font-size: 1.05rem;
    font-weight: 700;
    line-height: 1.3;
    margin: 0.6rem 0 0.2rem;
  }
  .rich-editor :global(h4) {
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0.5rem 0 0.15rem;
  }
  .rich-editor :global(h5) {
    font-size: 0.875rem;
    font-weight: 600;
    margin: 0.4rem 0 0.1rem;
  }
  .rich-editor :global(b) { font-weight: 700; }
  .rich-editor :global(a) {
    color: #6366f1;
    text-decoration: underline;
    text-underline-offset: 2px;
    cursor: pointer;
  }
  .rich-editor :global(*:last-child) { margin-bottom: 0; }
</style>
