<script setup>
import { ref, onMounted, computed } from 'vue'
import { 
  Trophy, FileText, Clock, LogIn, LogOut, Edit, PlusCircle, TrendingUp, 
  CheckCircle, Download, Search, Filter, Loader2, ArrowLeft, Printer, MessageSquare, ExternalLink, Calendar, CreditCard, Box
} from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const activeTab = ref('All Contracts')
const searchQuery = ref('')
const isLoading = ref(true)
const supplierId = ref(null)
const contracts = ref([])
const payments = ref([]);
const blanketOrders = ref([]);

const selectedContract = ref(null) 

const tabs = ['All Contracts', 'Active', 'Pending', 'Completed']
const detailTabs = ['Overview', 'Line Items', 'Payments', 'Documents', 'Timeline']
const activeDetailTab = ref('Overview')

const handlePrint = () => {
  window.print();
};

const handleDownloadPO = async () => {
  if (!selectedContract.value?.internalName) return;

  try {
    const downloadUrl = `/api/method/frappe.utils.print_format.download_pdf?` + 
                        `doctype=Blanket Order&name=${selectedContract.value.internalName}&format=Standard&no_letterhead=0`;

    const response = await authStore.secureFetch(downloadUrl);
    
    if (!response.ok) throw new Error('Download failed');

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `PO-${selectedContract.value.internalName}.pdf`;
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error("Error triggering download:", error);
  }
};

const handleDownloadBlanketOrder = async (name) => {
  if (!name) return;

  try {
    const downloadUrl = `/api/method/frappe.utils.print_format.download_pdf?` + 
                        `doctype=Blanket Order&name=${name}&format=Standard&no_letterhead=0`;

    const response = await authStore.secureFetch(downloadUrl);
    
    if (!response.ok) throw new Error('Download failed');

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `${name}.pdf`;
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    showNotification(`Downloading ${name}...`);
    
  } catch (error) {
    console.error("Error downloading Blanket Order:", error);
  }
};

const processedOrders = computed(() => {
  return filteredContracts.value.map(contract => {
    const items = contract.items || [];
    const totalItemsCount = items.length;
    
    const deliveryCount = items.filter(item => 
      item.ordered_qty >= item.qty && item.qty > 0
    ).length;

    const percent = totalItemsCount > 0 ? (deliveryCount / totalItemsCount) * 100 : 0;
    console.log("-----------------------------percent",percent)

    return {
      ...contract,
      deliveryCount,
      totalItems: totalItemsCount,
      progressPercent: Math.round(percent) 
    };
  });
});

