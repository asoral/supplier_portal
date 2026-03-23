<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { 
  FileText, Download, Eye, Plus, CreditCard, 
  Clock, X, UploadCloud, CheckCircle 
} from 'lucide-vue-next'

const authStore = useAuthStore()
const { secureFetch } = authStore

const loading = ref(true)
const invoices = ref([]) 
const payments = ref([]) 
const activeTab = ref('Invoices')
const tabs = ['Invoices', 'Payments', 'Debit Notes']
const searchQuery = ref('')

const isUploadModalOpen = ref(false)
const newInvoice = ref({ po: '', number: '', date: '', amount: 0, file: null })

const downloadInvoice = async (invoice) => {
  try {
    const response = await secureFetch(`/api/method/supplier_portal.api.get_invoice_pdf?name=${invoice.id}`);
    
    if (!response.ok) throw new Error('Download failed');

    const blob = await response.blob();
    
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.setAttribute('download', `Invoice_${invoice.id}.pdf`); 
    
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error("Standard download failed:", error);
    alert("Could not download the file. Please try again.");
  }
}

const previewInvoice = (invoice) => {
  const url = `/api/method/supplier_portal.api.get_invoice_pdf?name=${invoice.id}&view=inline`;
  
  window.open(url, '_blank');
};

const fetchInvoices = async () => {
  try {
    const response = await secureFetch('/api/method/supplier_portal.api.get_supplier_invoices');
    const data = await response.json();
    if (data?.message) invoices.value = data.message;
  } catch (e) { console.error("Invoice Error:", e); }
};

const fetchPayments = async () => {
  try {
    const response = await secureFetch('/api/method/supplier_portal.api.get_supplier_payments');
    const data = await response.json();
    
    if (data?.message) {
      payments.value = data.message.map(p => ({
        id: p.id,
        date: p.date,
        amount: p.amount,
        ref_no: p.ref_no,
        method: p.method,
        against_invoice: p.against_invoice
      }));
    }
  } catch (e) { 
    console.error("Payment Error:", e); 
    payments.value = []; 
  }
};

onMounted(async () => {
  loading.value = true;
  await Promise.all([fetchInvoices(), fetchPayments()]);
  loading.value = false;
})

// --- Computed Stats ---
const stats = computed(() => {
  // Total of all non-return invoices
  const total = invoices.value
    .filter(inv => inv.status !== 'Return')
    .reduce((acc, inv) => acc + (Number(inv.amount) || 0), 0)
    
  // Actual payments received from the payments array
  const paid = payments.value.reduce((acc, pay) => acc + (Number(pay.amount) || 0), 0)
  
  // Count invoices that aren't fully paid or returned
  const pendingCount = invoices.value.filter(inv => inv.status !== 'Paid' && inv.status !== 'Return').length

  return [
    { name: 'Total Invoiced', value: `₹${total.toLocaleString('en-IN')}`, icon: FileText },
    { name: 'Payments Received', value: `₹${paid.toLocaleString('en-IN')}`, icon: CreditCard },
    { name: 'Pending Invoices', value: pendingCount.toString(), icon: Clock },
  ]
})

// --- Search Filters ---

// 1. Invoices (Excludes Returns)
const filteredInvoices = computed(() => {
  return (invoices.value || []).filter(inv => {
    const matchesSearch = !searchQuery.value || 
      inv.id?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      inv.supplier_name?.toLowerCase().includes(searchQuery.value.toLowerCase());
    
    return matchesSearch && inv.status !== 'Return';
  });
});

// 2. Payments
const filteredPayments = computed(() => {
  return (payments.value || []).filter(pay => {
    const query = searchQuery.value.toLowerCase();
    return !query || 
      pay.id?.toLowerCase().includes(query) || 
      pay.against_invoice?.toLowerCase().includes(query);
  });
});

// 3. Debit Notes (Only Returns)
const filteredDebitNotes = computed(() => {
  return (invoices.value || []).filter(inv => {
    const matchesSearch = !searchQuery.value || 
      inv.id?.toLowerCase().includes(searchQuery.value.toLowerCase());
    
    return matchesSearch && inv.status === 'Return';
  });
});

// --- Modal Actions ---
const openUploadModal = () => { isUploadModalOpen.value = true }
const closeUploadModal = () => { isUploadModalOpen.value = false }

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) newInvoice.value.file = file
}

