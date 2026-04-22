export function formatKrw(amount: number): string {
  return `₩${amount.toLocaleString('ko-KR')}`
}

export function formatLocalPrice(amount: number, currency: string): string {
  const symbols: Record<string, string> = {
    KRW: '₩', USD: '$', JPY: '¥', CNY: '¥', EUR: '€', GBP: '£', AUD: 'A$',
  }
  const symbol = symbols[currency] ?? currency
  const decimals = ['JPY', 'KRW'].includes(currency) ? 0 : 2
  return `${symbol}${amount.toFixed(decimals)}`
}

export function diffPercent(price: number, basePrice: number): number {
  return Math.round(((price - basePrice) / basePrice) * 100)
}

export function formatDate(isoString: string): string {
  return new Date(isoString).toLocaleString('ko-KR', {
    year: 'numeric', month: 'long', day: 'numeric',
    hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Seoul',
  })
}
