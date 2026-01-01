---
name: frontend
description: Complete frontend suite including frontend-component (Next.js 16+ App Router components with TypeScript and Tailwind CSS) and i18n-bilingual-translator (English/Urdu internationalization with RTL support, next-intl, and Noto Nastaliq Urdu typography).
version: 2.0.0
category: frontend
tags: [nextjs, typescript, tailwind, components, i18n, bilingual, rtl, urdu]
dependencies: [next.js, typescript, tailwindcss, next-intl]
---

# Frontend Skill

Comprehensive frontend development for Next.js applications.

## Quick Reference

| Feature | Location | Description |
|---------|----------|-------------|
| Examples | `examples/` | Component templates, i18n patterns |
| Scripts | `scripts/` | Frontend automation |
| Templates | `references/templates.md` | Reusable templates |
| Links | `references/links.md` | External resources |

## When to Use This Skill

Use this skill when:
- Building Next.js 16+ App Router pages/components
- Styling with Tailwind CSS
- Implementing English/Urdu bilingual support
- Adding RTL layout for Urdu text
- Creating TypeScript interfaces for backend types
- Integrating with backend APIs

## Common Issues & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Hydration errors | Server/client mismatch | Use dynamic imports or suppress |
| RTL layout broken | Missing directional utilities | Use `ms-`, `me-`, `ps-`, `pe-` instead of left/right |
| Urdu font not loading | Google Fonts not imported | Add `Noto_Nastaliq_Urdu` to layout |

---

## Part 1: Frontend Components

See the main SKILL.md (already comprehensive) for component templates.

---

## Part 2: i18n Bilingual Translator

**Quick setup**:
```bash
npm install next-intl
```

**Middleware** for locale detection
**RTL styles** for Urdu text

---

## Quality Checklist

- [ ] Components use TypeScript
- [ ] Client components have 'use client'
- [ ] Tailwind CSS for styling
- [ ] JWT in headers (not cookies)
- [ ] Loading/error states
- [ ] Responsive design
- [ ] Translation files for en/ur
- [ ] RTL styles for Urdu
- [ ] Language switcher component
- [ ] Directional utilities used
