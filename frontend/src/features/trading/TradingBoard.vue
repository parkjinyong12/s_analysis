<template>
  <div class="trading-board">
    <!-- 헤더 -->
    <div class="board-header">
      <h2>📈 주식 거래 데이터</h2>
      <p class="description">기관/외국인 투자자별 주식 거래 현황을 조회합니다</p>
    </div>

    <!-- 검색 및 필터 -->
    <div class="search-section">
      <div class="search-row">
        <div class="search-group">
          <label>주식 코드/이름:</label>
          <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="주식 코드 또는 이름 입력"
            @keyup.enter="searchTradingData"
            class="form-input"
          >
        </div>
        
        <div class="search-group">
          <label>시작 날짜:</label>
          <input 
            type="date" 
            v-model="startDate" 
            class="form-input"
          >
        </div>
        
        <div class="search-group">
          <label>종료 날짜:</label>
          <input 
            type="date" 
            v-model="endDate" 
            class="form-input"
          >
        </div>
        
        <div class="search-actions">
          <button @click="searchTradingData" class="btn btn-primary" :disabled="isLoading">
            🔍 검색
          </button>
          <button @click="resetSearch" class="btn btn-secondary">
            🔄 초기화
          </button>
        </div>
      </div>
      
              <!-- 데이터 관리 버튼 -->
        <div class="management-actions" v-if="!isLoading && tradingData.length > 0">
          <div class="action-group">
            <button @click="clearCurrentStockData" class="btn btn-danger-sm" :disabled="!searchQuery.trim()">
              🗑️ 현재 종목 데이터 삭제
            </button>
            <span v-if="!searchQuery.trim()" class="help-text">종목을 검색한 후 삭제할 수 있습니다</span>
          </div>
          
          <div class="action-group">
            <button @click="calculateAccumulatedData" class="btn btn-info-sm" :disabled="isLoading">
              📊 누적 데이터 계산
            </button>
            <span class="help-text">기관/외국인 누적 매수량을 과거부터 순차 계산</span>
          </div>
          
          <div class="action-group" v-if="searchQuery.trim()">
            <button @click="calculateCurrentStockAccumulated" class="btn btn-success-sm" :disabled="!searchQuery.trim() || isLoading">
              📈 현재 종목만 누적 계산
            </button>
            <span class="help-text">검색된 종목의 누적 데이터만 계산</span>
          </div>
        </div>
    </div>

    <!-- 통계 정보 -->
    <div class="stats-section" v-if="tradingData.length > 0">
      <div class="stat-card">
        <div class="stat-value">{{ tradingData.length }}</div>
        <div class="stat-label">총 거래 건수</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ uniqueStocks }}</div>
        <div class="stat-label">종목 수</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ earliestDate }}</div>
        <div class="stat-label">최초 데이터</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ latestDate }}</div>
        <div class="stat-label">최신 데이터</div>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>데이터를 불러오는 중...</p>
    </div>

    <!-- 에러 메시지 -->
    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>

    <!-- 데이터 테이블 -->
    <div v-if="!isLoading && tradingData.length > 0" class="table-section">
      <div class="table-controls">
        <div class="entries-info">
          총 {{ tradingData.length }}건의 데이터
        </div>
        <div class="sort-controls">
          <label>정렬:</label>
          <select v-model="sortBy" @change="sortData" class="form-select">
            <option value="trade_date">날짜순</option>
            <option value="stock_code">종목코드순</option>
            <option value="close_price">종가순</option>
            <option value="institution_net_buy">기관 순매수순</option>
            <option value="foreigner_net_buy">외국인 순매수순</option>
            <option value="institution_accum">기관 누적순</option>
            <option value="foreigner_accum">외국인 누적순</option>
          </select>
          <select v-model="sortOrder" @change="sortData" class="form-select">
            <option value="desc">내림차순</option>
            <option value="asc">오름차순</option>
          </select>
        </div>
      </div>

      <div class="table-container">
        <table class="trading-table">
          <thead>
            <tr>
              <th>날짜</th>
              <th>종목코드</th>
              <th>종목명</th>
              <th class="number">종가</th>
              <th class="number">기관 순매수</th>
              <th class="number">외국인 순매수</th>
              <th class="number">기관 누적</th>
              <th class="number">외국인 누적</th>
              <th>기관신호</th>
              <th>외국인신호</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in sortedTradingData" :key="item.id" class="table-row">
              <td class="date">{{ formatDate(item.trade_date) }}</td>
              <td class="stock-code">{{ item.stock_code }}</td>
              <td class="stock-name">{{ item.stock_name }}</td>
              <td class="number price">{{ formatNumber(item.close_price) }}원</td>
              <!-- 기관 순매수: institution_net_buy -->
              <td class="number" :class="getNetBuyClass(item.institution_net_buy)">
                {{ formatNumber(item.institution_net_buy) }}
              </td>
              <!-- 외국인 순매수: foreigner_net_buy -->
              <td class="number" :class="getNetBuyClass(item.foreigner_net_buy)">
                {{ formatNumber(item.foreigner_net_buy) }}
              </td>
              <!-- 기관 누적: institution_accum -->
              <td class="number" :class="getAccumClass(item.institution_accum)">
                {{ formatNumber(item.institution_accum) }}
              </td>
              <!-- 외국인 누적: foreigner_accum -->
              <td class="number" :class="getAccumClass(item.foreigner_accum)">
                {{ formatNumber(item.foreigner_accum) }}
              </td>
              <td class="signal">
                <span v-if="item.institution_trend_signal" class="signal-badge">
                  {{ item.institution_trend_signal }}
                </span>
              </td>
              <td class="signal">
                <span v-if="item.foreigner_trend_signal" class="signal-badge">
                  {{ item.foreigner_trend_signal }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 빈 상태 -->
    <div v-if="!isLoading && tradingData.length === 0 && !errorMessage" class="empty-state">
      <div class="empty-icon">📊</div>
      <h3>거래 데이터가 없습니다</h3>
      <p>검색 조건을 변경하거나 데이터 수집을 먼저 진행해주세요.</p>
    </div>
  </div>
</template>

<script>
import { api, API_ENDPOINTS } from '../../config/api.js'

export default {
  name: 'TradingBoard',
  data() {
    return {
      tradingData: [],
      searchQuery: '',
      startDate: '',
      endDate: '',
      isLoading: false,
      errorMessage: '',
      sortBy: 'trade_date',
      sortOrder: 'desc'
    }
  },
  computed: {
    sortedTradingData() {
      const sorted = [...this.tradingData].sort((a, b) => {
        let aVal = a[this.sortBy]
        let bVal = b[this.sortBy]
        
        // 날짜나 숫자 필드 처리
        if (this.sortBy === 'trade_date') {
          aVal = new Date(aVal)
          bVal = new Date(bVal)
        } else if (typeof aVal === 'string' && !isNaN(aVal)) {
          aVal = parseFloat(aVal) || 0
          bVal = parseFloat(bVal) || 0
        }
        
        if (this.sortOrder === 'desc') {
          return bVal > aVal ? 1 : -1
        } else {
          return aVal > bVal ? 1 : -1
        }
      })
      return sorted
    },
    uniqueStocks() {
      return new Set(this.tradingData.map(item => item.stock_code)).size
    },
    earliestDate() {
      if (this.tradingData.length === 0) return '-'
      const dates = this.tradingData.map(item => item.trade_date)
      const earliestDateObj = new Date(Math.min(...dates.map(date => new Date(date))))
      return earliestDateObj.toISOString().split('T')[0]
    },
    latestDate() {
      if (this.tradingData.length === 0) return '-'
      const dates = this.tradingData.map(item => item.trade_date)
      const latestDateObj = new Date(Math.max(...dates.map(date => new Date(date))))
      return latestDateObj.toISOString().split('T')[0]
    }
  },
  mounted() {
    this.loadTradingData()
    this.setDefaultDates()
  },
  methods: {
    async loadTradingData() {
      this.isLoading = true
      this.errorMessage = ''
      
      try {
        const response = await api.get(API_ENDPOINTS.TRADING.LIST)
        this.tradingData = response.data || []
      } catch (error) {
        console.error('거래 데이터 로딩 실패:', error)
        this.errorMessage = '거래 데이터를 불러오는데 실패했습니다.'
        this.tradingData = []
      } finally {
        this.isLoading = false
      }
    },
    
    async searchTradingData() {
      this.isLoading = true
      this.errorMessage = ''
      
      try {
        let url = API_ENDPOINTS.TRADING.LIST
        let params = new URLSearchParams()
        
        // 검색어와 날짜 범위를 조합해서 처리
        const hasSearchQuery = this.searchQuery.trim()
        const hasDateRange = this.startDate && this.endDate
        
        if (hasSearchQuery && hasDateRange) {
          // 검색어가 숫자로만 구성되어 있으면 stock_code로 가정
          const searchTerm = this.searchQuery.trim()
          if (/^\d+$/.test(searchTerm)) {
            // 검색어 + 날짜 범위: date-range API에 stock_code 추가 검색
            url = API_ENDPOINTS.TRADING.DATE_RANGE
            params.append('start_date', this.startDate)
            params.append('end_date', this.endDate)
            params.append('stock_code', searchTerm)
          } else {
            // 주식명인 경우 검색 API를 사용하고 클라이언트에서 날짜 필터링
            url = API_ENDPOINTS.TRADING.SEARCH
            params = new URLSearchParams() // clear() 대신 새 객체 생성
            params.append('query', searchTerm)
          }
        } else if (hasSearchQuery) {
          // 검색어만: 검색 API 사용
          url = API_ENDPOINTS.TRADING.SEARCH
          params.append('query', this.searchQuery.trim())
        } else if (hasDateRange) {
          // 날짜 범위만: date-range API 사용
          url = API_ENDPOINTS.TRADING.DATE_RANGE
          params.append('start_date', this.startDate)
          params.append('end_date', this.endDate)
        }
        
        const queryString = params.toString()
        const finalUrl = queryString ? `${url}?${queryString}` : url
        
        const response = await api.get(finalUrl)
        let data = response.data || []
        
        // 주식명 검색 + 날짜 범위인 경우 클라이언트에서 날짜 필터링
        if (hasSearchQuery && hasDateRange && !(/^\d+$/.test(this.searchQuery.trim()))) {
          data = data.filter(item => {
            const tradeDate = new Date(item.trade_date)
            const start = new Date(this.startDate)
            const end = new Date(this.endDate)
            return tradeDate >= start && tradeDate <= end
          })
        }
        
        this.tradingData = data
      } catch (error) {
        console.error('거래 데이터 검색 실패:', error)
        this.errorMessage = '거래 데이터 검색에 실패했습니다.'
        this.tradingData = []
      } finally {
        this.isLoading = false
      }
    },
    
    resetSearch() {
      this.searchQuery = ''
      this.startDate = ''
      this.endDate = ''
      this.sortBy = 'trade_date'
      this.sortOrder = 'desc'
      this.loadTradingData()
    },
    
    setDefaultDates() {
      const today = new Date()
      const oneMonthAgo = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate())
      
      this.endDate = today.toISOString().split('T')[0]
      this.startDate = oneMonthAgo.toISOString().split('T')[0]
    },
    
    sortData() {
      // computed에서 자동으로 처리됨
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      return new Date(dateString).toLocaleDateString('ko-KR')
    },
    
    formatNumber(value) {
      if (value === null || value === undefined) return '-'
      const num = parseFloat(value)
      if (isNaN(num)) return '-'
      return num.toLocaleString('ko-KR')
    },
    
    getNetBuyClass(value) {
      const num = parseFloat(value)
      if (isNaN(num) || num === 0) return ''
      return num > 0 ? 'positive' : 'negative'
    },
    
    getAccumClass(value) {
      const num = parseFloat(value)
      if (isNaN(num) || num === 0) return ''
      return num > 0 ? 'positive' : 'negative'
    },

    // 현재 검색된 종목의 데이터 삭제
    async clearCurrentStockData() {
      if (!this.searchQuery.trim()) {
        alert('삭제할 종목을 먼저 검색해주세요.')
        return
      }

      const stockName = this.searchQuery.trim()
      
      if (!confirm(`⚠️ "${stockName}" 종목의 모든 거래 데이터를 삭제하시겠습니까?\n\n이 작업은 되돌릴 수 없습니다.`)) {
        return
      }

      this.isLoading = true
      try {
        // 검색 결과에서 주식 코드 추출 (첫 번째 데이터 기준)
        let stockCode = stockName
        if (this.tradingData.length > 0) {
          stockCode = this.tradingData[0].stock_code
        }

        const response = await api.delete(`${API_ENDPOINTS.COLLECTOR.CLEAR_TRADING_BY_STOCK}/${stockCode}`)
        alert(`✅ ${response.data.message}`)
        
        // 데이터 다시 로드
        await this.loadTradingData()
        
      } catch (error) {
        console.error('종목 데이터 삭제 실패:', error)
        const message = error.response?.data?.error || '종목 데이터 삭제에 실패했습니다.'
        alert(`❌ 삭제 실패: ${message}`)
      } finally {
        this.isLoading = false
      }
    },

    // 전체 누적 데이터 계산
    async calculateAccumulatedData() {
      if (!confirm('⏱️ 모든 주식의 누적 매수량을 계산하시겠습니까?\n\n과거 데이터부터 최신까지 순차적으로 계산하므로 시간이 걸릴 수 있습니다.')) {
        return
      }

      this.isLoading = true
      try {
        const response = await api.post(API_ENDPOINTS.COLLECTOR.CALCULATE_ACCUMULATED)
        alert(`✅ ${response.data.message}`)
        
        // 데이터 다시 로드하여 누적 값 반영
        await this.loadTradingData()
        
      } catch (error) {
        console.error('누적 데이터 계산 실패:', error)
        const message = error.response?.data?.error || '누적 데이터 계산에 실패했습니다.'
        alert(`❌ 계산 실패: ${message}`)
      } finally {
        this.isLoading = false
      }
    },

    // 현재 검색된 종목의 누적 데이터 계산
    async calculateCurrentStockAccumulated() {
      if (!this.searchQuery.trim()) {
        alert('계산할 종목을 먼저 검색해주세요.')
        return
      }

      const stockName = this.searchQuery.trim()
      let stockCode = stockName
      
      // 검색 결과에서 주식 코드 추출
      if (this.tradingData.length > 0) {
        stockCode = this.tradingData[0].stock_code
      }
      
      if (!confirm(`📈 "${stockName}" (${stockCode}) 종목의 누적 매수량을 계산하시겠습니까?\n\n과거 데이터부터 최신까지 순차적으로 누적 계산합니다.`)) {
        return
      }

      this.isLoading = true
      try {
        // 개별 종목 누적 계산
        await api.post(`${API_ENDPOINTS.COLLECTOR.CALCULATE_ACCUMULATED}/${stockCode}`)
        alert(`✅ ${stockName} 종목의 누적 데이터 계산이 완료되었습니다.`)
        
        // 데이터 다시 로드하여 누적 값 반영
        await this.searchTradingData()
        
      } catch (error) {
        console.error('종목별 누적 데이터 계산 실패:', error)
        const message = error.response?.data?.error || '종목별 누적 데이터 계산에 실패했습니다.'
        alert(`❌ 계산 실패: ${message}`)
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.trading-board {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.board-header {
  margin-bottom: 30px;
  text-align: center;
}

.board-header h2 {
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 28px;
}

.description {
  color: #7f8c8d;
  font-size: 16px;
}

/* 검색 섹션 */
.search-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.search-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: end;
}

.search-group {
  display: flex;
  flex-direction: column;
  min-width: 150px;
}

.search-group label {
  font-weight: 600;
  margin-bottom: 5px;
  color: #34495e;
  font-size: 14px;
}

.form-input, .form-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-input:focus, .form-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.search-actions {
  display: flex;
  gap: 10px;
}

/* 통계 섹션 */
.stats-section {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.stat-label {
  color: #7f8c8d;
  font-size: 14px;
}

/* 테이블 섹션 */
.table-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.table-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.entries-info {
  font-weight: 600;
  color: #495057;
}

.sort-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sort-controls label {
  font-weight: 600;
  color: #495057;
}

.table-container {
  overflow-x: auto;
}

.trading-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.trading-table th {
  background: #f8f9fa;
  padding: 12px 8px;
  text-align: left;
  font-weight: 600;
  color: #495057;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.trading-table th.number {
  text-align: right;
}

.trading-table td {
  padding: 10px 8px;
  border-bottom: 1px solid #dee2e6;
}

.trading-table .table-row:hover {
  background: #f8f9fa;
}

.trading-table .number {
  text-align: right;
  font-family: 'Courier New', monospace;
}

.trading-table .date {
  font-weight: 500;
  color: #495057;
}

.trading-table .stock-code {
  font-weight: 600;
  color: #2c3e50;
}

.trading-table .stock-name {
  color: #495057;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.trading-table .price {
  font-weight: 600;
  color: #2c3e50;
}

.trading-table .positive {
  color: #e74c3c;
  font-weight: 600;
}

.trading-table .negative {
  color: #3498db;
  font-weight: 600;
}

.signal-badge {
  background: #e9ecef;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 12px;
  color: #495057;
}

/* 버튼 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

/* 상태 */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin-bottom: 10px;
  color: #2c3e50;
}

/* 데이터 관리 버튼 */
.management-actions {
  margin-top: 15px;
  padding: 15px;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-danger-sm {
  background: #dc3545;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-danger-sm:hover:not(:disabled) {
  background: #c82333;
}

.btn-danger-sm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-info-sm {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-info-sm:hover:not(:disabled) {
  background: #138496;
}

.btn-info-sm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-success-sm {
  background: #28a745;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-success-sm:hover:not(:disabled) {
  background: #218838;
}

.btn-success-sm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.help-text {
  font-size: 12px;
  color: #856404;
  font-style: italic;
}

/* 반응형 */
@media (max-width: 768px) {
  .search-row {
    flex-direction: column;
  }
  
  .search-group {
    min-width: 100%;
  }
  
  .stats-section {
    flex-direction: column;
  }
  
  .table-controls {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .sort-controls {
    justify-content: center;
  }
  
  .management-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-group {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
    gap: 5px;
  }
}
</style> 