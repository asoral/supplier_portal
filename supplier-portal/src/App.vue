<script setup>
import Navbar from './components/Navbar.vue'
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.initializeAuth()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex flex-col">
    <Navbar />
    <main class="flex-grow">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <footer class="bg-white border-t border-gray-200 py-12">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <!-- Brand -->
          <div class="col-span-1 md:col-span-2">
             <div class="flex items-center gap-2 mb-4">
               <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 shadow-sm">
                  <span class="text-xl font-bold text-white">T</span>
               </div>
               <span class="text-xl font-bold text-gray-900">TenderFlow</span>
             </div>
             <p class="text-sm text-gray-500 leading-relaxed max-w-sm">
               Streamline your procurement process with our comprehensive tender management and vendor collaboration platform. Fair, transparent, and efficient.
             </p>
          </div>

          <!-- Quick Links -->
          <div>
            <h3 class="text-sm font-bold text-gray-900 mb-4">Quick Links</h3>
            <ul class="space-y-3 text-sm text-gray-500">
              <li><router-link to="/tenders" class="hover:text-indigo-600 transition-colors">Active Tenders</router-link></li>
              <li><router-link to="/register" class="hover:text-indigo-600 transition-colors">Vendor Registration</router-link></li>
              <li><router-link to="/dashboard" class="hover:text-indigo-600 transition-colors">Vendor Dashboard</router-link></li>
            </ul>
          </div>

          <!-- Support -->
          <div>
            <h3 class="text-sm font-bold text-gray-900 mb-4">Support</h3>
            <ul class="space-y-3 text-sm text-gray-500">
              <li><router-link to="/help" class="hover:text-indigo-600 transition-colors">Help Center</router-link></li>
              <li><a href="#" class="hover:text-indigo-600 transition-colors">Terms & Conditions</a></li>
              <li><a href="#" class="hover:text-indigo-600 transition-colors">Privacy Policy</a></li>
            </ul>
          </div>
        </div>
        
        <div class="border-t border-gray-100 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-gray-400">
          <p>&copy; 2024 TenderFlow. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
