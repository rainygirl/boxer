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
    onChange(sanitizeHtml(editorEl.innerHTML).replace(/\u200B/g, ''));
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

  // ── URL auto-link (Space or Enter after a URL) ───────────────────────────
  function tryAutoLink(): boolean {
    const sel = window.getSelection();
    if (!sel?.rangeCount || !sel.getRangeAt(0).collapsed) return false;
    const range = sel.getRangeAt(0);
    const { startContainer, startOffset } = range;
    if (startContainer.nodeType !== Node.TEXT_NODE) return false;

    // Skip if already inside an <a>
    let n: Node | null = startContainer.parentNode;
    while (n && n !== editorEl) {
      if (n instanceof HTMLAnchorElement) return false;
      n = n.parentNode;
    }

    const textBefore = (startContainer.textContent || '').slice(0, startOffset);
    // Find a URL ending exactly at the cursor
    const urlMatch = textBefore.match(/https?:\/\/\S+$/);
    if (!urlMatch) return false;

    // Strip trailing punctuation that isn't part of the URL
    let url = urlMatch[0].replace(/[.,;:!?'")>\]]+$/, '');
    if (url.length < 9) return false; // shorter than https://x

    const textNode = startContainer as Text;
    const fullText = textNode.textContent!;
    const urlStartInFull = startOffset - urlMatch[0].length;
    const before = fullText.slice(0, urlStartInFull);
    // keep stripped trailing punct + anything after cursor as plain text
    const after = urlMatch[0].slice(url.length) + fullText.slice(startOffset);

    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.rel = 'noopener noreferrer';
    a.textContent = url;

    const afterNode = document.createTextNode(after);
    const parent = textNode.parentNode!;
    if (before) parent.insertBefore(document.createTextNode(before), textNode);
    parent.insertBefore(a, textNode);
    parent.insertBefore(afterNode, textNode);
    parent.removeChild(textNode);

    // Place cursor at start of afterNode so the trigger key (space/enter) lands there
    const newRange = document.createRange();
    newRange.setStart(afterNode, 0);
    newRange.collapse(true);
    sel.removeAllRanges();
    sel.addRange(newRange);
    return true;
  }

  // ── Bold shortcut (**text**) ──────────────────────────────────────────────
  function tryBoldShortcut(block: HTMLElement): boolean {
    const html = block.innerHTML;
    if (!/\*\*(.+?)\*\*/.test(html)) return false;
    block.innerHTML = html.replace(/\*\*(.+?)\*\*/g, '<b>$1</b>');
    // Place cursor outside <b> by inserting a zero-width space anchor after it
    const bEls = block.querySelectorAll('b');
    const lastB = bEls[bEls.length - 1];
    const r = document.createRange();
    if (lastB) {
      const anchor = document.createTextNode('\u200B');
      lastB.after(anchor);
      r.setStart(anchor, 1); // position 1 = after the ZWS, definitively outside <b>
    } else {
      r.selectNodeContents(block);
      r.collapse(false);
    }
    r.collapse(true);
    window.getSelection()?.removeAllRanges();
    window.getSelection()?.addRange(r);
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
      if (tryAutoLink()) emit();
      doEnterSplit();
      return;
    }

    if (e.key === ' ' && block) {
      if (tryHeadingShortcut(block)) {
        e.preventDefault();
        emit();
        return;
      }
      if (tryAutoLink()) {
        // space will be inserted normally after the link by the browser
        emit();
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

  // ── Paste helpers ─────────────────────────────────────────────────────────
  function escHtml(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  function escAttr(s: string): string {
    return s.replace(/&/g, '&amp;').replace(/"/g, '&quot;');
  }

  /**
   * Returns true if the link label looks like obfuscated/garbled content
   * (e.g. Facebook's anti-scraping timestamp encoding).
   * Heuristic: 2+ tokens that mix letters and digits within the same word.
   */
  function isGarbledLabel(label: string): boolean {
    const text = label.replace(/\*+/g, '').trim();
    const mixedTokens = text.split(/\s+/).filter((w) => w.length >= 3 && /[a-zA-Z]/.test(w) && /\d/.test(w));
    return mixedTokens.length >= 2;
  }

  /** Convert pasted HTML to a safe markdown string, then parse that. */
  function htmlToMarkdown(html: string): string {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;

    function nodeToMd(node: Node): string {
      if (node.nodeType === Node.TEXT_NODE) return node.textContent || '';
      if (!(node instanceof HTMLElement)) return '';
      const tag = node.tagName;
      if (tag === 'SCRIPT' || tag === 'STYLE' || tag === 'IFRAME' || tag === 'NOSCRIPT') return '';
      const inner = () => Array.from(node.childNodes).map(nodeToMd).join('');
      if (/^H[1-6]$/.test(tag)) {
        const hashes = '#'.repeat(Math.min(parseInt(tag[1]), 4));
        return `\n${hashes} ${inner().trim()}\n`;
      }
      if (tag === 'P' || tag === 'DIV' || tag === 'SECTION' || tag === 'ARTICLE') {
        const t = inner().trim();
        return t ? `\n${t}\n` : '';
      }
      if (tag === 'BR') return '\n';
      if (tag === 'LI') return `\n${inner().trim()}\n`;
      if (tag === 'UL' || tag === 'OL' || tag === 'BLOCKQUOTE') return `\n${inner()}\n`;
      if (tag === 'TR') return `\n${inner().trim()}\n`;
      if (tag === 'TD' || tag === 'TH') return `${inner().trim()} `;
      if (tag === 'B' || tag === 'STRONG') {
        const t = inner().trim();
        return t ? `**${t}**` : '';
      }
      if (tag === 'A') {
        let href = node.getAttribute('href') || '';
        if (href.startsWith('//')) href = 'https:' + href;
        const label = inner().trim();
        if (/^https?:\/\//i.test(href) && label && !isGarbledLabel(label)) {
          // Percent-encode [ ] in URL so markdown link parser isn't confused
          const safeHref = href.replace(/\[/g, '%5B').replace(/\]/g, '%5D');
          return `[${label}](${safeHref})`;
        }
        return label;
      }
      return inner();
    }

    const md = Array.from(tmp.childNodes).map(nodeToMd).join('');
    return md.replace(/\n{3,}/g, '\n\n').trim();
  }

  function inlineMarkdownToHtml(text: string): string {
    let out = '';
    let i = 0;
    while (i < text.length) {
      // Bold **...**
      if (text[i] === '*' && text[i + 1] === '*') {
        const end = text.indexOf('**', i + 2);
        if (end !== -1) {
          out += `<b>${escHtml(text.slice(i + 2, end))}</b>`;
          i = end + 2;
          continue;
        }
      }
      // Markdown link [label](url) — find ]( as a pair, then balance parentheses for URL end
      if (text[i] === '[') {
        let cb = -1;
        for (let j = i + 1; j < text.length - 1; j++) {
          if (text[j] === ']' && text[j + 1] === '(') { cb = j; break; }
        }
        if (cb !== -1) {
          let depth = 1, cp = -1;
          for (let j = cb + 2; j < text.length; j++) {
            if (text[j] === '(') depth++;
            else if (text[j] === ')') { if (--depth === 0) { cp = j; break; } }
          }
          if (cp !== -1) {
            const label = text.slice(i + 1, cb);
            const url = text.slice(cb + 2, cp);
            if (/^https?:\/\//i.test(url)) {
              const labelHtml = inlineMarkdownToHtml(label).replace(/<br>$/, '') || escHtml(label);
              out += `<a href="${escAttr(url)}" target="_blank" rel="noopener noreferrer">${labelHtml}</a>`;
              i = cp + 1;
              continue;
            }
          }
        }
      }
      // Bare URL
      const urlMatch = text.slice(i).match(/^https?:\/\/\S+/i);
      if (urlMatch) {
        const url = urlMatch[0].replace(/[.,;:!?'")>\]]+$/, '');
        const trail = urlMatch[0].slice(url.length);
        out += `<a href="${escAttr(url)}" target="_blank" rel="noopener noreferrer">${escHtml(url)}</a>${escHtml(trail)}`;
        i += urlMatch[0].length;
        continue;
      }
      out += escHtml(text[i]);
      i++;
    }
    return out || '<br>';
  }

  function parsePasteBlocks(text: string): HTMLElement[] {
    return text.split(/\r?\n/).map((rawLine) => {
      const line = rawLine.trimEnd();
      const hm = line.match(/^(#{1,4})\s+(.+)$/);
      if (hm) {
        const level = hm[1].length;
        const tag = level === 1 ? 'h2' : level === 2 ? 'h3' : level === 3 ? 'h4' : 'h5';
        const el = document.createElement(tag);
        el.textContent = hm[2];
        return el as HTMLElement;
      }
      const p = document.createElement('p');
      p.innerHTML = line.trim() ? inlineMarkdownToHtml(line) : '<br>';
      return p as HTMLElement;
    });
  }

  function handlePaste(e: ClipboardEvent) {
    e.preventDefault();
    const html = e.clipboardData?.getData('text/html') || '';
    const text = e.clipboardData?.getData('text/plain') || '';
    if (!html && !text) return;

    const source = html ? htmlToMarkdown(html) : text;
    if (!source.trim()) return;

    const sel = window.getSelection();
    if (!sel?.rangeCount) return;
    const range = sel.getRangeAt(0);
    range.deleteContents();

    const blocks = parsePasteBlocks(source).filter(
      (b) => b.textContent?.trim() || b.querySelector('a,br')
    );
    if (!blocks.length) return;

    // Single <p> block → insert inline at cursor
    if (blocks.length === 1 && blocks[0].tagName === 'P') {
      const frag = document.createDocumentFragment();
      for (const child of Array.from(blocks[0].childNodes)) frag.appendChild(child.cloneNode(true));
      range.insertNode(frag);
      range.collapse(false);
      sel.removeAllRanges();
      sel.addRange(range);
      setTimeout(() => { normalizeBlocks(); emit(); }, 0);
      return;
    }

    // Multiple blocks (or heading) → split current block and insert
    const currentBlock = getBlock(range.startContainer);
    if (!currentBlock) {
      const frag = document.createDocumentFragment();
      for (const b of blocks) frag.appendChild(b);
      editorEl?.appendChild(frag);
      if (blocks.length) setCursorAtEnd(blocks[blocks.length - 1]);
    } else {
      // Extract content after cursor from current block
      const afterRange = document.createRange();
      afterRange.setStart(range.startContainer, range.startOffset);
      if (currentBlock.lastChild) afterRange.setEndAfter(currentBlock.lastChild);
      else afterRange.setEnd(currentBlock, currentBlock.childNodes.length);
      const afterFrag = afterRange.extractContents();

      // Merge first block's content into current block
      for (const child of Array.from(blocks[0].childNodes)) {
        currentBlock.appendChild(child.cloneNode(true));
      }
      if (!currentBlock.textContent?.trim()) currentBlock.innerHTML = '<br>';

      // Insert middle blocks
      let anchor: HTMLElement = currentBlock;
      for (let i = 1; i < blocks.length - 1; i++) {
        anchor.after(blocks[i]);
        anchor = blocks[i];
      }

      // Build final block: last paste block + after-cursor content
      const lastPaste = blocks[blocks.length - 1];
      const finalBlock = document.createElement(lastPaste.tagName.toLowerCase()) as HTMLElement;
      for (const child of Array.from(lastPaste.childNodes)) {
        finalBlock.appendChild(child.cloneNode(true));
      }
      const cursorMark = document.createTextNode('\u200B');
      finalBlock.appendChild(cursorMark);
      finalBlock.appendChild(afterFrag);
      if (!finalBlock.textContent?.replace(/\u200B/g, '').trim()) finalBlock.innerHTML = '<br>';
      anchor.after(finalBlock);

      if (finalBlock.innerHTML !== '<br>') {
        const r = document.createRange();
        r.setStartAfter(cursorMark);
        r.collapse(true);
        sel.removeAllRanges();
        sel.addRange(r);
      } else {
        setCursorAtStart(finalBlock);
      }
    }

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
    class="min-h-[120px] focus:outline-none select-text"
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
