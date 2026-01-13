<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Bookmark, Clock, Bell, ArrowRight, Eye, Trash2 } from 'lucide-vue-next'
import { createToast } from 'mosha-vue-toastify'
import 'mosha-vue-toastify/dist/style.css'

const router = useRouter()

const stats = ref([
  { name: 'Total Saved', value: '0', icon: Bookmark, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  { name: 'Active', value: '0', icon: Clock, color: 'text-green-600', bg: 'bg-green-50' },
  { name: 'Closing Soon', value: '0', icon: Clock, color: 'text-orange-600', bg: 'bg-orange-50' },
  { name: 'Alerts On', value: '0', icon: Bell, color: 'text-blue-600', bg: 'bg-blue-50' },
])

const tenders = ref([])
const activeTab = ref('All')
const tabs = ['All', 'Active', 'Closed']
const searchQuery = ref('')
const isLoading = ref(true)

const fetchSavedTenders = async () => {
    isLoading.value = true
    try {
        const response = await fetch('/api/method/supplier_portal.supplier_portal.api.get_saved_tenders')
        const result = await response.json()
        if (result.message) {
            tenders.value = result.message
            updateStats()
        }
    } catch (error) {
        console.error('Error fetching saved tenders:', error)
        createToast('Failed to load saved tenders', { type: 'danger' })
    } finally {
        isLoading.value = false
    }
}

const updateStats = () => {
    const total = tenders.value.length
    const active = tenders.value.filter(t => t.status !== 'Closed').length
    const closing = tenders.value.filter(t => t.deadlineStatus === 'Deadline passed' || t.status === 'Closing Soon').length // Logic can be refined
    
    stats.value[0].value = total.toString()
    stats.value[1].value = active.toString()
    stats.value[2].value = closing.toString()
    // alerts stat mocked for now or need backend support
    stats.value[3].value = tenders.value.filter(t => t.alerts).length.toString()
}

const deleteTender = async (savedId) => {
    if (!confirm('Are you sure you want to remove this tender from your saved list?')) return

    try {
        const response = await fetch('/api/method/supplier_portal.supplier_portal.api.delete_saved_tender', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': window.csrf_token || ''
            },
            body: JSON.stringify({ saved_id: savedId })
        })
        const result = await response.json()
        
        if (result.message && result.message.status === 'success') {
            createToast('Tender removed from saved list', { type: 'success' })
            // Remove locally
            tenders.value = tenders.value.filter(t => t.saved_id !== savedId)
            updateStats()
        } else {
            createToast(result.message?.message || 'Failed to remove tender', { type: 'danger' })
        }
    } catch (error) {
        console.error('Error deleting saved tender:', error)
        createToast('An error occurred', { type: 'danger' })
    }
}

onMounted(() => {
    fetchSavedTenders()
})

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
        <p class="mt-1 text-sm text-gray-500">{{ stats[0].value }} tenders saved • {{ stats[1].value }} active</p>
      </div>
      <button class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 flex items-center gap-2" @click="$router.push('/tenders')">
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
    <div v-if="isLoading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-4 text-gray-500">Loading saved tenders...</p>
    </div>

    <div v-else-if="filteredTenders.length === 0" class="text-center py-12 bg-white rounded-lg border border-gray-200">
        <Bookmark class="mx-auto h-12 w-12 text-gray-300" />
        <h3 class="mt-2 text-sm font-semibold text-gray-900">No saved tenders</h3>
        <p class="mt-1 text-sm text-gray-500">You haven't saved any tenders yet.</p>
        <div class="mt-6">
            <button @click="$router.push('/tenders')" class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                <Search class="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
                Find Tenders
            </button>
        </div>
    </div>

    <div v-else class="space-y-4">
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
                 <button @click="deleteTender(tender.saved_id)" class="p-2 text-red-400 hover:text-red-600 bg-gray-50 rounded-md hover:bg-red-50" title="Remove from Saved">
                    <Trash2 class="h-4 w-4" />
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
