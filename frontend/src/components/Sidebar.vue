<template>
  <nav class="sidebar">
    <ul>
      <li :class="{active: $route.path==='/sample'}">
        <router-link to="/sample">📊 Sample</router-link>
      </li>
      <li :class="{active: $route.path==='/sample2'}">
        <router-link to="/sample2">📈 Sample2</router-link>
      </li>
      <li :class="{active: $route.path==='/collector'}">
        <router-link to="/collector">🔄 데이터 수집</router-link>
      </li>
    </ul>
  </nav>
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