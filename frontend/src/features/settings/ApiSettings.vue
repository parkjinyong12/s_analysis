<template>
  <div class="api-settings">
    <!-- 헤더 -->
    <header class="settings-header">
      <h2>API 설정</h2>
      <p class="settings-description">백엔드 API 서버 연결 설정을 관리합니다.</p>
    </header>

    <!-- 현재 설정 상태 -->
    <section class="current-status">
      <h3>현재 연결 상태</h3>
      <div class="status-card">
        <div class="status-info">
          <div class="status-badge" :class="connectionStatus.success ? 'connected' : 'disconnected'">
            {{ connectionStatus.success ? '연결됨' : '연결 실패' }}
          </div>
          <div class="status-details">
            <p><strong>서버:</strong> {{ currentConfig.BASE_URL }}</p>
            <p><strong>타임아웃:</strong> {{ currentConfig.TIMEOUT }}ms</p>
            <p><strong>디버그 모드:</strong> {{ currentConfig.DEBUG ? '활성화' : '비활성화' }}</p>
            <p v-if="connectionStatus.success"><strong>응답 시간:</strong> {{ connectionStatus.responseTime }}</p>
            <p v-if="!connectionStatus.success && connectionStatus.error">
              <strong>오류:</strong> {{ connectionStatus.error }}
            </p>
          </div>
        </div>
        <button 
          @click="testConnection" 
          :disabled="isLoading"
          class="btn btn-secondary"
        >
          {{ isLoading ? '테스트 중...' : '연결 테스트' }}
        </button>
      </div>
      
      <!-- 연결 테스트 메시지 (상태 섹션 바로 아래) -->
      <div v-if="testMessage" class="test-message" :class="testMessageType">
        {{ testMessage }}
      </div>
    </section>

    <!-- 설정 폼 -->
    <section class="settings-form">
      <h3>설정 변경</h3>
      <form @submit.prevent="saveSettings" class="form">
        <!-- API 기본 URL -->
        <div class="form-group">
          <label for="baseUrl">API 기본 URL</label>
          <input 
            id="baseUrl"
            v-model="formData.baseUrl" 
            type="url"
            placeholder="http://127.0.0.1:5000"
            required
            class="form-input"
            :class="{ 'error': errors.baseUrl }"
          />
          <span v-if="errors.baseUrl" class="error-text">{{ errors.baseUrl }}</span>
          <small class="form-help">백엔드 서버의 기본 URL을 입력하세요.</small>
        </div>

        <!-- 요청 타임아웃 -->
        <div class="form-group">
          <label for="timeout">요청 타임아웃 (밀리초)</label>
          <input 
            id="timeout"
            v-model.number="formData.timeout" 
            type="number"
            min="1000"
            max="60000"
            step="1000"
            required
            class="form-input"
            :class="{ 'error': errors.timeout }"
          />
          <span v-if="errors.timeout" class="error-text">{{ errors.timeout }}</span>
          <small class="form-help">API 요청 타임아웃 시간 (1000-60000ms)</small>
        </div>

        <!-- 디버그 모드 -->
        <div class="form-group">
          <label class="checkbox-label">
            <input 
              v-model="formData.debug" 
              type="checkbox"
              class="form-checkbox"
            />
            <span class="checkbox-text">디버그 모드 활성화</span>
          </label>
          <small class="form-help">API 요청/응답 로그를 콘솔에 출력합니다.</small>
        </div>

        <!-- 폼 액션 -->
        <div class="form-actions">
          <button 
            type="submit" 
            :disabled="isLoading || !isFormValid"
            class="btn btn-primary"
          >
            {{ isLoading ? '저장 중...' : '설정 저장' }}
          </button>
          <button 
            type="button" 
            @click="resetToDefaults"
            :disabled="isLoading"
            class="btn btn-outline"
          >
            기본값으로 초기화
          </button>
          <button 
            type="button" 
            @click="reloadSettings"
            :disabled="isLoading"
            class="btn btn-secondary"
          >
            현재 설정 불러오기
          </button>
        </div>
      </form>
    </section>

    <!-- 사전 정의된 설정 -->
    <section class="preset-settings">
      <h3>빠른 설정</h3>
      <div class="preset-list">
        <div 
          v-for="preset in presets" 
          :key="preset.name"
          class="preset-item"
          @click="applyPreset(preset)"
        >
          <div class="preset-info">
            <h4>{{ preset.name }}</h4>
            <p>{{ preset.description }}</p>
            <small>{{ preset.url }}</small>
          </div>
          <button class="btn btn-small">적용</button>
        </div>
      </div>
    </section>

    <!-- 에러 메시지 -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <!-- 성공 메시지 -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
  </div>
</template>

<script>
import { apiSettings } from '@/config/api';

