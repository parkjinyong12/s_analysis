<template>
  <div id="app" class="app-layout">
    <Sidebar />
    <main class="main-content">
      <div class="content-wrapper">
        <router-view @show-message="showMessage" />
      </div>
    </main>
    
    <!-- 메시지 토스트 -->
    <div v-if="message.show" :class="['message-toast', message.type]">
      <span>{{ message.text }}</span>
      <button @click="hideMessage" class="close-btn">×</button>
    </div>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'

export default {
  name: 'App',
  components: { Sidebar },
  data() {
    return {
      message: {
        show: false,
        text: '',
        type: 'info'
      }
    }
  },
  methods: {
    showMessage(text, type = 'info') {
      this.message = {
        show: true,
        text,
        type
      }
      
      // 5초 후 자동 숨김
      setTimeout(() => {
        this.hideMessage()
      }, 5000)
    },
    
    hideMessage() {
      this.message.show = false
    }
  }
}
</script>

<style>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}
.main-content {
  flex: 1;
  margin-left: 160px;
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
.content-wrapper {
  min-width: 700px;
  min-height: 600px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  padding: 32px 24px 24px 24px;
  width: 100%;
  max-width: 900px;
}

/* 메시지 토스트 스타일 */
.message-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 16px;
  border-radius: 6px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 300px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  animation: slideIn 0.3s ease-out;
}

.message-toast.success {
  background: #4caf50;
}

.message-toast.error {
  background: #f44336;
}

.message-toast.warning {
  background: #ff9800;
}

.message-toast.info {
  background: #2196f3;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  margin-left: auto;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
