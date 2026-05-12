import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import Toast, { type PluginOptions } from 'vue-toastification'
import 'vue-toastification/dist/index.css'

import App from './App.vue'
import router from './router'

if (localStorage.getItem('dark_mode') === 'true') {
  document.documentElement.classList.add('dark')
}

const toastOptions: PluginOptions = {
  timeout: 3000,
  closeOnClick: true,
  pauseOnHover: true,
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(Toast, toastOptions)
app.mount('#app')
