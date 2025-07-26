<template>
  <div class="api-test">
    <!-- 헤더 -->
    <header class="test-header">
      <h2>API 테스트</h2>
      <p class="test-description">서버의 모든 REST API 엔드포인트를 테스트하고 상태를 확인합니다.</p>
    </header>

    <!-- 컨트롤 패널 -->
    <section class="control-panel">
      <div class="control-buttons">
        <button 
          @click="runAllTests" 
          :disabled="isLoading"
          class="btn btn-primary"
        >
          {{ isLoading ? '테스트 실행 중...' : '전체 테스트 실행' }}
        </button>
        <button 
          @click="checkHealth" 
          :disabled="isLoading"
          class="btn btn-secondary"
        >
          서버 상태 확인
        </button>
        <button 
          @click="testDatabase" 
          :disabled="isLoading"
          class="btn btn-info"
        >
          데이터베이스 테스트
        </button>
        <button 
          @click="initializeDatabase" 
          :disabled="isLoading"
          class="btn btn-success"
          title="테이블이 없는 경우에만 생성 (기존 데이터 보존)"
        >
          테이블 생성
        </button>
        <button 
          @click="resetDatabase" 
          :disabled="isLoading"
          class="btn btn-warning"
          title="⚠️ 모든 테스트 데이터 삭제 (복구 불가)"
        >
          데이터 초기화
        </button>
        <button 
          @click="clearResults" 
          :disabled="isLoading"
          class="btn btn-outline"
        >
          결과 초기화
        </button>
      </div>
      
      <!-- 자동 새로고침 -->
      <div class="auto-refresh">
        <label class="checkbox-label">
          <input 
            type="checkbox" 
            v-model="autoRefresh"
            @change="toggleAutoRefresh"
          />
          자동 새로고침 (30초)
        </label>
      </div>
    </section>

    <!-- 에러 메시지 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- 테스트 요약 -->
    <section v-if="testSummary" class="test-summary">
      <h3>테스트 요약</h3>
      <div class="summary-cards">
        <div class="summary-card total">
          <div class="card-value">{{ testSummary.total_tests }}</div>
          <div class="card-label">전체 테스트</div>
        </div>
        <div class="summary-card success">
          <div class="card-value">{{ testSummary.successful_tests }}</div>
          <div class="card-label">성공</div>
        </div>
        <div class="summary-card failed">
          <div class="card-value">{{ testSummary.failed_tests }}</div>
          <div class="card-label">실패</div>
        </div>
        <div class="summary-card rate">
          <div class="card-value">{{ testSummary.success_rate }}%</div>
          <div class="card-label">성공률</div>
        </div>
      </div>
      <div class="test-timestamp">
        마지막 테스트: {{ formatDate(testSummary.test_timestamp) }}
      </div>
    </section>

    <!-- 서버 상태 -->
    <section v-if="serverHealth" class="server-status">
      <h3>서버 상태</h3>
      <div class="status-info">
        <div class="status-badge" :class="serverHealth.status">
          {{ serverHealth.status === 'healthy' ? '정상' : '오류' }}
        </div>
        <div class="status-details">
          <p><strong>메시지:</strong> {{ serverHealth.message }}</p>
          <p><strong>서버:</strong> {{ serverHealth.server }}</p>
          <p><strong>확인 시간:</strong> {{ formatDate(serverHealth.timestamp) }}</p>
        </div>
      </div>
    </section>

    <!-- 데이터베이스 상태 -->
    <section v-if="databaseStatus" class="database-status">
      <h3>데이터베이스 상태</h3>
      <div class="db-info">
        <div class="status-badge" :class="databaseStatus.database_status">
          {{ getDbStatusText(databaseStatus.database_status) }}
        </div>
        <div v-if="databaseStatus.tables" class="tables-info">
          <h4>테이블 정보</h4>
          <div class="table-list">
            <div 
              v-for="(table, name) in databaseStatus.tables" 
              :key="name"
              class="table-item"
            >
              <span class="table-name">{{ name }}</span>
              <span class="table-status" :class="table.status">
                {{ table.status === 'accessible' ? '정상' : '오류' }}
              </span>
              <span class="table-count">{{ table.record_count }}개 레코드</span>
              <span v-if="table.error" class="table-error">{{ table.error }}</span>
            </div>
          </div>
        </div>
        <div v-if="databaseStatus.error" class="db-error">
          <strong>오류:</strong> {{ databaseStatus.error }}
        </div>
      </div>
    </section>

    <!-- 테스트 결과 -->
    <section v-if="testResults.length > 0" class="test-results">
      <h3>테스트 결과</h3>
      <div class="results-list">
        <div 
          v-for="(result, index) in testResults" 
          :key="index"
          class="result-item"
          :class="{ success: result.success, failed: !result.success }"
        >
          <div class="result-header">
            <div class="result-info">
              <span class="result-name">{{ result.name }}</span>
              <span class="result-method">{{ result.method }}</span>
              <span class="result-status" :class="{ success: result.success, failed: !result.success }">
                {{ result.success ? '성공' : '실패' }}
              </span>
            </div>
            <div class="result-meta">
              <span v-if="result.response_time_ms" class="response-time">
                {{ Math.round(result.response_time_ms) }}ms
              </span>
              <span class="status-code" :class="getStatusClass(result.actual_status)">
                {{ result.actual_status || 'N/A' }}
              </span>
            </div>
          </div>
          
          <div class="result-details">
            <div class="result-url">
              <strong>URL:</strong> {{ result.url }}
            </div>
            <div v-if="result.error" class="result-error">
              <strong>오류:</strong> {{ result.error }}
            </div>
            <div v-if="result.response_preview" class="result-preview">
              <strong>응답 미리보기:</strong>
              <pre class="response-data">{{ JSON.stringify(result.response_preview, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>API 테스트를 실행하고 있습니다...</p>
    </div>
  </div>
</template>

<script>
import { api, API_ENDPOINTS } from '@/config/api';

export default {
  name: 'ApiTest',
  
  data() {
    return {
      // 테스트 상태
      isLoading: false,
      errorMessage: '',
      
      // 테스트 결과
      testResults: [],
      testSummary: null,
      serverHealth: null,
      databaseStatus: null,
      
      // 자동 새로고침
      autoRefresh: false,
      refreshInterval: null,
      
      // API 설정 (더 이상 필요 없음 - 중앙화된 설정 사용)
    };
  },
  
  beforeUnmount() {
    // 컴포넌트 해제 시 자동 새로고침 중지
    this.clearAutoRefresh();
  },
  
  methods: {
    /**
     * 전체 API 테스트 실행
     */
    async runAllTests() {
      try {
        this.isLoading = true;
        this.clearError();
        
        const response = await api.get(API_ENDPOINTS.API_TEST.ENDPOINTS);
        
        this.testSummary = response.data.summary;
        this.testResults = response.data.results;
        
        this.showMessage('API 테스트가 완료되었습니다.', 'success');
        
      } catch (error) {
        console.error('API 테스트 실행 실패:', error);
        this.showError('API 테스트 실행에 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 서버 상태 확인
     */
    async checkHealth() {
      try {
        this.isLoading = true;
        this.clearError();
        
        const response = await api.get(API_ENDPOINTS.API_TEST.HEALTH);
        this.serverHealth = response.data;
        
        this.showMessage('서버 상태를 확인했습니다.', 'success');
        
      } catch (error) {
        console.error('서버 상태 확인 실패:', error);
        this.serverHealth = {
          status: 'error',
          message: '서버 연결 실패',
          timestamp: new Date().toISOString()
        };
        this.showError('서버 상태 확인에 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 데이터베이스 연결 테스트
     */
    async testDatabase() {
      try {
        this.isLoading = true;
        this.clearError();
        
        const response = await api.get(API_ENDPOINTS.API_TEST.DATABASE);
        this.databaseStatus = response.data;
        
        this.showMessage('데이터베이스 상태를 확인했습니다.', 'success');
        
      } catch (error) {
        console.error('데이터베이스 테스트 실패:', error);
        this.databaseStatus = {
          database_status: 'error',
          error: '데이터베이스 연결 실패',
          timestamp: new Date().toISOString()
        };
        this.showError('데이터베이스 테스트에 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 데이터베이스 초기화 (테이블 생성만, 데이터 삭제 안함)
     */
    async initializeDatabase() {
      const confirmMessage = '데이터베이스 테이블을 생성하시겠습니까?\n\n⚠️ 안전 알림:\n- 기존 테이블이 없는 경우에만 새로 생성됩니다\n- 기존 데이터는 삭제되지 않습니다\n- 테이블 구조만 생성하는 안전한 작업입니다';
      
      if (!confirm(confirmMessage)) {
        return;
      }
      
      try {
        this.isLoading = true;
        this.clearError();
        
        const response = await api.post(API_ENDPOINTS.API_TEST.DATABASE_INIT);
        
        if (response.data.status === 'success') {
          this.showMessage(`테이블이 생성되었습니다. (${response.data.total_tables}개 테이블) - 기존 데이터는 보존됨`, 'success');
          
          // 초기화 후 자동으로 데이터베이스 상태 재확인
          setTimeout(() => {
            if (!this.isLoading) {
              this.testDatabase();
            }
          }, 1000);
        } else {
          this.showError(response.data.message || '테이블 생성에 실패했습니다.');
        }
        
      } catch (error) {
        console.error('테이블 생성 실패:', error);
        this.showError('테이블 생성에 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 데이터베이스 데이터 초기화 (모든 데이터 삭제)
     */
    async resetDatabase() {
      const confirmMessage = '⚠️ 경고: 모든 테스트 데이터가 삭제됩니다!\n\n정말로 모든 데이터를 초기화하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.';
      
      if (!confirm(confirmMessage)) {
        return;
      }
      
      try {
        this.isLoading = true;
        this.clearError();
        
        const response = await api.post('/api-test/database/reset');
        
        if (response.data.status === 'success') {
          this.showMessage('모든 테스트 데이터가 초기화되었습니다.', 'success');
          
          // 초기화 후 자동으로 데이터베이스 상태 재확인
          setTimeout(() => {
            if (!this.isLoading) {
              this.testDatabase();
            }
          }, 1000);
        } else {
          this.showError(response.data.message || '데이터 초기화에 실패했습니다.');
        }
        
      } catch (error) {
        console.error('데이터 초기화 실패:', error);
        this.showError('데이터 초기화에 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 결과 초기화
     */
    clearResults() {
      this.testResults = [];
      this.testSummary = null;
      this.serverHealth = null;
      this.databaseStatus = null;
      this.clearError();
    },
    
    /**
     * 자동 새로고침 토글
     */
    toggleAutoRefresh() {
      if (this.autoRefresh) {
        this.startAutoRefresh();
      } else {
        this.clearAutoRefresh();
      }
    },
    
    /**
     * 자동 새로고침 시작
     */
    startAutoRefresh() {
      this.clearAutoRefresh();
      this.refreshInterval = setInterval(() => {
        if (!this.isLoading) {
          this.runAllTests();
        }
      }, 30000); // 30초마다 실행
    },
    
    /**
     * 자동 새로고침 중지
     */
    clearAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval);
        this.refreshInterval = null;
      }
    },
    
    /**
     * HTTP 상태 코드에 따른 CSS 클래스 반환
     */
    getStatusClass(statusCode) {
      if (!statusCode) return 'unknown';
      if (statusCode >= 200 && statusCode < 300) return 'success';
      if (statusCode >= 400 && statusCode < 500) return 'client-error';
      if (statusCode >= 500) return 'server-error';
      return 'info';
    },
    
    /**
     * 날짜 포맷팅
     */
    formatDate(dateString) {
      if (!dateString) return '-';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleString('ko-KR', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        });
      } catch (error) {
        console.warn('날짜 포맷팅 실패:', error);
        return dateString;
      }
    },
    
    /**
     * 에러 메시지 표시
     */
    showError(message) {
      this.errorMessage = message;
      setTimeout(() => {
        this.clearError();
      }, 5000);
    },
    
    /**
     * 에러 메시지 제거
     */
    clearError() {
      this.errorMessage = '';
    },
    
    /**
     * 성공 메시지 표시 (부모 컴포넌트의 toast 사용)
     */
    showMessage(message, type = 'info') {
      this.$emit('show-message', { message, type });
    },
    
    /**
     * 데이터베이스 상태 텍스트 반환
     */
    getDbStatusText(status) {
      switch (status) {
        case 'connected': return '연결됨';
        case 'connected_with_errors': return '연결됨 (일부 오류)';
        case 'error': return '오류';
        default: return status;
      }
    }
  }
};
</script>

<style scoped>
/* 메인 컨테이너 */
.api-test {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* 헤더 */
.test-header {
  margin-bottom: 32px;
  text-align: center;
}

.test-header h2 {
  color: #1976d2;
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 600;
}

.test-description {
  color: #666;
  font-size: 16px;
  margin: 0;
}

/* 컨트롤 패널 */
.control-panel {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.control-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.auto-refresh {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: #666;
}

/* 버튼 스타일 */
.btn {
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 120px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #1976d2;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1565c0;
  transform: translateY(-1px);
}

.btn-secondary {
  background: #43a047;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #388e3c;
}

.btn-info {
  background: #00acc1;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #00838f;
}

.btn-outline {
  background: transparent;
  color: #666;
  border: 2px solid #e0e0e0;
}

.btn-outline:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #bdbdbd;
}

.btn-warning {
  background: #ff9800;
  color: white;
}

.btn-warning:hover:not(:disabled) {
  background: #f57c00;
}

.btn-success {
  background: #43a047;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #388e3c;
}

/* 에러 메시지 */
.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 4px solid #e53935;
}

/* 테스트 요약 */
.test-summary {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-summary h3 {
  margin-bottom: 16px;
  color: #333;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.summary-card {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  color: white;
}

.summary-card.total {
  background: #1976d2;
}

.summary-card.success {
  background: #43a047;
}

.summary-card.failed {
  background: #e53935;
}

.summary-card.rate {
  background: #ff9800;
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 4px;
}

.card-label {
  font-size: 14px;
  opacity: 0.9;
}

.test-timestamp {
  text-align: center;
  color: #666;
  font-size: 14px;
}

/* 서버 상태 */
.server-status, .database-status {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.server-status h3, .database-status h3 {
  margin-bottom: 16px;
  color: #333;
}

.status-info, .db-info {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.status-badge {
  padding: 8px 16px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
}

.status-badge.healthy, .status-badge.connected, .status-badge.accessible {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-badge.connected_with_errors {
  background: #fff3e0;
  color: #f57c00;
}

.status-badge.error {
  background: #ffebee;
  color: #c62828;
}

.status-details {
  flex: 1;
}

.status-details p {
  margin: 4px 0;
  font-size: 14px;
}

/* 데이터베이스 테이블 정보 */
.tables-info h4 {
  margin: 16px 0 8px 0;
  color: #333;
  font-size: 16px;
}

.table-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.table-name {
  font-weight: 500;
  color: #333;
  min-width: 150px;
}

.table-status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 12px;
}

.table-status.accessible {
  background: #e8f5e8;
  color: #2e7d32;
}

.table-status.error {
  background: #ffebee;
  color: #c62828;
}

.table-count {
  color: #666;
  font-size: 14px;
}

.table-error {
  color: #c62828;
  font-size: 12px;
  font-style: italic;
}

.db-error {
  color: #c62828;
  font-size: 14px;
}

/* 테스트 결과 */
.test-results {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-results h3 {
  margin-bottom: 16px;
  color: #333;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.result-item {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s ease;
}

.result-item.success {
  border-color: #43a047;
  background: #f8fff8;
}

.result-item.failed {
  border-color: #e53935;
  background: #fff8f8;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.result-name {
  font-weight: 600;
  color: #333;
}

.result-method {
  padding: 4px 8px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.result-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.result-status.success {
  background: #e8f5e8;
  color: #2e7d32;
}

.result-status.failed {
  background: #ffebee;
  color: #c62828;
}

.result-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.response-time {
  color: #666;
  font-size: 12px;
}

.status-code {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-code.success {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-code.client-error {
  background: #fff3e0;
  color: #f57c00;
}

.status-code.server-error {
  background: #ffebee;
  color: #c62828;
}

.status-code.unknown {
  background: #f5f5f5;
  color: #666;
}

.result-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-url {
  font-size: 14px;
  color: #666;
  word-break: break-all;
}

.result-error {
  color: #c62828;
  font-size: 14px;
}

.result-preview {
  font-size: 14px;
}

.response-data {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  margin-top: 8px;
  max-height: 200px;
  overflow-y: auto;
}

/* 로딩 오버레이 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top: 4px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 반응형 */
@media (max-width: 768px) {
  .api-test {
    padding: 16px;
  }
  
  .control-panel {
    flex-direction: column;
    align-items: stretch;
  }
  
  .control-buttons {
    justify-content: center;
  }
  
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .status-info, .db-info {
    flex-direction: column;
  }
  
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .result-info {
    flex-wrap: wrap;
  }
}
</style> 