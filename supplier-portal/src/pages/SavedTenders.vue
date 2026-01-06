<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Bookmark, Clock, Bell, ArrowRight, Eye } from 'lucide-vue-next'

const router = useRouter()

const stats = [
  { name: 'Total Saved', value: '4', icon: Bookmark, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  { name: 'Active', value: '3', icon: Clock, color: 'text-green-600', bg: 'bg-green-50' },
  { name: 'Closing Soon', value: '1', icon: Clock, color: 'text-orange-600', bg: 'bg-orange-50' },
  { name: 'Alerts On', value: '2', icon: Bell, color: 'text-blue-600', bg: 'bg-blue-50' },
]

const tenders = ref([
 {
    id: 'TND-2024-001',
    title: 'Industrial Steel Plates - Grade A',
    category: 'Raw Materials',
    value: 2500000,
    deadline: '15 Feb 2024',
    savedOn: '20 Jan 2024',
    status: 'Active',
    alerts: true,
    deadlineStatus: 'Deadline passed', // Mocking based on image, though date is future
    bids: 12
  },
  {
    id: 'TND-2024-003',
    title: 'Safety Equipment Annual Supply',
    category: 'Safety Equipment',
    value: 850000,
    deadline: '10 Feb 2024',
    savedOn: '18 Jan 2024',
    status: 'Closing Soon',
    alerts: true,
    deadlineStatus: 'Deadline passed',
    bids: 8
  },
  {
    id: 'TND-2024-004',
    title: 'Electrical Control Panels',
    category: 'Electrical',
    value: 1200000,
    deadline: '20 Feb 2024',
    savedOn: '22 Jan 2024',
    status: 'Active',
    alerts: false,
    deadlineStatus: 'Deadline passed',
    bids: 5
  },
  {
    id: 'TND-2024-002',
    title: 'CNC Machining Center',
    category: 'Machinery',
    value: 4500000,
    deadline: '25 Jan 2024',
    savedOn: '10 Jan 2024',
    status: 'Closed',
    alerts: false,
    deadlineStatus: '',
    bids: 15
  }
])

const activeTab = ref('All')
const tabs = ['All', 'Active', 'Closed']
const searchQuery = ref('')

const filteredTenders = computed(() => {
  return tenders.value.filter(t => {
     const matchesSearch = t.title.toLowerCase().includes(searchQuery.value.toLowerCase())
     const matchesTab = activeTab.value === 'All' || 
                        (activeTab.value === 'Active' && t.status !== 'Closed') ||
                        (activeTab.value === 'Closed' && t.status === 'Closed')
     return matchesSearch && matchesTab
  })
})
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
     <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900 flex items-center gap-2">
           <Bookmark class="h-8 w-8 text-indigo-600 fill-current" />
           Saved Tenders
        </h1>
        <p class="mt-1 text-sm text-gray-500">4 tenders saved • 3 active</p>
      </div>
      <button class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 flex items-center gap-2">
         Browse More Tenders <ArrowRight class="h-4 w-4" />
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-4 mb-8">
       <div v-for="stat in stats" :key="stat.name" class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:p-6 border border-gray-100 flex items-center gap-4">
          <div :class="[stat.bg, 'rounded-md p-3']">
             <component :is="stat.icon" :class="[stat.color, 'h-6 w-6']" />
          </div>
          <div>
             <dt class="truncate text-sm font-medium text-gray-500">{{ stat.name }}</dt>
             <dd class="mt-1 text-2xl font-semibold tracking-tight text-gray-900">{{ stat.value }}</dd>
          </div>
       </div>
    </div>

    <!-- Controls -->
    <div class="flex flex-col sm:flex-row gap-4 mb-6 items-center">
       <div class="relative flex-grow w-full sm:w-auto">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
             <Search class="h-4 w-4 text-gray-400" />
          </div>
          <input 
            v-model="searchQuery"
            type="text" 
            class="block w-full rounded-md border-0 py-2 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
            placeholder="Search saved tenders..." 
          />
       </div>
       <div class="flex space-x-2 bg-gray-100 p-1 rounded-lg">
          <button
             v-for="tab in tabs"
             :key="tab"
             @click="activeTab = tab"
             :class="[
                activeTab === tab ? 'bg-white text-gray-900 shadow' : 'text-gray-500 hover:text-gray-900',
                'rounded-md px-3 py-1.5 text-sm font-medium transition-all'
             ]"
          >
             {{ tab }}
          </button>
       </div>
    </div>

    <!-- List -->
    <div class="space-y-4">
       <div v-for="tender in filteredTenders" :key="tender.id" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex flex-col sm:flex-row justify-between gap-4">
             <div class="flex-grow">
                <div class="flex items-center gap-2 mb-1">
                   <h3 class="text-base font-semibold text-gray-900">{{ tender.title }}</h3>
                   <span 
                      class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset"
                      :class="tender.status === 'Active' ? 'bg-blue-50 text-blue-700 ring-blue-700/10' : 
                              tender.status === 'Closing Soon' ? 'bg-orange-50 text-orange-700 ring-orange-600/20' : 
                              'bg-gray-50 text-gray-600 ring-gray-500/10'"
                   >
                      {{ tender.status }}
                   </span>
                   <span v-if="tender.alerts" class="inline-flex items-center gap-1 rounded-full bg-gray-50 px-2 py-0.5 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">
                      <Bell class="h-3 w-3" /> Alert
                   </span>
                </div>
                <p class="text-sm text-gray-500 mb-3">{{ tender.id }} • {{ tender.category }}</p>
                
                 <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-500">
                    <span class="flex items-center gap-1">
                       <span class="font-medium text-gray-900">₹{{ tender.value.toLocaleString() }}</span>
                    </span>
                    <span class="flex items-center gap-1">
                       <Clock class="h-4 w-4" /> {{ tender.deadline }}
                    </span>
                     <span v-if="tender.deadlineStatus" class="text-red-500 text-xs flex items-center px-2 py-0.5 bg-red-50 rounded">
                        {{ tender.deadlineStatus }}
                     </span>
                     <span>{{ tender.bids }} bids</span>
                 </div>
                 <p class="text-xs text-gray-400 mt-3">Saved on {{ tender.savedOn }}</p>
             </div>

             <div class="flex items-center gap-3 self-start sm:self-center">
                 <button class="p-2 text-gray-400 hover:text-indigo-600 bg-gray-50 rounded-md hover:bg-gray-100">
                   <Bell class="h-4 w-4" :class="{ 'text-indigo-600 fill-current': tender.alerts }" />
                 </button>
                 <button class="p-2 text-red-400 hover:text-red-600 bg-gray-50 rounded-md hover:bg-red-50">
                    <Bookmark class="h-4 w-4 fill-current" />
                 </button>
                 <button @click="$router.push('/tenders/' + tender.id)" class="inline-flex items-center gap-1 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    <Eye class="h-4 w-4" /> View
                 </button>
                 <button v-if="tender.status !== 'Closed'" @click="$router.push('/tenders/' + tender.id)" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                    Place Bid
                 </button>
             </div>
          </div>
       </div>
    </div>

  </div>
</template>
