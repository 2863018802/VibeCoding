import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { ChevronDown, ChevronUp, Copy, Check } from 'lucide-react'

interface SqlBlockProps {
  sql: string
  collapsed?: boolean
}

export function SqlBlock({ sql, collapsed = false }: SqlBlockProps) {
  const [isCollapsed, setIsCollapsed] = useState(collapsed)
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sql)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Fallback
      const ta = document.createElement('textarea')
      ta.value = sql
      document.body.appendChild(ta)
      ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="rounded-xl border border-border/80 bg-secondary/60 overflow-hidden my-2">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-border/60 bg-secondary/80">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-semibold text-primary uppercase tracking-wide">SQL</span>
          {!isCollapsed && (
            <span className="text-xs text-muted-foreground">
              {sql.split('\n').length} 行
            </span>
          )}
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleCopy}
            className="p-1 rounded hover:bg-background/80 transition-colors"
            title="复制 SQL"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-green-500" />
            ) : (
              <Copy className="w-3.5 h-3.5 text-muted-foreground" />
            )}
          </button>
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 rounded hover:bg-background/80 transition-colors"
            title={isCollapsed ? '展开' : '折叠'}
          >
            {isCollapsed ? (
              <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
            ) : (
              <ChevronUp className="w-3.5 h-3.5 text-muted-foreground" />
            )}
          </button>
        </div>
      </div>

      {/* Body */}
      {!isCollapsed && (
        <pre className="px-4 py-3 text-sm font-mono text-foreground overflow-x-auto leading-relaxed">
          <code>{sql}</code>
        </pre>
      )}
    </div>
  )
}
