<template>
  <div class="home-board">
    <div class="welcome-section">
      <h1 class="welcome-title">🏠 주식 분석 시스템에 오신 것을 환영합니다!</h1>
      <p class="welcome-subtitle">실시간 주식 데이터 분석 및 거래 정보를 확인하세요</p>
    </div>

    <div class="features-grid">
      <div class="feature-card" @click="navigateTo('/stock')">
        <div class="feature-icon">📊</div>
        <h3>주식 목록</h3>
        <p>실시간 주식 정보와 가격 데이터를 확인하세요</p>
        <div class="feature-stats">
          <span class="stat-item">
            <strong>{{ stockCount }}</strong> 종목
          </span>
        </div>
      </div>

      <div class="feature-card" @click="navigateTo('/trading')">
        <div class="feature-icon">📈</div>
        <h3>거래 데이터</h3>
        <p>투자자별 거래 현황과 패턴을 분석하세요</p>
        <div class="feature-stats">
          <span class="stat-item">
            <strong>{{ tradingCount }}</strong> 거래
          </span>
        </div>
      </div>

      <div class="feature-card" @click="navigateTo('/collector')">
        <div class="feature-icon">🔄</div>
        <h3>데이터 수집</h3>
        <p>최신 주식 데이터를 수집하고 업데이트하세요</p>
        <div class="feature-stats">
          <span class="stat-item">
            <strong>{{ lastUpdate }}</strong> 업데이트
          </span>
        </div>
      </div>

      <div class="feature-card" @click="navigateTo('/api-test')">
        <div class="feature-icon">🧪</div>
        <h3>API 테스트</h3>
        <p>백엔드 API 연결 상태를 확인하고 테스트하세요</p>
        <div class="feature-stats">
          <span class="stat-item">
            <strong>{{ apiStatus }}</strong> 상태
          </span>
        </div>
      </div>
    </div>

    <div class="quick-actions">
      <h2>빠른 액션</h2>
      <div class="action-buttons">
        <button class="action-btn primary" @click="navigateTo('/stock')">
          📊 주식 목록 보기
        </button>
        <button class="action-btn secondary" @click="navigateTo('/trading')">
          📈 거래 데이터 확인
        </button>
        <button class="action-btn secondary" @click="navigateTo('/collector')">
          🔄 데이터 수집 시작
        </button>
      </div>
    </div>

    <div class="system-info">
      <h2>시스템 정보</h2>
      <div class="info-grid">
        <div class="info-item">
          <span class="info-label">서버 상태:</span>
          <span class="info-value" :class="serverStatus.class">{{ serverStatus.text }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">데이터베이스:</span>
          <span class="info-value" :class="dbStatus.class">{{ dbStatus.text }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">마지막 업데이트:</span>
          <span class="info-value">{{ lastUpdateTime }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'HomeBoard',
  setup() {
    const router = useRouter()
    
    const stockCount = ref(0)
    const tradingCount = ref(0)
    const lastUpdate = ref('최근')
    const apiStatus = ref('정상')
    const serverStatus = ref({ text: '확인 중...', class: 'status-loading' })
    const dbStatus = ref({ text: '확인 중...', class: 'status-loading' })
    const lastUpdateTime = ref('로딩 중...')

    const navigateTo = (path) => {
      router.push(path)
    }

    const checkSystemStatus = async () => {
      try {
        // API 상태 확인
        const response = await axios.get('/api/health')
        if (response.status === 200) {
          serverStatus.value = { text: '정상', class: 'status-success' }
        }
      } catch (error) {
        serverStatus.value = { text: '오류', class: 'status-error' }
      }

      try {
        // 데이터베이스 상태 확인
        const dbResponse = await axios.get('/api/database')
        if (dbResponse.data.database_status === 'connected') {
          dbStatus.value = { text: '연결됨', class: 'status-success' }
          
          // 데이터 개수 가져오기
          const tables = dbResponse.data.tables
          if (tables.stock_list) {
            stockCount.value = tables.stock_list.record_count || 0
          }
          if (tables.stock_investor_trading) {
            tradingCount.value = tables.stock_investor_trading.record_count || 0
          }
        } else {
          dbStatus.value = { text: '연결 오류', class: 'status-error' }
        }
      } catch (error) {
        dbStatus.value = { text: '연결 실패', class: 'status-error' }
      }

      // 마지막 업데이트 시간 설정
      lastUpdateTime.value = new Date().toLocaleString('ko-KR')
    }

    onMounted(() => {
      checkSystemStatus()
    })

    return {
      stockCount,
      tradingCount,
      lastUpdate,
      apiStatus,
      serverStatus,
      dbStatus,
      lastUpdateTime,
      navigateTo
    }
  }
}
</script>

<style scoped>
.home-board {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
}

.welcome-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 16px;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.welcome-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  margin: 0;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.feature-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  border: 2px solid transparent;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
  border-color: #667eea;
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 16px;
  text-align: center;
}

.feature-card h3 {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.feature-card p {
  color: #666;
  margin-bottom: 16px;
  line-height: 1.5;
}

.feature-stats {
  display: flex;
  justify-content: center;
}

.stat-item {
  background: #f8f9fa;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #495057;
}

.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 40px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.quick-actions h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.action-btn.secondary {
  background: #f8f9fa;
  color: #495057;
  border: 2px solid #e9ecef;
}

.action-btn.secondary:hover {
  background: #e9ecef;
  border-color: #dee2e6;
}

.system-info {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.08);
}

.system-info h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-label {
  font-weight: 500;
  color: #495057;
}

.info-value {
  font-weight: 600;
}

.status-success {
  color: #28a745;
}

.status-error {
  color: #dc3545;
}

.status-loading {
  color: #ffc107;
}

/* 반응형 */
@media (max-width: 768px) {
  .welcome-title {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style> 