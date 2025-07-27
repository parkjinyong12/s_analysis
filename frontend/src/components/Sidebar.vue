<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <router-link to="/" class="logo-link">
        <h3>📊 Stock Analysis</h3>
      </router-link>
    </div>
    
    <nav class="sidebar-nav">
      <ul class="nav-list">
        <li class="nav-item">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
            <span class="nav-icon">🏠</span>
            <span class="nav-text">홈</span>
          </router-link>
        </li>
        
        <li class="nav-item">
          <router-link to="/sample" class="nav-link" :class="{ active: $route.path === '/sample' }">
            <span class="nav-icon">📝</span>
            <span class="nav-text">Sample</span>
          </router-link>
        </li>
        
        <li class="nav-item">
          <router-link to="/sample2" class="nav-link" :class="{ active: $route.path === '/sample2' }">
            <span class="nav-icon">📋</span>
            <span class="nav-text">Sample2</span>
          </router-link>
        </li>
        
        <li class="nav-item">
          <router-link to="/stock" class="nav-link" :class="{ active: $route.path === '/stock' }">
            <span class="nav-icon">📊</span>
            <span class="nav-text">주식 목록</span>
          </router-link>
        </li>
        
        <li class="nav-item">
          <router-link to="/trading" class="nav-link" :class="{ active: $route.path === '/trading' }">
            <span class="nav-icon">📈</span>
            <span class="nav-text">거래 데이터</span>
          </router-link>
        </li>
        
        <li class="nav-item">
          <router-link to="/history" class="nav-link" :class="{ active: $route.path === '/history' }">
            <span class="nav-icon">📋</span>
            <span class="nav-text">히스토리</span>
          </router-link>
        </li>
        
        <li class="nav-item">
          <router-link to="/collector" class="nav-link" :class="{ active: $route.path === '/collector' }">
            <span class="nav-icon">🔄</span>
            <span class="nav-text">데이터 수집</span>
          </router-link>
        </li>
        
        <li class="nav-item">
          <router-link to="/api-test" class="nav-link" :class="{ active: $route.path === '/api-test' }">
            <span class="nav-icon">🧪</span>
            <span class="nav-text">API 테스트</span>
          </router-link>
        </li>
        
        <li class="nav-item">
          <router-link to="/settings" class="nav-link" :class="{ active: $route.path === '/settings' }">
            <span class="nav-icon">⚙️</span>
            <span class="nav-text">설정</span>
          </router-link>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'SidebarComponent',
}
</script>

<style scoped>
.sidebar {
  width: 180px;
  background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
  color: #fff;
  height: 100vh;
  padding-top: 20px;
  position: fixed;
  left: 0;
  top: 0;
  box-shadow: 2px 0 12px rgba(0,0,0,0.15);
  z-index: 1000;
}

.sidebar-header {
  padding: 0 20px 20px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  margin-bottom: 10px;
}

.logo-link {
  text-decoration: none;
  color: inherit;
  display: block;
  transition: all 0.3s ease;
}

.logo-link:hover {
  transform: scale(1.05);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  text-align: center;
}

.sidebar-nav {
  padding: 0 10px;
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin-bottom: 4px;
  border-radius: 8px;
  overflow: hidden;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: rgba(255,255,255,0.9);
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  border-radius: 8px;
  position: relative;
}

.nav-link:hover {
  background: rgba(255,255,255,0.1);
  color: #fff;
}

.nav-link.active {
  background: rgba(255,255,255,0.95);
  color: #1976d2;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  font-weight: 600;
}

.nav-link.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #fff;
  border-radius: 0 2px 2px 0;
}

.nav-icon {
  font-size: 18px;
  margin-right: 12px;
  width: 20px;
  text-align: center;
}

.nav-text {
  flex: 1;
  white-space: nowrap;
}

/* 호버 시 아이콘 애니메이션 */
.nav-link:hover .nav-icon {
  transform: scale(1.1);
  transition: transform 0.2s ease;
}

/* 활성 상태에서 아이콘 강조 */
.nav-link.active .nav-icon {
  transform: scale(1.05);
}

/* 반응형 */
@media (max-width: 768px) {
  .sidebar {
    width: 60px;
  }
  
  .sidebar-header h3 {
    font-size: 12px;
  }
  
  .nav-text {
    display: none;
  }
  
  .nav-icon {
    margin-right: 0;
    font-size: 20px;
  }
  
  .nav-link {
    justify-content: center;
    padding: 16px 8px;
  }
}

/* 스크롤바 스타일링 */
.sidebar::-webkit-scrollbar {
  width: 4px;
}

.sidebar::-webkit-scrollbar-track {
  background: rgba(255,255,255,0.1);
}

.sidebar::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.3);
  border-radius: 2px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.5);
}
</style> 