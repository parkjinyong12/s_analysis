<template>
  <div id="app" class="app-layout">
    <Sidebar />
    <main class="main-content">
      <div class="content-wrapper">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script>
import Sidebar from './components/Sidebar.vue'
export default {
  name: 'App',
  components: { Sidebar },
}
</script>

<style>
.app-layout {
  display: flex;
  min-height: 100vh;
  background: #f5f7fa;
}
.main-content {
  flex: 1;
  margin-left: 160px;
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
.content-wrapper {
  min-width: 700px;
  min-height: 600px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
  padding: 32px 24px 24px 24px;
  width: 100%;
  max-width: 900px;
}
</style>
