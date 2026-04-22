import { formatDate } from '../utils/format'

interface Props {
  updatedAt: string
  isSample?: boolean
}

export default function Header({ updatedAt, isSample }: Props) {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-5xl mx-auto px-4 py-5">
        <h1 className="text-2xl font-bold text-gray-900">
          🌍 전세계 농산물 가격 비교
        </h1>
        <p className="text-sm text-gray-500 mt-1">
          한국 소비자를 위한 주요국 채소·과일 가격 비교 &middot; 100g 기준 &middot; KRW 환산
        </p>
        <p className="text-xs text-gray-400 mt-1">
          마지막 업데이트: {formatDate(updatedAt)}
        </p>
        {isSample && (
          <div className="mt-2 inline-flex items-center gap-1.5 bg-amber-50 border border-amber-200 text-amber-700 text-xs px-3 py-1 rounded-full">
            <span>⚠️</span>
            <span>현재 샘플 데이터입니다. 크롤러 실행 후 실제 데이터로 교체됩니다.</span>
          </div>
        )}
      </div>
    </header>
  )
}
