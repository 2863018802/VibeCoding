import React from 'react'
import { cn } from '@/lib/utils'
import { format } from 'date-fns'
import { zhCN } from 'date-fns/locale'
import { Session } from '@/api/session'
import { Trash2, MessageSquare, Clock } from 'lucide-react'

interface SessionItemProps {
  session: Session
  isActive: boolean
  onClick: () => void
  onDelete: () => void
}

export function SessionItem({ session, isActive, onClick, onDelete }: SessionItemProps) {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation()
    onDelete()
  }

  return (
    <div
      className={cn(
        'group relative flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-all duration-150',
        'hover:bg-secondary/70',
        isActive && 'bg-primary/10 border border-primary/30'
      )}
      onClick={onClick}
    >
      <MessageSquare className={cn('w-4 h-4 flex-shrink-0', isActive ? 'text-primary' : 'text-muted-foreground')} />
      <div className="flex-1 min-w-0">
        <div className={cn('text-sm truncate font-medium', isActive ? 'text-primary' : 'text-foreground')}>
          {session.title || '新会话'}
        </div>
        <div className="flex items-center gap-1 text-xs text-muted-foreground mt-0.5">
          <Clock className="w-3 h-3" />
          <span>{format(new Date(session.updated_at), 'MM/dd HH:mm', { locale: zhCN })}</span>
        </div>
      </div>
      <button
        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-destructive/10 hover:text-destructive transition-all"
        onClick={handleDelete}
        title="删除会话"
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>
    </div>
  )
}
