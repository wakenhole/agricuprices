import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell, ResponsiveContainer, ReferenceLine,
} from 'recharts'
import type { Item } from '../types/prices'
import { COUNTRIES, COUNTRY_COLORS } from '../constants/countries'
import { formatKrw } from '../utils/format'

interface Props {
  item: Item
}

export default function PriceChart({ item }: Props) {
  const krPrice = item.countries['kr']?.price_krw ?? 0

  const data = COUNTRIES
    .filter((c) => item.countries[c.code])
    .map((c) => ({
      name: `${c.flag} ${c.name_ko}`,
      price: item.countries[c.code].price_krw,
      code: c.code,
    }))
    .sort((a, b) => a.price - b.price)

  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-5">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">
        {item.emoji} {item.name_ko} — 100g 기준 가격 비교
      </h2>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} layout="vertical" margin={{ left: 8, right: 56, top: 4, bottom: 4 }}>
          <XAxis
            type="number"
            tickFormatter={(v: number) => `₩${v}`}
            tick={{ fontSize: 11, fill: '#6B7280' }}
          />
          <YAxis
            type="category"
            dataKey="name"
            width={88}
            tick={{ fontSize: 13 }}
          />
          <Tooltip
            formatter={(v: number) => [formatKrw(v), '가격 (100g)'] as [string, string]}
            cursor={{ fill: '#F3F4F6' }}
          />
          <ReferenceLine x={krPrice} stroke="#2563EB" strokeDasharray="4 3" strokeWidth={1.5} />
          <Bar dataKey="price" radius={[0, 6, 6, 0]} label={{ position: 'right', formatter: (v: number) => formatKrw(v), fontSize: 11, fill: '#374151' }}>
            {data.map((entry) => (
              <Cell
                key={entry.code}
                fill={
                  entry.code === 'kr'
                    ? COUNTRY_COLORS['kr']
                    : entry.price > krPrice
                    ? '#EF4444'
                    : '#10B981'
                }
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-xs text-gray-400 mt-2 text-right">파란 점선 = 한국 기준가</p>
    </div>
  )
}
