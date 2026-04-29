import { create } from 'zustand'
import { Session, Message, sessionApi } from '@/api/session'
import { chatApi } from '@/api/chat'

interface AppState {
  sessions: Session[]
  currentSessionId: number | null
  messages: Message[]
  isStreaming: boolean
  streamingContent: string
  isLoading: boolean
  chartData: Record<string, unknown>[] | null
  chartType: 'bar' | 'line' | 'pie' | 'table'
  error: string | null

  // Actions
  loadSessions: () => Promise<void>
  createSession: () => Promise<void>
  selectSession: (id: number) => Promise<void>
  deleteSession: (id: number) => Promise<void>
  sendMessage: (content: string) => Promise<void>
  setChartType: (type: 'bar' | 'line' | 'pie' | 'table') => void
  clearError: () => void
}

export const useAppStore = create<AppState>((set, get) => ({
  sessions: [],
  currentSessionId: null,
  messages: [],
  isStreaming: false,
  streamingContent: '',
  isLoading: false,
  chartData: null,
  chartType: 'bar',
  error: null,

  loadSessions: async () => {
    try {
      const res = await sessionApi.list()
      set({ sessions: res.data })
    } catch {
      set({ error: '加载会话列表失败' })
    }
  },

  createSession: async () => {
    try {
      const res = await sessionApi.create('新会话')
      const session = res.data
      set((state) => ({
        sessions: [session, ...state.sessions],
        currentSessionId: session.id,
        messages: [],
        chartData: null,
        streamingContent: '',
      }))
    } catch {
      set({ error: '创建会话失败' })
    }
  },

  selectSession: async (id: number) => {
    set({ currentSessionId: id, messages: [], chartData: null, streamingContent: '' })
    try {
      const res = await sessionApi.getMessages(id)
      set({ messages: res.data })
    } catch {
      set({ error: '加载消息失败' })
    }
  },

  deleteSession: async (id: number) => {
    try {
      await sessionApi.delete(id)
      set((state) => {
        const sessions = state.sessions.filter((s) => s.id !== id)
        const currentSessionId =
          state.currentSessionId === id ? (sessions[0]?.id ?? null) : state.currentSessionId
        return { sessions, currentSessionId, messages: currentSessionId === id ? [] : state.messages }
      })
      // If deleted current session, reload messages
      if (get().currentSessionId) {
        await get().selectSession(get().currentSessionId!)
      }
    } catch {
      set({ error: '删除会话失败' })
    }
  },

  sendMessage: async (content: string) => {
    const { currentSessionId } = get()
    if (!currentSessionId) {
      // Auto-create a session first
      await get().createSession()
    }
    const sessionId = get().currentSessionId!
    const userMsgId = Date.now()
    const userMsg: Message = {
      id: userMsgId,
      session_id: sessionId,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }

    set((state) => ({
      messages: [...state.messages, userMsg],
      isStreaming: true,
      streamingContent: '',
      chartData: null,
    }))

    try {
      let fullContent = ''
      const gen = chatApi.stream(sessionId, content, (chunk) => {
        fullContent += chunk
        set({ streamingContent: fullContent })
      })

      for await (const _ of gen) {
        // content appended via callback
      }

      // Finalize: save message + derive chart data
      const chartData = chatApi.getMockChartData(content)
      set({ chartData })
    } catch {
      set({ error: '发送消息失败' })
    } finally {
      set((state) => ({
        isStreaming: false,
        messages: [...state.messages.filter((m) => m.id !== userMsgId)],
      }))
    }
  },

  setChartType: (type) => set({ chartType: type }),

  clearError: () => set({ error: null }),
}))
