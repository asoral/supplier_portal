<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Search, Filter, LayoutGrid, List, X, Bell, Bookmark, UserCircle } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import TenderCard from '../components/TenderCard.vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const route = useRoute()
const router = useRouter()
const isSessionExpired = ref(false)
const searchQuery = ref('')

const refetchSession = async () => {
   // Try to bounce the session
   isLoading.value = true;
   isSessionExpired.value = false;
   await authStore.logout(false); // Clean logout
   router.push('/login?redirect=' + route.fullPath);
}
const viewMode = ref('grid') 
const priceRange = ref(5000000)
const sortBy = ref('Deadline (Soonest)')

// Filters
const selectedCategory = ref('All')
const selectedStatus = ref('All')
const selectedPriority = ref('All')
const liveBiddingOnly = ref(false)

const tenders = ref([])
const isLoading = ref(true)

const fetchTenders = async () => {
  isLoading.value = true
  try {
    // 1. Construct parameters properly
    const params = new URLSearchParams({ 
      limit: 20,
      offset: 0, // Always good to be explicit
      priority: selectedPriority.value 
    })

    // 2. Use the interpolated string correctly
    const response = await authStore.secureFetch(`/api/method/supplier_portal.api.get_active_tenders?${params.toString()}`)

    if (!response.ok) {
        if (response.status === 403 || response.status === 401) {
            isSessionExpired.value = true;
            throw new Error("Session Expired");
        }
        throw new Error(`HTTP Error: ${response.status}`);
    }

    const result = await response.json()
    const data = result.message || []
    
    // 3. Map the data (Your mapping logic is solid)
    tenders.value = data.map(rfq => ({
      id: rfq.name,                               
      title: rfq.custom_rfq_subject || rfq.name,               
      description: rfq.custom_rfq_description ? rfq.custom_rfq_description.replace(/<[^>]*>?/gm, '') : '', 
      category: rfq.custom_rfq_category,        
      status: rfq.custom_bid_status,             
      budget: parseFloat(rfq.custom_total_budget_) || 0, // Ensure this is a number for the slider
      deadline: rfq.custom_bid_submission_last_date,             
      publishedDate: rfq.custom_publish_date,
      priority: rfq.custom_priority,
      liveBidding: rfq.custom_bid_status === 'Active' && !!rfq.custom_enable_live_bidding
    }))
  } catch (error) {
    console.error("Failed to load tenders:", error)
    tenders.value = [] // Clear list on error to avoid stale data
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
   fetchTenders();
   if (route.query.category) {
      selectedCategory.value = route.query.category
   }
})


const categories = computed(() => {
  const counts = {} // { 'Raw Materials': 2, ... }
  tenders.value.forEach(t => {
      const cat = t.category || 'Uncategorized';
      counts[cat] = (counts[cat] || 0) + 1;
  })

  // Basic list from counts
  const list = Object.keys(counts).map(name => ({
      name: name,
      count: counts[name]
  }));

  // Add 'All' or ensure known categories are present? 
  // For now let's just list what is available + 'All'
  // Or keep the predefined list for UI structure but update counts?
  // Let's go with dynamic list to avoid "hard coded data" complaint strictly.
  
  const allCount = tenders.value.length;
  // Prepend All
  return [{ name: 'All', count: allCount }, ...list];
})

const statuses = ['All', 'Active', 'Closing Soon', 'Closed']
const priorities = ['All', 'Urgent', 'High', 'Normal', 'Low']

// Mock Data

const filteredTenders = computed(() => {
  let result = tenders.value.filter(tender => {
    const matchesSearch = tender.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          tender.id.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategory.value === 'All' || tender.category === selectedCategory.value
    const matchesStatus = selectedStatus.value === 'All' || tender.status === selectedStatus.value
    const matchesPriority = selectedPriority.value === 'All' || tender.priority === selectedPriority.value
    const matchesBudget = tender.budget <= priceRange.value
    const matchesLive = !liveBiddingOnly.value || tender.liveBidding
    
    return matchesSearch && matchesCategory && matchesStatus && matchesPriority && matchesBudget && matchesLive
  })

  // Sorting
  return result.sort((a, b) => {
    switch (sortBy.value) {
      case 'Deadline (Soonest)':
        return new Date(a.deadline) - new Date(b.deadline)
      case 'Deadline (Latest)':
        return new Date(b.deadline) - new Date(a.deadline)
      case 'Budget (Low to High)':
        return a.budget - b.budget
      case 'Budget (High to Low)':
        return b.budget - a.budget
      case 'Most Bids':
        return b.bids - a.bids
      default:
        // Recently Added (simulated by ID desc)
        return b.id.localeCompare(a.id)
    }
  })
})

