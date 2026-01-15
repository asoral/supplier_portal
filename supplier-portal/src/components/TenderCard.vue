<script setup>
import { Clock, DollarSign, MapPin, Calendar} from 'lucide-vue-next'
import { computed } from 'vue'

const props = defineProps({
  tender: {
    type: Object,
    required: true
  },
  viewMode: {
     type: String,
     default: 'grid'
  }
})
const formattedPublishedDate = computed(() => {
  if (!props.tender.publishedDate) return 'N/A'
  return new Date(props.tender.publishedDate).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  })
})

const hoursRemaining = computed(() => {
  if (!props.tender.deadline) return 'No Date Set'
  
  const deadline = new Date(props.tender.deadline)
  const now = new Date()
  
  const diffInMs = deadline - now
  
  const totalHours = Math.floor(diffInMs / (1000 * 60 * 60))
  
  return `${totalHours}h left`
})

const timerClass = computed(() => {
  const hours = parseInt(hoursRemaining.value)
  return hours < 0 ? 'text-red-600 font-bold' : 'text-green-600';
})

const formattedBudget = computed(() => {
  return new Intl.NumberFormat('en-IN', { 
    style: 'currency', 
    currency: 'INR', 
    maximumFractionDigits: 0 
  }).format(props.tender.budget)
})

const statusClasses = computed(() => {
  switch (props.tender.status) {
    case 'Active':
      return 'bg-green-50 text-green-700 border-green-200'
    case 'Closed':
      return 'bg-red-50 text-red-700 border-red-200'
    case 'Coming Soon':
      return 'bg-yellow-50 text-yellow-700 border-yellow-200'
    default:
      return 'bg-gray-50 text-gray-700 border-gray-200'
  }
})
</script>

<template>
  <div class="group relative flex flex-col overflow-hidden rounded-lg border border-gray-200 bg-white transition-all hover:shadow-md" :class="viewMode === 'list' ? 'flex-row' : ''">
    <div class="p-6 flex-grow flex flex-col">
      <div class="mb-4 flex items-start justify-between">
         <div class="flex flex-wrap gap-2">
            <span class="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600">
               {{ tender.category }}
            </span>
            
            <span 
               class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium border"
               :class="statusClasses"
            >
               {{ tender.status }}
            </span>

             <span v-if="tender.status === 'Active'" class="inline-flex items-center rounded-md bg-orange-50 px-2 py-1 text-xs font-medium text-orange-700 ring-1 ring-inset ring-orange-600/20">
               Live Bidding
            </span>
         </div>
      </div>

      <h3 class="text-base font-semibold leading-6 text-gray-900 group-hover:text-indigo-600 transition-colors">
        <router-link :to="{ name: 'TenderDetail', params: { id: tender.id } }">
          {{ tender.title }}
        </router-link>
      </h3>
      <p class="mt-1 text-xs text-gray-500 font-mono">{{ tender.id }}</p>
      
      <p class="mt-3 line-clamp-3 text-sm leading-6 text-gray-600">
        {{ tender.description }}
      </p>
      
      <div class="mt-auto pt-6 flex flex-wrap gap-y-3 gap-x-6 border-t border-gray-100">
        <div class="flex items-center text-sm font-semibold text-gray-900 min-w-[120px]">
          <DollarSign class="mr-1.5 h-4 w-4 text-gray-400" aria-hidden="true" />
          {{ formattedBudget }}
        </div>
        
        <div class="flex items-center text-sm font-medium min-w-[120px]" :class="timerClass">
          <Clock class="mr-1.5 h-4 w-4 opacity-70" aria-hidden="true" />
          <span>{{ hoursRemaining }}</span>
        </div>
        <div class="flex items-center text-sm font-semibold text-gray-600 mt-2">
          <Calendar class="mr-2 h-4 w-4 text-indigo-500" aria-hidden="true" />
          <span>{{ formattedPublishedDate }}</span>
        </div>
      </div>
       
       <div v-if="tender.liveBidding" class="mt-4 pt-3 flex items-center justify-between border-t border-dashed border-gray-200">
          <div class="text-xs text-orange-600 font-medium flex items-center gap-1">
             <span class="relative flex h-2 w-2">
               <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
               <span class="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
             </span>
             Current Lowest Bid
          </div>
          <div class="text-sm font-bold text-green-600">₹4,25,000</div>
       </div>

     <div class="mt-4 flex gap-2 z-20 relative">
        <router-link 
          v-if="tender.liveBidding"
          :to="{ name: 'TenderDetail', params: { id: tender.id } }" 
          class="flex-1 flex items-center justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 transition-colors text-center"
        >
          View & Bid
        </router-link>

        <router-link 
          v-else
          :to="{ name: 'TenderDetail', params: { id: tender.id } }" 
          class="flex-1 flex items-center justify-center rounded-md bg-indigo-50 px-3 py-2 text-sm font-semibold text-indigo-600 shadow-sm hover:bg-indigo-100 transition-colors text-center"
        >
          View Details
        </router-link>
      </div>
    </div>
  </div>
</template>