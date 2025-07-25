<template>
  <div class="sample-board">
    <!-- 헤더 -->
    <header class="board-header">
      <h2>Sample 게시판</h2>
      <p class="board-description">샘플 데이터를 관리할 수 있는 CRUD 게시판입니다.</p>
    </header>

    <!-- 입력 폼 -->
    <section class="form-section">
      <form class="sample-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <input 
            v-model="form.name" 
            placeholder="이름" 
            required 
            :disabled="isLoading"
            class="form-input"
          />
          <input 
            v-model="form.description" 
            placeholder="설명" 
            :disabled="isLoading"
            class="form-input"
          />
        </div>
        <div class="form-actions">
          <button 
            type="submit" 
            :disabled="isLoading || !form.name.trim()"
            class="btn btn-primary"
          >
            {{ isLoading ? '처리중...' : (form.id ? '수정' : '추가') }}
          </button>
          <button 
            v-if="form.id" 
            type="button" 
            @click="resetForm"
            :disabled="isLoading"
            class="btn btn-secondary"
          >
            취소
          </button>
        </div>
      </form>
    </section>

    <!-- 에러 메시지 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- 데이터 테이블 -->
    <section class="table-section">
      <!-- 로딩 상태 -->
      <div v-if="isLoading && samples.length === 0" class="loading-state">
        데이터를 불러오는 중...
      </div>

      <!-- 빈 상태 -->
      <div v-else-if="samples.length === 0" class="empty-state">
        <p>등록된 샘플이 없습니다.</p>
        <p class="empty-hint">위 폼을 사용해서 첫 번째 샘플을 추가해보세요!</p>
      </div>

      <!-- 데이터 테이블 -->
      <table v-else class="sample-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>이름</th>
            <th>설명</th>
            <th>생성일</th>
            <th>액션</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sample in samples" :key="sample.id" class="table-row">
            <td>{{ sample.id }}</td>
            <td class="name-cell">{{ sample.name }}</td>
            <td class="description-cell">{{ sample.description || '-' }}</td>
            <td class="date-cell">{{ formatDate(sample.created_at) }}</td>
            <td class="action-cell">
              <button 
                @click="editSample(sample)"
                :disabled="isLoading"
                class="btn btn-edit"
                title="수정"
              >
                수정
              </button>
              <button 
                @click="confirmDelete(sample)"
                :disabled="isLoading"
                class="btn btn-delete"
                title="삭제"
              >
                삭제
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<script>
import axios from 'axios';

/**
 * Sample CRUD 게시판 컴포넌트
 * 샘플 데이터의 생성, 조회, 수정, 삭제 기능을 제공합니다.
 */
