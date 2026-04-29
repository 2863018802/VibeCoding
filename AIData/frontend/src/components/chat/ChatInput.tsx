import React, { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { Send, Loader2 } from 'lucide-react'

interface ChatInputProps {
  onSend: (message: string) => void
  disabled?: boolean
  isStreaming?: boolean
}

export function ChatInput({ onSend, disabled, isStreaming }: ChatInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 160)}px`
  }, [value])

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled || isStreaming) return
    onSend(trimmed)
    setValue('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const canSend = value.trim().length > 0 && !disabled && !isStreaming

  return (
    <div className="flex items-end gap-2 p-4 border-t border-border bg-background">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="输入你的问题，按 Enter 发送，Shift+Enter 换行..."
        disabled={disabled}
        rows={1}
        className={cn(
          'flex-1 resize-none rounded-xl border border-border bg-secondary/50 px-4 py-3 text-sm',
          'placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary',
          'disabled:opacity-50 disabled:cursor-not-allowed transition-all',
          'leading-relaxed max-h-40 overflow-y-auto'
        )}
        style={{ minHeight: '48px' }}
      />
      <button
        onClick={handleSend}
        disabled={!canSend}
        className={cn(
          'flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all',
          'active:scale-95',
          canSend
            ? 'bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm'
            : 'bg-secondary text-muted-foreground cursor-not-allowed'
        )}
      >
        {isStreaming ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Send className="w-4 h-4" />
        )}
      </button>
    </div>
  )
}