const viewContract = async (contract) => {
    // Reset state and set initial values
    selectedContract.value = { ...contract, items: [], documents: [] };
    payments.value = []; 
    activeDetailTab.value = 'Overview';
    
    try {
        // --- 1. Fetch Blanket Order Details ---
        const docResponse = await authStore.secureFetch(`/api/resource/Blanket Order/${contract.internalName}`);
        const docResult = await docResponse.json();
        
        if (docResult.data) {
            const data = docResult.data;

            // Handle Items Logic
            if (data.items) {
                selectedContract.value.totalItems = data.items.length; 
                const deliveredCount = data.items.filter(item => 
                    item.ordered_qty >= item.qty && item.qty > 0
                ).length;
                selectedContract.value.deliveryCount = deliveredCount;

                selectedContract.value.items = data.items.map(item => ({
                    item_code: item.item_code,           
                    qty: item.qty,                       
                    uom: '-',                            
                    rate: item.rate,                     
                    custom_amount: item.custom_amount,   
                    delivered: '-',                      
                    status: item.ordered_qty >= item.qty ? 'Delivered' : 'Pending'                     
                }));
            }
        }

        const docApiRes = await authStore.secureFetch(
              `/api/method/supplier_portal.api.get_contract_documents?blanket_order=${contract.internalName}`
          );
          const docApiData = await docApiRes.json();

          if (docApiData.message) {
              selectedContract.value.documents = docApiData.message.map(doc => ({
                  id: doc.id,
                  name: doc.document_name,
                  file_url: doc.file_url,
                  date: doc.date
              }));
          }
        const payRes = await authStore.secureFetch(
            `/api/method/supplier_portal.api.get_contract_payments?blanket_order=${contract.internalName}`
        );
        const payData = await payRes.json();
        
        if (payData.data && payData.data.length > 0) {
            payments.value = payData.data.map(p => ({
                id: p.name,
                date: p.posting_date, 
                amount: p.paid_amount, 
                status: p.docstatus === 1 ? 'Paid' : 'Pending'
            }));
        } else {
            const poRes = await authStore.secureFetch(
                `/api/resource/Purchase Order?filters=[["Purchase Order Item","blanket_order","=","${contract.internalName}"]]&fields=["name"]`
            );
            const poData = await poRes.json();

            if (poData.data && poData.data.length > 0) {
                const poNames = poData.data.map(po => po.name);
                const payResFallback = await authStore.secureFetch(
                    `/api/resource/Payment Entry?filters=[["Payment Entry Reference","reference_name","in",${JSON.stringify(poNames)}]]&fields=["name","posting_date","paid_amount","docstatus"]`
                );
                const payDataFallback = await payResFallback.json();
                if (payDataFallback.data) {
                    payments.value = payDataFallback.data.map(p => ({
                        id: p.name, 
                        date: p.posting_date, 
                        amount: p.paid_amount, 
                        status: p.docstatus === 1 ? 'Paid' : 'Pending'
                    }));
                }
            }
        }

        const paymentRes = await authStore.secureFetch(
            `/api/method/supplier_portal.api.get_blanket_order_payment_stats?blanket_order=${contract.internalName}`
        );
        const pResult = await paymentRes.json();
        if (pResult.message) {
            selectedContract.value.amountReceived = pResult.message.total_paid || 0;
            const totalVal = contract.value || 0;
            selectedContract.value.paymentProgress = totalVal > 0 
                ? Math.min(Math.round((pResult.message.total_paid / totalVal) * 100), 100) 
                : 0;
        }

    } catch (e) {
        console.error("Error loading details:", e);
    }
}

const downloadPaymentEntry = async (paymentId) => {
  try {
    const printFormat = 'Standard'; 
    const downloadUrl = `/api/method/frappe.utils.print_format.download_pdf?` + 
                        `doctype=Payment Entry&name=${paymentId}&format=${printFormat}&no_letterhead=0`;

    const response = await authStore.secureFetch(downloadUrl);
    
    if (!response.ok) throw new Error('Download failed');

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.href = url;
    link.download = `${paymentId}.pdf`; 
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
  } catch (error) {
    console.error("Error downloading payment receipt:", error);
  }
};

const fetchContracts = async (sId) => {
    try {
        const filters = JSON.stringify([
            ["blanket_order_type", "=", "Purchasing"],
            ["supplier", "=", sId],
            ["docstatus", "!=", 2]
        ])
        const response = await authStore.secureFetch(
          `/api/resource/Blanket Order?filters=${filters}&fields=["*"]`
        )
        const result = await response.json()
        
        if (result.data) {
            contracts.value = result.data.map(doc => {
                const totalQty = doc.items?.reduce((sum, item) => sum + (item.qty || 0), 0) || 0;
                const orderedQty = doc.items?.reduce((sum, item) => sum + (item.ordered_qty || 0), 0) || 0;
                const items = doc.items || [];
                console.log("-----------------------items",items)
                const totalItemsCount = items.length; 
                const totalValue = doc.items?.reduce((sum, item) => sum + ((item.qty || 0) * (item.rate || 0)), 0) || 0;
                console.log("------------------------totalValue",totalValue)
                
                const deliveryCount = items.filter(item => 
                    item.ordered_qty >= item.qty && item.qty > 0
                ).length;

                return {
                    id: doc.order_no || doc.name,
                    internalName: doc.name,
                    title: doc.custom_contract_subject_for_supplier_portal || "Blanket Order",
                    date: doc.from_date,
                    value: doc.custom_total_inr || totalValue || 0,
                    deliveryDate: doc.to_date,
                    deliveredItems: orderedQty,
                    items: doc.items || [],
                    totalItems: totalQty,
                    status: doc.docstatus === 1 ? 'Active' : 'Pending',
                    progress: doc.custom_delivery_ ? Math.round(doc.custom_delivery_) : 0,
                    deliveryCount: deliveryCount, 
                    totalItems: totalItemsCount,
                    amountReceived: 0,
                    paymentProgress: 0,
                    tenderId: doc.tender_id || 'TND-2024-005',
                    paymentTerms: doc.payment_terms_template || '30 days from delivery',
                    buyer: {
                        name: doc.company || 'Tata Steel Limited',
                        division: 'Procurement - Safety Division',
                        phone: '+91 657 242 5000',
                        email: 'procurement.safety@tatasteel.com',
                        address: 'Jamshedpur, Jharkhand 831001'
                    }
                }
            })
        }
    } catch (e) {
        console.error("Contracts Sync Error:", e)
    }
}


