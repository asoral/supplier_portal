<script setup>
import { ref, computed } from 'vue'
import { FileText, Download, Eye, Plus, CreditCard, Clock, X, UploadCloud } from 'lucide-vue-next'

const stats = [
  { name: 'Total Invoiced', value: '₹20,54,000', change: '+12%', icon: FileText },
  { name: 'Payments Received', value: '₹3,20,000', change: '+8%', icon: CreditCard },
  { name: 'Pending Invoices', value: '2', value2: '₹17.34,000', icon: Clock },
]

const invoices = ref([
  {
    id: 'INV-2024-001',
    po: 'PO-2023-0125',
    project: 'Safety Equipment Annual Supply',
    date: '10 Feb 2024',
    dueDate: '12 Mar 2024',
    amount: 750000,
    tax: 14800,
    status: 'Approved',
  },
  {
    id: 'INV-2024-002',
    po: 'PO-2023-0098',
    project: 'Office Furniture Supply',
    date: '18 Dec 2023',
    dueDate: '18 Jan 2024',
    amount: 320000,
    tax: 2854,
    status: 'Paid',
  },
   {
    id: 'INV-2024-003',
    po: 'PO-2024-0155',
    project: 'Industrial Steel Plates - Advance',
    date: '22 Feb 2024',
    dueDate: '7 Mar 2024',
    amount: 984000,
    tax: 110502,
    status: 'Pending Approval',
  }
])

const activeTab = ref('Invoices')
const tabs = ['Invoices', 'Payments', 'Debit Notes']
const searchQuery = ref('')

// Upload Modal Logic
const isUploadModalOpen = ref(false)
const newInvoice = ref({
  po: '',
  number: '',
  date: '',
  amount: '',
  file: null
})

const openUploadModal = () => isUploadModalOpen.value = true
const closeUploadModal = () => {
  isUploadModalOpen.value = false
  newInvoice.value = { po: '', number: '', date: '', amount: '', file: null }
}

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    newInvoice.value.file = file
  }
}

