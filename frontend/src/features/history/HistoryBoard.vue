<template>
  <div class="history-board">
    <!-- 헤더 -->
    <header class="history-header">
      <h2>거래 데이터 히스토리</h2>
      <p class="history-description">거래 데이터의 모든 변경 이력과 시스템 활동 로그를 확인합니다.</p>
    </header>

    <!-- 필터 패널 -->
    <section class="filter-panel">
      <div class="filter-controls">
        <div class="filter-group">
          <label>히스토리 타입</label>
          <select v-model="selectedType" @change="loadHistory">
            <option value="data">거래 데이터 히스토리</option>
            <option value="system">시스템 로그</option>
          </select>
        </div>
        
        <div class="filter-group" v-if="selectedType === 'data'">
          <label>작업 유형</label>
          <select v-model="selectedAction" @change="loadHistory">
            <option value="">전체</option>
            <option value="CREATE">생성</option>
            <option value="UPDATE">수정</option>
            <option value="DELETE">삭제</option>
          </select>
        </div>
        
        <div class="filter-group" v-if="selectedType === 'system'">
          <label>로그 레벨</label>
          <select v-model="selectedLevel" @change="loadHistory">
            <option value="">전체</option>
            <option value="INFO">정보</option>
            <option value="WARNING">경고</option>
            <option value="ERROR">오류</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>조회 개수</label>
          <select v-model="limit" @change="loadHistory">
            <option value="10">10개</option>
            <option value="25">25개</option>
            <option value="50">50개</option>
            <option value="100">100개</option>
          </select>
        </div>
      </div>
      
      <div class="filter-actions">
        <button @click="loadHistory" :disabled="isLoading" class="btn btn-primary">
          {{ isLoading ? '조회 중...' : '조회' }}
        </button>
        <button @click="loadStats" :disabled="isLoading" class="btn btn-secondary">
          통계 보기
        </button>
        <button @click="clearFilters" :disabled="isLoading" class="btn btn-outline">
          필터 초기화
        </button>
      </div>
    </section>

    <!-- 통계 요약 -->
    <section v-if="showStats" class="stats-summary">
      <h3>히스토리 통계</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_data_history || 0 }}</div>
          <div class="stat-label">전체 거래 데이터 히스토리</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.total_system_logs || 0 }}</div>
          <div class="stat-label">전체 시스템 로그</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.today_data_history || 0 }}</div>
          <div class="stat-label">오늘 거래 데이터 히스토리</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.today_system_logs || 0 }}</div>
          <div class="stat-label">오늘 시스템 로그</div>
        </div>
      </div>
      
      <div class="stats-details">
        <div class="action-stats" v-if="stats.action_stats">
          <h4>작업별 통계</h4>
          <div class="action-list">
            <div v-for="(count, action) in stats.action_stats" :key="action" class="action-item">
              <span class="action-name">{{ getActionName(action) }}</span>
              <span class="action-count">{{ count }}</span>
            </div>
          </div>
        </div>
        
        <div class="level-stats" v-if="stats.level_stats">
          <h4>로그 레벨별 통계</h4>
          <div class="level-list">
            <div v-for="(count, level) in stats.level_stats" :key="level" class="level-item">
              <span class="level-name">{{ getLevelName(level) }}</span>
              <span class="level-count">{{ count }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 히스토리 목록 -->
    <section class="history-list">
      <div class="list-header">
        <h3>{{ getListTitle() }}</h3>
        <div class="list-info">
          총 {{ historyList.length }}개 항목
        </div>
      </div>
      
      <div v-if="isLoading" class="loading">
        <div class="loading-spinner"></div>
        <p>히스토리를 불러오는 중...</p>
      </div>
      
      <div v-else-if="historyList.length === 0" class="empty-state">
        <p>조회된 히스토리가 없습니다.</p>
      </div>
      
      <div v-else class="history-items">
        <div 
          v-for="item in historyList" 
          :key="item.id" 
          class="history-item"
          :class="getItemClass(item)"
        >
          <div class="item-header">
            <div class="item-info">
              <span class="item-action" v-if="selectedType === 'data'">
                {{ getActionName(item.action) }}
              </span>
              <span class="item-level" v-if="selectedType === 'system'">
                {{ getLevelName(item.level) }}
              </span>
              <span class="item-time">{{ formatDate(item.created_at) }}</span>
            </div>
            <div class="item-meta">
              <span class="item-id">#{{ item.id }}</span>
            </div>
          </div>
          
          <div class="item-content">
            <div class="item-description" v-if="selectedType === 'data'">
              <strong>{{ item.table_name }}</strong>
              <span v-if="item.record_id"> (ID: {{ item.record_id }})</span>
              <span v-if="item.description"> - {{ item.description }}</span>
            </div>
            <div class="item-message" v-if="selectedType === 'system'">
              <strong>{{ item.category }}</strong> - {{ item.message }}
            </div>
          </div>
          
          <div class="item-details" v-if="showDetails">
            <div class="detail-row" v-if="item.field_name">
              <span class="detail-label">필드:</span>
              <span class="detail-value">{{ item.field_name }}</span>
            </div>
            <div class="detail-row" v-if="item.old_value">
              <span class="detail-label">이전 값:</span>
              <span class="detail-value old-value">{{ item.old_value }}</span>
            </div>
            <div class="detail-row" v-if="item.new_value">
              <span class="detail-label">새 값:</span>
              <span class="detail-value new-value">{{ item.new_value }}</span>
            </div>
            <div class="detail-row" v-if="item.ip_address">
              <span class="detail-label">IP:</span>
              <span class="detail-value">{{ item.ip_address }}</span>
            </div>
            <div class="detail-row" v-if="item.details">
              <span class="detail-label">상세:</span>
              <span class="detail-value">{{ item.details }}</span>
            </div>
          </div>
          
          <div class="item-actions">
            <button 
              @click="toggleDetails(item.id)" 
              class="btn-details"
            >
              {{ getDetailsButtonText(item.id) }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- 에러 메시지 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
  </div>
</template>

<script>
import { api, API_ENDPOINTS } from '@/config/api';

export default {
  name: 'HistoryBoard',
  
  data() {
    return {
      // 필터 설정
      selectedType: 'data',
      selectedAction: '',
      selectedLevel: '',
      limit: 25,
      
      // 데이터
      historyList: [],
      stats: {},
      showStats: false,
      
      // 상태
      isLoading: false,
      errorMessage: '',
      expandedItems: new Set(),
      
      // 상세 정보 표시 여부
      showDetails: false
    };
  },
  
  mounted() {
    this.loadHistory();
  },
  
  methods: {
    /**
     * 히스토리 데이터 로드
     */
    async loadHistory() {
      try {
        this.isLoading = true;
        this.clearError();
        
        let endpoint = '';
        let params = { limit: this.limit };
        
        if (this.selectedType === 'data') {
          endpoint = API_ENDPOINTS.HISTORY.DATA;
          if (this.selectedAction) {
            params.action = this.selectedAction;
          }
        } else {
          endpoint = API_ENDPOINTS.HISTORY.SYSTEM;
          if (this.selectedLevel) {
            params.level = this.selectedLevel;
          }
        }
        
        const response = await api.get(endpoint, { params });
        this.historyList = response.data;
        
      } catch (error) {
        console.error('히스토리 로드 실패:', error);
        this.showError('히스토리를 불러오는데 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 통계 데이터 로드
     */
    async loadStats() {
      try {
        this.isLoading = true;
        this.clearError();
        
        const response = await api.get(API_ENDPOINTS.HISTORY.STATS);
        this.stats = response.data;
        this.showStats = true;
        
      } catch (error) {
        console.error('통계 로드 실패:', error);
        this.showError('통계를 불러오는데 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 필터 초기화
     */
    clearFilters() {
      this.selectedAction = '';
      this.selectedLevel = '';
      this.limit = 25;
      this.showStats = false;
      this.expandedItems.clear();
      this.loadHistory();
    },
    
    /**
     * 상세 정보 토글
     */
    toggleDetails(itemId) {
      if (this.expandedItems.has(itemId)) {
        this.expandedItems.delete(itemId);
      } else {
        this.expandedItems.add(itemId);
      }
    },
    
    /**
     * 상세 정보 버튼 텍스트
     */
    getDetailsButtonText(itemId) {
      return this.expandedItems.has(itemId) ? '접기' : '상세보기';
    },
    
    /**
     * 아이템 CSS 클래스
     */
    getItemClass(item) {
      const classes = [];
      
      if (this.expandedItems.has(item.id)) {
        classes.push('expanded');
      }
      
      if (this.selectedType === 'data') {
        classes.push(`action-${item.action.toLowerCase()}`);
      } else {
        classes.push(`level-${item.level.toLowerCase()}`);
      }
      
      return classes.join(' ');
    },
    
    /**
     * 리스트 제목
     */
    getListTitle() {
      if (this.selectedType === 'data') {
        return '거래 데이터 변경 히스토리';
      } else {
        return '시스템 로그';
      }
    },
    
    /**
     * 작업 이름 변환
     */
    getActionName(action) {
      const actionNames = {
        'CREATE': '생성',
        'UPDATE': '수정',
        'DELETE': '삭제',
        'READ': '조회'
      };
      return actionNames[action] || action;
    },
    
    /**
     * 로그 레벨 이름 변환
     */
    getLevelName(level) {
      const levelNames = {
        'INFO': '정보',
        'WARNING': '경고',
        'ERROR': '오류'
      };
      return levelNames[level] || level;
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
    }
  }
};
</script>

<style scoped>
/* 메인 컨테이너 */
.history-board {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

/* 헤더 */
.history-header {
  margin-bottom: 32px;
  text-align: center;
}

.history-header h2 {
  color: #1976d2;
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 600;
}

.history-description {
  color: #666;
  font-size: 16px;
  margin: 0;
}

/* 필터 패널 */
.filter-panel {
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

.filter-controls {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.filter-group select {
  padding: 8px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
  min-width: 120px;
}

.filter-group select:focus {
  outline: none;
  border-color: #1976d2;
}

.filter-actions {
  display: flex;
  gap: 12px;
}

/* 버튼 스타일 */
.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
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
}

.btn-secondary {
  background: #43a047;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #388e3c;
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

/* 통계 요약 */
.stats-summary {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stats-summary h3 {
  margin-bottom: 16px;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
  border: 2px solid #e0e0e0;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #1976d2;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.stats-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.action-stats h4, .level-stats h4 {
  margin-bottom: 12px;
  color: #333;
  font-size: 16px;
}

.action-list, .level-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-item, .level-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.action-name, .level-name {
  font-weight: 500;
  color: #333;
}

.action-count, .level-count {
  font-weight: bold;
  color: #1976d2;
}

/* 히스토리 목록 */
.history-list {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.list-header {
  padding: 20px 24px;
  border-bottom: 2px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.list-info {
  color: #666;
  font-size: 14px;
}

/* 로딩 상태 */
.loading {
  padding: 60px 24px;
  text-align: center;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e0e0e0;
  border-top: 4px solid #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 빈 상태 */
.empty-state {
  padding: 60px 24px;
  text-align: center;
  color: #666;
}

/* 히스토리 아이템 */
.history-items {
  max-height: 600px;
  overflow-y: auto;
}

.history-item {
  border-bottom: 1px solid #f0f0f0;
  padding: 16px 24px;
  transition: all 0.2s ease;
}

.history-item:hover {
  background: #f8f9fa;
}

.history-item.expanded {
  background: #f8f9fa;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-action, .item-level {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.item-action {
  background: #e3f2fd;
  color: #1976d2;
}

.action-create .item-action {
  background: #e8f5e8;
  color: #2e7d32;
}

.action-update .item-action {
  background: #fff3e0;
  color: #f57c00;
}

.action-delete .item-action {
  background: #ffebee;
  color: #c62828;
}

.item-level {
  background: #f3e5f5;
  color: #7b1fa2;
}

.level-info .item-level {
  background: #e3f2fd;
  color: #1976d2;
}

.level-warning .item-level {
  background: #fff3e0;
  color: #f57c00;
}

.level-error .item-level {
  background: #ffebee;
  color: #c62828;
}

.item-time {
  color: #666;
  font-size: 14px;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.item-id {
  color: #999;
  font-size: 12px;
  font-family: monospace;
}

.item-content {
  margin-bottom: 12px;
}

.item-description, .item-message {
  font-size: 14px;
  line-height: 1.4;
}

.item-details {
  background: #f8f9fa;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-row {
  display: flex;
  gap: 8px;
}

.detail-label {
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.detail-value {
  color: #666;
  word-break: break-all;
}

.old-value {
  color: #c62828;
  text-decoration: line-through;
}

.new-value {
  color: #2e7d32;
  font-weight: 600;
}

.item-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-details {
  background: none;
  border: none;
  color: #1976d2;
  font-size: 14px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.btn-details:hover {
  background: #e3f2fd;
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

/* 반응형 */
@media (max-width: 768px) {
  .history-board {
    padding: 16px;
  }
  
  .filter-panel {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-controls {
    justify-content: center;
  }
  
  .filter-actions {
    justify-content: center;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stats-details {
    grid-template-columns: 1fr;
  }
  
  .item-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .item-info {
    flex-wrap: wrap;
  }
}
</style> 