export default {
  name: 'ApiSettings',
  
  data() {
    return {
      // 현재 설정
      currentConfig: {},
      
      // 폼 데이터
      formData: {
        baseUrl: '',
        timeout: 10000,
        debug: false
      },
      
      // 연결 상태
      connectionStatus: {
        success: false,
        error: null,
        responseTime: null
      },
      
      // UI 상태
      isLoading: false,
      errorMessage: '',
      successMessage: '',
      
      // 연결 테스트 메시지 (상단 표시용)
      testMessage: '',
      testMessageType: 'success', // 'success' or 'error'
      
      // 폼 검증 에러
      errors: {},
      
      // 사전 정의된 설정
      presets: [
        {
          name: '로컬 개발 서버',
          description: '기본 개발 환경 설정',
          url: 'http://127.0.0.1:5000',
          timeout: 10000,
          debug: true
        },
        {
          name: '로컬 호스트',
          description: 'localhost 사용',
          url: 'http://localhost:5000',
          timeout: 10000,
          debug: true
        },
        {
          name: '운영 서버',
          description: '운영 환경 설정 (예시)',
          url: 'https://api.production.com',
          timeout: 15000,
          debug: false
        },
        {
          name: '테스트 서버',
          description: '테스트 환경 설정 (예시)',
          url: 'http://test-server:3000',
          timeout: 8000,
          debug: true
        }
      ]
    };
  },
  
  computed: {
    isFormValid() {
      return this.formData.baseUrl && 
             this.formData.timeout >= 1000 && 
             this.formData.timeout <= 60000 &&
             Object.keys(this.errors).length === 0;
    }
  },
  
  mounted() {
    this.loadCurrentSettings();
    this.testConnection();
  },
  
  methods: {
    /**
     * 현재 설정 불러오기
     */
    loadCurrentSettings() {
      this.currentConfig = apiSettings.getConfig();
      this.formData = {
        baseUrl: this.currentConfig.BASE_URL,
        timeout: this.currentConfig.TIMEOUT,
        debug: this.currentConfig.DEBUG
      };
    },
    
    /**
     * 설정 다시 불러오기
     */
    reloadSettings() {
      this.loadCurrentSettings();
      this.clearMessages();
      this.showSuccess('현재 설정을 불러왔습니다.');
    },
    
    /**
     * 연결 테스트
     */
    async testConnection() {
      this.isLoading = true;
      this.clearMessages();
      this.clearTestMessage();
      
      try {
        this.connectionStatus = await apiSettings.testConnection();
        
        if (this.connectionStatus.success) {
          this.showTestMessage('서버 연결이 성공했습니다! 🎉', 'success');
        } else {
          this.showTestMessage(`서버 연결에 실패했습니다: ${this.connectionStatus.error}`, 'error');
        }
      } catch (error) {
        this.connectionStatus = {
          success: false,
          error: error.message
        };
        this.showTestMessage('연결 테스트 중 오류가 발생했습니다.', 'error');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 폼 검증
     */
    validateForm() {
      this.errors = {};
      
      // URL 검증
      if (!this.formData.baseUrl) {
        this.errors.baseUrl = 'API URL을 입력해주세요.';
      } else {
        try {
          new URL(this.formData.baseUrl);
        } catch {
          this.errors.baseUrl = '올바른 URL 형식을 입력해주세요.';
        }
      }
      
      // 타임아웃 검증
      if (!this.formData.timeout || this.formData.timeout < 1000 || this.formData.timeout > 60000) {
        this.errors.timeout = '타임아웃은 1000-60000ms 범위여야 합니다.';
      }
      
      return Object.keys(this.errors).length === 0;
    },
    
    /**
     * 설정 저장
     */
    async saveSettings() {
      if (!this.validateForm()) {
        this.showError('입력값을 확인해주세요.');
        return;
      }
      
      this.isLoading = true;
      this.clearMessages();
      
      try {
        // 설정 적용
        apiSettings.setBaseURL(this.formData.baseUrl);
        apiSettings.setTimeout(this.formData.timeout);
        apiSettings.setDebug(this.formData.debug);
        
        // 현재 설정 업데이트
        this.loadCurrentSettings();
        
        this.showSuccess('설정이 저장되었습니다!');
        
        // 저장 후 연결 테스트
        setTimeout(() => {
          this.testConnection();
        }, 1000);
        
      } catch (error) {
        console.error('설정 저장 실패:', error);
        this.showError('설정 저장에 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 기본값으로 초기화
     */
    async resetToDefaults() {
      if (!confirm('설정을 기본값으로 초기화하시겠습니까?')) {
        return;
      }
      
      this.isLoading = true;
      this.clearMessages();
      
      try {
        apiSettings.resetToDefaults();
        this.loadCurrentSettings();
        this.showSuccess('설정이 기본값으로 초기화되었습니다.');
        
        // 초기화 후 연결 테스트
        setTimeout(() => {
          this.testConnection();
        }, 1000);
        
      } catch (error) {
        console.error('설정 초기화 실패:', error);
        this.showError('설정 초기화에 실패했습니다.');
      } finally {
        this.isLoading = false;
      }
    },
    
    /**
     * 사전 정의된 설정 적용
     */
    applyPreset(preset) {
      this.formData = {
        baseUrl: preset.url,
        timeout: preset.timeout,
        debug: preset.debug
      };
      
      this.clearMessages();
      this.showSuccess(`"${preset.name}" 설정이 적용되었습니다. 저장 버튼을 클릭하세요.`);
    },
    
    /**
     * 성공 메시지 표시
     */
    showSuccess(message) {
      this.successMessage = message;
      setTimeout(() => {
        this.successMessage = '';
      }, 5000);
    },
    
    /**
     * 에러 메시지 표시
     */
    showError(message) {
      this.errorMessage = message;
      setTimeout(() => {
        this.errorMessage = '';
      }, 5000);
    },
    
    /**
     * 메시지 초기화
     */
    clearMessages() {
      this.errorMessage = '';
      this.successMessage = '';
    },
    
    /**
     * 연결 테스트 메시지 표시 (상단)
     */
    showTestMessage(message, type = 'success') {
      this.testMessage = message;
      this.testMessageType = type;
      
      // 5초 후 자동 사라짐
      setTimeout(() => {
        this.clearTestMessage();
      }, 5000);
    },
    
    /**
     * 연결 테스트 메시지 초기화
     */
    clearTestMessage() {
      this.testMessage = '';
    }
  }
};
</script>

<style scoped>
/* 메인 컨테이너 */
.api-settings {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
}

/* 헤더 */
.settings-header {
  margin-bottom: 32px;
  text-align: center;
}

.settings-header h2 {
  color: #1976d2;
  margin-bottom: 8px;
  font-size: 28px;
  font-weight: 600;
}

.settings-description {
  color: #666;
  font-size: 16px;
  margin: 0;
}

/* 현재 상태 섹션 */
.current-status {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.current-status h3 {
  margin-bottom: 16px;
  color: #333;
}

.status-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.status-info {
  flex: 1;
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

.status-badge.connected {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-badge.disconnected {
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

/* 연결 테스트 메시지 (상단) */
.test-message {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 500;
  animation: slideDown 0.3s ease-out;
}

.test-message.success {
  background: #e8f5e8;
  color: #2e7d32;
  border-left: 4px solid #43a047;
}

.test-message.error {
  background: #ffebee;
  color: #c62828;
  border-left: 4px solid #e53935;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 설정 폼 */
.settings-form {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.settings-form h3 {
  margin-bottom: 24px;
  color: #333;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
}

.form-input {
  width: 100%;
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

.form-input.error {
  border-color: #e53935;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-checkbox {
  width: 18px;
  height: 18px;
}

.checkbox-text {
  font-weight: 600;
  color: #333;
}

.form-help {
  display: block;
  margin-top: 4px;
  font-size: 14px;
  color: #666;
}

.error-text {
  display: block;
  margin-top: 4px;
  font-size: 14px;
  color: #e53935;
}

.form-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 사전 정의된 설정 */
.preset-settings {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preset-settings h3 {
  margin-bottom: 16px;
  color: #333;
}

.preset-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.preset-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.preset-item:hover {
  border-color: #1976d2;
  background: #f8f9fa;
}

.preset-info {
  flex: 1;
}

.preset-info h4 {
  margin: 0 0 4px 0;
  color: #333;
  font-size: 16px;
}

.preset-info p {
  margin: 0 0 4px 0;
  color: #666;
  font-size: 14px;
}

.preset-info small {
  color: #999;
  font-size: 12px;
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

.btn-outline {
  background: transparent;
  color: #666;
  border: 2px solid #e0e0e0;
}

.btn-outline:hover:not(:disabled) {
  background: #f5f5f5;
  border-color: #bdbdbd;
}

.btn-small {
  padding: 8px 16px;
  min-width: 80px;
  background: #1976d2;
  color: white;
}

.btn-small:hover {
  background: #1565c0;
}

/* 메시지 */
.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 4px solid #e53935;
}

.success-message {
  background: #e8f5e8;
  color: #2e7d32;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 4px solid #43a047;
}

/* 반응형 */
@media (max-width: 768px) {
  .api-settings {
    padding: 16px;
  }
  
  .status-card {
    flex-direction: column;
    align-items: stretch;
  }
  
  .status-info {
    flex-direction: column;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .preset-list {
    grid-template-columns: 1fr;
  }
  
  .preset-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
}
</style> 