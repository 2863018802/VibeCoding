import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { ChartSelector, ChartType } from './ChartSelector'
import { ChartRenderer } from './ChartRenderer'
import { DataTable } from './DataTable'
import { BarChart2 } from 'lucide-react'

interface ChartPanelProps {
  data: Record<string, unknown>[] | null
  chartType: ChartType
  onChartTypeChange: (type: ChartType) => void
  title?: string
  loading?: boolean
}

export function ChartPanel({ data, chartType, onChartTypeChange, title, loading }: ChartPanelProps) {
  return (
    <div className="flex flex-col h-full p-4 gap-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-semibold text-foreground">可视化</span>
        <ChartSelector active={chartType} onChange={onChartTypeChange} />
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden rounded-xl border border-border bg-background">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
          </div>
        ) : !data || data.length === 0 ? (
          <EmptyChart />
        ) : chartType === 'table' ? (
          <div className="p-3 h-full overflow-hidden">
            <DataTable data={data} />
          </div>
        ) : (
          <div className="p-2 h-full">
            <ChartRenderer data={data} chartType={chartType} title={title} />
          </div>
        )}
      </div>
    </div>
  )
}

function EmptyChart() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-3 text-center px-4">
      <div className="w-14 h-14 rounded-xl bg-secondary/80 flex items-center justify-center">
        <BarChart2 className="w-7 h-7 text-muted-foreground" />
      </div>
      <div>
        <p className="text-sm font-medium text-foreground mb-1">暂无数据</p>
        <p className="text-xs text-muted-foreground">
          发送问题后，这里将展示<br />数据分析结果与图表
        </p>
      </div>
    </div>
  )
}
