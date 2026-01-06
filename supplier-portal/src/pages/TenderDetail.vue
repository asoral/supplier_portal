<script setup>
import { useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import { Calendar, CheckCircle2, DollarSign, FileText, MapPin, Package } from 'lucide-vue-next'

const route = useRoute()
const tenderId = route.params.id

// Mock Data Load (In real app, fetch from API using tenderId)
const tender = ref({
  id: tenderId,
  title: 'Supply of High Grade Steel Plates',
  description: 'Procurement of structural steel plates for heavy machinery manufacturing. The steel plates must be of Grade E350 and comply with IS 2062 standards. Total weight required is approximately 500 tons. Delivery must be made in phases over a period of 3 months to our Pune plant.',
  category: 'Raw Materials',
  status: 'Active',
  budget: 5000000,
  deadline: '2024-03-15',
  location: 'Pune, Maharashtra',
  quantity: '500 Tons',
  publisher: 'TATA Projects Ltd',
  specifications: [
    'Grade: E350 (IS 2062)',
    'Thickness: 10mm - 50mm',
    'Width: 1500mm - 2500mm',
    'Ultrasonic Tested',
    'Mill Test Certificate Required'
  ]
})

const bidAmount = ref('')
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <div class="lg:grid lg:grid-cols-3 lg:gap-x-8">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-8">
        <div class="bg-white shadow sm:rounded-lg overflow-hidden">
          <div class="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
             <div class="flex items-center justify-between">
                <div>
                   <h3 class="text-base font-semibold leading-6 text-gray-900">Tender Details</h3>
                   <p class="mt-1 max-w-2xl text-sm text-gray-500">ID: {{ tender.id }}</p>
                </div>
                <span class="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800">
                   Active
                </span>
             </div>
          </div>
          <div class="px-4 py-5 sm:p-6">
            <h1 class="text-2xl font-bold text-gray-900 mb-4">{{ tender.title }}</h1>
            
            <div class="prose prose-indigo max-w-none text-gray-500 mb-8">
              <p>{{ tender.description }}</p>
            </div>
            
            <h4 class="text-sm font-medium text-gray-900 mb-4">Specifications</h4>
            <ul role="list" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-2 list-disc pl-5 mb-8 text-gray-600">
               <li v-for="spec in tender.specifications" :key="spec">{{ spec }}</li>
            </ul>

            <h4 class="text-sm font-medium text-gray-900 mb-4">Documents Required</h4>
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
               <div class="relative flex items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400">
                  <div class="flex-shrink-0">
                     <FileText class="h-6 w-6 text-gray-400" />
                  </div>
                  <div class="min-w-0 flex-1">
                     <a href="#" class="focus:outline-none">
                        <span class="absolute inset-0" aria-hidden="true" />
                        <p class="text-sm font-medium text-gray-900">Tech_Specs.pdf</p>
                        <p class="truncate text-sm text-gray-500">2.4 MB</p>
                     </a>
                  </div>
               </div>
               <div class="relative flex items-center space-x-3 rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm focus-within:ring-2 focus-within:ring-indigo-500 focus-within:ring-offset-2 hover:border-gray-400">
                  <div class="flex-shrink-0">
                     <FileText class="h-6 w-6 text-gray-400" />
                  </div>
                  <div class="min-w-0 flex-1">
                     <a href="#" class="focus:outline-none">
                        <span class="absolute inset-0" aria-hidden="true" />
                        <p class="text-sm font-medium text-gray-900">NDA_Agreement.docx</p>
                        <p class="truncate text-sm text-gray-500">145 KB</p>
                     </a>
                  </div>
               </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sickebar -->
      <div class="mt-8 lg:mt-0 lg:col-span-1 space-y-6">
         <!-- Key Info Card -->
         <div class="bg-white shadow sm:rounded-lg overflow-hidden">
             <div class="px-4 py-5 sm:px-6 bg-gray-50 border-b border-gray-200">
                <h3 class="text-base font-semibold leading-6 text-gray-900">Summary</h3>
             </div>
             <div class="px-4 py-5 sm:p-6 space-y-4">
                <div class="flex items-center text-sm">
                   <DollarSign class="h-5 w-5 text-gray-400 mr-2" />
                   <span class="font-medium text-gray-900 mr-2">Budget:</span>
                   <span class="text-gray-600">₹{{ tender.budget.toLocaleString() }}</span>
                </div>
                 <div class="flex items-center text-sm">
                   <Calendar class="h-5 w-5 text-gray-400 mr-2" />
                   <span class="font-medium text-gray-900 mr-2">Deadline:</span>
                   <span class="text-gray-600">{{ tender.deadline }}</span>
                </div>
                 <div class="flex items-center text-sm">
                   <MapPin class="h-5 w-5 text-gray-400 mr-2" />
                   <span class="font-medium text-gray-900 mr-2">Location:</span>
                   <span class="text-gray-600">{{ tender.location }}</span>
                </div>
                 <div class="flex items-center text-sm">
                   <Package class="h-5 w-5 text-gray-400 mr-2" />
                   <span class="font-medium text-gray-900 mr-2">Quantity:</span>
                   <span class="text-gray-600">{{ tender.quantity }}</span>
                </div>
             </div>
         </div>

         <!-- Bid Submission Card -->
          <div class="bg-indigo-50 shadow sm:rounded-lg overflow-hidden border border-indigo-100">
             <div class="px-4 py-5 sm:p-6">
                <h3 class="text-lg font-bold text-indigo-900 mb-2">Submit Your Bid</h3>
                <p class="text-sm text-indigo-700 mb-4">Submit your best offer before the deadline.</p>
                
                <div class="mb-4">
                   <label for="bid" class="block text-sm font-medium leading-6 text-indigo-900">Bid Amount (₹)</label>
                   <div class="relative mt-2 rounded-md shadow-sm">
                      <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                         <span class="text-gray-500 sm:text-sm">₹</span>
                      </div>
                      <input type="text" name="bid" id="bid" v-model="bidAmount" class="block w-full rounded-md border-0 py-1.5 pl-7 pr-12 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="0.00" aria-describedby="price-currency" />
                      <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
                         <span class="text-gray-500 sm:text-sm">INR</span>
                      </div>
                   </div>
                </div>

                <button type="button" class="w-full rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                   Place Bid
                </button>
             </div>
         </div>
      </div>
    </div>
  </div>
</template>
