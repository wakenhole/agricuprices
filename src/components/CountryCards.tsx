import type { Item } from '../types/prices'
import { COUNTRIES, COUNTRY_COLORS } from '../constants/countries'
import { formatKrw, formatLocalPrice, diffPercent } from '../utils/format'

interface Props {
  item: Item
}

export default function CountryCards({ item }: Props) {
  const krPrice = item.countries['kr']?.price_krw ?? 0

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
      {COUNTRIES.filter((c) => item.countries[c.code]).map((country) => {
        const cp = item.countries[country.code]
        const diff = diffPercent(cp.price_krw, krPrice)
        const isKr = country.code === 'kr'
        const isCheaper = cp.price_krw < krPrice

        return (
          <div
            key={country.code}
            className="bg-white rounded-xl border border-gray-200 p-4 flex flex-col gap-2"
            style={{ borderTopColor: COUNTRY_COLORS[country.code], borderTopWidth: 3 }}
          >
            <div className="flex items-center gap-1.5">
              <span className="text-xl">{country.flag}</span>
              <span className="font-semibold text-gray-800 text-sm">{country.name_ko}</span>
            </div>
            <p className="text-xs text-gray-400">{cp.store}</p>
            <p className="text-xl font-bold text-gray-900">{formatKrw(cp.price_krw)}</p>
            {!isKr && (
              <p className="text-xs text-gray-500">
                {formatLocalPrice(cp.price_local, cp.currency)} / 100g
              </p>
            )}
            {isKr ? (
              <span className="text-xs text-blue-600 font-medium">기준</span>
            ) : (
              <span
                className={`text-xs font-semibold ${isCheaper ? 'text-emerald-600' : 'text-red-500'}`}
              >
                {isCheaper ? `▼ ${Math.abs(diff)}% 저렴` : `▲ ${diff}% 비쌈`}
              </span>
            )}
          </div>
        )
      })}
    </div>
  )
}
