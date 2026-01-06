<script setup>
import { ref, computed } from 'vue'
import { Package, Plus, Search, Filter, Edit2, Trash2, TrendingUp, Clock, CheckCircle, AlertCircle } from 'lucide-vue-next'

const activeTab = ref('My Catalog')
const tabs = ['My Catalog', 'Portal Items']
const searchQuery = ref('')

const stats = [
  { name: 'Total Products', value: '4', icon: Package, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  { name: 'Active Items', value: '3', icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
  { name: 'Pending Approval', value: '1', icon: Clock, color: 'text-orange-600', bg: 'bg-orange-50' },
  { name: 'Matched Tenders', value: '10', icon: TrendingUp, color: 'text-blue-600', bg: 'bg-blue-50' },
]

const products = ref([
  {
    id: 1,
    name: 'Industrial Safety Helmet (IS 2925)',
    sku: 'SH-IS2925-001',
    category: 'Safety',
    unit: 'Nos',
    description: 'ABS Shell, Ratchet Adjustment, ISI Mark, Ventilated',
    status: 'active',
    matches: 3,
    price: 450,
    tax: '18% GST',
    leadTime: '7 days',
    moq: 100
  },
  {
    id: 2,
    name: 'Safety Shoes (Steel Toe)',
    sku: 'SS-ST-001',
    category: 'Safety',
    unit: 'Pairs',
    description: 'PU Sole, Steel Toe Cap, Oil Resistant, Ankle Support',
    status: 'active',
    matches: 5,
    price: 1200,
    tax: '18% GST',
    leadTime: '10 days',
    moq: 50
  },
  {
    id: 3,
    name: 'Cut Resistant Gloves (Level 5)',
    sku: 'GL-CR5-001',
    category: 'Safety',
    unit: 'Pairs',
    description: 'HPPE Fiber, PU Coated Palm, EN388 Certified',
    status: 'active',
    matches: 2,
    price: 280,
    tax: '18% GST',
    leadTime: '5 days',
    moq: 200
  },
  {
    id: 4,
    name: 'MS Flat Bar 50x10mm',
    sku: 'MS-FB-5010',
    category: 'Raw Materials',
    unit: 'Kg',
    description: 'IS 2062 Grade E250, Mill Finish',
    status: 'pending',
    price: 65,
    tax: '18% GST',
    leadTime: '14 days',
    moq: 1000
  }
])

const filteredProducts = computed(() => {
  return products.value.filter(item => 
    item.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    item.sku.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Product Catalog</h1>
        <p class="mt-1 text-sm text-gray-500">Manage your product catalog and pricing.</p>
      </div>
      <button class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 flex items-center gap-2">
         <Plus class="h-4 w-4" /> Add Product
      </button>
    </div>

    <!-- Stats Grid -->
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
       <div class="flex space-x-2">
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
            placeholder="Search products..." 
          />
       </div>
       <button class="inline-flex items-center justify-center gap-2 rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
          <Filter class="h-4 w-4 text-gray-500" />
          Filters
       </button>
    </div>

    <!-- Product List -->
    <div class="space-y-4">
       <div v-for="product in filteredProducts" :key="product.id" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex flex-col lg:flex-row gap-6">
             <!-- Icon -->
             <div class="flex-shrink-0">
                <div class="h-16 w-16 rounded-lg bg-gray-100 flex items-center justify-center">
                   <Package class="h-8 w-8 text-gray-400" />
                </div>
             </div>

             <!-- Details -->
             <div class="flex-grow">
                <div class="flex flex-wrap items-center gap-2 mb-1">
                   <h3 class="text-base font-semibold text-gray-900">{{ product.name }}</h3>
                   <span 
                      class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset"
                      :class="product.status === 'active' ? 'bg-green-50 text-green-700 ring-green-600/20' : 'bg-orange-50 text-orange-700 ring-orange-600/20'"
                   >
                      {{ product.status }}
                   </span>
                   <span v-if="product.matches" class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                      <TrendingUp class="h-3 w-3" /> {{ product.matches }} matches
                   </span>
                </div>
                
                <div class="text-xs text-gray-500 mb-2 space-x-1">
                    <span class="font-medium text-gray-700">SKU:</span> {{ product.sku }}
                    <span>•</span>
                    <span class="font-medium text-gray-700">Category:</span> {{ product.category }}
                    <span>•</span>
                    <span class="font-medium text-gray-700">Unit:</span> {{ product.unit }}
                </div>

                <p class="text-sm text-gray-600 mb-3">{{ product.description }}</p>
             </div>

             <!-- Pricing & Actions -->
             <div class="flex lg:flex-col items-center lg:items-end justify-between lg:justify-center gap-4 min-w-[150px] border-t lg:border-t-0 lg:border-l border-gray-100 pt-4 lg:pt-0 lg:pl-6">
                 <div class="text-right">
                    <div class="text-lg font-bold text-gray-900">₹{{ product.price.toLocaleString() }}</div>
                    <div class="text-xs text-gray-500">+ {{ product.tax }}</div>
                 </div>

                 <div class="text-right text-xs text-gray-500 space-y-1">
                    <div>Lead: {{ product.leadTime }}</div>
                    <div>MOQ: {{ product.moq }}</div>
                 </div>

                 <div class="flex gap-2">
                    <button class="p-1.5 text-gray-400 hover:text-indigo-600 rounded hover:bg-gray-100">
                       <Edit2 class="h-4 w-4" />
                    </button>
                    <button class="p-1.5 text-gray-400 hover:text-red-600 rounded hover:bg-gray-100">
                       <Trash2 class="h-4 w-4" />
                    </button>
                 </div>
             </div>
          </div>
       </div>
    </div>
  </div>
</template>
