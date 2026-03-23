<script setup>
import { ref, computed, onMounted } from 'vue'
import { Plus, Package, Truck, CheckCircle, AlertCircle, Calendar, Clock, MapPin, ExternalLink, Edit, X } from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const activeTab = ref('All Deliveries')
const tabs = ['All Deliveries', 'In Transit', 'Scheduled', 'Delivered', 'Delayed']
const isLoading = ref(true)

// --- Modal & Form State ---
const isUpdateModalOpen = ref(false)
const selectedDelivery = ref(null)
const updateForm = ref({
  expected_date: '',
  status: '',
  note: ''
})

// --- Data State ---
const counts = ref({ total: 0, in_transit: 0, delivered: 0, delayed: 0 })
const deliveries = ref([])

// Compute stats for top cards
const stats = computed(() => [
  { name: 'Total Orders', value: counts.value.total, icon: Package, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  { name: 'In Transit', value: counts.value.in_transit, icon: Truck, color: 'text-blue-600', bg: 'bg-blue-50' },
  { name: 'Delivered', value: counts.value.delivered, icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
  { name: 'Delayed', value: counts.value.delayed, icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-50' },
])

const fetchData = async () => {
  isLoading.value = true
  try {
    const response = await authStore.secureFetch('/api/method/supplier_portal.api.get_dashboard_counts')
    const result = await response.json()
    if (result.message) {
      counts.value = result.message.counts || { total: 0, in_transit: 0, delivered: 0, delayed: 0 }
      deliveries.value = result.message.deliveries || []
    }
  } catch (error) {
    console.error("Fetch error:", error)
  } finally {
    isLoading.value = false
  }
}

// Modal Actions
const openUpdateModal = (delivery) => {
  selectedDelivery.value = delivery
  updateForm.value = {
    expected_date: delivery.expected,
    status: delivery.status,
    note: ''
  }
  isUpdateModalOpen.value = true
}

const saveDeliveryUpdate = async () => {
  if (!selectedDelivery.value) return;

  try {
    const response = await authStore.secureFetch('/api/method/supplier_portal.api.update_delivery_status', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        receipt_id: selectedDelivery.value.id,
        status: updateForm.value.status,
        expected_date: updateForm.value.expected_date,
        note: updateForm.value.note
      })
    })

    if (response.ok) {
      const result = await response.json();
      console.log("Update Successful:", result);
      
      isUpdateModalOpen.value = false;
      await fetchData(); 
    } else {
      const errorData = await response.json();
      console.error("Server Error:", errorData);
    }
  } catch (error) {
    console.error("Network error during update:", error);
  }
}

const filteredDeliveries = computed(() => {
  if (activeTab.value === 'All Deliveries') return deliveries.value
  return deliveries.value.filter(d => d.status === activeTab.value)
})

const getStatusColor = (status) => {
   switch(status) {
      case 'In Transit': return 'bg-blue-50 text-blue-700 ring-blue-700/10'
      case 'Delayed': return 'bg-red-50 text-red-700 ring-red-600/20'
      case 'Delivered': return 'bg-green-50 text-green-700 ring-green-600/20'
      case 'Scheduled': return 'bg-gray-100 text-gray-700 ring-gray-600/10'
      default: return 'bg-gray-50 text-gray-600'
   }
}

