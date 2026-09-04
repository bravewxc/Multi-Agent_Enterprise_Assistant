<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <Sidebar
      :sessions="sessions"
      :current-thread-id="currentThreadId"
      @select-session="handleSelectSession"
      @new-chat="handleNewChat"
      @delete-session="handleDeleteSession"
    />

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 对话区域 -->
      <ChatArea
        :messages="messages"
        :streaming="isStreaming"
        :show-tool-calls="showToolCalls"
      />

      <!-- ★ 人工介入中断横幅（数据补充 / HITL 审批） -->
      <InterruptBanner
        v-if="interruptData"
        :interrupt-data="interruptData"
        :submitting="isResuming"
        @resume="handleResume"
      />

      <!-- 输入区域：中断激活时隐藏，正常/流式时显示 -->
      <InputArea
        v-if="!interruptData"
        @send="handleSend"
        @stop="handleStop"
        @toggle-tool-calls="showToolCalls = $event"
        :disabled="false"
        :streaming="isStreaming"
        :show-tool-calls="showToolCalls"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import Sidebar from './components/Sidebar.vue'
import ChatArea from './components/ChatArea.vue'
import InputArea from './components/InputArea.vue'
import InterruptBanner from './components/InterruptBanner.vue'
import { streamChat, resumeChat } from './api/chat.js'
import { getSessions, getMessages, deleteSession } from './api/history.js'
import { getAsyncTaskStatus } from './api/asyncTasks.js'

/**
 * DeepAgent 聊天应用主组件
 *
 * 消息流按时间顺序混合展示：
 *   [user] → [assistant 文本] → [tool 调用] → [assistant 文本] → ...
 * 支持 Human-in-the-Loop 中断：
 *   ... → [interrupt] → [用户决策/补充] → [继续]
 */

// ============================================================
// 状态定义
// ============================================================

// 会话列表
const sessions = ref([])
// 当前会话 ID
const currentThreadId = ref(null)
// 消息列表（混合 user/assistant/tool，按时间顺序）
const messages = ref([])
// 是否正在流式输出
const isStreaming = ref(false)
// 是否正在处理中断恢复
const isResuming = ref(false)
// 是否显示工具调用
const showToolCalls = ref(true)
// 中断数据（null = 无中断，object = 有中断等待处理）
const interruptData = ref(null)
// AbortController 用于停止流式请求
let abortController = null
const asyncTaskPollers = new Map()
const ASYNC_TASK_POLL_INTERVAL_MS = 5000
const ASYNC_TASK_MAX_ATTEMPTS = 240

// ============================================================
// 生命周期
// ============================================================

/**
 * 组件挂载时加载会话列表
 */
onMounted(async () => {
  await loadSessions()
})

onUnmounted(() => {
  stopAllAsyncTaskPolling()
})

// ============================================================
// 会话管理
// ============================================================

/**
 * 加载会话列表
 */
async function loadSessions() {
  try {
    const response = await getSessions(1, 100)
    sessions.value = response.sessions || []
  } catch (error) {
    console.error('[App] 加载会话列表失败:', error)
    sessions.value = []
  }
}

/**
 * 选择会话
 */
async function handleSelectSession(threadId) {
  if (threadId === currentThreadId.value) return

  currentThreadId.value = threadId
  interruptData.value = null  // 切换会话时清除中断状态
  await loadMessages(threadId)
}

/**
 * 新建对话
 */
function handleNewChat() {
  // 如果有正在进行的请求，取消它
  if (abortController) {
    abortController.abort()
    abortController = null
  }
  stopAllAsyncTaskPolling()
  isStreaming.value = false
  isResuming.value = false
  interruptData.value = null
  currentThreadId.value = null
  messages.value = []
}

/**
 * 删除会话
 */
async function handleDeleteSession(threadId) {
  try {
    await deleteSession(threadId)
    await loadSessions()

    if (currentThreadId.value === threadId) {
      handleNewChat()
    }
  } catch (error) {
    console.error('[App] 删除会话失败:', error)
    alert('删除会话失败，请重试')
  }
}

/**
 * 加载会话消息
 */
async function loadMessages(threadId) {
  try {
    const response = await getMessages(threadId)
    messages.value = response.messages || []
  } catch (error) {
    console.error('[App] 加载会话消息失败:', error)
    messages.value = []
  }
}

// ============================================================
// 停止对话
// ============================================================

/**
 * 停止当前对话
 */
function handleStop() {
  if (abortController) {
    abortController.abort()
    abortController = null
    isStreaming.value = false
    isResuming.value = false
    console.log('[App] 用户停止了对话')
  }
}

