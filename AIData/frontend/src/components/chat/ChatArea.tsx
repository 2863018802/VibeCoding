import React, { useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { MessageBubble } from './MessageBubble'
import { ChatInput } from './ChatInput'
import { Message } from '@/api/session'
import { MessageSquarePlus } from 'lucide-react'

interface ChatAreaProps {
  messages: Message[]
  isStreaming: boolean
  streamingContent: string
  onSend: (message: string) => void
  disabled?: boolean
}

export function ChatArea({ messages, isStreaming, streamingContent, onSend, disabled }: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent, isStreaming])

  return (
    <div className="flex flex-col h-full">
      {/* Messages */}
      <div ref={containerRef} className="flex-1 overflow-y-auto py-4">
        {messages.length === 0 && !isStreaming ? (
          <EmptyState />
        ) : (
          <div className="space-y-1">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                isStreaming={false}
                streamingContent=""
              />
            ))}
            {isStreaming && messages.length > 0 && (
              <MessageBubble
                message={{ ...messages[messages.length - 1], content: streamingContent }}
                isStreaming={true}
                streamingContent={streamingContent}
              />
            )}
            {isStreaming && messages.length === 0 && (
              <MessageBubble
                message={{
                  id: -1,
                  session_id: 0,
                  role: 'assistant',
                  content: streamingContent,
                  created_at: new Date().toISOString(),
                }}
                isStreaming={true}
                streamingContent={streamingContent}
              />
            )}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <ChatInput onSend={onSend} disabled={disabled} isStreaming={isStreaming} />
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center h-full px-8 text-center space-y-4">
      <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center">
        <MessageSquarePlus className="w-8 h-8 text-primary" />
      </div>
      <div>
        <h3 className="text-base font-semibold text-foreground mb-1">开始对话</h3>
        <p className="text-sm text-muted-foreground">
          用自然语言描述你的数据分析需求，我会帮你生成 SQL、<br />
          执行查询并推荐合适的可视化图表。
        </p>
      </div>
      <div className="flex flex-wrap gap-2 justify-center mt-2">
        {[
          '各品类销售额统计',
          'VIP客户订单分析',
          '月销量趋势',
          '产品库存预警',
        ].map((example) => (
          <span
            key={example}
            className="px-3 py-1.5 text-xs rounded-full border border-border bg-secondary/50 text-muted-foreground hover:bg-secondary hover:text-foreground cursor-pointer transition-colors"
          >
            {example}
          </span>
        ))}
      </div>
    </div>
  )
}
