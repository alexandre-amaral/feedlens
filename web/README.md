# feedlens web

Vite + Preact + TypeScript SPA. See `specs/005-feed-ui/spec.md`.

```bash
pnpm i
pnpm dev      # http://localhost:5173, proxies /api → http://127.0.0.1:8765
pnpm build    # emits to ../src/feedlens/api/static
```
Scaffold with `pnpm create vite@latest . --template preact-ts` (task T-2.13); keep dependencies minimal (no UI framework).