// ============================================================
// 消息发送
// ============================================================

// ============================================================
// AsyncSubAgent task polling
// ============================================================

function extractAsyncTaskId(text) {
  if (!text) return null

  const candidates = []
  const collectStrings = (value) => {
    if (!value) return
    if (typeof value === 'string') {
      candidates.push(value)
      return
    }
    if (Array.isArray(value)) {
      value.forEach(collectStrings)
      return
    }
    if (typeof value === 'object') {
      for (const key of ['task_id', 'thread_id', 'id']) {
        if (typeof value[key] === 'string') candidates.push(value[key])
      }
      Object.values(value).forEach(collectStrings)
    }
  }

  try {
    collectStrings(JSON.parse(text))
  } catch {
    candidates.push(text)
  }

  const uuidPattern = /[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/
  for (const candidate of candidates) {
    const match = String(candidate).match(uuidPattern)
    if (match) return match[0]
  }
  return null
}

function appendAssistantMessage(content, source = 'procurement-analyst') {
  messages.value.push({
    id: `assistant-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    role: 'assistant',
    content,
    source
  })
}

function stopAllAsyncTaskPolling() {
  for (const stopPolling of asyncTaskPollers.values()) {
    stopPolling()
  }
  asyncTaskPollers.clear()
}

function startAsyncTaskPolling(taskId) {
  if (!taskId || asyncTaskPollers.has(taskId)) return

  const parentThreadId = currentThreadId.value
  appendAssistantMessage(
    `后台采购分析任务已启动。\n\n任务 ID：\`${taskId}\`\n\n任务完成后，页面会自动显示结果。`,
    'procurement-analyst'
  )

  let attempts = 0
  let timerId = null

  const stopPolling = () => {
    if (timerId) window.clearTimeout(timerId)
    asyncTaskPollers.delete(taskId)
  }

  const poll = async () => {
    attempts += 1
    try {
      const status = await getAsyncTaskStatus(taskId)
      if (status.done) {
        stopPolling()
        if (parentThreadId && currentThreadId.value && parentThreadId !== currentThreadId.value) return

        if (status.status === 'success') {
          appendAssistantMessage(
            `后台采购分析任务已完成。\n\n任务 ID：\`${taskId}\`\n\n${status.content || '任务已完成，但没有返回可展示的文本结果。'}`,
            'procurement-analyst'
          )
        } else {
          appendAssistantMessage(
            `后台采购分析任务未完成。\n\n任务 ID：\`${taskId}\`\n\n状态：\`${status.status}\`\n\n${status.error || '未返回具体错误信息。'}`,
            'procurement-analyst'
          )
        }
        return
      }

      if (attempts >= ASYNC_TASK_MAX_ATTEMPTS) {
        stopPolling()
        appendAssistantMessage(
          `后台采购分析任务仍在运行，已停止页面自动轮询。\n\n任务 ID：\`${taskId}\`\n\n你仍然可以稍后手动查询这个任务。`,
          'procurement-analyst'
        )
        return
      }
    } catch (error) {
      console.error('[App] Async task polling failed:', error)
      if (attempts >= 3) {
        stopPolling()
        appendAssistantMessage(
          `后台采购分析任务状态查询失败。\n\n任务 ID：\`${taskId}\`\n\n错误：${error.message}`,
          'procurement-analyst'
        )
        return
      }
    }

    timerId = window.setTimeout(poll, ASYNC_TASK_POLL_INTERVAL_MS)
  }

  asyncTaskPollers.set(taskId, stopPolling)
  timerId = window.setTimeout(poll, ASYNC_TASK_POLL_INTERVAL_MS)
}

/**
 * 发送消息
 */
async function handleSend(message) {
  if (isStreaming.value) return

  // 添加用户消息
  messages.value.push({
    id: `user-${Date.now()}`,
    role: 'user',
    content: message
  })

  // 清除中断状态（如果有）
  interruptData.value = null

  // 设置流式状态
  isStreaming.value = true

  // 创建新的 AbortController
  abortController = new AbortController()

  try {
    const result = await streamChat(
      message,
      currentThreadId.value,
      {
        // 接收到 token 时的回调
        onToken: (content, source) => {
          const lastMsg = messages.value[messages.value.length - 1]
          if (lastMsg && lastMsg.role === 'assistant') {
            // 追加到已有的 assistant 消息
            lastMsg.content += content
            lastMsg.source = source
          } else {
            // 前一条是 tool 或没有消息，创建新的 assistant 消息
            messages.value.push({
              id: `assistant-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
              role: 'assistant',
              content: content,
              source: source || 'main'
            })
          }
        },

        // 工具开始调用时的回调
        onToolStart: (tool) => {
          messages.value.push({
            id: tool.id,
            role: 'tool',
            tool_name: tool.name,
            args: '',
            text: '',
            images: [],
            source: tool.source || 'main',
            tool_status: 'calling'
          })
        },

        // 工具参数片段的回调
        onToolArgs: (args, source) => {
          // 从后向前查找最后一个 calling 状态的 tool，支持嵌套工具调用
          for (let i = messages.value.length - 1; i >= 0; i--) {
            if (messages.value[i].role === 'tool' && messages.value[i].tool_status === 'calling') {
              messages.value[i].args += args
              break
            }
          }
        },

        // 工具结果返回时的回调
        onToolResult: (tool) => {
          let toolMsg = null
          for (let i = messages.value.length - 1; i >= 0; i--) {
            if (messages.value[i].role === 'tool' && messages.value[i].id === tool.id) {
              toolMsg = messages.value[i]
              break
            }
          }
          if (toolMsg) {
            toolMsg.text = tool.text || ''
            toolMsg.images = tool.images || []
            toolMsg.tool_status = 'done'
          }
          if (tool.name === 'start_async_task') {
            const taskId = extractAsyncTaskId(tool.text)
            startAsyncTaskPolling(taskId)
          }
        },

        // 工具调用结束时的回调
        onToolEnd: (tool) => {
          if (tool) {
            let toolMsg = null
            for (let i = messages.value.length - 1; i >= 0; i--) {
              if (messages.value[i].role === 'tool' && messages.value[i].id === tool.id) {
                toolMsg = messages.value[i]
                break
              }
            }
            if (toolMsg && toolMsg.tool_status === 'calling') {
              toolMsg.tool_status = 'done'
            }
          }
          // 兜底：将所有仍在 calling 的工具标记为 done
          for (const m of messages.value) {
            if (m.role === 'tool' && m.tool_status === 'calling') {
              m.tool_status = 'done'
            }
          }
        },

        // ★ 中断检测回调
        onInterrupt: (data) => {
          console.log('[App] 检测到中断:', data.interrupt_type)
          // 兜底：将所有 calling 状态的工具标记为 done
          for (const m of messages.value) {
            if (m.role === 'tool' && m.tool_status === 'calling') {
              m.tool_status = 'done'
            }
          }
          // 清理空的 assistant 消息
          messages.value = messages.value.filter(m => {
            if (m.role === 'assistant' && !m.content) return false
            return true
          })
          // 设置中断数据，触发 InterruptBanner 显示
          interruptData.value = data
        },

        // 流结束时的回调
        onDone: (data) => {
          // 确保所有工具调用都标记为完成
          for (const m of messages.value) {
            if (m.role === 'tool' && m.tool_status === 'calling') {
              m.tool_status = 'done'
            }
          }
          // 清理空内容的 assistant 消息（流式过程中产生的残留）
          messages.value = messages.value.filter(m => {
            if (m.role === 'assistant' && !m.content && !data.aborted) {
              return false
            }
            return true
          })
          if (data.aborted) {
            const lastMsg = messages.value[messages.value.length - 1]
            if (lastMsg && lastMsg.role === 'assistant' && !lastMsg.content) {
              lastMsg.content = '（对话已停止）'
            }
          }
          // 仅在非中断完成时更新 thread_id
          if (data.thread_id && !currentThreadId.value && !data.interrupted) {
            currentThreadId.value = data.thread_id
            loadSessions()
          }
        },

        // 发生错误时的回调
        onError: (error) => {
          console.error('[App] 对话错误:', error)
          const lastMsg = messages.value[messages.value.length - 1]
          if (lastMsg && lastMsg.role === 'assistant' && !lastMsg.content) {
            lastMsg.content = `抱歉，发生了错误：${error.message}`
          } else {
            messages.value.push({
              id: `assistant-${Date.now()}`,
              role: 'assistant',
              content: `抱歉，发生了错误：${error.message}`,
              source: 'main'
            })
          }
        }
      },
      abortController.signal
    )
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('[App] 请求已被取消')
    } else {
      console.error('[App] 发送消息失败:', error)
    }
  } finally {
    isStreaming.value = false
    abortController = null
  }
}

// ============================================================
// 中断恢复
// ============================================================

/**
 * 处理中断恢复（由 InterruptBanner 触发）
 *
 * @param {Object} resumeData - 恢复数据：
 *   - 数据补充: { supplement: "..." }
 *   - HITL 审批: { decisions: [{ type: "approve" }] }
 */
async function handleResume(resumeData) {
  if (isResuming.value || !currentThreadId.value) return

  isResuming.value = true

  // 创建新的 AbortController
  abortController = new AbortController()

  try {
    const result = await resumeChat(
      currentThreadId.value,
      resumeData,
      {
        onToken: (content, source) => {
          const lastMsg = messages.value[messages.value.length - 1]
          if (lastMsg && lastMsg.role === 'assistant') {
            lastMsg.content += content
            lastMsg.source = source
          } else {
            messages.value.push({
              id: `assistant-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
              role: 'assistant',
              content: content,
              source: source || 'main'
            })
          }
        },

        onToolStart: (tool) => {
          messages.value.push({
            id: tool.id,
            role: 'tool',
            tool_name: tool.name,
            args: '',
            text: '',
            images: [],
            source: tool.source || 'main',
            tool_status: 'calling'
          })
        },

        onToolArgs: (args, source) => {
          for (let i = messages.value.length - 1; i >= 0; i--) {
            if (messages.value[i].role === 'tool' && messages.value[i].tool_status === 'calling') {
              messages.value[i].args += args
              break
            }
          }
        },

        onToolResult: (tool) => {
          for (let i = messages.value.length - 1; i >= 0; i--) {
            if (messages.value[i].role === 'tool' && messages.value[i].id === tool.id) {
              messages.value[i].text = tool.text || ''
              messages.value[i].images = tool.images || []
              messages.value[i].tool_status = 'done'
              break
            }
          }
          if (tool.name === 'start_async_task') {
            const taskId = extractAsyncTaskId(tool.text)
            startAsyncTaskPolling(taskId)
          }
        },

        onToolEnd: (tool) => {
          if (tool) {
            for (let i = messages.value.length - 1; i >= 0; i--) {
              if (messages.value[i].role === 'tool' && messages.value[i].id === tool.id && messages.value[i].tool_status === 'calling') {
                messages.value[i].tool_status = 'done'
                break
              }
            }
          }
          for (const m of messages.value) {
            if (m.role === 'tool' && m.tool_status === 'calling') {
              m.tool_status = 'done'
            }
          }
        },

        // ★ 恢复后仍可能再次中断（如：先数据补充 → 再 HITL 审批）
        onInterrupt: (data) => {
          console.log('[App] 恢复后再次中断:', data.interrupt_type)
          for (const m of messages.value) {
            if (m.role === 'tool' && m.tool_status === 'calling') {
              m.tool_status = 'done'
            }
          }
          messages.value = messages.value.filter(m => {
            if (m.role === 'assistant' && !m.content) return false
            return true
          })
          interruptData.value = data
        },

        onDone: (data) => {
          for (const m of messages.value) {
            if (m.role === 'tool' && m.tool_status === 'calling') {
              m.tool_status = 'done'
            }
          }
          messages.value = messages.value.filter(m => {
            if (m.role === 'assistant' && !m.content) return false
            return true
          })
          // 非中断完成 → 清除中断状态
          if (!data.interrupted) {
            interruptData.value = null
            // 更新 thread_id
            if (data.thread_id && !currentThreadId.value) {
              currentThreadId.value = data.thread_id
              loadSessions()
            }
          }
        },

        onError: (error) => {
          console.error('[App] 恢复对话错误:', error)
          interruptData.value = null  // 出错时清除中断状态，恢复普通输入
          const lastMsg = messages.value[messages.value.length - 1]
          if (lastMsg && lastMsg.role === 'assistant' && !lastMsg.content) {
            lastMsg.content = `抱歉，发生了错误：${error.message}`
          } else {
            messages.value.push({
              id: `assistant-${Date.now()}`,
              role: 'assistant',
              content: `抱歉，发生了错误：${error.message}`,
              source: 'main'
            })
          }
        }
      },
      abortController.signal
    )
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('[App] 恢复请求已被取消')
    } else {
      console.error('[App] 恢复请求失败:', error)
    }
  } finally {
    isResuming.value = false
    abortController = null
  }
}
</script>

<style scoped>
.app-container {
  display: flex;
  height: 100vh;
  background: #f8fafc;
  position: relative;
  overflow: hidden;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  width: 100%;
  background: #ffffff;
  position: relative;
  border-left: 1px solid #e2e8f0;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
}
</style>