const closeDetail = () => {
  selectedContract.value = null
}

const activeStats = computed(() => {
   const activeCount = contracts.value.filter(c => c.status === 'Active').length
   const totalValue = contracts.value.reduce((acc, curr) => acc + curr.value, 0)
   return { count: activeCount, totalValue }
})

const fetchSupplierIdentity = async () => {
    try {
        const response = await authStore.secureFetch('/api/method/supplier_portal.api.get_logged_user_supplier')
        const result = await response.json()
        if (result.message) {
            supplierId.value = result.message
            return result.message
        }
        return null
    } catch (e) {
        console.error("Identity Fetch Error:", e)
        return null
    }
}

const filteredContracts = computed(() => {
  return contracts.value.filter(contract => {
    const matchesTab = activeTab.value === 'All Contracts' || contract.status === activeTab.value
    const matchesSearch = contract.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          contract.id.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesTab && matchesSearch
  })
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(value || 0);
}

onMounted(async () => {
    isLoading.value = true
    try {
        if (!authStore.isAuthenticated) await authStore.initializeAuth()
        if (!authStore.isAuthenticated) {
            window.location.href = "/app"
            return
        }
        const sId = await fetchSupplierIdentity()
        if (sId) await fetchContracts(sId)
    } catch (error) {
        console.error("Mounting Error:", error)
    } finally {
        isLoading.value = false
    }
})
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    
    <div v-if="isLoading" class="flex items-center justify-center py-20">
      <Loader2 class="w-10 h-10 animate-spin text-indigo-600" />
    </div>

    <div v-else-if="!selectedContract">
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

      <div class="flex flex-col sm:flex-row gap-4 mb-6">
        <div class="relative flex-grow">
          <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Search class="h-4 w-4 text-gray-400" />
          </div>
          <input v-model="searchQuery" type="text" class="block w-full rounded-md border-0 py-2 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-indigo-600 sm:text-sm shadow-sm" placeholder="Search by PO number or tender title..." />
        </div>
        <button class="inline-flex items-center gap-2 rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-gray-300 hover:bg-gray-50">
          <Filter class="h-4 w-4 text-gray-500" /> Filters
        </button>
      </div>

      <div class="border-b border-gray-200 mb-6">
        <nav class="-mb-px flex space-x-8">
          <button v-for="tab in tabs" :key="tab" @click="activeTab = tab" :class="[activeTab === tab ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-all']">
            {{ tab }}
          </button>
        </nav>
      </div>

      <div class="space-y-4">
        <div v-for="contract in processedOrders" :key="contract.id" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex flex-col sm:flex-row justify-between gap-4">
            <div class="flex gap-4">
  <div class="h-10 w-10 rounded-lg bg-indigo-50 flex items-center justify-center shrink-0">
    <FileText class="h-5 w-5 text-indigo-600" />
  </div>
  
  <div>
    <h3 class="text-base font-bold text-gray-900 leading-tight">{{ contract.title }}</h3>
    
    <div class="text-xs text-gray-500 flex items-center gap-2 mt-1">
      <span>{{ contract.id }}</span>
      <span class="text-gray-300">&bull;</span>
      <span>{{ contract.date }}</span>
    </div>

    <div class="mt-4 flex flex-wrap gap-6 text-sm">
      <span class="font-bold text-gray-900">{{ formatCurrency(contract.value) }}</span>
      
      <span class="text-gray-500">
        Delivery: <span class="text-gray-900 font-medium">{{ contract.deliveryDate }}</span>
      </span>
      
    </div>
  </div>
</div>

         

              <div class="flex items-center gap-2">
               <span 
                class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset"
                :class="[
                  contract.status === 'Active' ? 'bg-blue-50 text-blue-700 ring-blue-700/10' : 
                  contract.status === 'Completed' ? 'bg-green-50 text-green-700 ring-green-600/20' : 
                  'bg-orange-50 text-orange-700 ring-orange-600/20'
                ]"
              >
                {{ contract.status }}
              </span>
                <button 
                  @click="viewContract(contract)" 
                  class="rounded-md bg-white px-3 py-1.5 text-xs font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 text-center min-w-[70px] transition-colors"
                >
                  View
                </button>
                <button 
                @click.stop="handleDownloadBlanketOrder(contract.internalName)" 
                class="p-1.5 text-gray-400 hover:text-indigo-600 border border-gray-200 rounded-lg transition-colors"
                title="Download Blanket Order"
              >
                <Download class="w-4 h-4" />
              </button>
              </div>
          </div>

          <div class="mt-6">
         <div class="flex justify-between text-xs mb-1">
            <span class="text-gray-500">Delivery Progress</span>
            <span class="font-medium text-gray-900">{{ contract.progress || 0 }}%</span>
         </div>
         <div class="w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
            <div 
               class="bg-indigo-600 h-1.5 rounded-full transition-all duration-700 ease-out" 
               :style="{ width: (contract.progress || 0) + '%' }"
            ></div>
         </div>
         </div>
        </div>
      </div>
    </div>

    <div v-else class="animate-in fade-in slide-in-from-bottom-2 duration-500">
      <nav class="flex mb-4 text-sm text-gray-500 items-center gap-2">
        <button @click="closeDetail" class="hover:text-indigo-600 transition-colors">Dashboard</button>
        <span>/</span>
        <button @click="closeDetail" class="hover:text-indigo-600 transition-colors">Contracts</button>
        <span>/</span>
        <span class="text-gray-900 font-medium">{{ selectedContract.id }}</span>
      </nav>

      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <div class="flex items-center gap-3">
            <h1 class="text-2xl font-bold text-gray-900">{{ selectedContract.id }}</h1>
            <span class="bg-blue-100 text-blue-800 px-2 py-0.5 rounded text-xs font-medium uppercase tracking-wide">Active</span>
          </div>
          <p class="text-gray-500 mt-1">{{ selectedContract.title }}</p>
          <div class="flex items-center gap-1 mt-2 text-sm text-gray-500">
             Tender ID: <a href="#" class="text-indigo-600 hover:underline">{{ selectedContract.tenderId }}</a>
          </div>
        </div>

        <div class="flex flex-wrap gap-3">
          <button 
            @click="handlePrint" 
            class="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-lg border border-gray-200 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 transition-colors"
          >
            <Printer class="w-4 h-4" /> 
            <span>Print</span>
          </button>

          <button 
            @click="handleDownloadPO" 
            class="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-lg border border-gray-200 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 transition-colors"
          >
            <Download class="w-4 h-4" /> 
            <span>Download PO</span>
          </button>

          <button class="inline-flex items-center gap-2 bg-indigo-600 px-4 py-2 rounded-lg text-white text-sm font-semibold shadow-sm hover:bg-indigo-700 transition-colors">
            <MessageSquare class="w-4 h-4" /> 
            <span>Contact Buyer</span>
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
          <div class="flex items-center gap-3 mb-3">
            <div class="p-2 bg-indigo-50 rounded-lg text-indigo-600"><CreditCard class="w-5 h-5" /></div>
            <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Contract Value</span>
          </div>
          <div class="text-xl font-bold text-gray-900">{{ formatCurrency(selectedContract.value) }}</div>
        </div>

        <div class="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
          <div class="flex items-center gap-3 mb-3">
            <div class="p-2 bg-green-50 rounded-lg text-green-600"><TrendingUp class="w-5 h-5" /></div>
            <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Amount Received</span>
          </div>
          <div class="text-xl font-bold text-gray-900">{{ formatCurrency(selectedContract.amountReceived) }}</div>
        </div>

        <div class="bg-white p-6 rounded-xl border border-gray-100 shadow-sm flex flex-col justify-between min-h-[120px]">
          <div class="flex items-center gap-3 mb-3">
            <div class="p-2 bg-orange-300 rounded-lg">
              <Package class="w-5 h-5 text-orange-600" />
            </div>
            <span class="text-xs font-medium text-gray-900 uppercase tracking-wider">
              Delivery Progress
            </span>
          </div>

          <div class="mt-4">
            <div class="text-xl font-bold text-gray-900">
              {{ selectedContract.deliveryCount }}/{{ selectedContract.totalItems }} Items
            </div>
          </div>
        </div>

        <div class="bg-white p-5 rounded-xl border border-gray-100 shadow-sm">
          <div class="flex items-center gap-3 mb-3">
            <div class="p-2 bg-blue-50 rounded-lg text-blue-600"><Calendar class="w-5 h-5" /></div>
            <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Delivery Deadline</span>
          </div>
          <div class="text-xl font-bold text-gray-900">{{ selectedContract.deliveryDate }}</div>
        </div>
      </div>

      <div class="border-b border-gray-200 mb-6">
        <nav class="-mb-px flex space-x-8">
          <button v-for="tab in detailTabs" :key="tab" @click="activeDetailTab = tab" :class="[activeDetailTab === tab ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-all']">
            {{ tab }}
          </button>
        </nav>
      </div>

        <div v-if="activeDetailTab === 'Overview'" class="grid grid-cols-1 lg:grid-cols-2 gap-8 animate-in fade-in duration-500">
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div class="flex items-center gap-2 mb-6 text-gray-900 font-bold"><FileText class="w-5 h-5" /> Contract Details</div>
          <div class="grid grid-cols-2 gap-y-6 text-sm">
            <div><p class="text-gray-500 mb-1">PO Number</p><p class="font-medium">{{ selectedContract.id }}</p></div>
            <div><p class="text-gray-500 mb-1">PO Date</p><p class="font-medium">{{ selectedContract.date }}</p></div>
            <div><p class="text-gray-500 mb-1">Tender ID</p><p class="font-medium text-indigo-600 underline">{{ selectedContract.tenderId }}</p></div>
            <div><p class="text-gray-500 mb-1">Payment Terms</p><p class="font-medium">{{ selectedContract.paymentTerms }}</p></div>
          </div>
          <div class="mt-8">
            <div class="flex justify-between text-xs mb-2 font-medium"><span class="text-gray-500">Delivery Progress</span><span>{{ selectedContract.progress }}%</span></div>
            <div class="w-full bg-gray-100 h-2 rounded-full overflow-hidden"><div class="h-full bg-indigo-600" :style="{ width: selectedContract.progress + '%' }"></div></div>
          </div>
          <div class="mt-6"> 
            <div class="flex justify-between text-xs mb-2 font-medium"><span class="text-gray-500">Payment Progress</span><span>{{ selectedContract.paymentProgress || 0 }}%</span></div>
            <div class="w-full bg-gray-100 h-2 rounded-full overflow-hidden"><div class="h-full bg-blue-600" :style="{ width: (selectedContract.paymentProgress || 0) + '%' }"></div></div>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div class="flex items-center gap-2 mb-6 text-gray-900 font-bold"><UserCircle class="w-5 h-5" /> Buyer Information</div>
          <div class="mb-4">
            <h3 class="text-lg font-bold text-gray-900">{{ selectedContract.buyer.name }}</h3>
            <p class="text-sm text-gray-500">{{ selectedContract.buyer.division }}</p>
          </div>
          <div class="space-y-3 text-sm text-gray-600">
            <p>{{ selectedContract.buyer.phone }}</p>
            <p>{{ selectedContract.buyer.email }}</p>
            <p>{{ selectedContract.buyer.address }}</p>
          </div>
          <button class="mt-6 w-full py-2.5 rounded-lg border border-gray-200 text-sm font-semibold hover:bg-gray-50 transition-colors">Send Message</button>
        </div>
      </div>

      <div v-if="activeDetailTab === 'Line Items'" class="animate-in fade-in duration-500">
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 font-bold text-gray-900 text-lg">Line Items</div>
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th class="px-6 py-3">Description</th>
                  <th class="px-6 py-3 text-center">Qty</th>
                  <th class="px-6 py-3 text-center">Unit</th>
                  <th class="px-6 py-3 text-right">Unit Price</th>
                  <th class="px-6 py-3 text-right">Total</th>
                  <th class="px-6 py-3 text-center">Delivered</th>
                  <th class="px-6 py-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="item in selectedContract.items" :key="item.item_code" class="hover:bg-gray-50 transition-colors">
                  <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ item.item_code }}</td>
                  <td class="px-6 py-4 text-center text-sm text-gray-600">{{ item.qty }}</td>
                  <td class="px-6 py-4 text-center text-sm text-gray-600">{{ item.uom }}</td>
                  <td class="px-6 py-4 text-right text-sm text-gray-600">{{ formatCurrency(item.rate) }}</td>
                  <td class="px-6 py-4 text-right text-sm font-bold text-gray-900">{{ formatCurrency(item.custom_amount) }}</td>
                  <td class="px-6 py-4 text-center text-sm text-gray-600">{{ item.delivered }}</td>
                  <td class="px-6 py-4 text-center text-sm text-gray-600">{{ item.status }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="px-6 py-6 bg-gray-50 border-t flex justify-end">
            <div class="text-right">
              <span class="text-xs font-medium text-gray-500 uppercase">Total Contract Value</span>
              <div class="text-2xl font-bold text-gray-900">{{ formatCurrency(selectedContract.value) }}</div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="activeDetailTab === 'Payments'" class="animate-in fade-in duration-500">
        <div class="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
          <div class="px-6 py-4 border-b border-gray-100 font-bold text-gray-900 text-lg">
            Payment History
          </div>
          
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr class="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <th class="px-6 py-3">Payment ID</th>
                  <th class="px-6 py-3">Posting Date</th>
                  <th class="px-6 py-3 text-right">Amount</th>
                  <th class="px-6 py-3 text-center">Status</th>
                  <th class="px-6 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="pay in payments" :key="pay.id" class="hover:bg-gray-50 transition-colors">
                  <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ pay.id }}</td>
                  <td class="px-6 py-4 text-sm text-gray-600">{{ pay.date }}</td>
                  <td class="px-6 py-4 text-right text-sm text-gray-600">
                    {{ formatCurrency(pay.amount) }}
                  </td>
                  <td class="px-6 py-4 text-center">
                    <span 
                      :class="[
                        pay.status === 'Paid' ? 'bg-green-50 text-green-700 ring-green-600/20' : 'bg-orange-50 text-orange-700 ring-orange-600/20'
                      ]" 
                      class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset"
                    >
                      {{ pay.status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-right">
              <button 
                @click="downloadPaymentEntry(pay.id)" 
                class="p-1.5 text-gray-400 hover:text-indigo-600 transition-colors"
                title="Download Invoice"
              >
                <Download class="w-4 h-4" />
              </button>
            </td>
                </tr>
                <tr v-if="payments && payments.length === 0">
                  <td colspan="4" class="px-6 py-10 text-center text-sm text-gray-500">
                    No payment entries found for this contract.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="px-6 py-6 bg-gray-50 border-t border-gray-100">
      <div class="flex justify-between items-end">
        <div class="text-left">
          <span class="text-xs font-medium text-gray-500 uppercase tracking-wider">Total Value</span>
          <div class="text-lg font-bold text-gray-900">
            {{ formatCurrency(selectedContract.value) }}
          </div>
        </div>

        <div class="flex gap-12 text-right">
          <div>
            <span class="text-xs font-medium text-green-600 uppercase tracking-wider">Amount Received</span>
            <div class="text-lg font-bold text-green-600">
              {{ formatCurrency(selectedContract.amountReceived) }}
            </div>
          </div>

        </div>
      </div>
    </div>
    </div>
  </div>

 <div v-if="activeDetailTab === 'Documents'" class="p-6">
    <div v-if="selectedContract.documents && selectedContract.documents.length > 0" class="space-y-4">
        <div v-for="doc in selectedContract.documents" :key="doc.id" 
             class="flex items-center justify-between p-4 bg-white border border-gray-100 rounded-xl hover:shadow-md transition-shadow">
            <div class="flex items-center gap-4">
                <div class="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
                    <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                </div>
                <div>
                    <h4 class="text-sm font-bold text-gray-900">{{ doc.name }}</h4>
                    <p class="text-xs text-gray-500">Uploaded: {{ doc.date }}</p>
                </div>
            </div>
            <a :href="doc.file_url" target="_blank" 
               class="px-4 py-2 text-xs font-semibold text-indigo-600 bg-indigo-50 rounded-lg hover:bg-indigo-100 transition-colors">
                View File
            </a>
        </div>
    </div>
    
    <div v-else class="flex flex-col items-center justify-center py-20 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
        <h3 class="text-sm font-medium text-gray-900">No Documents Found</h3>
        <p class="text-xs text-gray-500 mt-1">There are no files attached to this contract yet.</p>
    </div>
</div>

</div> 
</div>
  </template>