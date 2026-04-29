import { AppShell } from './components/layout/AppShell'
import { SessionList } from './components/session/SessionList'
import { ChatArea } from './components/chat/ChatArea'
import { ChartPanel } from './components/chart/ChartPanel'
import { useAppStore } from './stores/useAppStore'
import { useEffect } from 'react'

export default function App() {
  const {
    sessions,
    currentSessionId,
    messages,
    isStreaming,
    streamingContent,
    chartData,
    chartType,
    loadSessions,
    createSession,
    selectSession,
    deleteSession,
    sendMessage,
    setChartType,
  } = useAppStore()

  useEffect(() => {
    loadSessions()
  }, [])

  return (
    <AppShell
      leftPanel={
        <div className="p-4">
          <SessionList
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSelect={selectSession}
            onCreate={createSession}
            onDelete={deleteSession}
          />
        </div>
      }
      centerPanel={
        <ChatArea
          messages={messages}
          isStreaming={isStreaming}
          streamingContent={streamingContent}
          onSend={sendMessage}
          disabled={!currentSessionId && !isStreaming}
        />
      }
      rightPanel={
        <ChartPanel
          data={chartData}
          chartType={chartType}
          onChartTypeChange={setChartType}
        />
      }
    />
  )
}
