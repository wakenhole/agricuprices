export interface CountryPrice {
  price_krw: number
  price_local: number
  currency: string
  store: string
  fetched_at: string
}

export interface Item {
  name_ko: string
  name_en: string
  emoji: string
  category: 'vegetable' | 'fruit'
  unit: string
  countries: Record<string, CountryPrice>
}

export interface PricesData {
  updated_at: string
  is_sample?: boolean
  exchange_rates: Record<string, number>
  items: Record<string, Item>
}
