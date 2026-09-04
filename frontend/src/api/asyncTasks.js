const API_BASE = '/api/async-tasks'

export async function getAsyncTaskStatus(taskId) {
  const response = await fetch(`${API_BASE}/${encodeURIComponent(taskId)}`)

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `Failed to query async task: ${response.status}`)
  }

  return response.json()
}
