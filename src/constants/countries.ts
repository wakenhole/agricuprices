export interface Country {
  code: string
  name_ko: string
  name_en: string
  flag: string
  currency: string
}

export const COUNTRIES: Country[] = [
  { code: 'kr', name_ko: '한국', name_en: 'Korea', flag: '🇰🇷', currency: 'KRW' },
  { code: 'us', name_ko: '미국', name_en: 'USA', flag: '🇺🇸', currency: 'USD' },
  { code: 'jp', name_ko: '일본', name_en: 'Japan', flag: '🇯🇵', currency: 'JPY' },
  { code: 'cn', name_ko: '중국', name_en: 'China', flag: '🇨🇳', currency: 'CNY' },
  { code: 'de', name_ko: '독일', name_en: 'Germany', flag: '🇩🇪', currency: 'EUR' },
  { code: 'uk', name_ko: '영국', name_en: 'UK', flag: '🇬🇧', currency: 'GBP' },
  { code: 'au', name_ko: '호주', name_en: 'Australia', flag: '🇦🇺', currency: 'AUD' },
]

export const COUNTRY_COLORS: Record<string, string> = {
  kr: '#2563EB',
  us: '#DC2626',
  jp: '#D97706',
  cn: '#991B1B',
  de: '#7C3AED',
  uk: '#0891B2',
  au: '#059669',
}
