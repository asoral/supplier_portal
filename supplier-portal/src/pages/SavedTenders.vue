It looks like the blank page in your Saved Tenders view is likely caused by a JavaScript error in the template or script that is preventing the component from rendering. Because we added logic to handle the saved_id and specific data mapping, if the API returns data in a slightly different format than expected, the whole page can crash.

Let's fix the SavedTenders.vue file to be more "bulletproof" so it handles empty data or different naming conventions without breaking the UI.

The Corrected SavedTenders.vue
Replace your entire script and the top part of your template with this version. I have added extra safety checks (Optional Chaining ?.) to ensure that even if one tender has missing data, the rest of the page still loads.

Code snippet

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search, Bookmark, Clock, Bell, ArrowRight, Eye, Trash2 } from 'lucide-vue-next'
import { createToast } from 'mosha-vue-toastify'
import 'mosha-vue-toastify/dist/style.css'

const router = useRouter()
const tenders = ref([])
const activeTab = ref('All')
const tabs = ['All', 'Active', 'Closed']
const searchQuery = ref('')
const isLoading = ref(true)

// Stats configuration
const stats = ref([
  { name: 'Total Saved', value: '0', icon: Bookmark, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  { name: 'Active', value: '0', icon: Clock, color: 'text-green-600', bg: 'bg-green-50' },
  { name: 'Closing Soon', value: '0', icon: Clock, color: 'text-orange-600', bg: 'bg-orange-50' },
  { name: 'Alerts On', value: '0', icon: Bell, color: 'text-blue-600', bg: 'bg-blue-50' },
])

const updateStats = () => {
  if (!tenders.value) return
  stats.value[0].value = tenders.value.length.toString()
  stats.value[1].value = tenders.value.filter(t => t.status === 'Active').length.toString()
  stats.value[2].value = tenders.value.filter(t => t.status === 'Active').length.toString()
  stats.value[3].value = "0" 
}

const fetchSavedTenders = async () => {
    isLoading.value = true;
    try {
        const response = await fetch('/api/method/supplier_portal.api.get_saved_tenders', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': window.csrf_token || '',
            }
        });
        
        const result = await response.json();
        // Safety check: ensure result.message exists and is an array
        const rawData = result.message || [];
        
        tenders.value = rawData.map(item => ({
            // We use item.name if saved_id isn't provided by your custom API
            saved_id: item.saved_id || item.name, 
            id: item.id || item.rfq || 'N/A',
            title: item.title || 'Untitled Tender',
            status: item.status || 'Active',
            category: item.category || 'General',
            value: item.amount || item.total_budget || 0,
            deadline: item.deadline || 'N/A',
            savedOn: item.saved_on ? new Date(item.saved_on).toLocaleDateString('en-GB') : 'Recently'
        }));

        updateStats(); 
    } catch (error) {
        console.error('Fetch failed:', error);
    } finally {
        isLoading.value = false; 
    }
}

const deleteTender = async (savedId) => {
    if (!savedId) return
    if (!confirm('Remove this tender from your saved list?')) return

    try {
        const response = await fetch('/api/method/frappe.client.delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Frappe-CSRF-Token': window.csrf_token || ''
            },
            body: JSON.stringify({ 
                doctype: 'Saved RFQ',
                name: savedId 
            })
        })
        
        if(response.ok) {
            createToast('Tender removed', { type: 'success' })
            await fetchSavedTenders()
        }
    } catch (error) {
        console.error('Delete error:', error)
    }
}

const filteredTenders = computed(() => {
  const query = (searchQuery.value || "").toLowerCase();
  return (tenders.value || []).filter(t => {
     const title = (t.title || "").toLowerCase();
     const matchesSearch = title.includes(query) || t.id.toLowerCase().includes(query);
     const matchesTab = activeTab.value === 'All' || t.status === activeTab.value;
     return matchesSearch && matchesTab;
  })
})

