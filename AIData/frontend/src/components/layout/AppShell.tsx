import React from 'react'
interface AppShellProps {
  leftPanel?: React.ReactNode
  centerPanel?: React.ReactNode
  rightPanel?: React.ReactNode
}

export function AppShell({ leftPanel, centerPanel, rightPanel }: AppShellProps) {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      {/* Left Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-border bg-card flex flex-col">
        {leftPanel}
      </aside>

      {/* Center Chat Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {centerPanel}
      </main>

      {/* Right Chart Panel */}
      <aside className="w-96 flex-shrink-0 border-l border-border bg-card flex flex-col">
        {rightPanel}
      </aside>
    </div>
  )
}
