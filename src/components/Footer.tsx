export default function Footer() {
  return (
    <footer className="bg-white border-t border-gray-200 mt-12">
      <div className="max-w-5xl mx-auto px-4 py-6 text-xs text-gray-400 space-y-1">
        <p className="font-medium text-gray-500">데이터 출처</p>
        <p>한국: KAMIS (한국농수산식품유통공사) / 이마트 · 롯데마트</p>
        <p>미국: USDA AMS / Walmart · 독일: REWE · 영국: Tesco</p>
        <p>일본: AEON · 중국: 盒马(Hema) · 호주: Woolworths</p>
        <p className="pt-2">
          환율은 <a href="https://www.frankfurter.app" className="underline" target="_blank" rel="noreferrer">frankfurter.app</a>을 통해 매일 갱신됩니다.
          가격은 100g 기준 KRW 환산값이며 참고용입니다.
        </p>
      </div>
    </footer>
  )
}
