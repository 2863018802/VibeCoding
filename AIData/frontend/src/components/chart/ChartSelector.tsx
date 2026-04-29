import React from 'react'
import { cn } from '@/lib/utils'
import { BarChart2, TrendingUp, PieChart, Table } from 'lucide-react'

export type ChartType = 'bar' | 'line' | 'pie' | 'table'

interface ChartSelectorProps {
  active: ChartType
  onChange: (type: ChartType) => void
}

const tabs: { type: ChartType; label: string; icon: React.ReactNode }[] = [
  { type: 'bar', label: '柱状图', icon: <BarChart2 className="w-4 h-4" /> },
  { type: 'line', label: '折线图', icon: <TrendingUp className="w-4 h-4" /> },
  { type: 'pie', label: '饼图', icon: <PieChart className="w-4 h-4" /> },
  { type: 'table', label: '表格', icon: <Table className="w-4 h-4" /> },
]

export function ChartSelector({ active, onChange }: ChartSelectorProps) {
  return (
    <div className="flex items-center gap-1 p-1 bg-secondary/50 rounded-lg">
      {tabs.map(({ type, label, icon }) => (
        <button
          key={type}
          onClick={() => onChange(type)}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all',
            active === type
              ? 'bg-background text-foreground shadow-sm border border-border'
              : 'text-muted-foreground hover:text-foreground hover:bg-background/50'
          )}
        >
          {icon}
          <span>{label}</span>
        </button>
      ))}
    </div>
  )
}
