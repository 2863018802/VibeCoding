import client from './client'

export interface Session {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content: string
  sql_query?: string
  chart_data?: string
  created_at: string
}

export const sessionApi = {
  create: (title?: string) =>
    client.post<Session>('/api/sessions', { title }),

  list: () =>
    client.get<Session[]>('/api/sessions'),

  get: (id: number) =>
    client.get<Session>(`/api/sessions/${id}`),

  updateTitle: (id: number, title: string) =>
    client.patch<Session>(`/api/sessions/${id}/title`, { title }),

  delete: (id: number) =>
    client.delete(`/api/sessions/${id}`),

  getMessages: (id: number) =>
    client.get<Message[]>(`/api/sessions/${id}/messages`),
}
