<script setup>
import Navbar from './components/Navbar.vue'
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
    <footer class="bg-white border-t border-gray-200 py-8">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <div class="mb-4 md:mb-0">
             <span class="text-xl font-bold text-gray-900">TenderFlow</span>
             <p class="text-sm text-gray-500 mt-1">Next-Gen Procurement Portal</p>
          </div>
          <div class="flex space-x-6 text-sm text-gray-500">
            <a href="#" class="hover:text-indigo-600">Privacy Policy</a>
            <a href="#" class="hover:text-indigo-600">Terms of Service</a>
            <a href="#" class="hover:text-indigo-600">Contact Support</a>
          </div>
          <div class="mt-4 md:mt-0 text-sm text-gray-400">
            &copy; 2024 TenderFlow. All rights reserved.
          </div>
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
