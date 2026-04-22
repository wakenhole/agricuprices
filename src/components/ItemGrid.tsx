import type { Item } from '../types/prices'

interface Props {
  items: [string, Item][]
  selected: string
  onSelect: (key: string) => void
}

export default function ItemGrid({ items, selected, onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {items.map(([key, item]) => (
        <button
          key={key}
          onClick={() => onSelect(key)}
          className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium border transition-all ${
            selected === key
              ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
              : 'bg-white text-gray-700 border-gray-200 hover:border-blue-300 hover:bg-blue-50'
          }`}
        >
          <span>{item.emoji}</span>
          <span>{item.name_ko}</span>
        </button>
      ))}
    </div>
  )
}