const submitInvoice = () => {
  // Mock submission
  if (!newInvoice.value.number || !newInvoice.value.amount) return
  
  invoices.value.unshift({
    id: newInvoice.value.number,
    po: newInvoice.value.po,
    project: 'Industrial Steel Plates', // Mock
    date: newInvoice.value.date || new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' }),
    dueDate: 'Pending',
    amount: parseFloat(newInvoice.value.amount),
    tax: parseFloat(newInvoice.value.amount) * 0.18,
    status: 'Pending Approval'
  })
  
  closeUploadModal()
}
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Invoices & Payments</h1>
        <p class="mt-1 text-sm text-gray-500">Manage invoices, track payments, and view debit notes.</p>
      </div>
      <button @click="openUploadModal" class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 flex items-center gap-2">
         <Plus class="h-4 w-4" /> Upload Invoice
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3 mb-8">
       <div v-for="stat in stats" :key="stat.name" class="rounded-lg bg-white px-4 py-5 shadow sm:p-6 border border-gray-100 relative overflow-hidden">
          <div class="absolute right-4 top-4 p-2 bg-gray-50 rounded-lg text-gray-400">
             <component :is="stat.icon" class="h-6 w-6" />
          </div>
          <dt class="truncate text-sm font-medium text-gray-500">{{ stat.name }}</dt>
          <dd class="mt-2 flex items-baseline">
             <span class="text-2xl font-bold tracking-tight text-gray-900">{{ stat.value }}</span>
             <span v-if="stat.value2" class="ml-2 text-sm font-medium text-gray-500 sm:ml-4 sm:pl-4 sm:border-l sm:border-gray-200">{{ stat.value2 }}</span>
             <span v-if="stat.change" class="ml-2 inline-flex items-center rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700">{{ stat.change }}</span>
          </dd>
       </div>
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

    <!-- Search Tool -->
    <div class="mb-6">
       <input 
          v-model="searchQuery"
          type="text" 
          class="block w-full sm:w-80 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 pl-3"
          placeholder="Search invoices..." 
       />
    </div>

    <!-- Table -->
    <div class="overflow-hidden rounded-lg border border-gray-200 bg-white shadow">
       <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
             <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice #</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">PO / Tender</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th scope="col" class="relative px-6 py-3"><span class="sr-only">Actions</span></th>
             </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 bg-white">
             <tr v-for="inv in invoices" :key="inv.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">{{ inv.id }}</td>
                 <td class="px-6 py-4">
                    <div class="text-sm font-medium text-gray-900">{{ inv.project }}</div>
                    <div class="text-xs text-gray-500">{{ inv.po }}</div>
                 </td>
                 <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ inv.date }}</td>
                 <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ inv.dueDate }}</td>
                 <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right">
                    <div class="font-bold">₹{{ inv.amount.toLocaleString() }}</div>
                    <div class="text-xs text-gray-400">incl. ₹{{ inv.tax.toLocaleString() }} tax</div>
                 </td>
                 <td class="px-6 py-4 whitespace-nowrap">
                    <span 
                      class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset"
                      :class="{
                         'bg-green-50 text-green-700 ring-green-600/20': inv.status === 'Paid',
                         'bg-blue-50 text-blue-700 ring-blue-700/10': inv.status === 'Approved',
                         'bg-orange-50 text-orange-700 ring-orange-600/20': inv.status === 'Pending Approval',
                      }"
                    >
                       {{ inv.status }}
                    </span>
                 </td>
                 <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex items-center justify-end gap-2">
                       <button class="text-gray-400 hover:text-gray-600"><Eye class="h-4 w-4" /></button>
                       <button class="text-gray-400 hover:text-gray-600"><Download class="h-4 w-4" /></button>
                    </div>
                 </td>
             </tr>
          </tbody>
       </table>
    </div>

    <!-- Upload Invoice Modal -->
    <div v-if="isUploadModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6" role="dialog" aria-modal="true">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeUploadModal"></div>
      
      <div class="relative transform overflow-hidden rounded-xl bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
        <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
          <button type="button" class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none" @click="closeUploadModal">
            <span class="sr-only">Close</span>
            <X class="h-5 w-5" aria-hidden="true" />
          </button>
        </div>
        
        <div>
          <h3 class="text-lg font-bold leading-6 text-gray-900 mb-6" id="modal-title">Upload Invoice</h3>
          <div class="space-y-4">
             <div>
               <label for="po" class="block text-sm font-semibold text-gray-900 mb-1.5">Purchase Order</label>
               <input type="text" id="po" v-model="newInvoice.po" placeholder="Select PO Number" class="block w-full rounded-lg border-0 py-2.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
             </div>

             <div>
               <label for="inv-number" class="block text-sm font-semibold text-gray-900 mb-1.5">Invoice Number</label>
               <input type="text" id="inv-number" v-model="newInvoice.number" placeholder="Enter your invoice number" class="block w-full rounded-lg border-0 py-2.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
             </div>

             <div class="grid grid-cols-2 gap-4">
                <div>
                  <label for="inv-date" class="block text-sm font-semibold text-gray-900 mb-1.5">Invoice Date</label>
                  <input type="date" id="inv-date" v-model="newInvoice.date" class="block w-full rounded-lg border-0 py-2.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                </div>
                <div>
                  <label for="amount" class="block text-sm font-semibold text-gray-900 mb-1.5">Amount (₹)</label>
                  <input type="number" id="amount" v-model="newInvoice.amount" placeholder="0.00" class="block w-full rounded-lg border-0 py-2.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                </div>
             </div>

             <div>
               <label class="block text-sm font-semibold text-gray-900 mb-1.5">Invoice Document</label>
               <div class="mt-2 flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10 bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer relative">
                 <div class="text-center">
                   <UploadCloud class="mx-auto h-12 w-12 text-gray-300" aria-hidden="true" />
                   <div class="mt-4 flex text-sm leading-6 text-gray-600 justify-center">
                     <label for="file-upload" class="relative cursor-pointer rounded-md font-semibold text-indigo-600 focus-within:outline-none focus-within:ring-2 focus-within:ring-indigo-600 focus-within:ring-offset-2 hover:text-indigo-500">
                       <span>Click to upload</span>
                       <input id="file-upload" name="file-upload" type="file" class="sr-only" @change="handleFileUpload">
                     </label>
                     <p class="pl-1">or drag and drop</p>
                   </div>
                   <p class="text-xs leading-5 text-gray-600">PDF only, max 10MB</p>
                   <p v-if="newInvoice.file" class="mt-2 text-sm text-indigo-600 font-medium">{{ newInvoice.file.name }}</p>
                 </div>
               </div>
             </div>
          </div>
          
          <div class="mt-6">
             <button @click="submitInvoice" type="button" class="inline-flex w-full justify-center rounded-lg bg-indigo-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all">
               Submit Invoice
             </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
