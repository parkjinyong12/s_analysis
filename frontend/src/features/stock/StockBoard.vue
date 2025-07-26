<template>
  <div class="stock-board">
    <div class="board-header">
      <h2>📈 주식 목록 관리</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        ➕ 새 주식 등록
      </button>
    </div>

    <!-- 검색 바 -->
    <div class="search-bar">
      <input 
        v-model="searchName" 
        @input="searchStocks"
        placeholder="주식명으로 검색..." 
        class="search-input"
      />
      <input 
        v-model="searchCode" 
        @input="searchStocks"
        placeholder="주식 코드로 검색..." 
        class="search-input"
      />
      <button @click="loadStocks" class="btn btn-secondary">🔄 전체 조회</button>
    </div>

    <!-- 주식 목록 테이블 -->
    <div class="table-container">
      <table class="stock-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>주식 코드</th>
            <th>주식명</th>
            <th>초기화 날짜</th>
            <th>기관 누적 초기값</th>
            <th>외국인 누적 초기값</th>
            <th>액션</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="loading">로딩 중...</td>
          </tr>
          <tr v-else-if="stocks.length === 0">
            <td colspan="7" class="no-data">등록된 주식이 없습니다.</td>
          </tr>
          <tr v-else v-for="stock in stocks" :key="stock.id">
            <td>{{ stock.id }}</td>
            <td class="stock-code">{{ stock.stock_code }}</td>
            <td class="stock-name">{{ stock.stock_name }}</td>
            <td>{{ stock.init_date || '-' }}</td>
            <td class="number">{{ stock.institution_accum_init?.toLocaleString() || 0 }}</td>
            <td class="number">{{ stock.foreigner_accum_init?.toLocaleString() || 0 }}</td>
            <td class="actions">
              <button @click="editStock(stock)" class="btn btn-sm btn-edit">✏️</button>
              <button @click="deleteStock(stock)" class="btn btn-sm btn-delete">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 생성/수정 모달 -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h3>{{ showCreateModal ? '새 주식 등록' : '주식 정보 수정' }}</h3>
          <button @click="closeModal" class="modal-close">✕</button>
        </div>
        
        <form @submit.prevent="saveStock" class="modal-form">
          <div class="form-group">
            <label>주식 코드 *</label>
            <input 
              v-model="formData.stock_code" 
              :disabled="showEditModal"
              placeholder="예: 005930" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label>주식명 *</label>
            <input 
              v-model="formData.stock_name" 
              placeholder="예: 삼성전자" 
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label>초기화 날짜</label>
            <input 
              v-model="formData.init_date" 
              type="date" 
              class="form-input"
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>기관 누적 초기값</label>
              <input 
                v-model.number="formData.institution_accum_init" 
                type="number" 
                min="0"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label>외국인 누적 초기값</label>
              <input 
                v-model.number="formData.foreigner_accum_init" 
                type="number" 
                min="0"
                class="form-input"
              />
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn btn-secondary">취소</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? '저장 중...' : (showCreateModal ? '등록' : '수정') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '@/config/api'

