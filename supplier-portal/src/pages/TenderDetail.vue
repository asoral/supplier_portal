<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, BadgeCheck, Clock, Download, Share2, Printer, 
  AlertCircle, DollarSign, Calendar, MapPin, Building2, UserCircle, FileText,
  TrendingDown, Banknote, Hourglass, Bookmark, ArrowRight, Zap ,MessageSquare
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const isLoading = ref(true)
const goToQueries = () => {
  // This navigates to the Queries page based on your project structure
  // Usually, this is /queries or /supplier-portal/queries
  router.push('/queries') 
}


// Initialize tender as null so we can check if data has arrived
const tender = ref(null)

// API Fetching Logic
const fetchTenderDetails = async () => {
  isLoading.value = true
  try {
    const response = await fetch('/api/method/supplier_portal.api.get_tender_details?' + new URLSearchParams({
        name: route.params.id
    }), { credentials: 'include' }) // include credentials for auth check
    
    const result = await response.json()
    // Frappe custom API returns data in result.message
    const data = result.message

    if (!data) {
        throw new Error("No data returned")
    }

    // Map the API structure to UI variables
    tender.value = {
      id: data.name,
      title: data.title,
      publishedDate: data.publish_date ? new Date(data.publish_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : 'N/A',
      location: data.billing_address ,
      category: data.category,
      status: data.status,
      // Status 'Active' plus explicit enable check
      liveBidding: data.status === 'Active' && data.enable_live_bidding,
      description: data.description ,
      quantity: data.total_quantity ,
      bidsReceived: data.bidsReceived || 0, // Fallback if field missing
      estBudget: data.total_budget ,
      deadline: data.submission_date ,
      department: data.department ,
      currentLowestBid: data.total_budget , // Placeholder until we have sorting logic for bids
      minBidDecrement: data.min_bid_decrement ,
      emdRequired: data.emd_amount ,
      termsData: data.terms || 'No terms and conditions provided.',
      autoExtension: data.auto_extension_limit ? data.auto_extension_limit + ' mins' : '0 mins',
      deliveryDate: data.schedule_date,
      
      // Dynamic Data from Child Tables
      items: data.items || [],
      documents: (data.documents || []).map(d => ({
          name: d.file_name,
          url: d.file_url,
          size: d.file_size + ' bytes' // Simple formatting
      })),

      // Dynamic Timeline
      timeline: [
        { stage: 'Published', date: data.publish_date, completed: !!data.publish_date },
        { stage: 'Bid Submission Starts', date: data.submission_start_date, completed: new Date() > new Date(data.submission_start_date) },
        { stage: 'Submission Ends', date: data.submission_date, completed: new Date() > new Date(data.submission_date) },
        { stage: 'Result Declaration', date: data.result_date, completed: false },
        { stage: 'Delivery Expected', date: data.schedule_date, completed: false }
      ].filter(t => t.date), // Filter out steps with no date
      
      similarTenders: [] // Logic for similars would need another API call
    }
  } catch (error) {
    console.error("Failed to fetch tender details:", error)
  } finally {
    isLoading.value = false
  }
}

const activeTab = ref('Overview')
const tabs = ['Overview', 'Specifications', 'Documents', 'Timeline']

const bidAmount = ref()

const placeBid = () => {
   alert(`Bid placed for ₹${bidAmount.value}`)
}

const quickBid = (amount) => {
   if (tender.value && tender.value.currentLowestBid) {
      bidAmount.value = tender.value.currentLowestBid - amount
   }
}

// Computed properties with safety checks
const formattedBudget = computed(() => {
   if (!tender.value) return '₹0'
   return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(tender.value.estBudget)
})

const formattedLowestBid = computed(() => {
   if (!tender.value) return '₹0'
   return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(tender.value.currentLowestBid)
})

const mainBoqUrl = computed(() => {
   if (!tender.value || !tender.value.items) return null
   const itemWithBoq = tender.value.items.find(i => i.attach_boq)
   return itemWithBoq ? itemWithBoq.attach_boq : null
})

onMounted(() => {
  fetchTenderDetails()
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 pb-12">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center min-h-[60vh]">
        <div class="flex flex-col items-center gap-4">
            <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600"></div>
            <p class="text-gray-500 text-sm font-medium">Loading tender details...</p>
        </div>
    </div>

    <div v-else-if="!tender" class="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
        <AlertCircle class="w-12 h-12 text-red-500 mb-4" />
        <h3 class="text-lg font-bold text-gray-900">Tender Not Found</h3>
        <p class="text-gray-500 mt-2 max-w-md">The tender you are looking for does not exist or you do not have permission to view it.</p>
        <button @click="router.push('/tenders')" class="mt-6 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition">Back to Tenders</button>
    </div>

    <!-- Main Content -->
    <div v-else>
     <!-- Header/Breadcrumb -->
     <div class="bg-white border-b border-gray-200">
       <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
         <button @click="router.back()" class="flex items-center text-sm text-gray-500 hover:text-gray-900 mb-4 transition-colors">
           <ArrowLeft class="w-4 h-4 mr-1" /> Back to Tenders
         </button>
         
         <div class="flex flex-col md:flex-row md:items-start justify-between gap-4">
           <div>
             <div class="flex flex-wrap gap-2 mb-3">
                <span class="inline-flex items-center rounded-md bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600">
                   {{ tender.category }}
                </span>
                <span class="inline-flex items-center rounded-md bg-indigo-50 px-2.5 py-0.5 text-xs font-medium text-indigo-700 border border-indigo-100">
                   {{ tender.status }}
                </span>
                <span v-if="tender.liveBidding" class="inline-flex items-center rounded-md bg-orange-50 px-2.5 py-0.5 text-xs font-medium text-orange-700 border border-orange-100">
                   <span class="relative flex h-2 w-2 mr-1.5">
                     <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
                     <span class="relative inline-flex rounded-full h-2 w-2 bg-orange-500"></span>
                   </span>
                   Live Bidding
                </span>
             </div>
             <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ tender.title }}</h1>
             <div class="flex flex-wrap items-center gap-4 text-xs text-gray-500">
                <span class="flex items-center gap-1"><BadgeCheck class="w-3.5 h-3.5" /> {{ tender.id }}</span>
                <span class="flex items-center gap-1"><Calendar class="w-3.5 h-3.5" /> Published: {{ tender.publishedDate }}</span>
                <span class="flex items-center gap-1"><MapPin class="w-3.5 h-3.5" /> {{ tender.location }}</span>
                <span class="flex items-center gap-1"><UserCircle class="w-3.5 h-3.5" /> {{ tender.views || 0 }} views</span>
             </div>
           </div>
           
           <div class="flex gap-2">
              <button class="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 border border-transparent hover:border-gray-200">
                 <Share2 class="w-4 h-4" />
              </button>
              <button class="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 border border-transparent hover:border-gray-200">
                 <Printer class="w-4 h-4" />
              </button>
           </div>
         </div>
         
         <!-- Tabs -->
         <div class="flex gap-6 mt-8 border-b border-gray-100">
            <button 
               v-for="tab in tabs" 
               :key="tab"
               @click="activeTab = tab"
               class="pb-3 text-sm font-medium border-b-2 transition-colors"
               :class="activeTab === tab ? 'border-indigo-600 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700'"
             >
               {{ tab }}
            </button>
         </div>
       </div>
     </div>
 
     <!-- Main Body -->
     <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
       <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          <!-- Left Column (Details) -->
          <div class="lg:col-span-2 space-y-6">
             
             <!-- OVERVIEW TAB -->
             <div v-if="activeTab === 'Overview'" class="space-y-6">
                 <!-- Description -->
                <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Description</h3>
                
                <div 
                   class="text-sm text-gray-600 leading-relaxed mb-8" 
                   v-html="tender.description || 'No description provided.'"
                ></div>
 
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                   <div class="p-4 bg-blue-50 rounded-lg border border-blue-100 flex items-center gap-3">
                      <div class="p-2 bg-blue-100 rounded-lg text-blue-600">
                      <TrendingDown class="w-5 h-5" />
                      </div>
                      <div>
                      <div class="text-xs text-blue-600 font-medium mb-0.5">Min Bid Decrement</div>
                      <div class="text-sm font-bold text-gray-900">
                         ₹{{ tender.minBidDecrement?.toLocaleString('en-IN') || 0 }}
                      </div>
                      </div>
                   </div>
 
                   <div class="p-4 bg-green-50 rounded-lg border border-green-100 flex items-center gap-3">
                      <div class="p-2 bg-green-100 rounded-lg text-green-600">
                      <Banknote class="w-5 h-5" />
                      </div>
                      <div>
                      <div class="text-xs text-green-600 font-medium mb-0.5">EMD Required</div>
                      <div class="text-sm font-bold text-gray-900">
                         ₹{{ tender.emdRequired?.toLocaleString('en-IN') || 0 }}
                      </div>
                      </div>
                   </div>
 
                   <div class="p-4 bg-orange-50 rounded-lg border border-orange-100 flex items-center gap-3">
                      <div class="p-2 bg-orange-100 rounded-lg text-orange-600">
                      <Hourglass class="w-5 h-5" />
                      </div>
                      <div>
                      <div class="text-xs text-orange-600 font-medium mb-0.5">Auto Extension</div>
                      <div class="text-sm font-bold text-gray-900">
                         {{ tender.autoExtension || '0 mins' }}
                      </div>
                      </div>
                   </div>
                </div>
                </div>
 
                 <!-- Terms -->
                <div class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <h3 class="text-lg font-semibold text-gray-900 mb-4">Terms & Conditions</h3>
 
                <div 
                   class="prose prose-sm max-w-none text-gray-600 leading-relaxed" 
                   v-html="tender.termsData"
                ></div>
                </div>
                 
                  <!-- Similar Tenders -->
                  <div v-if="tender.similarTenders && tender.similarTenders.length > 0" class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <Bookmark class="w-4 h-4 text-gray-400" /> Similar Tenders
                    </h3>
                    <div class="space-y-3">
                       <div v-for="sim in tender.similarTenders" :key="sim.id" class="flex items-center justify-between p-4 rounded-lg border border-gray-100 hover:border-indigo-200 hover:bg-slate-50 transition-colors cursor-pointer group">
                          <div>
                             <div class="text-sm font-bold text-gray-900 group-hover:text-indigo-600">{{ sim.title }}</div>
                             <div class="text-xs text-gray-500 mt-1">Budget: {{ sim.budget }} • Deadline: {{ sim.deadline }}</div>
                          </div>
                          <ArrowRight class="w-4 h-4 text-gray-400 group-hover:text-indigo-600" />
                       </div>
                    </div>
                 </div>
             </div>
 
             <!-- SPECIFICATIONS TAB -->
             <div v-if="activeTab === 'Specifications'" class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <h3 class="text-lg font-semibold text-gray-900 mb-6">Technical Specifications</h3>
                <div class="space-y-4">
                   <div v-if="tender.items.length === 0" class="text-gray-500 italic">No items specified.</div>
                   <div v-for="(item, idx) in tender.items" :key="idx" class="p-4 bg-gray-50 rounded-lg border border-gray-100 flex items-start gap-3">
                      <BadgeCheck class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                      <div class="flex-grow">
                         <span class="text-sm font-semibold text-gray-900 block">{{ item.item_name }} ({{ item.item_code }})</span>
                         <div class="text-xs text-gray-500 mt-1" v-if="item.description" v-html="item.description"></div>
                         <div class="mt-2 flex gap-4 text-xs font-medium text-gray-700 items-center">
                             <span class="bg-white px-2 py-1 rounded border border-gray-200">Qty: {{ item.qty }} {{ item.uom }}</span>
                             <span v-if="item.budget" class="bg-white px-2 py-1 rounded border border-gray-200">Budget Rate: ₹{{ item.budget }}</span>
                             <a v-if="item.attach_boq" :href="item.attach_boq" target="_blank" class="flex items-center gap-1 text-indigo-600 hover:text-indigo-800 hover:underline">
                                 <Download class="w-3 h-3" /> Download BOQ
                             </a>
                         </div>
                      </div>
                   </div>
                </div>
 
                <div class="mt-8">
                   <h3 class="text-lg font-semibold text-gray-900 mb-4">Delivery Requirements</h3>
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                       <div class="p-4 border border-gray-200 rounded-lg">
                          <div class="text-xs text-gray-500 mb-1">Delivery Location</div>
                          <div class="font-medium text-gray-900">Delhi NCR</div>
                       </div>
                       <div class="p-4 border border-gray-200 rounded-lg">
                          <div class="text-xs text-gray-500 mb-1">Expected Delivery Date</div>
                          <div class="font-medium text-gray-900">15 March 2024</div>
                       </div>
                       <div class="p-4 border border-gray-200 rounded-lg">
                          <div class="text-xs text-gray-500 mb-1">Delivery Terms</div>
                          <div class="font-medium text-gray-900">FOR Destination</div>
                       </div>
                       <div class="p-4 border border-gray-200 rounded-lg">
                          <div class="text-xs text-gray-500 mb-1">Inspection</div>
                          <div class="font-medium text-gray-900">Before Dispatch + At Site</div>
                       </div>
                    </div>
                </div>
             </div>
 
             <!-- DOCUMENTS TAB -->
             <div v-if="activeTab === 'Documents'" class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <h3 class="text-lg font-semibold text-gray-900 mb-6">Tender Documents</h3>
                <div class="space-y-3">
                   <div v-if="!tender.documents || tender.documents.length === 0" class="text-gray-500 italic">No documents attached.</div>
                   <div v-for="(doc, idx) in tender.documents" :key="idx" class="flex items-center justify-between p-4 rounded-lg border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50/30 transition-all group">
                      <div class="flex items-center gap-4">
                         <div class="p-2 bg-red-50 rounded-lg text-red-500">
                            <FileText class="w-6 h-6" /> 
                         </div>
                         <div>
                            <div class="font-medium text-gray-900 group-hover:text-indigo-700">{{ doc.name }}</div>
                            <div class="text-xs text-gray-500">{{ doc.size }}</div>
                         </div>
                      </div>
                      <a :href="doc.url" target="_blank" class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-white rounded-full transition-colors shadow-sm">
                         <Download class="w-4 h-4" />
                      </a>
                   </div>
                </div>
             </div>
 
             <!-- TIMELINE TAB -->
             <div v-if="activeTab === 'Timeline'" class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <h3 class="text-lg font-semibold text-gray-900 mb-6">Tender Timeline</h3>
                <div class="relative pl-4">
                   <!-- Vertical Line -->
                   <div class="absolute left-[27px] top-4 bottom-4 w-0.5 bg-gray-200"></div>
 
                   <div v-for="(step, idx) in tender.timeline" :key="idx" class="relative flex gap-6 mb-8 last:mb-0">
                      <div class="relative z-10 flex-shrink-0 w-6 h-6 rounded-full border-2 flex items-center justify-center bg-white" 
                           :class="step.completed ? 'border-indigo-600 bg-indigo-50' : 'border-gray-300'">
                         <div v-if="step.completed" class="w-2.5 h-2.5 rounded-full bg-indigo-600"></div>
                      </div>
                      <div class="flex-grow pt-0.5">
                         <h4 class="text-sm font-bold text-gray-900">{{ step.stage }}</h4>
                         <p class="text-xs text-gray-500 mt-1">{{ step.date }}</p>
                      </div>
                      <div v-if="step.completed" class="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded self-start">
                         Completed
                      </div>
                   </div>
                </div>
             </div>
 
             <!-- Similar Tenders (Always Visible) -->
              <div v-if="tender.similarTenders && tender.similarTenders.length > 0" class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                   <Share2 class="w-4 h-4 text-gray-400" /> Similar Tenders
                </h3>
                <div class="space-y-3">
                   <div v-for="sim in tender.similarTenders" :key="sim.id" class="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:border-indigo-200 hover:bg-slate-50 transition-colors cursor-pointer">
                      <div>
                         <div class="text-sm font-medium text-gray-900">{{ sim.title }}</div>
                         <div class="text-xs text-gray-500 mt-1">Budget: {{ sim.budget }} • Deadline: {{ sim.deadline }}</div>
                      </div>
                      <ArrowLeft class="w-4 h-4 text-gray-400 rotate-180" />
                   </div>
                </div>
             </div>
 
          </div>
 
          <!-- Right Column (Stats & Actions) -->
          <div class="lg:col-span-1 space-y-6">
             
             
          <!-- Summary Card -->
             <div class="bg-white rounded-xl border border-gray-200 px-6 py-6 shadow-sm relative overflow-hidden">
                <h3 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">Tender Summary</h3>
                
                <div class="grid grid-cols-2 gap-y-4 gap-x-2 text-sm mb-6">
                   <div>
                      <div class="text-xs text-gray-500 mb-0.5">Quantity</div>
                      <div class="font-semibold text-gray-900">{{ tender.quantity }}</div>
                   </div>
                    <div>
                      <div class="text-xs text-gray-500 mb-0.5">Bids Received</div>
                      <div class="font-semibold text-gray-900">{{ tender.bidsReceived }}</div>
                   </div>
                    <div>
                      <div class="text-xs text-gray-500 mb-0.5">Est. Budget</div>
                      <div class="font-semibold text-gray-900">{{ formattedBudget }}</div>
                   </div>
                    <div>
                      <div class="text-xs text-gray-500 mb-0.5">Delivery Date</div>
                      <div class="font-semibold text-gray-900">{{ tender.deliveryDate }}</div>
                   </div>
                </div>
 
                <div class="pt-4 border-t border-gray-100 mb-6">
                   <div class="flex items-center gap-2 text-xs text-red-600 mb-1 font-medium">
                      <Clock class="w-3.5 h-3.5" /> Deadline
                   </div>
                   <div class="text-sm font-bold text-gray-900 mb-1">{{ tender.deadline }}</div>
                    <div class="text-xs text-gray-500">Department: {{ tender.department }}</div>
                </div>
 
                <button class="w-full bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold py-2.5 rounded-lg shadow-sm transition-colors mb-3 flex items-center justify-center gap-2">
                  <BadgeCheck class="w-4 h-4" /> Submit Your Bid
               </button>

               <div class="flex items-center gap-2">
                  <a :href="mainBoqUrl || '#'" target="_blank" 
                     class="flex-grow bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 text-sm font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 cursor-pointer no-underline">
                     <Download class="w-4 h-4 text-gray-500" /> Download BOQ
                  </a>

                  <button 
                  @click="goToQueries"
                  class="p-2.5 bg-white border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors shadow-sm"
                  title="View Queries"
               >
                  <MessageSquare class="w-5 h-5" />
               </button>
               </div>
            </div>
            
            
             <!-- Live Bidding Card -->
             <div v-if="tender.liveBidding" class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm ring-1 ring-gray-200">
                 <div class="flex items-center justify-between mb-6">
                    <div class="inline-flex items-center rounded-full bg-red-50 px-3 py-1 text-xs font-semibold text-red-600 ring-1 ring-inset ring-red-600/20">
                       <span class="relative flex h-2 w-2 mr-2">
                         <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                         <span class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
                       </span>
                       Live Bidding Active
                    </div>
                    <span class="text-xs text-gray-400">Updated 2s ago</span>
                 </div>
 
                 <div class="text-center py-6 bg-white rounded-xl border-2 border-green-500/20 mb-6 shadow-[0_0_15px_rgba(34,197,94,0.1)]">
                   <div class="text-xs text-gray-500 font-medium mb-1 uppercase tracking-wider">Current Lowest Bid</div>
                   <div class="text-3xl font-bold text-green-600 tracking-tight">{{ formattedLowestBid }}</div>
                    <div class="text-xs font-medium text-green-600 mt-1 flex items-center justify-center gap-1">
                       <TrendingDown class="w-3 h-3" /> ₹20,000 below budget
                    </div>
                 </div>
 
                 <div class="space-y-4">
                    <div>
                       <label class="text-xs font-semibold text-gray-700 mb-2 block">Enter Your Bid Amount</label>
                       <div class="flex gap-2">
                          <div class="relative flex-grow">
                             <span class="absolute left-3 top-2.5 text-gray-400">₹</span>
                             <input v-model="bidAmount" type="number" class="w-full pl-7 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-400 focus:border-amber-400" placeholder="Enter amount">
                          </div>
                          <button @click="placeBid" class="bg-amber-400 hover:bg-amber-500 text-amber-950 px-6 py-2 rounded-lg text-sm font-bold shadow-sm transition-colors whitespace-nowrap">Place Bid</button>
                       </div>
                    </div>
                    
                    <button @click="quickBid(tender.minBidDecrement)" class="w-full group flex items-center justify-center gap-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 text-gray-600 text-xs font-semibold py-2.5 rounded-lg transition-all">
                       <Zap class="w-3 h-3 text-amber-500 group-hover:text-amber-600" />
                       Quick bid: ₹{{ (tender.currentLowestBid - tender.minBidDecrement).toLocaleString() }}
                    </button>
                 </div>
 
                 <div class="mt-8 pt-6 border-t border-gray-100">
                    <h4 class="text-xs font-bold text-gray-900 mb-4">Recent Bid Activity</h4>
                    <div class="space-y-3">
                       <div v-for="(bid, idx) in tender.recentBids" :key="idx" class="flex items-center justify-between text-xs pb-3 border-b border-gray-50 last:border-0 last:pb-0">
                          <span class="font-medium text-gray-600">{{ bid.vendor }}</span>
                          <div class="text-right">
                             <div class="font-bold text-green-600">₹{{ bid.amount.toLocaleString() }}</div>
                             <span class="text-gray-400 text-[10px]">{{ bid.time }}</span>
                          </div>
                       </div>
                    </div>
                 </div>
             </div>
 
             <!-- Help Box -->
             <div class="bg-indigo-900 rounded-xl p-6 text-white text-center">
                <h4 class="font-bold text-sm mb-2">Need Help?</h4>
                <p class="text-xs text-indigo-200 mb-4 leading-relaxed">Have questions about this tender? Contact our support team.</p>
                <button class="w-full bg-white text-indigo-900 text-xs font-bold py-2 rounded-lg shadow-sm hover:bg-indigo-50 transition-colors flex items-center justify-center gap-2">
                   Contact Support
                </button>
             </div>
 
          </div>
       </div>
     </div>
    </div>
  </div>
</template>
