import { createRouter, createWebHistory } from 'vue-router'
import Sample from '@/features/sample/SampleBoard.vue'
import Sample2 from '@/features/sample2/Sample2Board.vue'
import DataCollector from '@/features/collector/DataCollector.vue'

const routes = [
  {
    path: '/',
    redirect: '/sample'
  },
  {
    path: '/sample',
    name: 'Sample',
    component: Sample
  },
  {
    path: '/sample2',
    name: 'Sample2',
    component: Sample2
  },
  {
    path: '/collector',
    name: 'DataCollector',
    component: DataCollector
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 