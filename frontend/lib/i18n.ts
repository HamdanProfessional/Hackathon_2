/**
 * Internationalization (i18n) configuration for English and Urdu support
 */

export const locales = ['en', 'ur'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'en';

/**
 * Translation messages for English and Urdu
 */
export const messages = {
  en: {
    // Navigation
    nav: {
      dashboard: 'Dashboard',
      chat: 'AI Assistant',
      login: 'Login',
      register: 'Register',
      logout: 'Logout',
    },
    // Dashboard
    dashboard: {
      title: 'My Tasks',
      empty: 'No tasks yet. Add your first task!',
      addTask: 'Add Task',
      searchPlaceholder: 'Search tasks...',
      filterAll: 'All',
      filterPending: 'Pending',
      filterCompleted: 'Completed',
    },
    // Task Form
    task: {
      title: 'Task Title',
      description: 'Description (optional)',
      priority: 'Priority',
      dueDate: 'Due Date',
      priorityLow: 'Low',
      priorityMedium: 'Medium',
      priorityHigh: 'High',
      save: 'Save Task',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      complete: 'Mark Complete',
      uncomplete: 'Mark Incomplete',
    },
    // Chat
    chat: {
      title: 'AI Task Assistant',
      placeholder: 'Ask me to manage your tasks... (e.g., "Add a task to buy groceries")',
      newChat: 'New Chat',
      deleteConversation: 'Delete',
      typing: 'AI is typing...',
    },
    // Auth
    auth: {
      email: 'Email',
      password: 'Password',
      name: 'Full Name',
      login: 'Sign In',
      register: 'Create Account',
      loginTitle: 'Welcome Back',
      registerTitle: 'Create Account',
      orContinueWith: 'Or continue with',
      noAccount: "Don't have an account?",
      hasAccount: 'Already have an account?',
    },
    // Common
    common: {
      loading: 'Loading...',
      error: 'An error occurred',
      success: 'Success!',
      cancel: 'Cancel',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',
      back: 'Back',
      next: 'Next',
      submit: 'Submit',
    },
  },
  ur: {
    // Navigation
    nav: {
      dashboard: 'ڈیش بورڈ',
      chat: 'اییاہ مددگار',
      login: 'لاگ ان',
      register: 'رجسٹر',
      logout: 'لاگ آؤٹ',
    },
    // Dashboard
    dashboard: {
      title: 'میرے کام',
      empty: 'ابھی کوئی کام نہیں۔ اپنا پہلا کام شامل کریں!',
      addTask: 'کام شامل کریں',
      searchPlaceholder: 'کام تلاش کریں...',
      filterAll: 'سب',
      filterPending: 'زیر التوا',
      filterCompleted: 'مکمل',
    },
    // Task Form
    task: {
      title: 'کام کا عنوان',
      description: 'تفصیل (اختیاری)',
      priority: 'ترجیح',
      dueDate: 'مہلت کی تاریخ',
      priorityLow: ' کم',
      priorityMedium: 'متوسط',
      priorityHigh: 'زیادہ',
      save: 'محفوظ کریں',
      cancel: 'منسوخ کریں',
      delete: 'حذف کریں',
      edit: 'ترمیم کریں',
      complete: 'مکمل نشانیت',
      uncomplete: 'نامکمل نشانیت',
    },
    // Chat
    chat: {
      title: 'ایی آئی ٹاسک اسسٹنٹ',
      placeholder: 'میرے کام کا انتظام کرنے کے لیے پوچھیں... (مثال: "خریداری کے لیے کام شامل کریں")',
      newChat: 'نئی بات چیت',
      deleteConversation: 'حذف',
      typing: 'ایی آئی لک رہا ہے...',
    },
    // Auth
    auth: {
      email: 'ای میل',
      password: 'پاس ورڈ',
      name: 'پورا نام',
      login: 'سائن ان',
      register: 'اکاؤنٹ بنائیں',
      loginTitle: 'خوش آمدید',
      registerTitle: 'اکاؤنٹ بنائیں',
      orContinueWith: 'یا جاری رکھیں',
      noAccount: 'اکاؤنٹ نہیں ہے؟',
      hasAccount: 'پہلے سے اکاؤنٹ ہے؟',
    },
    // Common
    common: {
      loading: 'لوڈ ہو رہا ہے...',
      error: 'ایک نقص پیش آ گیا',
      success: 'کامیابی!',
      cancel: 'منسوخ کریں',
      save: 'محفوظ کریں',
      delete: 'حذف کریں',
      edit: 'ترمیم کریں',
      back: 'پیچھے',
      next: 'اگلا',
      submit: 'جمع کروائیں',
    },
  },
} as const;

/**
 * Get translated message by key path
 * @param locale - Current locale
 * @param key - Dot-separated key path (e.g., 'nav.dashboard')
 * @returns Translated string
 */
export function t(locale: Locale, key: string): string {
  const keys = key.split('.');
  let value: any = messages[locale];

  for (const k of keys) {
    value = value?.[k];
  }

  return value || key;
}

/**
 * Check if locale is RTL (Right-to-Left)
 * @param locale - Current locale
 * @returns True if RTL
 */
export function isRTL(locale: Locale): boolean {
  return locale === 'ur';
}

/**
 * Get text direction for locale
 * @param locale - Current locale
 * @returns 'rtl' or 'ltr'
 */
export function getDirection(locale: Locale): 'rtl' | 'ltr' {
  return isRTL(locale) ? 'rtl' : 'ltr';
}
