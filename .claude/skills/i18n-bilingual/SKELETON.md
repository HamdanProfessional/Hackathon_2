# i18n Bilingual (English/Urdu) Skill

Add English/Urdu bilingual support with RTL layout to Next.js applications.

## When to Use This Skill

Use this skill when you need to:
- Add multi-language support (English + Urdu)
- Implement RTL (Right-to-Left) layout for Urdu
- Add language switcher component
- Manage translations across the application

## Features

- English and Urdu languages
- RTL support for Urdu text
- Language preference persistence (localStorage + cookie)
- Language switcher UI component
- Translation helper functions

## Generated Files

1. **i18n Configuration**: `frontend/lib/i18n.ts`
2. **Locale Utilities**: `frontend/lib/i18n/locale.ts`
3. **Language Switcher**: `frontend/components/language-switcher.tsx`
4. **Translation Messages**: Embedded in `i18n.ts`

## Translation Structure

```typescript
messages = {
  en: {
    nav: { dashboard: 'Dashboard', chat: 'AI Assistant' },
    dashboard: { title: 'My Tasks', addTask: 'Add Task' },
    // ...
  },
  ur: {
    nav: { dashboard: 'ڈیش بورڈ', chat: 'اییاہ مددگار' },
    dashboard: { title: 'میرے کام', addTask: 'کام شامل کریں' },
    // ...
  }
}
```

## Usage in Components

```typescript
import { t, getDirection } from '@/lib/i18n';

function MyComponent() {
  const locale = 'ur'; // or 'en'
  const dir = getDirection(locale);

  return (
    <div dir={dir}>
      <h1>{t(locale, 'dashboard.title')}</h1>
      <p>{t(locale, 'dashboard.addTask')}</p>
    </div>
  );
}
```

## Language Switcher

The language switcher component:
- Globe icon with current language name
- Dropdown with all available languages
- Persists selection to localStorage and cookie
- Updates document `dir` attribute automatically

## RTL Styling

For Urdu (RTL), add these Tailwind utilities:
```css
[dir="rtl"] {
  direction: rtl;
  text-align: right;
}

/* Mirror margins/paddings */
[dir="rtl"] .ml-4 {
  margin-left: 0;
  margin-right: 1rem;
}
```

## Urdu Typography

Use **Noto Nastaliq Urdu** font for proper Urdu rendering:

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap');

[dir="rtl"] body {
  font-family: 'Noto Nastaliq Urdu', 'Inter', sans-serif;
}
```

## Supported Languages

| Code | Name | Native Name | Direction |
|------|------|-------------|----------|
| `en` | English | English | LTR |
| `ur` | Urdu | اردو | RTL |

## Adding New Translations

1. Add key to both `en` and `ur` in `messages`
2. Use dot-notation for nested keys: `'nav.dashboard'`
3. Keep translations concise and consistent

## Browser Language Detection

Auto-detects browser language:
- Checks if browser language starts with `"ur"` for Urdu
- Defaults to English otherwise
- Respects stored preference if set

## Example Translations

| English | Urdu |
|---------|------|
| Dashboard | ڈیش بورڈ |
| My Tasks | میرے کام |
| Add Task | کام شامل کریں |
| Search | تلاش |
| Settings | ترتیبات |
| Logout | لاگ آؤٹ |
| AI Assistant | اے آئی اسسٹنٹ |
