import React, { useState } from 'react'
import { cn } from '@/lib/utils'

interface DataTableProps {
  data: Record<string, unknown>[]
  pageSize?: number
}

export function DataTable({ data, pageSize = 10 }: DataTableProps) {
  const [page, setPage] = useState(0)

  if (!data || data.length === 0) return null

  const columns = Object.keys(data[0])
  const totalPages = Math.ceil(data.length / pageSize)
  const pageData = data.slice(page * pageSize, (page + 1) * pageSize)

  return (
    <div className="flex flex-col h-full">
      <div className="overflow-auto flex-1 rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-secondary/80">
            <tr>
              {columns.map((col) => (
                <th
                  key={col}
                  className="px-3 py-2.5 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wide border-b border-border whitespace-nowrap"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {pageData.map((row, i) => (
              <tr key={i} className="hover:bg-primary/5 transition-colors border-b border-border/50 last:border-0">
                {columns.map((col) => (
                  <td key={col} className="px-3 py-2 text-foreground whitespace-nowrap">
                    {formatCellValue(row[col])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between mt-3 text-xs text-muted-foreground">
          <span>
            第 {page * pageSize + 1}–{Math.min((page + 1) * pageSize, data.length)} 条，共 {data.length} 条
          </span>
          <div className="flex gap-1">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="px-2 py-1 rounded border border-border disabled:opacity-40 hover:bg-secondary transition-colors"
            >
              上一页
            </button>
            <span className="px-2 py-1">{page + 1} / {totalPages}</span>
            <button
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page === totalPages - 1}
              className="px-2 py-1 rounded border border-border disabled:opacity-40 hover:bg-secondary transition-colors"
            >
              下一页
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function formatCellValue(val: unknown): string {
  if (val === null || val === undefined) return '—'
  if (typeof val === 'number') {
    return Number.isInteger(val) ? String(val) : val.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
  }
  return String(val)
}