const submitInvoice = async () => {
  if (!newInvoice.value.number || !newInvoice.value.amount) return
  
  try {
    loading.value = true
    const response = await secureFetch('/api/method/supplier_portal.api.upload_invoice', {
      method: 'POST',
      body: JSON.stringify(newInvoice.value)
    })
    
    const data = await response.json()
    if (data.message === "success") {
      await fetchInvoices()
      closeUploadModal()
    }
  } catch (error) {
    console.error("Upload failed:", error)
  } finally {
    loading.value = false
  }
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
  
  <table v-if="activeTab === 'Invoices'" class="min-w-full divide-y divide-gray-200">
    <thead class="bg-gray-50">
      <tr>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Invoice #</th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">PO / Tender</th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Due Date</th>
        <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
        <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
        <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>      </tr>
    </thead>
    <tbody class="divide-y divide-gray-200 bg-white">
      <tr v-for="inv in filteredInvoices" :key="inv.id" class="hover:bg-gray-50 transition-colors">
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">{{ inv.id }}</td>
        <td class="px-6 py-4">
          <div class="text-sm font-semibold text-gray-900">{{ inv.supplier_name }}</div>
          <div v-if="inv.po" class="text-xs font-bold text-indigo-600 mt-0.5">{{ inv.po }}</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ inv.date }}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ inv.dueDate }}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-right">
          <div class="font-bold text-gray-900">₹{{ Number(inv.amount).toLocaleString('en-IN') }}</div>
          <div class="text-xs text-gray-400">incl. ₹{{ Number(inv.tax).toLocaleString('en-IN') }} tax</div>
        </td>
        <td class="px-6 py-4 whitespace-nowrap">
          <span 
            class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset"
            :class="{
              'bg-green-50 text-green-700 ring-green-600/20': inv.status === 'Paid',
              'bg-blue-50 text-blue-700 ring-blue-700/10': inv.status === 'Approved',
              'bg-orange-50 text-orange-700 ring-orange-600/20': ['Pending Approval', 'Unpaid'].includes(inv.status),
              'bg-gray-50 text-gray-600 ring-gray-500/10': inv.status === 'Return'
            }"
          >
            {{ inv.status }}
          </span>
        </td>
        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
          <div class="flex items-center justify-end gap-3 text-gray-400">
            <button 
              @click="previewInvoice(inv)" 
              class="hover:text-indigo-600 p-1"
              title="Preview Invoice"
            >
              <Eye class="h-4 w-4" />
            </button>
            <button 
              @click="downloadInvoice(inv)" 
              class="hover:text-indigo-600 p-1"
              title="Download Invoice"
            >
              <Download class="h-4 w-4" />
            </button>
          </div>
        </td>
      </tr>
    </tbody>
  </table>

  <div v-if="activeTab === 'Payments'" class="p-6 bg-white">
    <div class="flex items-center gap-2 mb-6">
      <CreditCard class="h-5 w-5 text-indigo-600" />
      <h3 class="text-lg font-bold text-gray-900">Payment History</h3>
    </div>

    <div v-for="pay in filteredPayments" :key="pay.id" class="border rounded-xl p-4 mb-4 hover:bg-gray-50 border-gray-100 shadow-sm transition-all">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-4">
          <div class="bg-green-100 p-2 rounded-full">
            <CheckCircle class="h-5 w-5 text-green-600" />
          </div>
          <div>
            <div class="text-sm font-bold text-gray-900">{{ pay.id }}</div>
            <div class="text-xs text-gray-500">{{ pay.method || 'NEFT' }} • Ref: {{ pay.ref_no || 'N/A' }}</div>
            <div class="text-xs font-medium text-indigo-600 mt-1">Against: {{ pay.against_invoice }}</div>
          </div>
        </div>
        <div class="text-right">
          <div class="text-base font-bold text-green-600">₹{{ Number(pay.amount).toLocaleString('en-IN') }}</div>
          <div class="text-xs text-gray-400">{{ pay.date }}</div>
        </div>
      </div>
    </div>
    
    <div v-if="filteredPayments.length === 0" class="text-center py-12 text-gray-500">
      No payment records found.
    </div>
  </div>

  <table v-if="activeTab === 'Debit Notes'" class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr class="text-xs font-medium text-gray-500 uppercase tracking-wider">
            <th class="px-6 py-3 text-left">Debit Note #</th>
            <th class="px-6 py-3 text-left">Supplier</th>
            <th class="px-6 py-3 text-left">Date</th>
            <th class="px-6 py-3 text-right">Deduction Amount</th>
            <th class="px-6 py-3 text-left">Status</th>
            <th class="relative px-6 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr v-for="note in filteredDebitNotes" :key="note.id" class="hover:bg-red-50/30 transition-colors">
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-600">{{ note.id }}</td>
            <td class="px-6 py-4 text-sm text-gray-900">{{ note.supplier_name }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ note.date }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-right font-bold text-gray-900">
               -₹{{ Number(note.amount).toLocaleString('en-IN') }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20">
                Returned
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="activeTab === 'Debit Notes' && filteredDebitNotes.length === 0" class="p-12 text-center text-gray-500">
        No Debit Notes found.
      </div>
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
