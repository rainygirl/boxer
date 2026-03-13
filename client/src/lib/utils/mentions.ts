type Member = { id: number | string; name: string };

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Builds a regex that matches @KnownName (including spaces) first, then falls back to @\S+
function buildMentionRegex(members: Member[]): RegExp {
  if (!members.length) return /@\S+/g;
  const sorted = [...members].sort((a, b) => b.name.length - a.name.length);
  const nameAlts = sorted.map((m) => escapeRegex(m.name)).join('|');
  return new RegExp(`@(${nameAlts}|\\S+)`, 'g');
}

// HTML-escapes text and converts @Name to <a> links for known members.
export function renderMentions(text: string, members: Member[]): string {
  const escaped = escapeHtml(text);
  const pattern = buildMentionRegex(members);

  return escaped.replace(pattern, (_match, name) => {
    const member = members.find((m) => m.name === name);
    if (member) {
      return `<a href="/app/member-issues/${member.id}" class="text-brand-600 dark:text-brand-400 font-semibold hover:underline cursor-pointer">@${escapeHtml(name)}</a>`;
    }
    return `<span class="text-brand-500 dark:text-brand-400 font-semibold">@${escapeHtml(name)}</span>`;
  });
}

// Returns HTML for the textarea highlight overlay.
// Passes members so that multi-word names (e.g. "Jun Lee") are highlighted in full.
export function highlightMentions(text: string, members: Member[] = []): string {
  const escaped = escapeHtml(text);
  const pattern = buildMentionRegex(members);

  const highlighted = escaped.replace(
    pattern,
    (match) =>
      `<mark class="bg-brand-100 dark:bg-brand-900/40 rounded" style="color:transparent">${match}</mark>`
  );
  return `<span style="color:transparent">${highlighted}</span>`;
}
