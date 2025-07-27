import { createRouter, createWebHistory } from 'vue-router'
import HomeBoard from '../features/home/HomeBoard.vue'
import SampleBoard from '../features/sample/SampleBoard.vue'
import Sample2Board from '../features/sample2/Sample2Board.vue'
import StockBoard from '../features/stock/StockBoard.vue'
import TradingBoard from '../features/trading/TradingBoard.vue'
import HistoryBoard from '../features/history/HistoryBoard.vue'
import DataCollector from '../features/collector/DataCollector.vue'
import ApiTest from '../features/api-test/ApiTest.vue'
import ApiSettings from '../features/settings/ApiSettings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomeBoard
  },
  {
    path: '/sample',
    name: 'Sample',
    component: SampleBoard
  },
  {
    path: '/sample2',
    name: 'Sample2',
    component: Sample2Board
  },
  {
    path: '/stock',
    name: 'Stock',
    component: StockBoard
  },
  {
    path: '/trading',
    name: 'Trading',
    component: TradingBoard
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryBoard
  },
  {
    path: '/collector',
    name: 'DataCollector',
    component: DataCollector
  },
  {
    path: '/api-test',
    name: 'ApiTest',
    component: ApiTest
  },
  {
    path: '/settings',
    name: 'Settings',
    component: ApiSettings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 