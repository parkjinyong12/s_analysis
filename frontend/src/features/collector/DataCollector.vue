<template>
  <div class="data-collector">
    <!-- 헤더 -->
    <div class="collector-header">
      <h2>📊 데이터 수집</h2>
      <p class="description">네이버 금융에서 주식 거래 데이터를 수집합니다</p>
    </div>

    <!-- 수집 설정 -->
    <div class="collector-settings" v-if="!status.is_running">
      <div class="setting-group">
        <label for="years">수집 기간:</label>
        <select id="years" v-model="settings.years" class="form-select">
          <option value="1">1년</option>
          <option value="2">2년</option>
          <option value="3">3년</option>
          <option value="5">5년</option>
        </select>
      </div>
      
      <div class="setting-info">
        <p>💡 <strong>{{ stockList.length }}개 종목</strong>의 최근 {{ settings.years }}년간 데이터를 수집합니다</p>
        <p>⏱️ 예상 소요 시간: 약 {{ estimatedTime }}분</p>
      </div>
    </div>

    <!-- 진행률 표시 -->
    <div class="progress-section" v-if="status.is_running || status.current_phase !== 'idle'">
      <div class="progress-header">
        <h3>{{ getPhaseText(status.current_phase) }}</h3>
        <div class="progress-stats">
          <span class="stat success">성공: {{ status.success_count }}</span>
          <span class="stat failed">실패: {{ status.failed_count }}</span>
          <span class="stat total">전체: {{ status.total_stocks }}</span>
        </div>
      </div>

      <!-- 진행률 바 -->
      <div class="progress-bar-container">
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: status.progress + '%' }"
            :class="getProgressClass(status.current_phase)"
          ></div>
        </div>
        <span class="progress-text">{{ status.progress }}%</span>
      </div>

      <!-- 현재 처리 중인 주식 -->
      <div class="current-stock" v-if="status.current_stock">
        <p>🔄 현재 처리 중: <strong>{{ status.current_stock }}</strong></p>
      </div>

      <!-- 경과 시간 -->
      <div class="elapsed-time" v-if="status.elapsed_time">
        <p>⏱️ 경과 시간: {{ formatElapsedTime(status.elapsed_time) }}</p>
      </div>
    </div>

    <!-- 제어 버튼 -->
    <div class="control-buttons">
      <button 
        @click="startCollection" 
        :disabled="status.is_running || isLoading"
        class="btn btn-primary"
        v-if="!status.is_running"
      >
        <span v-if="isLoading">⏳ 시작 중...</span>
        <span v-else>🚀 수집 시작</span>
      </button>

      <button 
        @click="stopCollection" 
        :disabled="!status.is_running || status.current_phase === 'stopping'"
        class="btn btn-danger"
        v-if="status.is_running"
      >
        <span v-if="status.current_phase === 'stopping'">⏳ 중단 중...</span>
        <span v-else>⏹️ 수집 중단</span>
      </button>

      <button 
        @click="resetStatus" 
        :disabled="status.is_running"
        class="btn btn-secondary"
        v-if="status.current_phase === 'completed' || status.current_phase === 'error' || status.current_phase === 'cancelled'"
      >
        🔄 초기화
      </button>
    </div>

    <!-- 오류 메시지 -->
    <div class="error-message" v-if="status.error_message">
      <h4>❌ 오류 발생</h4>
      <p>{{ status.error_message }}</p>
    </div>

    <!-- 실패한 주식 목록 -->
    <div class="failed-stocks" v-if="status.failed_stocks && status.failed_stocks.length > 0">
      <h4>⚠️ 실패한 주식 ({{ status.failed_stocks.length }}개)</h4>
      <div class="failed-list">
        <div 
          v-for="(stock, index) in status.failed_stocks" 
          :key="index"
          class="failed-item"
        >
          {{ stock }}
        </div>
      </div>
    </div>

    <!-- 수집 가능한 주식 목록 -->
    <div class="stock-list-section" v-if="showStockList">
      <h4>📋 수집 대상 주식 목록</h4>
      <button @click="showStockList = false" class="btn btn-sm btn-outline">숨기기</button>
      <div class="stock-grid">
        <div 
          v-for="stock in stockList" 
          :key="stock.code"
          class="stock-item"
        >
          <span class="stock-code">{{ stock.code }}</span>
          <span class="stock-name">{{ stock.name }}</span>
        </div>
      </div>
    </div>

    <div class="show-stock-list" v-if="!showStockList">
      <button @click="showStockList = true" class="btn btn-sm btn-outline">
        📋 수집 대상 주식 목록 보기 ({{ stockList.length }}개)
      </button>
    </div>

    <!-- 완료 메시지 -->
    <div class="completion-message" v-if="status.current_phase === 'completed'">
      <h3>✅ 데이터 수집 완료!</h3>
      <div class="completion-stats">
        <p>📊 총 {{ status.total_stocks }}개 종목 중 {{ status.success_count }}개 성공</p>
        <p>⏱️ 총 소요 시간: {{ formatElapsedTime(status.elapsed_time) }}</p>
        <p v-if="status.failed_count > 0">⚠️ {{ status.failed_count }}개 종목 실패</p>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'DataCollector',
  data() {
    return {
      settings: {
        years: 3
      },
      status: {
        is_running: false,
        current_stock: '',
        progress: 0,
        total_stocks: 0,
        success_count: 0,
        failed_count: 0,
        start_time: null,
        end_time: null,
        current_phase: 'idle',
        error_message: '',
        failed_stocks: [],
        elapsed_time: null
      },
      stockList: [],
      isLoading: false,
      showStockList: false,
      statusInterval: null
    }
  },
  computed: {
    estimatedTime() {
      // 주식당 약 3초 + 네트워크 지연 고려
      return Math.ceil((this.stockList.length * 3) / 60)
    }
  },
  mounted() {
    this.loadStockList()
    this.loadStatus()
    this.startStatusPolling()
  },
  beforeUnmount() {
    this.stopStatusPolling()
  },
  methods: {
    async loadStockList() {
      try {
        const response = await axios.get('/collector/stocks')
        this.stockList = response.data.stocks || []
      } catch (error) {
        console.error('주식 목록 로딩 실패:', error)
        this.$emit('show-message', '주식 목록을 불러오는데 실패했습니다.', 'error')
      }
    },

    async loadStatus() {
      try {
        const response = await axios.get('/collector/status')
        this.status = { ...this.status, ...response.data }
      } catch (error) {
        console.error('상태 로딩 실패:', error)
      }
    },

    startStatusPolling() {
      // 2초마다 상태 업데이트
      this.statusInterval = setInterval(() => {
        this.loadStatus()
      }, 2000)
    },

    stopStatusPolling() {
      if (this.statusInterval) {
        clearInterval(this.statusInterval)
        this.statusInterval = null
      }
    },

    async startCollection() {
      this.isLoading = true
      try {
        const response = await axios.post('/collector/start', {
          years: this.settings.years
        })
        
        this.$emit('show-message', response.data.message, 'success')
        this.loadStatus() // 즉시 상태 업데이트
        
      } catch (error) {
        console.error('수집 시작 실패:', error)
        const message = error.response?.data?.error || '데이터 수집을 시작하는데 실패했습니다.'
        this.$emit('show-message', message, 'error')
      } finally {
        this.isLoading = false
      }
    },

    async stopCollection() {
      try {
        const response = await axios.post('/collector/stop')
        this.$emit('show-message', response.data.message, 'warning')
        
      } catch (error) {
        console.error('수집 중단 실패:', error)
        const message = error.response?.data?.error || '데이터 수집을 중단하는데 실패했습니다.'
        this.$emit('show-message', message, 'error')
      }
    },

    async resetStatus() {
      try {
        const response = await axios.post('/collector/reset')
        this.$emit('show-message', response.data.message, 'info')
        this.loadStatus()
        
      } catch (error) {
        console.error('상태 초기화 실패:', error)
        const message = error.response?.data?.error || '상태를 초기화하는데 실패했습니다.'
        this.$emit('show-message', message, 'error')
      }
    },

    getPhaseText(phase) {
      const phaseTexts = {
        'idle': '대기 중',
        'initializing': '초기화 중',
        'collecting': '데이터 수집 중',
        'completed': '수집 완료',
        'error': '오류 발생',
        'cancelled': '수집 중단됨',
        'stopping': '중단 중'
      }
      return phaseTexts[phase] || phase
    },

    getProgressClass(phase) {
      const classes = {
        'initializing': 'progress-initializing',
        'collecting': 'progress-collecting',
        'completed': 'progress-completed',
        'error': 'progress-error',
        'cancelled': 'progress-cancelled'
      }
      return classes[phase] || ''
    },

    formatElapsedTime(timeStr) {
      if (!timeStr) return '0초'
      
      // "0:05:23.123456" 형식을 파싱
      const parts = timeStr.split(':')
      if (parts.length === 3) {
        const hours = parseInt(parts[0])
        const minutes = parseInt(parts[1])
        const seconds = Math.floor(parseFloat(parts[2]))
        
        if (hours > 0) {
          return `${hours}시간 ${minutes}분 ${seconds}초`
        } else if (minutes > 0) {
          return `${minutes}분 ${seconds}초`
        } else {
          return `${seconds}초`
        }
      }
      
      return timeStr
    }
  }
}
</script>

