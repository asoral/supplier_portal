<script setup>
import { ref, computed } from 'vue'
import { Plus, Package, Truck, CheckCircle, AlertCircle, Calendar, Clock, MapPin, ExternalLink, Edit } from 'lucide-vue-next'

const activeTab = ref('All Deliveries')
const tabs = ['All Deliveries', 'In Transit', 'Scheduled', 'Delivered', 'Delayed']

const stats = [
  { name: 'Total Orders', value: '4', icon: Package, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  { name: 'In Transit', value: '1', icon: Truck, color: 'text-blue-600', bg: 'bg-blue-50' },
  { name: 'Delivered', value: '1', icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
  { name: 'Delayed', value: '1', icon: AlertCircle, color: 'text-red-600', bg: 'bg-red-50' },
]

const deliveries = ref([
  {
    id: 1,
    title: 'Steel Reinforcement Bars',
    po: 'PO-2024-0156',
    quantity: '500 tons',
    status: 'In Transit',
    scheduled: '2024-02-15',
    expected: '2024-02-15',
    location: 'Site A - Industrial Zone, Block 5',
    tracking: 'TRK-789456123',
    progress: 83,
    alert: null,
    milestones: [
        { name: 'Order Confirmed', date: '2024-02-01', completed: true },
        { name: 'Production Started', date: '2024-02-05', completed: true },
        { name: 'Quality Check', date: '2024-02-10', completed: true },
        { name: 'Dispatched', date: '2024-02-12', completed: true },
        { name: 'In Transit', date: '2024-02-12', completed: true },
        { name: 'Delivered', date: '', completed: false },
    ]
  },
  {
    id: 2,
    title: 'Portland Cement Grade 53',
    po: 'PO-2024-0142',
    quantity: '1000 bags',
    status: 'Delayed',
    scheduled: '2024-02-10',
    expected: '2024-03-12',
    expectedDateClass: 'text-orange-600 font-medium',
    location: 'Warehouse B - Main Storage',
    tracking: 'TRK-456789012',
    progress: 50,
    alert: 'Delay due to transport vehicle breakdown. New vehicle assigned.',
    milestones: [
        { name: 'Order Confirmed', date: '2024-01-25', completed: true },
        { name: 'Production Started', date: '2024-01-28', completed: true },
        { name: 'Quality Check', date: '2024-02-05', completed: true },
        { name: 'Dispatched', date: '', completed: false },
        { name: 'In Transit', date: '', completed: false },
        { name: 'Delivered', date: '', completed: false },
    ]
  },
  {
    id: 3,
    title: 'IT Equipment - Laptops',
    po: 'PO-2024-0138',
    quantity: '50 units',
    status: 'Delivered',
    scheduled: '2024-02-08',
    expected: '2024-02-08',
    location: 'Head Office - IT Department',
    tracking: 'TRK-221854987',
    progress: 100,
    alert: null,
    milestones: [
        { name: 'Order Confirmed', date: '2024-01-20', completed: true },
        { name: 'Procurement', date: '2024-01-25', completed: true },
        { name: 'Quality Check', date: '2024-02-01', completed: true },
        { name: 'Dispatched', date: '2024-02-06', completed: true },
        { name: 'In Transit', date: '2024-02-07', completed: true },
        { name: 'Delivered', date: '2024-02-08', completed: true },
    ]
  },
  {
    id: 4,
    title: 'Office Furniture Set',
    po: 'PO-2024-0165',
    quantity: '25 sets',
    status: 'Scheduled',
    scheduled: '2024-02-20',
    expected: '2024-02-20',
    location: 'New Branch Office - Floor 3',
    tracking: '-',
    progress: 17,
    alert: null,
    milestones: [
        { name: 'Order Confirmed', date: '2024-02-05', completed: true },
        { name: 'Manufacturing', date: '', completed: false },
        { name: 'Quality Check', date: '', completed: false },
        { name: 'Dispatched', date: '', completed: false },
        { name: 'In Transit', date: '', completed: false },
        { name: 'Delivered', date: '', completed: false },
    ]
  }
])

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
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
     <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Delivery Schedule</h1>
        <p class="mt-1 text-sm text-gray-500">Track shipments and manage delivery milestones</p>
      </div>
      <button class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 flex items-center gap-2">
         <Plus class="h-4 w-4" /> Schedule New Delivery
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-4 mb-8">
       <div v-for="stat in stats" :key="stat.name" class="rounded-lg bg-white px-4 py-5 shadow sm:p-6 border border-gray-100 flex items-center gap-4">
          <div :class="[stat.bg, 'rounded-md p-3']">
             <component :is="stat.icon" :class="[stat.color, 'h-6 w-6']" />
          </div>
          <div>
             <dt class="truncate text-sm font-medium text-gray-500">{{ stat.name }}</dt>
             <dd class="mt-1 text-2xl font-semibold tracking-tight text-gray-900">{{ stat.value }}</dd>
          </div>
       </div>
    </div>

    <!-- Tabs -->
    <div class="mb-6">
       <div class="flex flex-wrap gap-2">
          <button
             v-for="tab in tabs"
             :key="tab"
             @click="activeTab = tab"
             :class="[
                activeTab === tab 
                   ? 'bg-gray-100 text-gray-900 font-semibold' 
                   : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50',
                'rounded-md px-3 py-2 text-sm font-medium transition-colors'
             ]"
          >
             {{ tab }}
          </button>
       </div>
    </div>

    <!-- List -->
    <div class="space-y-6">
       <div v-for="delivery in filteredDeliveries" :key="delivery.id" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
          <div class="flex flex-col lg:flex-row gap-8">
             <!-- Left: Details -->
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
                   <button class="inline-flex items-center gap-1 rounded bg-white px-2.5 py-1.5 text-xs font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
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
                      <span class="font-medium">Expected:</span> <span :class="delivery.expectedDateClass || ''">{{ delivery.expected }}</span>
                   </div>
                   <div class="flex items-center gap-2 text-gray-600">
                      <ExternalLink class="h-4 w-4 text-blue-500" />
                      <span class="font-medium">Tracking:</span> <a href="#" class="text-blue-600 hover:underline">{{ delivery.tracking }}</a>
                   </div>
                   <div class="flex items-center gap-2 text-gray-600">
                      <MapPin class="h-4 w-4 text-gray-400" />
                       <span class="truncate">{{ delivery.location }}</span>
                   </div>
                </div>

                <div v-if="delivery.alert" class="rounded-md bg-orange-50 p-3 text-sm text-orange-700 border border-orange-100">
                   {{ delivery.alert }}
                </div>
             </div>

             <!-- Right: Progress -->
             <div class="w-full lg:w-80 flex-shrink-0 border-t lg:border-t-0 lg:border-l border-gray-100 pt-6 lg:pt-0 lg:pl-6">
                <div class="flex items-center justify-between text-xs font-semibold text-gray-900 mb-2">
                   <span>Progress</span>
                   <span>{{ delivery.progress }}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2 mb-6">
                   <div class="bg-blue-600 h-2 rounded-full transition-all duration-500" :style="`width: ${delivery.progress}%`"></div>
                </div>

                <div class="relative space-y-4">
                   <!-- Vertical line -->
                   <div class="absolute left-1.5 top-1.5 bottom-1.5 w-0.5 bg-gray-200 z-0"></div>

                   <div v-for="(milestone, index) in delivery.milestones" :key="index" class="relative z-10 flex gap-3 text-xs">
                       <div 
                         class="h-3 w-3 rounded-full border-2 flex-shrink-0 mt-0.5 bg-white"
                         :class="milestone.completed ? 'border-green-500 bg-green-500' : 'border-gray-300'"
                       ></div>
                       <div class="flex justify-between w-full">
                          <span :class="milestone.completed ? 'text-gray-900 font-medium' : 'text-gray-500'">{{ milestone.name }}</span>
                          <span v-if="milestone.date" class="text-gray-400">{{ milestone.date }}</span>
                       </div>
                   </div>
                </div>
             </div>
          </div>
       </div>
    </div>

  </div>
</template>