export default {
  name: 'StockBoard',
  data() {
    return {
      stocks: [],
      loading: false,
      saving: false,
      showCreateModal: false,
      showEditModal: false,
      searchName: '',
      searchCode: '',
      searchTimeout: null,
      formData: {
        stock_code: '',
        stock_name: '',
        init_date: '',
        institution_accum_init: 0,
        foreigner_accum_init: 0
      },
      editingStockId: null
    }
  },
  
  async mounted() {
    await this.loadStocks()
  },
  
  methods: {
    // 주식 목록 조회
    async loadStocks() {
      this.loading = true
      try {
        const response = await api.get('/stocks/')
        this.stocks = response.data
      } catch (error) {
        console.error('주식 목록 조회 실패:', error)
        alert('주식 목록을 불러오는데 실패했습니다.')
      } finally {
        this.loading = false
      }
    },

    // 주식 검색
    searchStocks() {
      // 검색 디바운싱
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(async () => {
        if (!this.searchName.trim() && !this.searchCode.trim()) {
          await this.loadStocks()
          return
        }

        this.loading = true
        try {
          const params = new URLSearchParams()
          if (this.searchName.trim()) params.append('name', this.searchName.trim())
          if (this.searchCode.trim()) params.append('code', this.searchCode.trim())
          
          const response = await api.get(`/stocks/search?${params}`)
          this.stocks = response.data
        } catch (error) {
          console.error('주식 검색 실패:', error)
          alert('주식 검색에 실패했습니다.')
        } finally {
          this.loading = false
        }
      }, 300)
    },

    // 주식 수정 모달 열기
    editStock(stock) {
      this.editingStockId = stock.id
      this.formData = {
        stock_code: stock.stock_code,
        stock_name: stock.stock_name,
        init_date: stock.init_date || '',
        institution_accum_init: stock.institution_accum_init || 0,
        foreigner_accum_init: stock.foreigner_accum_init || 0
      }
      this.showEditModal = true
    },

    // 주식 삭제
    async deleteStock(stock) {
      if (!confirm(`정말로 "${stock.stock_name}" 주식을 삭제하시겠습니까?`)) {
        return
      }

      try {
        await api.delete(`/stocks/${stock.id}`)
        alert('주식이 삭제되었습니다.')
        await this.loadStocks()
      } catch (error) {
        console.error('주식 삭제 실패:', error)
        alert('주식 삭제에 실패했습니다.')
      }
    },

    // 주식 생성/수정
    async saveStock() {
      this.saving = true
      try {
        if (this.showCreateModal) {
          // 새 주식 생성
          await api.post('/stocks/', this.formData)
          alert('새 주식이 등록되었습니다.')
        } else {
          // 주식 수정
          await api.put(`/stocks/${this.editingStockId}`, this.formData)
          alert('주식 정보가 수정되었습니다.')
        }
        
        this.closeModal()
        await this.loadStocks()
      } catch (error) {
        console.error('주식 저장 실패:', error)
        const message = error.response?.data?.error || '주식 저장에 실패했습니다.'
        alert(message)
      } finally {
        this.saving = false
      }
    },

    // 모달 닫기
    closeModal() {
      this.showCreateModal = false
      this.showEditModal = false
      this.editingStockId = null
      this.formData = {
        stock_code: '',
        stock_name: '',
        init_date: '',
        institution_accum_init: 0,
        foreigner_accum_init: 0
      }
    },

    // 기본 주식 데이터 삽입
    async insertDefaultStocks() {
             if (!confirm('기본 주식 목록(삼성전자, SK하이닉스 등 10개)을 추가하시겠습니까?')) {
        return
      }

      this.loading = true
      try {
                 const response = await api.post('/collector/insert-default-stocks')
                 alert(response.data.message)
        await this.loadStocks()
             } catch (error) {
         console.error('기본 주식 추가 실패:', error)
         const message = error.response?.data?.error || '기본 주식 추가에 실패했습니다.'
         alert(message)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.stock-board {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e0e0e0;
}

.board-header h2 {
  color: #1976d2;
  margin: 0;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.table-container {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.stock-table {
  width: 100%;
  border-collapse: collapse;
}

.stock-table th {
  background: #f5f5f5;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #ddd;
}

.stock-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
}

.stock-table tr:hover {
  background: #f9f9f9;
}

.stock-code {
  font-family: 'Courier New', monospace;
  font-weight: bold;
  color: #1976d2;
}

.stock-name {
  font-weight: 500;
}

.number {
  text-align: right;
  font-family: 'Courier New', monospace;
}

.actions {
  text-align: center;
}

.loading, .no-data {
  text-align: center;
  padding: 40px;
  color: #666;
  font-style: italic;
}

/* 버튼 스타일 */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #1976d2;
  color: white;
}

.btn-primary:hover {
  background: #1565c0;
}

.btn-secondary {
  background: #666;
  color: white;
}

.btn-secondary:hover {
  background: #555;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
  margin: 0 2px;
}

.btn-edit {
  background: #4caf50;
  color: white;
}

.btn-edit:hover {
  background: #45a049;
}

.btn-delete {
  background: #f44336;
  color: white;
}

.btn-delete:hover {
  background: #da190b;
}

.btn-info {
  background: #2196f3;
  color: white;
}

.btn-info:hover {
  background: #1976d2;
}

/* 모달 스타일 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #1976d2;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.modal-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-row {
  display: flex;
  gap: 15px;
}

.form-row .form-group {
  flex: 1;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.form-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #1976d2;
  box-shadow: 0 0 0 2px rgba(25,118,210,0.2);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}
</style> 