onMounted(fetchData)
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Delivery Schedule</h1>
        <p class="mt-1 text-sm text-gray-500">Track shipments and manage delivery milestones</p>
      </div>
      <button class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 flex items-center gap-2">
         <Plus class="h-4 w-4" /> Schedule New Delivery
      </button>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-4 mb-8">
       <div v-for="stat in stats" :key="stat.name" class="rounded-lg bg-white px-4 py-5 shadow sm:p-6 border border-gray-100 flex items-center gap-4">
          <div :class="[stat.bg, 'rounded-md p-3']">
             <component :is="stat.icon" :class="[stat.color, 'h-6 w-6']" />
          </div>
          <div>
             <dt class="truncate text-sm font-medium text-gray-500">{{ stat.name }}</dt>
             <dd class="mt-1 text-2xl font-semibold tracking-tight text-gray-900">
                {{ isLoading ? '...' : stat.value }}
             </dd>
          </div>
       </div>
    </div>

    <div class="mb-6">
       <div class="flex flex-wrap gap-2">
          <button
             v-for="tab in tabs" :key="tab"
             @click="activeTab = tab"
             :class="[activeTab === tab ? 'bg-gray-100 text-gray-900 font-semibold' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50', 'rounded-md px-3 py-2 text-sm font-medium transition-colors']"
          >
             {{ tab }}
          </button>
       </div>
    </div>

    <div v-if="isLoading" class="flex flex-col items-center justify-center py-20">
       <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mb-4"></div>
       <p class="text-gray-500">Loading delivery data...</p>
    </div>

    <div v-else-if="filteredDeliveries.length > 0" class="space-y-6">
       <div v-for="delivery in filteredDeliveries" :key="delivery.id" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col lg:flex-row gap-8">
             <div class="flex-grow space-y-4">
                <div class="flex items-start justify-between">
                   <div>
                      <div class="flex items-center gap-3">
                         <h3 class="text-base font-semibold text-gray-900">{{ delivery.title }}</h3>
                         <span :class="['inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset', getStatusColor(delivery.status)]">
                            <component :is="delivery.status === 'Delayed' ? AlertCircle : delivery.status === 'Delivered' ? CheckCircle : Truck" class="w-3 h-3 mr-1" />
                            {{ delivery.status }}
                         </span>
                      </div>
                      <p class="text-sm text-gray-500 mt-1">{{ delivery.po }} • {{ delivery.quantity }}</p>
                   </div>
                   <button @click="openUpdateModal(delivery)" class="inline-flex items-center gap-1 rounded bg-white px-2.5 py-1.5 text-xs font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                      <Edit class="h-3 w-3" /> Update
                   </button>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-y-4 gap-x-8 text-sm">
                   <div class="flex items-center gap-2 text-gray-600">
                      <Calendar class="h-4 w-4 text-gray-400" />
                      <span class="font-medium">Scheduled:</span> {{ delivery.scheduled }}
                   </div>
                   <div class="flex items-center gap-2 text-gray-600">
                      <Clock class="h-4 w-4 text-gray-400" />
                      <span class="font-medium">Expected:</span> 
                      <span :class="delivery.status === 'Delayed' ? 'text-red-600 font-bold' : ''">{{ delivery.expected }}</span>
                   </div>
                   <div class="flex items-center gap-2 text-gray-600">
                      <ExternalLink class="h-4 w-4 text-blue-500" />
                      <span class="font-medium">Tracking:</span> <a href="#" class="text-blue-600 hover:underline">{{ delivery.tracking || '-' }}</a>
                   </div>
                   <div class="flex items-center gap-2 text-gray-600">
                      <MapPin class="h-4 w-4 text-gray-400" />
                       <span class="truncate">{{ delivery.location || 'Location Pending' }}</span>
                   </div>
                </div>
             </div>

             <div class="w-full lg:w-80 flex-shrink-0 border-t lg:border-t-0 lg:border-l border-gray-100 pt-6 lg:pt-0 lg:pl-6">
                <div class="flex items-center justify-between text-xs font-semibold text-gray-900 mb-2">
                   <span>Progress</span>
                   <span>{{ delivery.progress }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2 mb-6">
                   <div class="bg-blue-600 h-2 rounded-full transition-all duration-500" :style="`width: ${delivery.progress}%`"></div>
                </div>
                <div class="relative space-y-4">
                   <div class="absolute left-1.5 top-1.5 bottom-1.5 w-0.5 bg-gray-200 z-0"></div>
                   <div v-for="(m, i) in delivery.milestones" :key="i" class="relative z-10 flex gap-3 text-xs">
                       <div class="h-3 w-3 rounded-full border-2 flex-shrink-0 mt-0.5 bg-white" :class="m.completed ? 'border-green-500 bg-green-500' : 'border-gray-300'"></div>
                       <div class="flex justify-between w-full">
                          <span :class="m.completed ? 'text-gray-900 font-medium' : 'text-gray-500'">{{ m.name }}</span>
                          <span v-if="m.date" class="text-gray-400">{{ m.date }}</span>
                       </div>
                   </div>
                </div>
             </div>
          </div>
       </div>
    </div>

    <div v-if="isUpdateModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl animate-in fade-in zoom-in duration-200">
        <div class="flex items-center justify-between mb-4 border-b pb-3">
          <h3 class="text-lg font-semibold text-gray-900">Update Delivery Details</h3>
          <button @click="isUpdateModalOpen = false" class="text-gray-400 hover:text-gray-600"><X class="h-5 w-5"/></button>
        </div>
        
        <p class="text-xs text-gray-500 mb-4 bg-gray-50 p-2 rounded">Updating for: <span class="font-bold">{{ selectedDelivery?.po }}</span></p>

        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">Expected Delivery Date</label>
            <input type="date" v-model="updateForm.expected_date" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">Status</label>
            <select v-model="updateForm.status" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
              <option v-for="t in tabs.filter(x => x !== 'All Deliveries')" :key="t">{{ t }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">Update Note</label>
            <textarea v-model="updateForm.note" rows="3" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" placeholder="Reason for change..."></textarea>
          </div>
        </div>

        <div class="mt-6 flex justify-end gap-3">
          <button @click="isUpdateModalOpen = false" class="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">Cancel</button>
          <button @click="saveDeliveryUpdate" class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 shadow-sm">Save Changes</button>
        </div>
      </div>
    </div>
  </div>
</template>