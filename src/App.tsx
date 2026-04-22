import { useState, useMemo } from 'react'
import { usePrices } from './hooks/usePrices'
import Header from './components/Header'
import CategoryTabs from './components/CategoryTabs'
import ItemGrid from './components/ItemGrid'
import PriceChart from './components/PriceChart'
import CountryCards from './components/CountryCards'
import Footer from './components/Footer'

export default function App() {
  const { data, loading, error } = usePrices()
  const [category, setCategory] = useState<'vegetable' | 'fruit'>('vegetable')
  const [selectedItem, setSelectedItem] = useState<string | null>(null)

  const filteredItems = useMemo(() => {
    if (!data) return []
    return Object.entries(data.items).filter(([, item]) => item.category === category)
  }, [data, category])

  const activeItemKey = selectedItem && filteredItems.find(([k]) => k === selectedItem)
    ? selectedItem
    : filteredItems[0]?.[0] ?? null

  const activeItem = activeItemKey ? data?.items[activeItemKey] : null

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-gray-500 text-sm">가격 데이터 로딩 중...</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-2">
          <p className="text-2xl">😕</p>
          <p className="text-gray-700 font-medium">데이터를 불러오지 못했습니다</p>
          <p className="text-gray-400 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header updatedAt={data.updated_at} isSample={data.is_sample} />

      <main className="max-w-5xl mx-auto w-full px-4 py-8 flex-1 space-y-6">
        <div className="space-y-4">
          <CategoryTabs
            selected={category}
            onChange={(cat) => {
              setCategory(cat)
              setSelectedItem(null)
            }}
          />
          <ItemGrid
            items={filteredItems}
            selected={activeItemKey ?? ''}
            onSelect={setSelectedItem}
          />
        </div>

        {activeItem && (
          <div className="space-y-4">
            <PriceChart item={activeItem} />
            <CountryCards item={activeItem} />
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}
