interface Props {
  selected: 'vegetable' | 'fruit'
  onChange: (cat: 'vegetable' | 'fruit') => void
}

export default function CategoryTabs({ selected, onChange }: Props) {
  return (
    <div className="flex gap-2">
      {(['vegetable', 'fruit'] as const).map((cat) => (
        <button
          key={cat}
          onClick={() => onChange(cat)}
          className={`px-5 py-2 rounded-full text-sm font-medium transition-colors ${
            selected === cat
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
          }`}
        >
          {cat === 'vegetable' ? '🥦 채소' : '🍎 과일'}
        </button>
      ))}
    </div>
  )
}
