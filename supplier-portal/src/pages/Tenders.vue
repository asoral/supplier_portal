<script setup>
import { ref, computed } from 'vue'
import { Search, Filter, LayoutGrid, List, X, Bell, Bookmark } from 'lucide-vue-next'
import TenderCard from '../components/TenderCard.vue'

const searchQuery = ref('')
const viewMode = ref('grid') // 'grid' | 'list'
const priceRange = ref(5000000)

// Filters
const selectedCategory = ref('All')
const selectedStatus = ref('All')
const selectedPriority = ref('All')
const liveBiddingOnly = ref(false)

const categories = [
  { name: 'All', count: 6 },
  { name: 'Raw Materials', count: 2 },
  { name: 'Machinery', count: 1 },
  { name: 'Consumables', count: 1 },
  { name: 'Electrical', count: 1 },
  { name: 'Safety', count: 1 },
  { name: 'Packaging', count: 0 },
  { name: 'Chemicals', count: 0 },
]

const statuses = ['All', 'Active', 'Closing Soon', 'Closed']
const priorities = ['All', 'Urgent', 'High', 'Normal', 'Low']

// Mock Data
const tenders = ref([
  {
    id: 'TND-2024-001',
    title: 'Industrial Steel Plates - Grade A',
    description: 'High-quality steel plates for manufacturing heavy machinery components.',
    category: 'Raw Materials',
    status: 'Active',
    priority: 'High',
    liveBidding: true,
    budget: 2500000,
    deadline: '15 Feb 2024',
    location: 'Pune, MH',
    bids: 12
  },
  {
    id: 'TND-2024-003',
    title: 'Safety Equipment Annual Supply',
    description: 'Annual rate contract for safety equipment and PPE for 500+ workforce.',
    category: 'Safety',
    status: 'Closing Soon',
    priority: 'Urgent',
    liveBidding: false,
    budget: 850000,
    deadline: '10 Feb 2024',
    location: 'Mumbai, MH',
    bids: 8
  },
  {
    id: 'TND-2024-004',
    title: 'Electrical Control Panels',
    description: 'Custom electrical control panels for production line automation upgrade.',
    category: 'Electrical',
    status: 'Active',
    priority: 'Normal',
    liveBidding: false,
    budget: 1200000,
    deadline: '20 Feb 2024',
    location: 'Delhi, NCR',
    bids: 5
  },
  {
    id: 'TND-2024-002',
    title: 'CNC Machining Center',
    description: '5-axis CNC vertical machining center for precision components manufacturing.',
    category: 'Machinery',
    status: 'Active',
    priority: 'High',
    liveBidding: true,
    budget: 4500000,
    deadline: '25 Jan 2024',
    location: 'Bangalore, KA',
    bids: 15
  },
   {
    id: 'TND-2024-005',
    title: 'Industrial Lubricants Package',
    description: 'Annual contract for supply of industrial lubricants including hydraulic oils, gear oils.',
    category: 'Consumables',
    status: 'Active',
    priority: 'Normal',
    liveBidding: false,
    budget: 320000,
    deadline: '15 Mar 2024',
    location: 'Chennai, TN',
    bids: 3
  }
])

const filteredTenders = computed(() => {
  return tenders.value.filter(tender => {
    const matchesSearch = tender.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          tender.id.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategory.value === 'All' || tender.category === selectedCategory.value
    const matchesStatus = selectedStatus.value === 'All' || tender.status === selectedStatus.value
    // Budget filter logic could be added here
    
    return matchesSearch && matchesCategory && matchesStatus
  })
})

const clearFilters = () => {
   selectedCategory.value = 'All'
   selectedStatus.value = 'All'
   selectedPriority.value = 'All'
   liveBiddingOnly.value = false
   searchQuery.value = ''
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
            <button @click="clearFilters" class="text-xs font-medium text-indigo-600 hover:text-indigo-500">Clear All</button>
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
               <select class="block w-full rounded-md border-0 py-2 pl-3 pr-8 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 shadow-sm">
                  <option>Deadline: Soonest</option>
                  <option>Value: Low to High</option>
                  <option>Value: High to Low</option>
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
         <div v-if="selectedCategory !== 'All' || selectedStatus !== 'All'" class="flex items-center gap-2 mb-6 text-sm">
            <span class="text-gray-500">Active filters:</span>
            <span v-if="selectedCategory !== 'All'" class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
               {{ selectedCategory }} <button @click="selectedCategory = 'All'" class="hover:text-indigo-900"><X class="h-3 w-3" /></button>
            </span>
             <span v-if="selectedStatus !== 'All'" class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
               {{ selectedStatus }} <button @click="selectedStatus = 'All'" class="hover:text-indigo-900"><X class="h-3 w-3" /></button>
            </span>
            <button @click="clearFilters" class="text-xs text-gray-500 hover:text-gray-900 underline">Clear all</button>
         </div>

         <!-- Tender Grid -->
         <div class="mb-4">
            <p class="text-sm text-gray-500">Showing {{ filteredTenders.length }} of {{ tenders.length }} tenders</p>
         </div>

         <div :class="viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6' : 'flex flex-col gap-4'">
            <div v-if="filteredTenders.length === 0" class="col-span-full py-20 text-center bg-white rounded-lg border border-gray-200 border-dashed">
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
