<script setup>
import { ref, computed } from 'vue'
import { FileText, Download, Filter, Search } from 'lucide-vue-next'

const tabs = ['All Contracts', 'Active', 'Pending', 'Completed']
const activeTab = ref('All Contracts')
const searchQuery = ref('')

const contracts = ref([
  {
    id: 'PO_7845_2023',
    title: 'Safety Equipment Annual Supply',
    date: '3 Feb 2023',
    value: 750000,
    deliveryDate: '31 Dec 2024',
    deliveredItems: 3,
    totalItems: 4,
    status: 'Active',
    progress: 75
  },
  {
    id: 'PO_1524_2023',
    title: 'Office Furniture Supply',
    date: '28 Nov 2023',
    value: 125000,
    deliveryDate: '15 Dec 2023',
    deliveredItems: 3,
    totalItems: 3,
    status: 'Completed',
    progress: 100
  },
  {
    id: 'PO_8921_2024',
    title: 'Industrial Steel Plates',
    date: '20 Feb 2024',
    value: 1285000,
    deliveryDate: '30 Mar 2024',
    deliveredItems: 0,
    totalItems: 1,
    status: 'Pending',
    progress: 0
  }
])

const filteredContracts = computed(() => {
  return contracts.value.filter(contract => {
    const matchesTab = activeTab.value === 'All Contracts' || contract.status === activeTab.value
    const matchesSearch = contract.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          contract.id.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesTab && matchesSearch
  })
})

const activeStats = computed(() => {
   const activeCount = contracts.value.filter(c => c.status === 'Active').length
   const totalValue = contracts.value.reduce((acc, curr) => acc + curr.value, 0)
   return { count: activeCount, totalValue }
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(value)
}
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Contracts & Orders</h1>
        <p class="mt-1 text-sm text-gray-500">Manage your purchase orders and contracts.</p>
      </div>
      <div class="mt-4 md:mt-0 flex gap-8">
         <div class="text-right">
            <span class="block text-xs font-medium text-gray-500 uppercase tracking-wider">Active Contracts</span>
            <span class="block text-2xl font-bold text-orange-600">{{ activeStats.count }}</span>
         </div>
         <div class="text-right">
            <span class="block text-xs font-medium text-gray-500 uppercase tracking-wider">Total Value</span>
            <span class="block text-2xl font-bold text-green-600">{{ formatCurrency(activeStats.totalValue) }}</span>
         </div>
      </div>
    </div>

    <!-- Controls -->
    <div class="flex flex-col sm:flex-row gap-4 mb-6">
       <div class="relative flex-grow">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
             <Search class="h-4 w-4 text-gray-400" />
          </div>
          <input 
            v-model="searchQuery"
            type="text" 
            class="block w-full rounded-md border-0 py-2 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 shadow-sm"
            placeholder="Search by PO number or tender title..." 
          />
       </div>
       <button class="inline-flex items-center justify-center gap-2 rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
          <Filter class="h-4 w-4 text-gray-500" />
          Filters
       </button>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-8" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          @click="activeTab = tab"
          :class="[
            activeTab === tab
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium'
          ]"
        >
          {{ tab }}
        </button>
      </nav>
    </div>

    <!-- List -->
    <div class="space-y-4">
       <div v-for="contract in filteredContracts" :key="contract.id" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
             <div class="flex gap-4">
                <div class="h-10 w-10 flex-shrink-0 rounded-lg bg-indigo-50 flex items-center justify-center">
                   <FileText class="h-5 w-5 text-indigo-600" />
                </div>
                <div>
                   <h3 class="text-base font-semibold text-gray-900">{{ contract.title }}</h3>
                   <div class="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1 text-xs text-gray-500">
                      <span class="font-mono">{{ contract.id }}</span>
                      <span>&bull;</span>
                      <span>{{ contract.date }}</span>
                   </div>
                   
                   <div class="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm">
                      <div class="flex items-center gap-1 font-medium text-gray-900">
                         <span class="text-gray-500 font-normal">₹</span>
                         {{ contract.value.toLocaleString('en-IN') }}
                      </div>
                      <div class="flex items-center gap-1 text-gray-500">
                         <span class="font-normal">Delivery:</span>
                         <span class="text-gray-900">{{ contract.deliveryDate }}</span>
                      </div>
                       <div class="flex items-center gap-1 text-gray-500">
                         <span class="font-normal">Items:</span>
                         <span class="text-gray-900">{{ contract.deliveredItems }}/{{ contract.totalItems }} delivered</span>
                      </div>
                   </div>
                </div>
             </div>

             <div class="flex flex-row sm:flex-col items-center sm:items-end gap-3 sm:gap-4">
                <span 
                  class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset"
                  :class="{
                     'bg-blue-50 text-blue-700 ring-blue-700/10': contract.status === 'Active',
                     'bg-green-50 text-green-700 ring-green-600/20': contract.status === 'Completed',
                     'bg-orange-50 text-orange-700 ring-orange-600/20': contract.status === 'Pending',
                  }"
                >
                   {{ contract.status }}
                </span>
                
                <div class="flex items-center gap-2">
                   <button class="rounded-md bg-white px-3 py-1.5 text-xs font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 text-center min-w-[70px]">View</button>
                    <button class="p-1.5 text-gray-400 hover:text-gray-600">
                        <Download class="h-4 w-4" />
                    </button>
                </div>
             </div>
          </div>

          <!-- Progress Bar -->
          <div class="mt-6" v-if="contract.status !== 'Completed'">
             <div class="flex justify-between text-xs mb-1">
                <span class="text-gray-500">Delivery Progress</span>
                <span class="font-medium text-gray-900">{{ contract.progress }}%</span>
             </div>
             <div class="w-full bg-gray-200 rounded-full h-1.5">
                <div class="bg-indigo-600 h-1.5 rounded-full transition-all duration-500" :style="{ width: contract.progress + '%' }"></div>
             </div>
          </div>
       </div>
    </div>
  </div>
</template>
