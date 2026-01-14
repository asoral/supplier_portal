<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { Menu, X, Bell, User, ChevronDown, FileText, FileCode, Webhook, HelpCircle, Package, Truck, MessageSquare, Bookmark, LogOut, Settings, LayoutDashboard } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const isLoggedIn = computed(() => authStore.isAuthenticated)
const logout = authStore.logout
const state = authStore
const isOpen = ref(false)
const isProfileOpen = ref(false)
const isNotificationsOpen = ref(false)
const notificationRef = ref(null)
const profileRef = ref(null)

const closeDropdowns = (e) => {
  if (isNotificationsOpen.value && notificationRef.value && !notificationRef.value.contains(e.target)) {
    isNotificationsOpen.value = false
  }
  if (isProfileOpen.value && profileRef.value && !profileRef.value.contains(e.target)) {
    isProfileOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', closeDropdowns)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdowns)
})

const guestNavigation = [
  { name: 'Home', href: '/' },
  { name: 'Active Tenders', href: '/tenders' },
]

const userNavigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Tenders', href: '/tenders', icon: FileText },
  { name: 'Saved', href: '/saved-tenders', icon: Bookmark },
  { name: 'Contracts', href: '/contracts', icon: FileCode },
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
  HelpCircle,
  Bookmark
}

const activeNavigation = computed(() => {
  return isLoggedIn.value ? userNavigation : guestNavigation
})

const toggleMenu = () => {
  isOpen.value = !isOpen.value
}

const handleLogout = () => {
  logout()
  isProfileOpen.value = false
  window.location.href = '/login'
}
</script>

