/**
 * 한글 초중종성 자동완성 검색 유틸리티 (TypeScript)
 * 원본: restaurant.coroke.net/hangul-search.js
 */

const HANGUL_START = 0xac00;

const JONG_TO_CHO: Record<number, number> = {
  1: 0, 2: 1, 4: 2, 7: 3, 8: 5,
  16: 6, 17: 7, 19: 9, 20: 10, 21: 11,
  22: 12, 23: 14, 24: 15, 25: 16, 26: 17, 27: 18,
};

const JAMO_TO_CHO: Record<number, number> = {
  0x3131: 0, 0x3132: 1, 0x3134: 2, 0x3137: 3, 0x3138: 4,
  0x3139: 5, 0x3141: 6, 0x3142: 7, 0x3143: 8, 0x3145: 9,
  0x3146: 10, 0x3147: 11, 0x3148: 12, 0x3149: 13, 0x314a: 14,
  0x314b: 15, 0x314c: 16, 0x314d: 17, 0x314e: 18,
};

function escRx(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function choRange(choIdx: number): string {
  const base = HANGUL_START + choIdx * 21 * 28;
  return `[${String.fromCharCode(base)}-${String.fromCharCode(base + 20 * 28 + 27)}]`;
}

export function buildKoreanSearchPattern(query: string): string {
  if (!query) return '';
  let pattern = '';

  for (let i = 0; i < query.length; i++) {
    const ch = query[i];
    const code = ch.charCodeAt(0);
    const isLast = i === query.length - 1;

    if (code >= 0x3131 && code <= 0x314e) {
      const choIdx = JAMO_TO_CHO[code];
      if (choIdx !== undefined && isLast) {
        pattern += choRange(choIdx);
      } else {
        pattern += escRx(ch);
      }
      continue;
    }

    if (code < 0xac00 || code > 0xd7a3) {
      pattern += escRx(ch);
      continue;
    }

    if (!isLast) {
      pattern += escRx(ch);
      continue;
    }

    const offset = code - HANGUL_START;
    const jong = offset % 28;
    const jung = Math.floor(offset / 28) % 21;
    const cho = Math.floor(offset / (21 * 28));
    const base = HANGUL_START + cho * 21 * 28 + jung * 28;

    if (jong === 0) {
      pattern += `[${String.fromCharCode(base)}-${String.fromCharCode(base + 27)}]`;
    } else {
      const altExact = escRx(String.fromCharCode(base + jong));
      const choIdxFromJong = JONG_TO_CHO[jong];
      const altSplit = choIdxFromJong !== undefined
        ? escRx(String.fromCharCode(base)) + choRange(choIdxFromJong)
        : '';
      pattern += altSplit ? `(?:${altExact}|${altSplit})` : altExact;
    }
  }

  return pattern;
}

export function matchKorean(query: string, text: string): boolean {
  if (!query) return true;
  if (!text) return false;
  try {
    const pat = buildKoreanSearchPattern(query);
    return pat ? new RegExp(pat, 'i').test(text) : text.toLowerCase().includes(query.toLowerCase());
  } catch {
    return text.includes(query);
  }
}
