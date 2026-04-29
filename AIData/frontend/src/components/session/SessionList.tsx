import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { SessionItem } from './SessionItem'
import { Session } from '@/api/session'
import { Plus, Search, Trash2, Bot } from 'lucide-react'

interface SessionListProps {
  sessions: Session[]
  currentSessionId: number | null
  onSelect: (id: number) => void
  onCreate: () => void
  onDelete: (id: number) => void
  onRename?: (id: number, title: string) => void
}

export function SessionList({ sessions, currentSessionId, onSelect, onCreate, onDelete }: SessionListProps) {
  const [search, setSearch] = useState('')
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const filtered = sessions.filter((s) =>
    (s.title || '新会话').toLowerCase().includes(search.toLowerCase())
  )

  const handleDelete = (id: number) => {
    setDeletingId(id)
    setTimeout(() => {
      onDelete(id)
      setDeletingId(null)
    }, 200)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-primary" />
          <span className="font-semibold text-foreground">AIData</span>
        </div>
        <button
          onClick={onCreate}
          className={cn(
            'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-all',
            'bg-primary text-primary-foreground hover:bg-primary/90 active:scale-95'
          )}
        >
          <Plus className="w-4 h-4" />
          <span>新建</span>
        </button>
      </div>

      {/* Search */}
      <div className="relative mb-3">
        <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <input
          type="text"
          placeholder="搜索会话..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className={cn(
            'w-full pl-8 pr-3 py-2 text-sm rounded-lg border border-border bg-background',
            'placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary',
            'transition-all'
          )}
        />
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto space-y-1 pr-1">
        {filtered.length === 0 ? (
          <div className="text-center py-8 text-sm text-muted-foreground">
            {search ? '未找到匹配的会话' : '暂无会话，点击"新建"开始'}
          </div>
        ) : (
          filtered.map((session) => (
            <div
              key={session.id}
              className={cn(
                'transition-all duration-200',
                deletingId === session.id && 'opacity-0 scale-95'
              )}
            >
              <SessionItem
                session={session}
                isActive={session.id === currentSessionId}
                onClick={() => onSelect(session.id)}
                onDelete={() => handleDelete(session.id)}
              />
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="pt-3 mt-2 border-t border-border/50 text-xs text-muted-foreground text-center">
        {sessions.length} 个会话
      </div>
    </div>
  )
}
