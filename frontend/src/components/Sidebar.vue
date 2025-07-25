<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h3>📊 Stock Analysis</h3>
    </div>
    
    <nav class="sidebar-nav">
      <ul class="nav-list">
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
  width: 160px;
  background: #1976d2;
  color: #fff;
  height: 100vh;
  padding-top: 40px;
  position: fixed;
  left: 0;
  top: 0;
  box-shadow: 2px 0 8px rgba(0,0,0,0.07);
}
.sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.sidebar li {
  padding: 18px 24px;
  cursor: pointer;
  font-size: 17px;
  transition: background 0.2s, color 0.2s;
}
.sidebar li.active, .sidebar li:hover {
  background: #fff;
  color: #1976d2;
}
.sidebar a {
  color: inherit;
  text-decoration: none;
  display: block;
}
</style> 