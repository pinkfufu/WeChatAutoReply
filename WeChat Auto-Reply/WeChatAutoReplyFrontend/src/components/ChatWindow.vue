<template>
  <div class="app-layout">
    <div class="bg-mask"></div>

    <div class="main-content">
      <div class="chat-container">
        <div class="message-list" ref="messaggListRef">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="[
              'message',
              message.isUser ? 'user-message' : 'bot-message'
            ]"
          >
            <i
              :class="[
                'message-icon',
                message.isUser ? 'fa-solid fa-user' : 'fa-solid fa-robot'
              ]"
            ></i>

            <div class="message-content">
              <div class="markdown-body" v-html="renderMarkdown(message.content)"></div>
              
              <span
                class="loading-dots"
                v-if="message.isThinking || message.isTyping"
              >
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </span>
            </div>
          </div>
        </div>

        <div class="fixed-copy-container">
          <div 
            v-if="messages.length > 0 && !messages[messages.length-1].isUser && !isSending" 
            class="copy-action-fixed" 
            @click="copyToClipboard(messages[messages.length-1].content)"
          >
            <i class="fa-regular fa-copy"></i>
            <span class="copy-tips">复制最新回复</span>
          </div>
        </div>

        <div class="input-container">
          <el-input
            v-model="inputMessage"
            placeholder="请输入您的问题..."
            @keyup.enter="sendMessage"
            clearable
          />
          <el-button
            type="primary"
            :disabled="isSending"
            @click="sendMessage"
          >
            发送
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import MarkdownIt from 'markdown-it'
import { ElMessage } from 'element-plus'

const messaggListRef = ref()
const inputMessage = ref('')
const messages = ref([])
const isSending = ref(false)
const uuid = ref()

const md = new MarkdownIt({ html: true, linkify: true, breaks: true })

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage({ message: '内容已存入剪贴板', type: 'success', duration: 1000 })
  } catch (err) {
    ElMessage.error('复制失败')
  }
}

const renderMarkdown = (content) => {
  if (!content) return ''
  let html = md.render(content)
  return html.replace(/\*\*\s*([\s\S]+?)\s*\*\*/g, (match, p1) => {
    return `<strong style="font-weight: 900 !important; color: inherit; text-shadow: 0.6px 0 0 currentColor;">${p1}</strong>`
  })
}

onMounted(() => {
  initUUID()
  watch(messages, scrollToBottom, { deep: true })
  hello()
})

const hello = () => {
  messages.value.push({
    isUser: false,
    content: '你好，我是 **小助手**',
    isTyping: false
  })
}

const sendMessage = () => {
  if (!inputMessage.value.trim() || isSending.value) return
  const text = inputMessage.value.trim()
  messages.value.push({ isUser: true, content: text })
  sendRequest(text)
  inputMessage.value = ''
}

const sendRequest = (message) => {
  isSending.value = true
  const botMsg = { isUser: false, content: '', isTyping: true }
  messages.value.push(botMsg)
  const lastIdx = messages.value.length - 1

  axios.post('/api/xiaozhi/chat', { memoryId: uuid.value, message }, {
    responseType: 'text',
    onDownloadProgress: (e) => {
      messages.value[lastIdx].content = e.event.target.responseText
      scrollToBottom()
    }
  }).then(() => {
    messages.value[lastIdx].isTyping = false
    isSending.value = false
  }).catch(() => {
    messages.value[lastIdx].content = '❌ 连接失败'
    messages.value[lastIdx].isTyping = false
    isSending.value = false
  })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messaggListRef.value) {
      messaggListRef.value.scrollTop = messaggListRef.value.scrollHeight
    }
  })
}

const initUUID = () => {
  let id = localStorage.getItem('user_uuid')
  if (!id) { 
    id = Math.floor(Math.random() * 1000000)
    localStorage.setItem('user_uuid', id) 
  }
  uuid.value = id
}
</script>

<style scoped>
.app-layout {
  height: 100vh;
  display: flex;
  background: #f0f2f5;
  position: relative;
}

.bg-mask {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(4px);
}

.main-content {
  z-index: 1;
  flex: 1;
  padding: 20px;
  overflow: hidden;
}

.chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding-bottom: 20px;
}

.message {
  display: flex;
  margin-bottom: 20px;
}

.message-content {
  max-width: 85%;
  padding: 12px;
  background: #f4f4f5;
  border-radius: 8px;
  margin: 0 10px;
  font-size: 14px;
  line-height: 1.6;
}

.user-message { flex-direction: row-reverse; }
.user-message .message-content { background: #39c5bb; color: #fff; }

/* ================= 固定复制按钮容器 ================= */
.fixed-copy-container {
  height: 45px; /* 固定高度，确保下方输入框坐标不动 */
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 10px;
  border-top: 1px dashed #eee;
}

.copy-action-fixed {
  background: #39c5bb;
  color: #fff;
  padding: 6px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  box-shadow: 0 2px 5px rgba(57, 197, 187, 0.4);
}

.copy-action-fixed:active {
  transform: translateY(1px);
}

/* ================= 输入框区域 ================= */
.input-container {
  display: flex;
  gap: 10px;
  padding-top: 15px;
}

.loading-dots .dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #39c5bb;
  border-radius: 50%;
  margin-left: 4px;
  animation: pulse 1.2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(0.8); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 1; }
}
</style>