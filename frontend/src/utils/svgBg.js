export function getFieldBgSvg() {
  const color =
    getComputedStyle(document.documentElement).getPropertyValue('--code-bg-svg-fill').trim() ||
    'rgba(42,116,128,0.12)'
  const encoded = encodeURIComponent(color)
  return `url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="320" height="320" viewBox="0 0 320 320"><g fill="none" stroke="${encoded}" stroke-width="1.5"><path d="M-40 72 C60 22 118 122 220 70 S370 86 420 34"/><path d="M-30 180 C58 132 130 220 224 174 S356 176 410 130"/><path d="M-20 284 C68 236 132 320 238 276 S354 278 410 232"/><ellipse cx="92" cy="92" rx="54" ry="18" transform="rotate(-28 92 92)"/><ellipse cx="238" cy="222" rx="58" ry="19" transform="rotate(35 238 222)"/></g><g fill="${encoded}"><circle cx="92" cy="92" r="4"/><circle cx="238" cy="222" r="4"/><circle cx="150" cy="160" r="2.5"/></g></svg>')`
}