<template>
  <nav class="sticky top-0 z-50 w-full border-b border-gray-100 bg-white">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 justify-between items-center">
        <!-- Logo -->
        <div class="flex items-center cursor-pointer gap-2" @click="router.push('/')">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 shadow-sm">
            <span class="text-xl font-bold text-white">T</span>
          </div>
          <span class="text-lg font-bold text-gray-900 tracking-tight">TenderFlow</span>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex md:items-center md:gap-8">
          <router-link
            v-for="item in activeNavigation"
            :key="item.name"
            :to="item.href"
            class="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors flex items-center gap-2"
            active-class="text-indigo-600 font-semibold bg-indigo-50 px-3 py-1.5 rounded-md"
          >
             <component v-if="item.name === 'Saved'" :is="Bookmark" class="h-4 w-4" />
             <component v-if="item.name === 'Dashboard'" :is="LayoutDashboard" class="h-4 w-4" />
            {{ item.name }}
          </router-link>

          <!-- More Dropdown (Only for logged in users) -->
          <div v-if="isLoggedIn" class="relative group">
            <button class="flex items-center gap-1 text-sm font-medium text-gray-500 hover:text-gray-900 focus:outline-none transition-colors">
              More <ChevronDown class="h-4 w-4" />
            </button>
            <div class="absolute left-0 mt-2 w-56 origin-top-right rounded-xl bg-white shadow-xl ring-1 ring-black ring-opacity-5 focus:outline-none opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 overflow-hidden transform group-hover:translate-y-0 translate-y-2">
               <div class="p-1">
                  <router-link 
                     v-for="item in moreNavigation" 
                     :key="item.name"
                     :to="item.href"
                     class="group flex items-center px-4 py-2.5 text-sm text-gray-600 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg transition-colors"
                     @click="isOpen = false"
                  >
                     <component 
                        :is="iconMap[item.icon] || Package" 
                        class="mr-3 h-4 w-4 text-gray-400 group-hover:text-indigo-600 transition-colors" 
                     />
                     {{ item.name }}
                  </router-link>
               </div>
            </div>
          </div>
        </div>

        <!-- Desktop Auth Buttons -->
        <div class="hidden md:flex md:items-center md:gap-4">
          <template v-if="!isLoggedIn">
            <button 
              @click="router.push('/login')"
              class="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors px-3 py-2"
            >
              Sign In
            </button>
            <button
              @click="router.push('/register')"
              class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all hover:shadow-md"
            >
              Register as Vendor
            </button>
          </template>
          <template v-else>
            <!-- Notifications Dropdown -->
            <div class="relative" ref="notificationRef">
               <button 
                  @click="isNotificationsOpen = !isNotificationsOpen" 
                  class="p-2 text-gray-400 hover:text-gray-600 transition-colors relative rounded-full hover:bg-gray-100 focus:outline-none"
               >
                  <Bell class="h-5 w-5" />
                  <span class="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white"></span>
               </button>

               <div v-if="isNotificationsOpen" class="absolute right-0 mt-2 w-80 origin-top-right rounded-xl bg-white shadow-xl ring-1 ring-black ring-opacity-5 focus:outline-none z-50 overflow-hidden">
                  <div class="px-4 py-3 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
                     <h3 class="text-sm font-semibold text-gray-900">Notifications</h3>
                     <span class="inline-flex items-center rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-600/20">2 new</span>
                  </div>
                  <div class="max-h-96 overflow-y-auto">
                     <div class="divide-y divide-gray-100">
                        <!-- Item 1 -->
                        <div class="p-4 hover:bg-gray-50 transition-colors cursor-pointer relative group">
                           <div class="flex items-start gap-3">
                              <div class="flex-shrink-0 mt-0.5">
                                 <span class="inline-flex items-center justify-center h-2 w-2 rounded-full bg-blue-600 ring-2 ring-white absolute left-3 top-5"></span>
                              </div>
                              <div class="flex-grow">
                                 <div class="flex items-center justify-between mb-1">
                                    <span class="inline-flex items-center rounded-md bg-blue-50 px-1.5 py-0.5 text-[10px] font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">Bid</span>
                                    <span class="text-xs text-gray-400">7m ago</span>
                                 </div>
                                 <p class="text-sm font-semibold text-gray-900 mb-0.5">Outbid Alert</p>
                                 <p class="text-xs text-gray-500 leading-snug">Your bid on 'Industrial Steel Plates' has been outbid. Current lowest: ₹32,80,000</p>
                              </div>
                           </div>
                        </div>

                        <!-- Item 2 -->
                        <div class="p-4 hover:bg-gray-50 transition-colors cursor-pointer relative group">
                           <div class="flex items-start gap-3">
                              <div class="flex-shrink-0 mt-0.5">
                                 <span class="inline-flex items-center justify-center h-2 w-2 rounded-full bg-blue-600 ring-2 ring-white absolute left-3 top-5"></span>
                              </div>
                              <div class="flex-grow">
                                 <div class="flex items-center justify-between mb-1">
                                    <span class="inline-flex items-center rounded-md bg-green-50 px-1.5 py-0.5 text-[10px] font-medium text-green-700 ring-1 ring-inset ring-green-600/20">Order</span>
                                    <span class="text-xs text-gray-400">2h ago</span>
                                 </div>
                                 <p class="text-sm font-semibold text-gray-900 mb-0.5">Order Confirmed</p>
                                 <p class="text-xs text-gray-500 leading-snug">Congratulations! Your bid on 'Safety Equipment Annual Supply' has been accepted.</p>
                              </div>
                           </div>
                        </div>

                         <!-- Item 3 -->
                        <div class="p-4 hover:bg-gray-50 transition-colors cursor-pointer">
                           <div class="flex items-start gap-3 pl-3"> <!-- Added padding to align since no dot -->
                              <div class="flex-grow">
                                 <div class="flex items-center justify-between mb-1">
                                    <span class="inline-flex items-center rounded-md bg-indigo-50 px-1.5 py-0.5 text-[10px] font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">Tender</span>
                                    <span class="text-xs text-gray-400">5h ago</span>
                                 </div>
                                 <p class="text-sm font-semibold text-gray-900 mb-0.5">New Tender in Your Category</p>
                                 <p class="text-xs text-gray-500 leading-snug">A new tender for 'Industrial Fasteners' has been published matching your preferences.</p>
                              </div>
                           </div>
                        </div>
                        
                        <!-- Item 4 -->
                        <div class="p-4 hover:bg-gray-50 transition-colors cursor-pointer">
                           <div class="flex items-start gap-3 pl-3">
                              <div class="flex-grow">
                                 <div class="flex items-center justify-between mb-1">
                                    <span class="inline-flex items-center rounded-md bg-orange-50 px-1.5 py-0.5 text-[10px] font-medium text-orange-700 ring-1 ring-inset ring-orange-600/20">Alert</span>
                                    <span class="text-xs text-gray-400">1d ago</span>
                                 </div>
                                 <p class="text-sm font-semibold text-gray-900 mb-0.5">Tender Closing Soon</p>
                                 <p class="text-xs text-gray-500 leading-snug">CNC Machining Center tender closes in 24 hours.</p>
                              </div>
                           </div>
                        </div>
                     </div>
                  </div>
                  <div class="p-3 border-t border-gray-100 bg-gray-50 text-center">
                     <button class="text-xs font-semibold text-indigo-600 hover:text-indigo-700 transition-colors">View all notifications</button>
                  </div>
               </div>
            </div>
            
            <!-- User Profile Dropdown -->
            <div class="relative ml-2" ref="profileRef">
               <button 
                  @click="isProfileOpen = !isProfileOpen" 
                  class="flex items-center gap-3 rounded-full hover:bg-gray-50 p-1 pr-3 transition-colors border border-transparent hover:border-gray-200"
               >
                  <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-semibold border border-indigo-200">
                     {{ state.user?.name?.charAt(0) || 'U' }}
                  </div>
                  <div class="flex flex-col items-start">
                     <span class="text-sm font-medium text-gray-700 leading-none">{{ state.user?.name || 'User' }}</span>
                     <span class="text-xs text-gray-500 leading-none mt-1">{{ state.user?.company || 'Company' }}</span>
                  </div>
                  <ChevronDown class="h-3 w-3 text-gray-400" />
               </button>

               <div v-if="isProfileOpen" class="absolute right-0 mt-2 w-56 origin-top-right rounded-xl bg-white shadow-xl ring-1 ring-black ring-opacity-5 focus:outline-none z-50 overflow-hidden">
                   <div class="px-4 py-3 border-b border-gray-100 bg-gray-50">
                     <p class="text-sm leading-5 font-medium text-gray-900 truncate">{{ state.user?.name }}</p>
                     <p class="text-xs leading-4 text-gray-500 truncate">{{ state.user?.email }}</p>
                   </div>
                   <div class="p-1">
                     <router-link to="/profile" class="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg">
                        <User class="mr-3 h-4 w-4 text-gray-400 group-hover:text-indigo-600" />
                        My Profile
                     </router-link>
                     <router-link to="/dashboard" class="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg">
                        <LayoutDashboard class="mr-3 h-4 w-4 text-gray-400 group-hover:text-indigo-600" />
                        Dashboard
                     </router-link>
                     <router-link to="/profile" class="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-600 rounded-lg">
                        <Settings class="mr-3 h-4 w-4 text-gray-400 group-hover:text-indigo-600" />
                        Settings
                     </router-link>
                   </div>
                   <div class="p-1 border-t border-gray-100">
                     <button @click="handleLogout" class="group flex w-full items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg">
                        <LogOut class="mr-3 h-4 w-4 text-red-600" />
                        Sign Out
                     </button>
                   </div>
               </div>
            </div>
          </template>
        </div>

        <!-- Mobile menu button -->
        <div class="flex items-center md:hidden">
          <button 
            @click="toggleMenu"
            class="inline-flex items-center justify-center rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none"
          >
            <Menu v-if="!isOpen" class="block h-6 w-6" />
            <X v-else class="block h-6 w-6" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-show="isOpen" class="md:hidden bg-white border-b border-gray-200 shadow-lg">
      <div class="space-y-1 px-4 pb-4 pt-2">
        <router-link
          v-for="item in activeNavigation"
          :key="item.name"
          :to="item.href"
          class="block rounded-lg px-3 py-2 text-base font-medium text-gray-600 hover:bg-indigo-50 hover:text-indigo-600"
          active-class="bg-indigo-50 text-indigo-600"
          @click="isOpen = false"
        >
          <div class="flex items-center gap-3">
             <component v-if="item.icon" :is="item.icon" class="h-5 w-5" />
             {{ item.name }}
          </div>
        </router-link>
        
        <template v-if="isLoggedIn">
           <div class="border-t border-gray-100 my-2 pt-2">
              <p class="px-3 text-xs font-semibold text-gray-400 uppercase mb-2">More</p>
              <router-link
                 v-for="item in moreNavigation"
                 :key="item.name"
                 :to="item.href"
                 class="block rounded-lg px-3 py-2 text-sm font-medium text-gray-600 hover:bg-indigo-50 hover:text-indigo-600"
                 @click="isOpen = false"
              >
                  <div class="flex items-center gap-3">
                     <component :is="iconMap[item.icon]" class="h-4 w-4" />
                     {{ item.name }}
                  </div>
              </router-link>
           </div>
           <div class="border-t border-gray-100 my-2 pt-2">
              <button @click="handleLogout" class="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-base font-medium text-red-600 hover:bg-red-50">
                 <LogOut class="h-5 w-5" />
                 Sign Out
              </button>
           </div>
        </template>
        <template v-else>
           <div class="mt-4 grid grid-cols-2 gap-3">
            <router-link
               to="/login"
               class="flex items-center justify-center rounded-lg border border-gray-300 bg-white px-4 py-2 text-base font-medium text-gray-700 shadow-sm hover:bg-gray-50"
               @click="isOpen = false"
            >
               Sign In
            </router-link>
            <router-link
               to="/register"
               class="flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-base font-medium text-white shadow-sm hover:bg-indigo-500"
               @click="isOpen = false"
            >
               Register
            </router-link>
           </div>
        </template>
      </div>
    </div>
  </nav>
</template>
