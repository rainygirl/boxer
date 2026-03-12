// Global popup registry — ensures only one custom dropdown is open at a time.
// Call registerPopup(closeFn) when opening any dropdown.
// Call closeActivePopup() from window onclick handlers.

let closeCurrent: (() => void) | null = null;

/** Clamp popup left so it stays within the viewport (8px margin on each side). */
export function popupLeft(rectLeft: number, popupWidth: number): number {
  const margin = 8;
  return Math.max(margin, Math.min(rectLeft, window.innerWidth - popupWidth - margin));
}

export function registerPopup(closeFn: () => void) {
  closeCurrent?.();
  closeCurrent = closeFn;
}

export function closeActivePopup() {
  closeCurrent?.();
  closeCurrent = null;
}