export default {
  name: 'SampleBoard',
  
  data() {
    return {
      // 샘플 데이터 목록
      samples: [],
      
      // 폼 데이터
      form: {
        id: null,
        name: '',
        description: ''
      },
      
      // UI 상태
      isLoading: false,
      errorMessage: '',
      
      // API 설정
      apiUrl: 'http://127.0.0.1:5000/samples',
    };
  },
  
  /**
   * 컴포넌트 생성 시 데이터 로드
   */
  async created() {
    await this.loadSamples();
  },
  
  methods: {
    /**
     * 샘플 목록 조회
     */
    async loadSamples() {
      try {
        this.isLoading = true;
        this.clearError();
        
        const response = await axios.get(`${this.apiUrl}/`);
        this.samples = response.data || [];
        
      } catch (error) {
        console.error('샘플 목록 조회 실패:', error);
        this.showError('샘플 목록을 불러오는데 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 폼 제출 처리 (생성/수정)
     */
    async handleSubmit() {
      if (!this.form.name.trim()) {
        this.showError('이름을 입력해주세요.');
        return;
      }

      try {
        this.isLoading = true;
        this.clearError();

        const requestData = {
          name: this.form.name.trim(),
          description: this.form.description.trim() || null
        };

        if (this.form.id) {
          // 수정
          await axios.put(`${this.apiUrl}/${this.form.id}`, requestData);
        } else {
          // 생성
          await axios.post(`${this.apiUrl}/`, requestData);
        }

        // 성공 후 처리
        this.resetForm();
        await this.loadSamples();
        
      } catch (error) {
        console.error('샘플 저장 실패:', error);
        const action = this.form.id ? '수정' : '생성';
        this.showError(`샘플 ${action}에 실패했습니다.`);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 수정 모드로 전환
     * @param {Object} sample - 수정할 샘플 객체
     */
    editSample(sample) {
      this.form = {
        id: sample.id,
        name: sample.name,
        description: sample.description || ''
      };
      this.clearError();
    },

    /**
     * 폼 초기화
     */
    resetForm() {
      this.form = {
        id: null,
        name: '',
        description: ''
      };
      this.clearError();
    },

    /**
     * 삭제 확인 및 실행
     * @param {Object} sample - 삭제할 샘플 객체
     */
    async confirmDelete(sample) {
      const confirmMessage = `"${sample.name}" 샘플을 정말 삭제하시겠습니까?`;
      
      if (!confirm(confirmMessage)) {
        return;
      }

      try {
        this.isLoading = true;
        this.clearError();
        
        await axios.delete(`${this.apiUrl}/${sample.id}`);
        await this.loadSamples();
        
        // 수정 중인 항목이 삭제된 경우 폼 초기화
        if (this.form.id === sample.id) {
          this.resetForm();
        }
        
      } catch (error) {
        console.error('샘플 삭제 실패:', error);
        this.showError('샘플 삭제에 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 날짜 포맷팅
     * @param {string} dateString - ISO 날짜 문자열
     * @returns {string} 포맷된 날짜 문자열
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
          minute: '2-digit'
        });
      } catch (error) {
        console.warn('날짜 포맷팅 실패:', error);
        return dateString;
      }
    },

    /**
     * 에러 메시지 표시
     * @param {string} message - 에러 메시지
     */
    showError(message) {
      this.errorMessage = message;
      // 5초 후 자동으로 에러 메시지 제거
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
.sample-board {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

/* 헤더 */
.board-header {
  margin-bottom: 32px;
  text-align: center;
}

.board-header h2 {
  color: #1976d2;
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 600;
}

.board-description {
  color: #666;
  font-size: 16px;
  margin: 0;
}

/* 폼 섹션 */
.form-section {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
}

.sample-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.form-input {
  flex: 1;
  min-width: 200px;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  outline: none;
  transition: all 0.2s ease;
}

.form-input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
}

.form-input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-start;
}

/* 버튼 스타일 */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
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
  transform: translateY(-1px);
}

.btn-secondary {
  background: #757575;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #616161;
}

.btn-edit {
  background: #43a047;
  color: white;
  padding: 8px 16px;
  font-size: 14px;
  margin-right: 8px;
}

.btn-edit:hover:not(:disabled) {
  background: #388e3c;
}

.btn-delete {
  background: #e53935;
  color: white;
  padding: 8px 16px;
  font-size: 14px;
}

.btn-delete:hover:not(:disabled) {
  background: #d32f2f;
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

/* 상태 메시지 */
.loading-state,
.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: #666;
}

.empty-hint {
  font-size: 14px;
  color: #999;
  margin-top: 8px;
}

/* 테이블 */
.table-section {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.sample-table {
  width: 100%;
  border-collapse: collapse;
}

.sample-table th {
  background: #e3f2fd;
  color: #1976d2;
  font-weight: 600;
  padding: 16px 12px;
  text-align: left;
  border-bottom: 2px solid #bbdefb;
}

.sample-table td {
  padding: 16px 12px;
  border-bottom: 1px solid #f0f0f0;
}

.table-row:hover {
  background: #f8f9fa;
}

.name-cell {
  font-weight: 500;
  color: #1976d2;
}

.description-cell {
  color: #666;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.date-cell {
  color: #999;
  font-size: 14px;
  white-space: nowrap;
}

.action-cell {
  white-space: nowrap;
}

/* 반응형 */
@media (max-width: 768px) {
  .sample-board {
    padding: 16px;
  }
  
  .form-group {
    flex-direction: column;
  }
  
  .form-input {
    min-width: unset;
  }
  
  .sample-table {
    font-size: 14px;
  }
  
  .sample-table th,
  .sample-table td {
    padding: 12px 8px;
  }
  
  .description-cell {
    max-width: 120px;
  }
}
</style> 