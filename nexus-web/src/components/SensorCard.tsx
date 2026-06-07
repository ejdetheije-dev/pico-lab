type Props = {
  label: string
  value: number | null
  unit: string
  updatedAt: string | null
}

export default function SensorCard({ label, value, unit, updatedAt }: Props) {
  return (
    <div className="bg-gray-900 rounded-xl p-6 flex flex-col gap-2">
      <span className="text-sm text-gray-400">{label}</span>
      <span className="text-4xl font-bold">
        {value !== null ? `${value}${unit}` : '—'}
      </span>
      {updatedAt && (
        <span className="text-xs text-gray-500">
          {new Date(updatedAt).toLocaleTimeString('nl-NL')}
        </span>
      )}
    </div>
  )
}