<style scoped>
.data-collector {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.collector-header {
  text-align: center;
  margin-bottom: 30px;
}

.collector-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.description {
  color: #7f8c8d;
  font-size: 14px;
}

.collector-settings {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.setting-group {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.setting-group label {
  font-weight: 600;
  min-width: 80px;
}

.form-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.setting-info {
  background: #e3f2fd;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #2196f3;
}

.setting-info p {
  margin: 5px 0;
  font-size: 14px;
}

.progress-section {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.progress-header h3 {
  margin: 0;
  color: #2c3e50;
}

.progress-stats {
  display: flex;
  gap: 15px;
}

.stat {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
  font-weight: 600;
}

.stat.success {
  background: #e8f5e8;
  color: #2e7d32;
}

.stat.failed {
  background: #ffebee;
  color: #c62828;
}

.stat.total {
  background: #e3f2fd;
  color: #1976d2;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 15px;
}

.progress-bar {
  flex: 1;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
  border-radius: 10px;
}

.progress-initializing {
  background: linear-gradient(90deg, #ffc107, #ff9800);
}

.progress-collecting {
  background: linear-gradient(90deg, #2196f3, #03a9f4);
}

.progress-completed {
  background: linear-gradient(90deg, #4caf50, #8bc34a);
}

.progress-error {
  background: linear-gradient(90deg, #f44336, #e57373);
}

.progress-cancelled {
  background: linear-gradient(90deg, #9e9e9e, #bdbdbd);
}

.progress-text {
  font-weight: 600;
  min-width: 40px;
  text-align: right;
}

.current-stock {
  background: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
}

.current-stock p {
  margin: 0;
  font-size: 14px;
}

.elapsed-time p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.control-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-outline {
  background: transparent;
  border: 1px solid #007bff;
  color: #007bff;
}

.btn-outline:hover {
  background: #007bff;
  color: white;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.error-message {
  background: #ffebee;
  border: 1px solid #f44336;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
}

.error-message h4 {
  margin: 0 0 10px 0;
  color: #c62828;
}

.failed-stocks {
  background: #fff3e0;
  border: 1px solid #ff9800;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
}

.failed-stocks h4 {
  margin: 0 0 15px 0;
  color: #ef6c00;
}

.failed-list {
  max-height: 200px;
  overflow-y: auto;
}

.failed-item {
  background: #fff;
  padding: 8px 12px;
  margin-bottom: 5px;
  border-radius: 4px;
  font-size: 13px;
  border-left: 3px solid #ff9800;
}

.stock-list-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.stock-list-section h4 {
  margin: 0 0 15px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  max-height: 300px;
  overflow-y: auto;
  margin-top: 15px;
}

.stock-item {
  background: white;
  padding: 10px;
  border-radius: 4px;
  border: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stock-code {
  font-family: monospace;
  font-weight: 600;
  color: #1976d2;
}

.stock-name {
  font-size: 13px;
  color: #666;
}

.show-stock-list {
  text-align: center;
  margin-bottom: 20px;
}

.completion-message {
  background: #e8f5e8;
  border: 1px solid #4caf50;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
}

.completion-message h3 {
  margin: 0 0 15px 0;
  color: #2e7d32;
}

.completion-stats p {
  margin: 5px 0;
  font-size: 14px;
}
</style> 