onMounted(() => {
    fetchSavedTenders()
})
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900 flex items-center gap-2">
           <Bookmark class="h-8 w-8 text-indigo-600 fill-indigo-600" />
           Saved Tenders
        </h1>
        <p class="mt-1 text-sm text-gray-500">
          {{ stats[0].value }} tenders saved • {{ stats[1].value }} active
        </p>
      </div>
      <button 
        class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 flex items-center gap-2 transition-colors" 
        @click="router.push('/tenders')"
      >
         Browse More Tenders <ArrowRight class="h-4 w-4" />
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-4 mb-8">
       <div v-for="stat in stats" :key="stat.name" class="overflow-hidden rounded-lg bg-white px-4 py-5 shadow-sm border border-gray-100 flex items-center gap-4">
          <div :class="[stat.bg, 'rounded-md p-3']">
             <component :is="stat.icon" :class="[stat.color, 'h-6 w-6']" />
          </div>
          <div>
             <dt class="truncate text-sm font-medium text-gray-500">{{ stat.name }}</dt>
             <dd class="mt-1 text-2xl font-semibold tracking-tight text-gray-900">{{ stat.value }}</dd>
          </div>
       </div>
    </div>

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

    <div v-if="isLoading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
        <p class="mt-4 text-gray-500 font-medium">Loading saved tenders...</p>
    </div>

    <div v-else-if="filteredTenders.length === 0" class="text-center py-12 bg-white rounded-xl border-2 border-dashed border-gray-200">
        <Bookmark class="mx-auto h-12 w-12 text-gray-300" />
        <h3 class="mt-2 text-sm font-semibold text-gray-900">No saved tenders found</h3>
        <p class="mt-1 text-sm text-gray-500">Try adjusting your search or browse new tenders.</p>
        <div class="mt-6">
            <button @click="router.push('/tenders')" class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                <Search class="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
                Find Tenders
            </button>
        </div>
    </div>

    <div v-else class="space-y-4">
       <div v-for="tender in filteredTenders" :key="tender.id" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-all">
          <div class="flex flex-col sm:flex-row justify-between gap-4">
             <div class="flex-grow">
                <div class="flex items-center gap-2 mb-1">
                   <h3 class="text-base font-semibold text-gray-900 hover:text-indigo-600 cursor-pointer" @click="router.push('/tenders/' + tender.id)">
                      {{ tender.title }}
                   </h3>
                   <span 
                      class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset"
                      :class="tender.status === 'Active' ? 'bg-blue-50 text-blue-700 ring-blue-700/10' : 
                              tender.status === 'Closing Soon' ? 'bg-orange-50 text-orange-700 ring-orange-600/20' : 
                              'bg-gray-50 text-gray-600 ring-gray-500/10'"
                   >
                      {{ tender.status }}
                   </span>
                </div>
                <p class="text-sm text-gray-500 mb-3">{{ tender.id }} • {{ tender.category }}</p>
                
                 <div class="flex flex-wrap gap-x-6 gap-y-2 text-sm text-gray-600">
                    <span class="flex items-center gap-1 font-semibold text-gray-900">
                       ₹{{ tender.value?.toLocaleString('en-IN') || '0' }}
                    </span>
                    <span class="flex items-center gap-1">
                       <Clock class="h-4 w-4 text-gray-400" /> {{ tender.deadline }}
                    </span>
                     <span v-if="tender.deadlineStatus" class="text-red-600 text-xs font-medium flex items-center px-2 py-0.5 bg-red-50 rounded">
                        {{ tender.deadlineStatus }}
                     </span>
                 </div>
                 <p class="text-xs text-gray-400 mt-3 font-medium">Saved on {{ tender.savedOn }}</p>
             </div>

             <div class="flex items-center gap-3 self-start sm:self-center">
                 <div class="p-2 bg-indigo-50 rounded-md" title="Tender is saved">
                    <Bookmark class="h-4 w-4 text-indigo-600 fill-indigo-600" />
                 </div>

                 <button @click="deleteTender(tender.saved_id)" class="p-2 text-gray-400 hover:text-red-600 bg-gray-50 rounded-md hover:bg-red-50 transition-colors" title="Remove from Saved">
                    <Trash2 class="h-4 w-4" />
                 </button>

                 <button @click="router.push('/tenders/' + tender.id)" class="inline-flex items-center gap-1 rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    <Eye class="h-4 w-4" /> View Details
                 </button>

                 <button v-if="tender.status !== 'Closed'" @click="router.push('/tenders/' + tender.id)" class="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors">
                    Place Bid
                 </button>
             </div>
          </div>
       </div>
    </div>
  </div>
</template>