import Vue from 'vue'
import VueRouter from 'vue-router'

import LoginPage from '@/views/LoginPage.vue'
import HomePage from '@/views/HomePage.vue'
import MqttDashboard from '@/views/MqttDashboard.vue'
import DevicePage from '@/views/DevicePage.vue'
import PersonalDataPage from '@/views/PersonalDataPage.vue'
import RealTimeStatusPage from '@/views/RealTimeStatusPage.vue'
import WaterHeaterPage from '@/views/WaterHeaterPage.vue'
import LightingControllerPage from '@/views/LightingControllerPage.vue';
import SurveillanceCameraPage from '@/views/SurveillanceCameraPage.vue'
import DataHistory from '@/views/DataHistory.vue'
import DeviceData from '@/views/DeviceData.vue';
import WaterHeaterHistory from '@/views/WaterHeaterHistory.vue';
import SurveillanceCameraHistory from '@/views/SurveillanceCameraHistory.vue';
import LightingControllerHistory from '@/views/LightingControllerHistory.vue';
import DeviceControlPage from '@/views/DeviceControlPage.vue';


Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'LoginPage',
    component: LoginPage
  },
  {
    path: '/home',
    name: 'HomePage',
    component: HomePage
  },
  {
    path: '/mqtt',
    name: 'MqttDashboard',
    component: MqttDashboard
  },
  {
    path: '/personal-data',
    name: 'PersonalDataPage',
    component: PersonalDataPage
  },
  {
    path: '/real-time-status',
    name: 'RealTimeStatusPage',
    component: RealTimeStatusPage
  },
  {
    path: '/device/:deviceId',
    name: 'DevicePage',
    component: DevicePage,
    props: true
  },
  {
    path: '/water-heater/:deviceId',
    name: 'WaterHeaterPage',
    component: WaterHeaterPage,
    props: true
  },
  {
    path: '/light-control/:deviceId',
    name: 'LightingControllerPage',
    component: LightingControllerPage,
    props: true
  },
  {
    path: '/surveillance-camera/:deviceId',
    name: 'SurveillanceCameraPage',
    component: SurveillanceCameraPage,
    props: true
  },
  {
    path: '/device-control',
    name: 'DeviceControlPage',
    component: DeviceControlPage
  },
  {
    path: '/data-history',
    name: 'DataHistory',
    component: DataHistory
  },
  {
    path: '/device-data/:deviceId',
    name: 'DeviceData',
    component: DeviceData
  },
  {
    path: '/water-heater-history',
    name: 'WaterHeaterHistory',
    component: WaterHeaterHistory
  },
  {
    path: '/surveillance-camera-history',
    name: 'SurveillanceCameraHistory',
    component: SurveillanceCameraHistory
  },
  {
    path: '/lighting-controller-history',
    name: 'LightingControllerHistory',
    component: LightingControllerHistory
  }
]

const router = new VueRouter({
  mode: 'hash',
  routes
})

// 登录守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('loggedIn') === 'true'
  if (to.path !== '/login' && !isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router



