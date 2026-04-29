import React, { useEffect, useRef, useState } from 'react'
import { cn } from '@/lib/utils'
import { Message } from '@/api/session'
import { SqlBlock } from './SqlBlock'
import { Bot, User } from 'lucide-react'

interface MessageBubbleProps {
  message: Message
  isStreaming?: boolean
  streamingContent?: string
}

export function MessageBubble({ message, isStreaming, streamingContent }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const content = isStreaming ? streamingContent ?? '' : message.content
  const [displayedContent, setDisplayedContent] = useState(content)

  // Streaming effect: typewriter
  useEffect(() => {
    if (!isStreaming) {
      setDisplayedContent(content)
      return
    }
    setDisplayedContent(content)
  }, [content, isStreaming])

  // Parse markdown-like content for the assistant
  const renderContent = () => {
    if (!displayedContent) return null

    // If there's SQL in the content, parse it out
    const sqlMatch = message.sql_query || (isUser ? null : displayedContent.match(/```sql\n([\s\S]*?)```/))

    if (!isUser && sqlMatch && displayedContent.includes('```sql')) {
      const parts = displayedContent.split(/```sql\n[\s\S]*?```/)
      const sqlContent = displayedContent.match(/```sql\n([\s\S]*?)```/)?.[1] || ''

      return (
        <div>
          {parts[0] && <p className="text-sm leading-relaxed whitespace-pre-wrap">{parts[0]}</p>}
          <SqlBlock sql={message.sql_query || sqlContent} />
          {parts[1] && <p className="text-sm leading-relaxed whitespace-pre-wrap mt-2">{parts[1]}</p>}
        </div>
      )
    }

    return <p className="text-sm leading-relaxed whitespace-pre-wrap">{displayedContent}</p>
  }

  return (
    <div className={cn('flex gap-3 px-4 py-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      {/* Avatar */}
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
          isUser ? 'bg-primary' : 'bg-secondary border border-border'
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-primary-foreground" />
        ) : (
          <Bot className="w-4 h-4 text-foreground" />
        )}
      </div>

      {/* Bubble */}
      <div
        className={cn(
          'flex flex-col max-w-[75%]',
          isUser ? 'items-end' : 'items-start'
        )}
      >
        <div
          className={cn(
            'rounded-2xl px-4 py-3',
            isUser
              ? 'bg-primary text-primary-foreground rounded-tr-sm'
              : 'bg-secondary/80 border border-border/60 rounded-tl-sm'
          )}
        >
          {renderContent()}
          {isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-primary/70 rounded-sm animate-pulse align-middle" />
          )}
        </div>
        {message.sql_query && !isStreaming && !displayedContent.includes('```sql') && (
          <SqlBlock sql={message.sql_query} collapsed={true} />
        )}
      </div>
    </div>
  )
}
