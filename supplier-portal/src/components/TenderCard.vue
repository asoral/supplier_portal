<script setup>
import { Clock, DollarSign, MapPin } from 'lucide-vue-next'
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

const formattedBudget = computed(() => {
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(props.tender.budget)
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
               :class="tender.status === 'Active' ? 'bg-white text-indigo-700 border-indigo-200' : 'bg-white text-gray-700 border-gray-200'"
            >
               {{ tender.status }}
            </span>
             <span v-if="tender.liveBidding" class="inline-flex items-center rounded-md bg-orange-50 px-2 py-1 text-xs font-medium text-orange-700 ring-1 ring-inset ring-orange-600/20">
               Live Bidding
            </span>
         </div>
      </div>

      <h3 class="text-base font-semibold leading-6 text-gray-900 group-hover:text-indigo-600 transition-colors">
        <a href="#">
          <span class="absolute inset-0" />
          {{ tender.title }}
        </a>
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
        <div class="flex items-center text-sm font-medium text-gray-500 min-w-[120px]">
          <Clock class="mr-1.5 h-4 w-4 text-gray-400" aria-hidden="true" />
          <span>{{ tender.deadline }}</span>
        </div>
         <div class="flex items-center text-sm font-medium text-gray-500 min-w-[120px]">
          <MapPin class="mr-1.5 h-4 w-4 text-gray-400" aria-hidden="true" />
          <span>{{ tender.location || 'Remote' }}</span>
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

      <div class="mt-4 flex gap-2 z-10 relative">
          <button class="flex-1 rounded-md bg-indigo-50 px-3 py-2 text-sm font-semibold text-indigo-600 shadow-sm hover:bg-indigo-100">View Details</button>
          <button class="flex-1 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">View & Bid</button>
      </div>

    </div>
  </div>
</template>
