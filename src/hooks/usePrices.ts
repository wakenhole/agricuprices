import { useEffect, useState } from 'react'
import type { PricesData } from '../types/prices'

export function usePrices() {
  const [data, setData] = useState<PricesData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const url = `${import.meta.env.BASE_URL}data/prices.json`
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json() as Promise<PricesData>
      })
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return { data, loading, error }
}
