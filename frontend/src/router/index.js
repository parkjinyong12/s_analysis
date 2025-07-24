import { createRouter, createWebHistory } from 'vue-router'
import SampleBoard from '../features/sample/SampleBoard.vue'
import Sample2Board from '../features/sample/Sample2Board.vue'

const routes = [
  { path: '/', redirect: '/sample' },
  { path: '/sample', component: SampleBoard },
  { path: '/sample2', component: Sample2Board },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 