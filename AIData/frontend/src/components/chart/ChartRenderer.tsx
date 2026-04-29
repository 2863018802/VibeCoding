import React, { useRef, useEffect } from 'react'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { ChartType } from './ChartSelector'

interface ChartRendererProps {
  data: Record<string, unknown>[]
  chartType: ChartType
  xKey?: string
  yKey?: string
  title?: string
}

export function ChartRenderer({ data, chartType, xKey, yKey, title }: ChartRendererProps) {
  const chartRef = useRef<HTMLDivElement>(null)
  const instanceRef = useRef<echarts.ECharts | null>(null)

  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0) return

    if (!instanceRef.current) {
      instanceRef.current = echarts.init(chartRef.current)
    }

    const chart = instanceRef.current
    const option = buildOption(data, chartType, xKey, yKey, title)
    chart.setOption(option, true)

    const resizeObserver = new ResizeObserver(() => chart.resize())
    resizeObserver.observe(chartRef.current)

    return () => {
      resizeObserver.disconnect()
      chart.dispose()
      instanceRef.current = null
    }
  }, [data, chartType, xKey, yKey, title])

  return (
    <div
      ref={chartRef}
      className="w-full h-full min-h-[250px]"
      style={{ minHeight: '250px' }}
    />
  )
}

function buildOption(
  data: Record<string, unknown>[],
  chartType: ChartType,
  xKey?: string,
  yKey?: string,
  title?: string
): EChartsOption {
  if (chartType === 'table') {
    return {}
  }

  const keys = Object.keys(data[0] || {})
  const catKey = xKey || (keys.length > 1 ? keys[0] : 'x')
  const valKey = yKey || (keys.length > 1 ? keys[1] : 'value')

  const categories = data.map((d) => String(d[catKey]))
  const values = data.map((d) => Number(d[valKey]) || 0)

  const baseConfig = {
    title: {
      text: title || '',
      left: 'center',
      top: 8,
      textStyle: { fontSize: 13, fontWeight: 'normal', color: '#6b7280' },
    },
    grid: { top: 40, right: 20, bottom: 30, left: 50, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
  }

  switch (chartType) {
    case 'bar':
      return {
        ...baseConfig,
        xAxis: { type: 'category', data: categories, axisLabel: { fontSize: 11 } },
        yAxis: { type: 'value', axisLabel: { fontSize: 11 } },
        series: [{ data: values, type: 'bar', itemStyle: { color: '#8b5cf6', borderRadius: [4, 4, 0, 0] } }],
      } as EChartsOption

    case 'line':
      return {
        ...baseConfig,
        xAxis: { type: 'category', data: categories, axisLabel: { fontSize: 11 } },
        yAxis: { type: 'value', axisLabel: { fontSize: 11 } },
        series: [
          {
            data: values,
            type: 'line',
            smooth: true,
            areaStyle: { color: 'rgba(139, 92, 246, 0.1)' },
            lineStyle: { color: '#8b5cf6', width: 2 },
            itemStyle: { color: '#8b5cf6' },
          },
        ],
      } as EChartsOption

    case 'pie':
      return {
        title: { text: title || '', left: 'center', top: 8, textStyle: { fontSize: 13, fontWeight: 'normal', color: '#6b7280' } },
        tooltip: { trigger: 'item' },
        legend: { bottom: 8, type: 'scroll' },
        series: [
          {
            type: 'pie',
            radius: ['40%', '70%'],
            data: data.map((d) => ({ name: String(d[catKey]), value: Number(d[valKey]) || 0 })),
            label: { fontSize: 11 },
            itemStyle: { borderRadius: 4, borderColor: '#fff', borderWidth: 2 },
          },
        ],
      } as EChartsOption

    default:
      return {}
  }
}
