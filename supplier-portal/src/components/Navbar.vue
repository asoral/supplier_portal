<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, X, Bell, User, ChevronDown, FileText, FileCode, Webhook, HelpCircle, Package, Truck, MessageSquare, Bookmark } from 'lucide-vue-next'

const router = useRouter()
const isOpen = ref(false)
const isLoggedIn = ref(false) // TODO: Connect to auth store

const navigation = [
  { name: 'Home', href: '/' },
  { name: 'Active Tenders', href: '/tenders' },
  { name: 'Saved', href: '/saved-tenders' },
  { name: 'Contracts', href: '/contracts' },
]

const moreNavigation = [
  { name: 'My Catalog', href: '/catalog', icon: 'Package' },
  { name: 'Deliveries', href: '/deliveries', icon: 'Truck' },
  { name: 'Invoices', href: '/invoices', icon: 'FileText' },
  { name: 'Documents', href: '/documents', icon: 'FileCode' },
  { name: 'Queries', href: '/queries', icon: 'MessageSquare' },
  { name: 'Integrations', href: '/integrations', icon: 'Webhook' },
  { name: 'Help', href: '/help', icon: 'HelpCircle' },
]

const iconMap = {
  Package,
  Truck,
  FileText,
  FileCode,
  MessageSquare,
  Webhook,
  HelpCircle
}

const toggleMenu = () => {
  isOpen.value = !isOpen.value
}
</script>

<template>
  <nav class="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/80 backdrop-blur-md">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 justify-between items-center">
        <!-- Logo -->
        <div class="flex items-center cursor-pointer" @click="router.push('/')">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600">
            <span class="text-xl font-bold text-white">T</span>
          </div>
          <span class="ml-2 text-xl font-bold text-gray-900">TenderFlow</span>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex md:items-center md:space-x-8">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.href"
            class="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors flex items-center gap-2"
            active-class="text-indigo-600"
          >
             <component v-if="item.name === 'Saved'" :is="Bookmark" class="h-4 w-4" />
            {{ item.name }}
          </router-link>

          <!-- More Dropdown -->
          <div class="relative group">
            <button class="flex items-center gap-1 text-sm font-medium text-gray-700 hover:text-indigo-600 focus:outline-none transition-colors">
              More <ChevronDown class="h-4 w-4" />
            </button>
            <div class="absolute left-0 mt-2 w-56 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
               <div class="py-1">
                  <router-link 
                     v-for="item in moreNavigation" 
                     :key="item.name"
                     :to="item.href"
                     class="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 hover:text-indigo-600"
                     @click="isOpen = false"
                  >
                     <component 
                        :is="iconMap[item.icon] || Package" 
                        class="mr-3 h-4 w-4 text-gray-400 group-hover:text-indigo-600" 
                     />
                     {{ item.name }}
                  </router-link>
               </div>
            </div>
          </div>
        </div>

        <!-- Desktop Auth Buttons -->
        <div class="hidden md:flex md:items-center md:space-x-4">
          <template v-if="!isLoggedIn">
            <button 
              @click="router.push('/login')"
              class="text-sm font-medium text-gray-700 hover:text-indigo-600 transition-colors"
            >
              Sign In
            </button>
            <button
              @click="router.push('/register')"
              class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all hover:scale-105 active:scale-95"
            >
              Register as Vendor
            </button>
          </template>
          <template v-else>
             <button class="p-2 text-gray-400 hover:text-gray-500">
              <Bell class="h-6 w-6" />
            </button>
            <button 
              @click="router.push('/dashboard')"
              class="flex items-center gap-2 rounded-full bg-gray-100 px-3 py-1.5 hover:bg-gray-200 transition-colors"
            >
              <User class="h-5 w-5 text-gray-600" />
              <span class="text-sm font-medium text-gray-700">Dashboard</span>
            </button>
          </template>
        </div>

        <!-- Mobile menu button -->
        <div class="flex items-center md:hidden">
          <button 
            @click="toggleMenu"
            class="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <Menu v-if="!isOpen" class="block h-6 w-6" />
            <X v-else class="block h-6 w-6" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-show="isOpen" class="md:hidden bg-white border-b border-gray-200">
      <div class="space-y-1 px-2 pb-3 pt-2 sm:px-3">
        <router-link
          v-for="item in navigation"
          :key="item.name"
          :to="item.href"
          class="block rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-indigo-600"
          @click="isOpen = false"
        >
          {{ item.name }}
        </router-link>
        <template v-if="!isLoggedIn">
           <router-link
            to="/login"
            class="block rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-indigo-600"
            @click="isOpen = false"
          >
            Sign In
          </router-link>
           <router-link
            to="/register"
            class="block rounded-md px-3 py-2 text-base font-medium text-indigo-600 hover:bg-indigo-50"
            @click="isOpen = false"
          >
            Register as Vendor
          </router-link>
        </template>
        <template v-else>
          <router-link
            to="/dashboard"
            class="block rounded-md px-3 py-2 text-base font-medium text-gray-700 hover:bg-gray-50 hover:text-indigo-600"
            @click="isOpen = false"
          >
            Dashboard
          </router-link>
        </template>
      </div>
    </div>
  </nav>
</template>
