<template>
  <div class="home-board">

    <!-- 통계 카드 섹션 -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-content">
            <div class="stat-number">{{ stockCount }}</div>
            <div class="stat-label">등록된 종목</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📈</div>
          <div class="stat-content">
            <div class="stat-number">{{ tradingCount }}</div>
            <div class="stat-label">거래 기록</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔄</div>
          <div class="stat-content">
            <div class="stat-number">{{ lastUpdate }}</div>
            <div class="stat-label">최근 업데이트</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚡</div>
          <div class="stat-content">
            <div class="stat-number">{{ apiStatus }}</div>
            <div class="stat-label">API 상태</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 메인 기능 섹션 -->
    <div class="main-features">
      <h2 class="section-title">주요 기능</h2>
      <div class="features-grid">
        <div class="feature-card" @click="navigateTo('/stock')">
          <div class="feature-header">
            <div class="feature-icon">📊</div>
            <h3>주식 목록</h3>
          </div>
          <p>실시간 주식 정보와 가격 데이터를 확인하세요</p>
          <div class="feature-action">
            <span class="action-text">바로가기</span>
            <span class="action-arrow">→</span>
          </div>
        </div>

        <div class="feature-card" @click="navigateTo('/trading')">
          <div class="feature-header">
            <div class="feature-icon">📈</div>
            <h3>거래 데이터</h3>
          </div>
          <p>투자자별 거래 현황과 패턴을 분석하세요</p>
          <div class="feature-action">
            <span class="action-text">바로가기</span>
            <span class="action-arrow">→</span>
          </div>
        </div>

        <div class="feature-card" @click="navigateTo('/collector')">
          <div class="feature-header">
            <div class="feature-icon">🔄</div>
            <h3>데이터 수집</h3>
          </div>
          <p>최신 주식 데이터를 수집하고 업데이트하세요</p>
          <div class="feature-action">
            <span class="action-text">바로가기</span>
            <span class="action-arrow">→</span>
          </div>
        </div>

        <div class="feature-card" @click="navigateTo('/api-test')">
          <div class="feature-header">
            <div class="feature-icon">🧪</div>
            <h3>API 테스트</h3>
          </div>
          <p>백엔드 API 연결 상태를 확인하고 테스트하세요</p>
          <div class="feature-action">
            <span class="action-text">바로가기</span>
            <span class="action-arrow">→</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 빠른 액션 섹션 -->
    <div class="quick-actions">
      <h2 class="section-title">빠른 액션</h2>
      <div class="action-buttons">
        <button class="action-btn primary" @click="navigateTo('/stock')">
          <span class="btn-icon">📊</span>
          <span class="btn-text">주식 목록 보기</span>
        </button>
        <button class="action-btn secondary" @click="navigateTo('/trading')">
          <span class="btn-icon">📈</span>
          <span class="btn-text">거래 데이터 확인</span>
        </button>
        <button class="action-btn secondary" @click="navigateTo('/collector')">
          <span class="btn-icon">🔄</span>
          <span class="btn-text">데이터 수집 시작</span>
        </button>
      </div>
    </div>

    <!-- 시스템 상태 섹션 -->
    <div class="system-status">
      <h2 class="section-title">시스템 상태</h2>
      <div class="status-grid">
        <div class="status-card">
          <div class="status-header">
            <span class="status-icon">🖥️</span>
            <span class="status-title">서버</span>
          </div>
          <div class="status-value" :class="serverStatus.class">
            {{ serverStatus.text }}
          </div>
        </div>
        <div class="status-card">
          <div class="status-header">
            <span class="status-icon">💾</span>
            <span class="status-title">데이터베이스</span>
          </div>
          <div class="status-value" :class="dbStatus.class">
            {{ dbStatus.text }}
          </div>
        </div>
        <div class="status-card">
          <div class="status-header">
            <span class="status-icon">🕒</span>
            <span class="status-title">마지막 업데이트</span>
          </div>
          <div class="status-value">
            {{ lastUpdateTime }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api, { API_ENDPOINTS } from '../../config/api.js'

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
        const response = await api.get(API_ENDPOINTS.API_TEST.HEALTH)
        if (response.status === 200) {
          serverStatus.value = { text: '정상', class: 'status-success' }
        }
      } catch (error) {
        serverStatus.value = { text: '오류', class: 'status-error' }
      }

      try {
        // 데이터베이스 상태 확인
        const dbResponse = await api.get(API_ENDPOINTS.API_TEST.DATABASE)
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

      // 히스토리에서 최근 활동 확인
      try {
        const latestActivityResponse = await api.get(API_ENDPOINTS.HISTORY.LATEST, {
          params: { limit: 1 }
        })
        
        if (latestActivityResponse.data && latestActivityResponse.data.length > 0) {
          const latestActivity = latestActivityResponse.data[0]
          const lastUpdateDate = new Date(latestActivity.created_at)
          lastUpdateTime.value = lastUpdateDate.toLocaleString('ko-KR')
          
          // "최근" 텍스트를 실제 시간으로 변경
          const now = new Date()
          const diffInHours = Math.floor((now - lastUpdateDate) / (1000 * 60 * 60))
          
          if (diffInHours < 1) {
            lastUpdate.value = '방금 전'
          } else if (diffInHours < 24) {
            lastUpdate.value = `${diffInHours}시간 전`
          } else {
            const diffInDays = Math.floor(diffInHours / 24)
            lastUpdate.value = `${diffInDays}일 전`
          }
        } else {
          // 히스토리가 없으면 "기록 없음"으로 설정
          lastUpdateTime.value = '-'
          lastUpdate.value = '기록 없음'
        }
      } catch (error) {
        // API 호출 실패 시 "확인 불가"로 설정
        lastUpdateTime.value = '-'
        lastUpdate.value = '확인 불가'
      }
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



/* 통계 섹션 */
.stats-section {
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.stat-icon {
  font-size: 2.5rem;
  color: #667eea;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 2rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
  line-height: 1;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  font-weight: 500;
}

/* 섹션 제목 */
.section-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 30px;
  color: #333;
  position: relative;
  padding-bottom: 12px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
}

/* 메인 기능 섹션 */
.main-features {
  margin-bottom: 50px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.feature-card {
  background: white;
  border-radius: 16px;
  padding: 28px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.feature-card:hover::before {
  transform: scaleX(1);
}

.feature-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.feature-icon {
  font-size: 2.5rem;
  color: #667eea;
  flex-shrink: 0;
}

.feature-card h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.feature-card p {
  color: #666;
  margin-bottom: 24px;
  line-height: 1.6;
  flex-grow: 1;
  font-size: 1rem;
}

.feature-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #667eea;
  font-weight: 600;
  font-size: 0.95rem;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.action-arrow {
  font-size: 1.2rem;
  transition: transform 0.3s ease;
}

.feature-card:hover .action-arrow {
  transform: translateX(4px);
}

/* 빠른 액션 섹션 */
.quick-actions {
  margin-bottom: 50px;
}

.action-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.action-btn {
  padding: 16px 24px;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 200px;
  justify-content: center;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.action-btn.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

.action-btn.secondary {
  background: white;
  color: #495057;
  border: 2px solid #e9ecef;
}

.action-btn.secondary:hover {
  background: #f8f9fa;
  border-color: #667eea;
  color: #667eea;
  transform: translateY(-2px);
}

.btn-icon {
  font-size: 1.3rem;
}

/* 시스템 상태 섹션 */
.system-status {
  background: white;
  border-radius: 16px;
  padding: 32px;
  border: 1px solid #e9ecef;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.status-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  border: 1px solid #e9ecef;
  transition: all 0.3s ease;
}

.status-card:hover {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-icon {
  font-size: 1.5rem;
  color: #667eea;
}

.status-title {
  font-weight: 600;
  color: #333;
  font-size: 1rem;
}

.status-value {
  font-weight: 700;
  font-size: 1.1rem;
  padding: 8px 16px;
  border-radius: 20px;
  background: white;
  border: 1px solid #e9ecef;
}

.status-success {
  color: #28a745;
  background: #d4edda;
  border-color: #c3e6cb;
}

.status-error {
  color: #dc3545;
  background: #f8d7da;
  border-color: #f5c6cb;
}

.status-loading {
  color: #ffc107;
  background: #fff3cd;
  border-color: #ffeaa7;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .home-board {
    padding: 15px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-card {
    padding: 20px;
  }

  .stat-icon {
    font-size: 2rem;
  }

  .stat-number {
    font-size: 1.6rem;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .feature-card {
    padding: 24px;
  }

  .feature-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .feature-icon {
    font-size: 2rem;
  }

  .feature-card h3 {
    font-size: 1.3rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
    min-width: auto;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }

  .status-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }

  .section-title {
    font-size: 1.6rem;
  }
}

@media (max-width: 480px) {

  .feature-card {
    padding: 20px;
  }

  .action-btn {
    padding: 14px 20px;
    font-size: 0.9rem;
  }
}
</style> 