const clearFilters = () => {
   selectedCategory.value = 'All'
   selectedStatus.value = 'All'
   selectedPriority.value = 'All'
   liveBiddingOnly.value = false
   searchQuery.value = ''
   priceRange.value = 20000000
   sortBy.value = 'Deadline (Soonest)'
}
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
     <!-- Page Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Active Tenders</h1>
        <p class="mt-1 text-sm text-gray-500">{{ filteredTenders.length }} active tenders • 1 closing soon</p>
      </div>
      <div class="mt-4 md:mt-0 flex gap-3">
         <button class="inline-flex items-center gap-2 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            <Bookmark class="h-4 w-4" /> Saved (0)
         </button>
         <button class="inline-flex items-center gap-2 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            <Bell class="h-4 w-4" /> Set Alert
         </button>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-x-8 gap-y-10 lg:grid-cols-4">
      <!-- Sidebar Filters -->
      <div class="hidden lg:block space-y-6">
         <div class="flex items-center justify-between">
            <h3 class="font-semibold text-gray-900 flex items-center gap-2"><Filter class="h-4 w-4" /> Filters</h3>
            <button @click.prevent="clearFilters" class="text-xs font-medium text-indigo-600 hover:text-indigo-500">Clear All</button>
         </div>

         <!-- Category Filter -->
         <div>
            <h4 class="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-3">Category</h4>
            <div class="space-y-2">
               <div v-for="cat in categories" :key="cat.name" class="flex items-center justify-between group cursor-pointer" @click="selectedCategory = cat.name">
                  <div class="flex items-center">
                     <span class="w-3 h-3 rounded-full border border-gray-300 mr-2 flex items-center justify-center transition-colors" :class="{ 'border-indigo-600 bg-indigo-600': selectedCategory === cat.name }">
                        <span v-if="selectedCategory === cat.name" class="w-1.5 h-1.5 rounded-full bg-white"></span>
                     </span>
                     <span class="text-sm text-gray-600 group-hover:text-gray-900" :class="{ 'font-medium text-gray-900': selectedCategory === cat.name }">{{ cat.name }}</span>
                  </div>
                  <span class="text-xs text-gray-400">({{ cat.count }})</span>
               </div>
            </div>
         </div>

         <div class="border-t border-gray-200 my-4"></div>

         <!-- Status Filter -->
         <div>
            <h4 class="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-3">Status</h4>
            <div class="flex flex-wrap gap-2">
               <button 
                  v-for="status in statuses" 
                  :key="status"
                  @click="selectedStatus = status"
                  class="rounded-full px-3 py-1 text-xs font-medium border transition-colors"
                  :class="selectedStatus === status ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'"
               >
                  {{ status }}
               </button>
            </div>
         </div>

         <div class="border-t border-gray-200 my-4"></div>

         <!-- Priority Filter -->
         <div>
            <h4 class="text-xs font-semibold text-gray-900 uppercase tracking-wider mb-3">Priority</h4>
            <div class="flex flex-wrap gap-2">
               <button 
                  v-for="priority in priorities" 
                  :key="priority"
                  @click="selectedPriority = priority"
                  class="rounded-md px-3 py-1 text-xs font-medium border transition-colors"
                  :class="selectedPriority === priority ? 'bg-indigo-50 text-indigo-700 border-indigo-200' : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'"
               >
                  {{ priority }}
               </button>
            </div>
         </div>

         <div class="border-t border-gray-200 my-4"></div>

         <!-- Budget Range -->
         <div>
            <div class="flex items-center justify-between mb-2">
               <h4 class="text-xs font-semibold text-gray-900 uppercase tracking-wider">Budget Range</h4>
               <span class="text-xs text-indigo-600 font-medium">₹{{ (priceRange / 100000).toFixed(1) }}L</span>
            </div>
            <input 
               type="range" 
               v-model="priceRange" 
               min="100000" 
               max="20000000" 
               step="100000"
               class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <div class="flex justify-between text-xs text-gray-400 mt-1">
               <span>₹1L</span>
               <span>₹2Cr</span>
            </div>
         </div>

         <div class="border-t border-gray-200 my-4"></div>

         <!-- Live Bidding Toggle -->
         <div class="flex items-center justify-between cursor-pointer" @click="liveBiddingOnly = !liveBiddingOnly">
            <span class="flex items-center gap-2 text-sm font-medium text-gray-900">
               <span class="flex h-2 w-2 rounded-full bg-orange-500"></span> Live Bidding Only
            </span>
            <div class="relative inline-flex h-5 w-9 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none" :class="liveBiddingOnly ? 'bg-indigo-600' : 'bg-gray-200'">
               <span class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="liveBiddingOnly ? 'translate-x-4' : 'translate-x-0'"></span>
            </div>
         </div>

      </div>

      <!-- Main Content -->
      <div class="lg:col-span-3">
         <!-- Search & Tools -->
         <div class="flex flex-col sm:flex-row gap-4 mb-6">
            <div class="relative flex-grow">
               <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                  <Search class="h-4 w-4 text-gray-400" />
               </div>
               <input 
                  v-model="searchQuery"
                  type="text" 
                  class="block w-full rounded-md border-0 py-2.5 pl-10 text-gray-900 ring-1 ring-inset ring-gray-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 shadow-sm"
                  placeholder="Search by tender ID, title, or keywords..." 
               />
            </div>
            <div class="flex items-center gap-2">
               <select v-model="sortBy" class="block w-full rounded-md border-0 py-2 pl-3 pr-8 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 shadow-sm">
                  <option>Deadline (Soonest)</option>
                  <option>Deadline (Latest)</option>
                  <option>Budget (High to Low)</option>
                  <option>Budget (Low to High)</option>
                  <option>Most Bids</option>
                  <option>Recently Added</option>
               </select>
               <div class="flex items-center rounded-md bg-white shadow-sm ring-1 ring-inset ring-gray-200">
                  <button 
                     @click="viewMode = 'grid'"
                     class="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-l-md border-r border-gray-200"
                     :class="viewMode === 'grid' ? 'bg-gray-50 text-indigo-600' : ''"
                  >
                     <LayoutGrid class="h-4 w-4" />
                  </button>
                  <button 
                     @click="viewMode = 'list'"
                     class="p-2 text-gray-500 hover:text-gray-900 hover:bg-gray-50 rounded-r-md"
                     :class="viewMode === 'list' ? 'bg-gray-50 text-indigo-600' : ''"
                  >
                     <List class="h-4 w-4" />
                  </button>
               </div>
            </div>
         </div>

         <!-- Active Filters Chips -->
         <div v-if="selectedCategory !== 'All' || selectedStatus !== 'All' || selectedPriority !== 'All' || priceRange < 20000000 || liveBiddingOnly" class="flex items-center gap-2 mb-6 text-sm flex-wrap">
            <span class="text-gray-500">Active filters:</span>
            <span v-if="selectedCategory !== 'All'" class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
               {{ selectedCategory }} <button @click="selectedCategory = 'All'" class="hover:text-indigo-900"><X class="h-3 w-3" /></button>
            </span>
             <span v-if="selectedStatus !== 'All'" class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
               {{ selectedStatus }} <button @click="selectedStatus = 'All'" class="hover:text-indigo-900"><X class="h-3 w-3" /></button>
            </span>
             <span v-if="selectedPriority !== 'All'" class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
               {{ selectedPriority }} <button @click="selectedPriority = 'All'" class="hover:text-indigo-900"><X class="h-3 w-3" /></button>
            </span>
             <span v-if="priceRange < 20000000" class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
               < ₹{{ (priceRange/100000).toFixed(1) }}L <button @click="priceRange = 20000000" class="hover:text-indigo-900"><X class="h-3 w-3" /></button>
            </span>
             <span v-if="liveBiddingOnly" class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
               Live Bidding <button @click="liveBiddingOnly = false" class="hover:text-indigo-900"><X class="h-3 w-3" /></button>
            </span>
            <button @click="clearFilters" class="text-xs text-gray-500 hover:text-gray-900 underline">Clear all</button>
         </div>

         <!-- Tender Grid -->
         <div class="mb-4">
            <p class="text-sm text-gray-500">Showing {{ filteredTenders.length }} of {{ tenders.length }} tenders</p>
         </div>

         <div :class="viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6' : 'flex flex-col gap-4'">
            <div v-if="isSessionExpired" class="col-span-full py-20 text-center bg-white rounded-lg border border-gray-200">
               <UserCircle class="mx-auto h-12 w-12 text-orange-500 mb-4" />
               <h3 class="text-lg font-bold text-gray-900">Session Expired</h3>
               <p class="mt-1 text-sm text-gray-500 mb-6 max-w-md mx-auto">Your session has timed out. Please reconnect to continue viewing active tenders.</p>
               <button @click="refetchSession" class="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                  Reconnect Session
               </button>
            </div>

            <div v-else-if="filteredTenders.length === 0" class="col-span-full py-20 text-center bg-white rounded-lg border border-gray-200 border-dashed">
               <div class="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-gray-100 mb-4">
                  <Search class="h-6 w-6 text-gray-400" />
               </div>
               <h3 class="mt-2 text-sm font-semibold text-gray-900">No tenders found</h3>
               <p class="mt-1 text-sm text-gray-500 mb-6">Try adjusting your search or filter criteria to find what you're looking for.</p>
               <button @click="clearFilters" class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                  Clear All Filters
               </button>
            </div>
            
            <TenderCard v-for="tender in filteredTenders" :key="tender.id" :tender="tender" :view-mode="viewMode" />
         </div>

      </div>
    </div>
  </div>
</template>
