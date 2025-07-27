<template>
  <div class="stock-board">
    <div class="board-header">
      <h2>📈 주식 목록 관리</h2>
      <div class="header-actions">
        <button @click="showExcelUploadModal = true" class="btn btn-success">
          📊 엑셀 업로드
        </button>
        <button @click="showCreateModal = true" class="btn btn-primary">
          ➕ 새 주식 등록
        </button>
      </div>
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
            <th>상장일자</th>
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
            <label>상장일자</label>
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

    <!-- 엑셀 업로드 모달 -->
    <div v-if="showExcelUploadModal" class="modal-overlay" @click="closeModal">
      <div class="modal excel-upload-modal" @click.stop>
        <div class="modal-header">
          <h3>📊 엑셀/CSV 파일 업로드</h3>
          <button @click="closeModal" class="modal-close">✕</button>
        </div>
        
        <div class="modal-content">
          <div class="upload-section">
            <div class="file-upload-area" 
                 @click="triggerFileInput"
                 @dragover.prevent
                 @drop.prevent="handleFileDrop"
                 :class="{ 'dragover': isDragOver }">
              <input 
                ref="fileInput"
                type="file" 
                accept=".xlsx,.xls,.csv"
                @change="handleFileSelect"
                style="display: none;"
              />
              <div class="upload-icon">📁</div>
              <p>클릭하거나 파일을 드래그하여 엑셀/CSV 파일을 선택하세요</p>
              <p class="file-info">지원 형식: .xlsx, .xls, .csv</p>
            </div>
            
            <div v-if="selectedFile" class="selected-file">
              <p>선택된 파일: <strong>{{ selectedFile.name }}</strong></p>
              <button @click="removeFile" class="btn btn-sm btn-secondary">파일 제거</button>
            </div>
          </div>

          <div class="excel-format-info">
            <h4>📋 파일 형식</h4>
            <div class="format-table">
              <table>
                <thead>
                  <tr>
                    <th>컬럼명</th>
                    <th>설명</th>
                    <th>필수/선택</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><code>단축코드</code></td>
                    <td>6자리 주식 코드</td>
                    <td><span class="required">필수</span></td>
                  </tr>
                  <tr>
                    <td><code>한글 종목명</code></td>
                    <td>주식명</td>
                    <td><span class="required">필수</span></td>
                  </tr>
                  <tr>
                    <td><code>상장일</code></td>
                    <td>상장 날짜 (YYYY.MM.DD)</td>
                    <td><span class="optional">선택</span></td>
                  </tr>
                  <tr>
                    <td><code>시장구분</code></td>
                    <td>KOSPI/KOSDAQ</td>
                    <td><span class="optional">선택</span></td>
                  </tr>
                  <tr>
                    <td><code>액면가</code></td>
                    <td>액면가</td>
                    <td><span class="optional">선택</span></td>
                  </tr>
                  <tr>
                    <td><code>상장주식수</code></td>
                    <td>상장 주식 수</td>
                    <td><span class="optional">선택</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="uploadResult" class="upload-result">
            <h4>📊 업로드 결과</h4>
            <div class="result-summary">
              <div class="result-item">
                <span class="label">총 행 수:</span>
                <span class="value">{{ uploadResult.total_rows }}</span>
              </div>
              <div class="result-item">
                <span class="label">성공:</span>
                <span class="value success">{{ uploadResult.success_count }}</span>
              </div>
              <div class="result-item">
                <span class="label">업데이트:</span>
                <span class="value update">{{ uploadResult.update_count }}</span>
              </div>
              <div class="result-item">
                <span class="label">생성:</span>
                <span class="value create">{{ uploadResult.create_count }}</span>
              </div>
              <div class="result-item">
                <span class="label">실패:</span>
                <span class="value error">{{ uploadResult.failed_count }}</span>
              </div>
            </div>
            
            <div v-if="uploadResult.failed_list && uploadResult.failed_list.length > 0" class="failed-list">
              <h5>❌ 실패한 항목</h5>
              <div class="failed-items">
                <div v-for="item in uploadResult.failed_list" :key="item.row" class="failed-item">
                  <span class="row">행 {{ item.row }}:</span>
                  <span class="code">{{ item.stock_code }}</span>
                  <span class="name">{{ item.stock_name }}</span>
                  <span class="error">{{ item.error }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="modal-actions">
          <button @click="closeModal" class="btn btn-secondary">닫기</button>
          <button 
            @click="uploadExcelFile" 
            :disabled="!selectedFile || uploading"
            class="btn btn-primary"
          >
            {{ uploading ? '업로드 중...' : '업로드' }}
          </button>
        </div>
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
      editingStockId: null,
      // 엑셀 업로드 관련
      showExcelUploadModal: false,
      selectedFile: null,
      uploading: false,
      uploadResult: null,
      isDragOver: false
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
      this.showExcelUploadModal = false
      this.editingStockId = null
      this.formData = {
        stock_code: '',
        stock_name: '',
        init_date: '',
        institution_accum_init: 0,
        foreigner_accum_init: 0
      }
      // 엑셀 업로드 관련 상태 초기화
      this.selectedFile = null
      this.uploadResult = null
      this.isDragOver = false
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
    },

    // 엑셀 업로드 관련 메서드들
    triggerFileInput() {
      this.$refs.fileInput.click()
    },

    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        this.selectedFile = file
      }
    },

    handleFileDrop(event) {
      this.isDragOver = false
      const files = event.dataTransfer.files
      if (files.length > 0) {
        const file = files[0]
        if (file.type.includes('spreadsheet') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv')) {
          this.selectedFile = file
        } else {
          alert('엑셀/CSV 파일(.xlsx, .xls, .csv)만 업로드 가능합니다.')
        }
      }
      event.preventDefault()
    },

    removeFile() {
      this.selectedFile = null
      this.uploadResult = null
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },

    async uploadExcelFile() {
      if (!this.selectedFile) {
        alert('업로드할 파일을 선택해주세요.')
        return
      }

      this.uploading = true
      this.uploadResult = null

      try {
        const formData = new FormData()
        formData.append('file', this.selectedFile)

        const response = await api.post('/stocks/upload-excel', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        this.uploadResult = response.data.results
        await this.loadStocks() // 주식 목록 새로고침
        
        alert(`엑셀 파일 업로드 완료!\n총 ${this.uploadResult.total_rows}행, 성공 ${this.uploadResult.success_count}개, 업데이트 ${this.uploadResult.update_count}개, 생성 ${this.uploadResult.create_count}개, 실패 ${this.uploadResult.failed_count}개`)
        
        // 실패가 없으면 팝업 자동 닫기
        if (this.uploadResult.failed_count === 0) {
          this.closeModal()
        }
        
      } catch (error) {
        console.error('엑셀 파일 업로드 실패:', error)
        alert('엑셀 파일 업로드에 실패했습니다.')
      } finally {
        this.uploading = false
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

.btn-success {
  background: #4caf50;
  color: white;
}

.btn-success:hover {
  background: #45a049;
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

.excel-upload-modal {
  width: 800px;
  max-width: 90vw;
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

/* 엑셀 업로드 모달 스타일 */
.modal-content {
  padding: 20px;
}

.upload-section {
  margin-bottom: 20px;
}

.file-upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
}

.file-upload-area:hover,
.file-upload-area.dragover {
  border-color: #1976d2;
  background: #f8f9ff;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.file-info {
  color: #666;
  font-size: 12px;
  margin-top: 5px;
}

.selected-file {
  margin-top: 15px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.excel-format-info {
  margin-bottom: 20px;
}

.excel-format-info h4 {
  color: #1976d2;
  margin-bottom: 10px;
}

.format-table {
  overflow-x: auto;
}

.format-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.format-table th,
.format-table td {
  padding: 8px;
  border: 1px solid #ddd;
  text-align: left;
}

.format-table th {
  background: #f5f5f5;
  font-weight: 600;
}

.required {
  color: #f44336;
  font-weight: 600;
}

.optional {
  color: #666;
}

.upload-result {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.upload-result h4 {
  color: #1976d2;
  margin-bottom: 10px;
}

.result-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
}

.result-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
}

.result-item .label {
  font-weight: 500;
}

.result-item .value {
  font-weight: 600;
}

.result-item .value.success {
  color: #4caf50;
}

.result-item .value.update {
  color: #2196f3;
}

.result-item .value.create {
  color: #ff9800;
}

.result-item .value.error {
  color: #f44336;
}

.failed-list {
  margin-top: 15px;
}

.failed-list h5 {
  color: #f44336;
  margin-bottom: 10px;
}

.failed-items {
  max-height: 200px;
  overflow-y: auto;
}

.failed-item {
  display: flex;
  gap: 10px;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
  font-size: 12px;
}

.failed-item .row {
  font-weight: 600;
  min-width: 50px;
}

.failed-item .code {
  font-family: monospace;
  min-width: 80px;
}

.failed-item .name {
  flex: 1;
}

.failed-item .error {
  color: #f44336;
  font-size: 11px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #eee;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style> 