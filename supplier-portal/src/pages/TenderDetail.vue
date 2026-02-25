<script setup>
import { ref, onMounted, computed , watch} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  ArrowLeft, BadgeCheck, Clock, Download, Share2, Printer, 
  AlertCircle, DollarSign, Calendar, MapPin, Building2, UserCircle, FileText,
  TrendingDown, Banknote, Hourglass, Bookmark, ArrowRight, Zap ,MessageSquare
} from 'lucide-vue-next'
import { createToast } from 'mosha-vue-toastify'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const isLoading = ref(true)
const isSaved = ref(false)
const savedTendersList = ref([])
const isSessionExpired = ref(false)

const showSupportModal = ref(false);
const tenderDetails = ref({
  custom_contact_person_display: '',
  custom_contact_address_display: ''
});

const refetchSession = async () => {
   // Try to bounce the session
   isLoading.value = true;
   isSessionExpired.value = false;
   await authStore.logout(false); // Clean logout
   router.push('/login?redirect=' + route.fullPath);
}

// --- ADDED: Logic to check database on page load ---
const authStore = useAuthStore()
const { secureFetch } = authStore

// --- ADDED: Logic to check database on page load ---
const checkSavedStatus = async () => {
  // Only check if logged in
  if (!authStore.isAuthenticated) return;

  try {
    const response = await secureFetch('/api/method/supplier_portal.api.get_saved_tenders')
    const result = await response.json()
    const savedData = result.message || []
    
    // Find if this tender is in the list
    const existing = savedData.find(t => t.id === route.params.id)
    if (existing) {
      isSaved.value = true
      // Store the doc name (saved_id) so we can delete it later
      if (tender.value) tender.value.saved_record_name = existing.saved_id
    }
  } catch (error) {
    console.error("Error checking saved status:", error)
  }
}

const handleShare = async () => {
  if (navigator.share) {
    try {
      await navigator.share({
        title: selectedContract.value?.title || 'TenderFlow Document',
        text: `Check out this tender: ${selectedContract.value?.id}`,
        url: window.location.href, // Shares the current browser URL
      });
      console.log('Successfully shared');
    } catch (error) {
      console.error('Error sharing:', error);
    }
  } else {
    // Fallback: Copy link to clipboard if Share API is not supported (e.g., non-secure origins or old browsers)
    try {
      await navigator.clipboard.writeText(window.location.href);
      alert('Link copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy link:', err);
    }
  }
};

const handlePrint = () => {
  window.print();
};

const similarTenders = ref([])

const fetchSimilarTenders = async (category, currentId) => {
  try {
    const url = '/api/method/supplier_portal.api.get_similar_tenders?' + new URLSearchParams({
        category: category,
        exclude_id: currentId
    });
    
    const response = await secureFetch(url);
    const result = await response.json();
    
    if (result.message) {
      similarTenders.value = result.message.map(t => ({
        id: t.id,
        title: t.title, 
        budget: parseFloat(t.budget) || 0,
        deadline: t.deadline ? new Date(t.deadline).toLocaleDateString('en-IN', { 
            day: '2-digit', 
            month: 'short', 
            year: 'numeric' 
        }) : 'N/A'
      }));
    }
  } catch (error) {
    console.error("Error fetching similar tenders:", error);
  }
}

const navigateToTender = (tenderId) => {
  // Push the new ID to the router
  router.push(`/tenders/${tenderId}`).then(() => {
    // Force a scroll to the top so the user sees the new tender from the start
    window.scrollTo({ top: 0, behavior: 'smooth' });
    
    // Explicitly call your fetch function again because 
    // onMounted only runs once per component lifecycle
    fetchTenderDetails(); 
  });
}

const handleSave = async () => {
  if (!tender.value) return 

  // Double check auth just in case
  if (!authStore.isAuthenticated) {
      createToast('Please login to save tenders', { type: 'warning' })
      return
  }

  // If already blue, we Unsave (Delete)
  if (isSaved.value) {
    try {
      const response = await secureFetch('/api/method/supplier_portal.api.delete_saved_tender', {
        method: 'POST',
        body: JSON.stringify({
          saved_id: tender.value.saved_record_name
        })
      })
      const result = await response.json()
      
      if (response.ok && result.message?.status === 'success') {
        isSaved.value = false
        createToast('Removed from saved list', { type: 'info' })
      } else {
        console.error('Delete failed:', result)
        createToast('Failed to remove tender', { type: 'danger' })
      }
    } catch (error) {
      console.error('Delete error:', error)
    }
    return
  }

  // If not blue, we Save (Insert)
  try {
    const response = await secureFetch('/api/method/supplier_portal.api.save_tender', {
      method: 'POST',
      body: JSON.stringify({
        rfq_id: tender.value.id
      })
    })

    const result = await response.json()

    if (response.ok) {
        const msg = result.message;
        
        // Handle explicit error returned as JSON (e.g. from Guest save attempt)
        if (msg && msg.status === 'error') {
             createToast(msg.message || 'Error saving tender', { type: 'danger' })
             return
        }

        // Handle "Already saved" or "Success"
        if (msg && (msg.status === 'success' || msg.status === 'skipped')) {
             isSaved.value = true
             if (msg.name) {
                 tender.value.saved_record_name = msg.name
             } else {
                 await checkSavedStatus() 
             }
             createToast(msg.message || 'Tender saved successfully', { type: 'success' })
        } else {
             // Fallback for unexpected success structure
             createToast('Tender saved', { type: 'success' })
        }
    } else {
        console.error('Save failed:', result)
        createToast(result.message || 'Failed to save tender', { type: 'danger' })
    }
  } catch (error) {
    console.error('Save error:', error)
  }
}

const goToQueries = () => {
  router.push('/queries') 
}

const tender = ref(null)

const fetchTenderDetails = async () => {
  isLoading.value = true
  try {
    const response = await authStore.secureFetch('/api/method/supplier_portal.api.get_tender_details?' + new URLSearchParams({
        name: route.params.id
    }))
    
    if (!response.ok && (response.status === 403 || response.status === 401)) {
       isSessionExpired.value = true;
       throw new Error("Session Expired");
    }

    const result = await response.json()
    const data = result.message

    if (!data) throw new Error("No data returned")

    tenderDetails.value = {
      custom_contact_person_display: data.custom_contact_person_display,
      custom_contact_address_display: data.custom_contact_address_display
    }

    tender.value = {
      id: data.name,
      title: data.title,
      publishedDate: data.publish_date ? new Date(data.publish_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : 'N/A',
      location: data.billing_address ? data.billing_address.replace(/<br\s*\/?>/gi, ', ') : 'N/A',
      category: data.category,
      status: data.status,
      liveBidding: data.enable_live_bidding,
      description: data.description ,
      contactPerson: data.custom_contact_person_display,
      contactAddress: data.custom_contact_address_display,
      UOM:data.uom,
      quantity: data.total_quantity?.toLocaleString('en-IN') || 0,      
      bidsReceived: data.bidsReceived || 0,
      estBudget: data.total_budget ,
      deadline: data.submission_date ,
      department: data.department ,
      currentLowestBid: parseFloat(data.custom_total_budget_ || data.total_budget) || 0,
      minBidDecrement: data.min_bid_decrement ,
      emdRequired: data.emd_amount ,
      termsData: data.terms || 'No terms and conditions provided.',
      autoExtension: data.auto_extension_limit ? data.auto_extension_limit + ' mins' : '0 mins',
      deliveryDate: data.schedule_date,
      items: data.items || [],
      documents: (data.documents || []).map(d => ({
          name: d.file_name,
          url: d.file_url,
          size: d.file_size + ' bytes'
      })),
      timeline: [
        { stage: 'Published', date: data.publish_date, completed: !!data.publish_date },
        { stage: 'Bid Submission Starts', date: data.submission_start_date, completed: new Date() > new Date(data.submission_start_date) },
        { stage: 'Submission Ends', date: data.submission_date, completed: new Date() > new Date(data.submission_date) },
        { stage: 'Result Declaration', date: data.result_date, completed: false },
        { stage: 'Delivery Expected', date: data.schedule_date, completed: false }
      ].filter(t => t.date),
      similarTenders: []
    }
    if (data.category) {
            await fetchSimilarTenders(data.category, data.name)
        }
  } catch (error) {
    console.error("Failed to fetch tender details:", error)
  } finally {
    isLoading.value = false
  }
}

const openSupportModal = () => {
  showSupportModal.value = true;
}

const activeTab = ref('Overview')
const tabs = ['Overview', 'Specifications', 'Documents', 'Timeline']
const bidAmount = ref()
const recentBids = ref([]);
const portalSettings = ref({ quick_bid_percent: 0 });
const currentSupplier = ref('');


const quickBid = (amount) => {
   if (tender.value && tender.value.currentLowestBid) {
      bidAmount.value = tender.value.currentLowestBid - amount
   }
}

const totalBidsReceived = ref(0);

const fetchBidCount = async (rfqId) => {
  try {
    const response = await secureFetch(`/api/method/supplier_portal.api.get_tender_summary_stats?rfq_id=${rfqId}`);
    const result = await response.json();
    
    // Check if result.message is an object and extract total_bids
    if (result.message && typeof result.message === 'object') {
      totalBidsReceived.value = result.message.total_bids || 0;
    } else if (result.message !== undefined) {
      // Fallback if the API returns a direct number
      totalBidsReceived.value = result.message;
    }
  } catch (e) {
    console.error("Error fetching bid count:", e);
    totalBidsReceived.value = 0;
  }
};

const formattedBudget = computed(() => {
   if (!tender.value) return '₹0'
   return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(tender.value.estBudget)
})
const fetchSettings = async () => {
    try {
        const response = await fetch('/api/method/supplier_portal.api.get_portal_settings');
        const result = await response.json();
        // Frappe result is always in result.message
        if (result.message) {
            portalSettings.value = result.message;
        }
    } catch (e) {
        console.error("Failed to fetch settings", e);
    }
};

const formattedLowestBid = computed(() => {
  if (recentBids.value && recentBids.value.length > 0) {
    const minBid = Math.min(...recentBids.value.map(bid => bid.total || 0));
    return new Intl.NumberFormat('en-IN', { 
      style: 'currency', currency: 'INR', maximumFractionDigits: 0 
    }).format(minBid);
  }
  return new Intl.NumberFormat('en-IN', { 
    style: 'currency', currency: 'INR', maximumFractionDigits: 0 
  }).format(tender.value?.currentLowestBid || 0);
});

const fetchRecentBids = async (tId) => {
  if (!tId) return; // Prevent calling with undefined ID
  
  try {
    // Ensure you use secureFetch to pass the session cookie/headers
    const response = await secureFetch(`/api/method/supplier_portal.api.get_recent_bid_activity?rfq_id=${tId}`);
    const result = await response.json();
    
    // 1. Frappe always wraps the return in 'message'
    const data = result.message;

    // 2. Check if data exists and bids is an array (even if empty)
    if (data && Array.isArray(data.bids)) {
      
      // 3. Map the bids to your local state
      recentBids.value = data.bids.map(bid => ({
        supplier: bid.supplier,
        // Use the 'total' field mapped in your Python: "grand_total as total"
        total: parseFloat(bid.total) || 0,
        // Ensure formatBidTime handles the 'creation' string correctly
        time: formatBidTime(bid.creation) 
      }));

      // 4. CRITICAL: Store the current supplier ID for your HTML masking logic
      // Without this, {{ bid.supplier === currentSupplier }} will always be false
      currentSupplier.value = data.current_supplier || '';

      console.log("Bids updated:", recentBids.value);
      console.log("Current Supplier Identity:", currentSupplier.value);

    } else {
      console.warn("No bids data found in response:", result);
      recentBids.value = [];
    }
  } catch (error) {
    console.error("Fetch error in fetchRecentBids:", error);
    recentBids.value = [];
  }
};

const formatBidTime = (dateStr) => {
  const diffInMinutes = Math.floor((new Date() - new Date(dateStr)) / 60000);
  if (diffInMinutes < 1) return 'now';
  if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
  return `${Math.floor(diffInMinutes / 60)}h ago`;
}


const placeBid = async () => {
  if (!tender.value?.liveBidding) {
    createToast('Bidding is not currently active for this tender', { type: 'danger' });
    return;
  }
  
  if (!bidAmount.value || bidAmount.value <= 0) {
    createToast('Please enter a valid bid amount', { type: 'warning' });
    return;
  }

  // --- NEW: Min Bid Decrement Validation ---
  // 1. Determine current L1 from recent activity or initial budget
  const currentL1 = recentBids.value.length > 0 
  ? Math.min(...recentBids.value.map(b => b.total)) 
  : (tender.value?.currentLowestBid || 0);

// Ensure this field exists in your 'tender' object
const minDecrement = tender.value?.minBidDecrement || 0;
const maxAllowedBid = currentL1 - minDecrement;

console.log("Current L1:", currentL1, "Min Decrement:", minDecrement, "Max Allowed:", maxAllowedBid);

if (bidAmount.value > maxAllowedBid) {
    createToast(
      `Invalid Bid: You must bid ₹${maxAllowedBid.toLocaleString()} or lower (Min drop of ₹${minDecrement.toLocaleString()} required).`, 
      { 
        type: 'danger', 
        timeout: 5000,
        showIcon: true 
      }
    );
    return; // This stops the code from reaching the API call
  }

  try {
    isLoading.value = true;
    
    const response = await secureFetch('/api/method/supplier_portal.api.place_supplier_bid', {
      method: 'POST',
      body: JSON.stringify({
        rfq_id: tender.value.id,
        amount: bidAmount.value
      })
    });

    const result = await response.json();

    // Matching the backend return: {"status": "success", "message": "..."}
    if (result.message && result.message.status === 'success') {
      createToast(`Bid of ₹${Number(bidAmount.value).toLocaleString('en-IN')} placed!`, { type: 'success' });
      
      // TRIGGER REFRESH: This makes the new bid appear in the list immediately
      await fetchRecentBids(tender.value.id); 
      await fetchTenderDetails(tender.value.id);
      await fetchBidCount(tender.value.id);
      
      bidAmount.value = null; 
    } else {
      // Backend error handling
      const errorMsg = result.message?.message || 'Failed to place bid';
      createToast(errorMsg, { type: 'danger' });
    }
  } catch (error) {
    console.error("Bid submission error:", error);
    createToast('An error occurred while placing the bid', { type: 'danger' });
  } finally {
    isLoading.value = false;
  }
}

const currentL1Value = computed(() => {
  // 1. If bids exist, use the lowest one
  if (recentBids.value.length > 0) {
    return Math.min(...recentBids.value.map(b => b.total));
  }
  
  // 2. IF NO BIDS, use the Budget as the benchmark
  // This prevents the "0" you see in the console
  return tender.value?.estBudget || 0; 
});

const maxAllowedPrice = computed(() => {
  const benchmark = currentL1Value.value; // Use the computed property above
  const minDecrement = tender.value?.minBidDecrement || 0;

  if (recentBids.value.length === 0) {
    return benchmark > 0 ? benchmark : 999999999;
  }
  return benchmark - minDecrement;
});

const budgetSavings = computed(() => {
  const budget = tender.value?.total_budget || 0;
  const currentL1 = recentBids.value.length > 0 
    ? Math.min(...recentBids.value.map(b => b.total)) 
    : (tender.value?.currentLowestBid || 0);

  // If budget is 0, just show ₹0 savings or hide it
  if (budget <= 0) return 0;

  return budget - currentL1;
});

const quickBidAmount = computed(() => {
  const benchmark = recentBids.value.length > 0 
    ? Math.min(...recentBids.value.map(b => b.total)) 
    : (tender.value?.estBudget || 0);
  
  if (benchmark <= 0) return 0;

  let percent = portalSettings.value.live_bidding_quick_entry_percent || 0;
  if (percent > 100) percent = percent / 1000; 

  const percentageDrop = benchmark * (percent / 100);

  // For the first bid, just suggest the Budget minus the percentage drop
  if (recentBids.value.length === 0) {
    return Math.floor(benchmark - percentageDrop);
  }

  // For competitive bidding, use the larger of percentage or min decrement
  const minDecrement = tender.value?.minBidDecrement || 0;
  const actualDrop = Math.max(percentageDrop, minDecrement);
  
  const nextBid = benchmark - actualDrop;
  return nextBid > 0 ? Math.floor(nextBid) : 0;
});


const refreshAllData = async (id) => {
   if (!id) return;
   isLoading.value = true;
   recentBids.value = []; 
  
  try {
    await Promise.all([
      fetchTenderDetails(id),
      checkSavedStatus(id),
      fetchRecentBids(id),
      fetchSettings(),
      fetchBidCount(id),
    ]);
  } catch (error) {
    console.error("Error refreshing data:", error);
  } finally {
    isLoading.value = false;
  }
};

const mainBoqUrl = computed(() => {
   if (!tender.value || !tender.value.items) return null;
      const itemWithBoq = tender.value.items.find(i => i.attach_boq);
   
   return itemWithBoq ? itemWithBoq.attach_boq : null;
});

watch(() => route.params.id, (newId) => {
  if (newId) {
   //  fetchTenderDetails(newId); 
   //  checkSavedStatus(newId);
    refreshAllData(newId);
    window.scrollTo({ top: 0, behavior: 'smooth' }); 
  }
}); 

onMounted(async () => {
  if (route.params.id) {
   //  await fetchTenderDetails(route.params.id)
   //  await checkSavedStatus(route.params.id)
   //  await fetchRecentBids(route.params.id)
   //  await fetchSettings();
    await refreshAllData(route.params.id);
  }
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

    <div v-else-if="isSessionExpired" class="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
        <UserCircle class="w-12 h-12 text-orange-500 mb-4" />
        <h3 class="text-lg font-bold text-gray-900">Session Expired</h3>
        <p class="text-gray-500 mt-2 max-w-md">Your secure session has timed out properly. Please save your work (if any) and reconnect.</p>
        <button @click="refetchSession" class="mt-6 px-6 py-2.5 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition shadow-sm">
           Reconnect Session
        </button>
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
        </div>
      </div>
      
      <div class="flex gap-2">
        <button 
          v-if="authStore.isAuthenticated"
          @click="handleSave"
          class="flex items-center gap-1.5 px-3 py-2 rounded-md border transition-all duration-200"
          :class="isSaved 
            ? 'text-indigo-600 bg-indigo-50 border-indigo-200 shadow-sm' 
            : 'text-slate-500 bg-white border-gray-200 hover:text-indigo-600 hover:border-indigo-100 hover:bg-gray-50'"
        >
          <Bookmark 
            class="w-5 h-5 transition-transform duration-200 active:scale-90" 
            :fill="isSaved ? 'currentColor' : 'none'" 
          />
          <span class="text-sm font-semibold">{{ isSaved ? 'Saved' : 'Save' }}</span>
        </button>

        <button @click="handleShare" class="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 border border-gray-200 transition-colors">
          <Share2 class="w-4 h-4" />
        </button>

        <button @click="handlePrint" class="p-2 text-gray-400 hover:text-gray-600 rounded-md hover:bg-gray-100 border border-gray-200 transition-colors">
          <Printer class="w-4 h-4" />
        </button>
      </div>
    </div>
    
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
                      <div class="text-xs text-orange-600 font-medium mb-0.5"> Bid Submission Last Date</div>
                      <div class="text-sm font-bold text-gray-900">
                         {{ tender.deadline || '0 mins' }}
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
                   <div v-if="similarTenders && similarTenders.length > 0" class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Bookmark class="w-4 h-4 text-gray-400" /> Similar Tenders
                    </h3>
                    <div class="space-y-3">
                      <div 
                        v-for="sim in similarTenders" 
                        :key="sim.id" 
                        @click="navigateToTender(sim.id)"
                        class="flex items-center justify-between p-4 rounded-lg border border-gray-100 hover:border-green-200 hover:bg-green-50/30 transition-all cursor-pointer group"
                      >
                        <div>
                          <div class="text-sm font-bold text-gray-900 group-hover:text-green-600 transition-colors">
                            {{ sim.title }}
                          </div>
                          <div class="text-xs text-gray-500 mt-1">
                            Budget: ₹{{ sim.budget.toLocaleString('en-IN') }} • Deadline: {{ sim.deadline }}
                          </div>
                        </div>
                        <ArrowRight class="w-4 h-4 text-gray-400 group-hover:text-green-600 transform group-hover:translate-x-1 transition-all" />
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
          </div>
 
          <!-- Right Column (Stats & Actions) -->
          <div class="lg:col-span-1 space-y-6">
             
             
          <!-- Summary Card -->
             <div class="bg-white rounded-xl border border-gray-200 px-6 py-6 shadow-sm relative overflow-hidden">
    <h3 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2">Tender Summary</h3>
    
    <div class="grid grid-cols-2 gap-y-4 gap-x-2 text-sm mb-6">
       <div>
      <div class="flex items-center gap-1.5 text-xs text-gray-500 mb-0.5">
         <FileText class="w-3.5 h-3.5" /> Quantity
      </div>
      <div class="font-bold text-gray-900">{{ tender.quantity }} {{ tender.UOM }}</div>
   </div>

   <div>
      <div class="flex items-center gap-1.5 text-xs text-gray-500 mb-0.5">
         <UserCircle class="w-3.5 h-3.5" /> Bids Received
      </div>
     {{ typeof totalBidsReceived === 'object' ? totalBidsReceived.total_bids : totalBidsReceived }}
   </div>

   <div>
      <div class="flex items-center gap-1.5 text-xs text-gray-500 mb-0.5">
         <Banknote class="w-3.5 h-3.5" /> Est. Budget
      </div>
      <div class="font-bold text-gray-900">{{ formattedBudget }}</div>
   </div>
        <div>
          <div class="flex items-center gap-1.5 text-xs text-gray-500 mb-0.5">
             <Calendar class="w-3.5 h-3.5" /> Delivery Date
          </div>
          <div class="font-bold text-gray-900">{{ tender.deliveryDate }}</div>
       </div>
    </div>

    <div class="pt-4 border-t border-gray-100 mb-6 space-y-3">
       <div class="flex justify-between items-center">
          <div class="flex items-center gap-2 text-sm text-gray-500">
             <Clock class="w-4 h-4" /> Deadline
          </div>
          <div class="text-sm font-bold text-gray-900">{{ tender.deadline }}</div>
       </div>
       
       <div class="flex justify-between items-center">
          <div class="flex items-center gap-2 text-sm text-gray-500">
             <Building2 class="w-4 h-4" /> Department
          </div>
          <div class="text-sm font-bold text-gray-900">{{ tender.department }}</div>
       </div>
    </div>

    <div class="flex items-center gap-2 mb-3">
  <button 
    class="flex-grow bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold py-2.5 rounded-lg shadow-sm transition-colors flex items-center justify-center gap-2"
    @click="openBidModal"
  >
    <Zap class="w-4 h-4" /> Submit Your Bid
  </button>

  <button 
    @click="goToQueries" 
    class="p-2.5 bg-white border border-gray-200 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors shadow-sm"
    title="Ask a Query"
  >
    <MessageSquare class="w-5 h-5" />
  </button>
</div>

<div v-if="mainBoqUrl">
  <a 
    :href="mainBoqUrl" 
    target="_blank" 
    class="w-full bg-white hover:bg-gray-50 text-gray-700 border border-gray-200 text-sm font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 cursor-pointer no-underline"
  >
    <Download class="w-4 h-4 text-gray-500" /> Download BOQ
  </a>
</div>
</div>

            
             <!-- Live Bidding Card -->
          <div v-if="tender.liveBidding" class="bg-white rounded-xl border border-gray-200 p-6 shadow-sm ring-1 ring-gray-200">
  
  <div class="flex items-center justify-between mb-4">
    <div class="flex items-center gap-2 px-2.5 py-1 bg-red-50 rounded-full border border-red-100">
      <span class="relative flex h-2 w-2">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
      </span>
      <span class="text-[10px] font-bold text-red-600 uppercase tracking-wider">Live Bidding Active</span>
    </div>
    <div class="text-[10px] text-gray-400 font-medium italic">
      Updated 0s ago
    </div>
  </div>

  <div class="text-center py-6 bg-white rounded-xl border-2 border-green-500/20 mb-6 shadow-[0_0_15px_rgba(34,197,94,0.1)]">
    <div class="text-xs text-gray-500 font-medium mb-1 uppercase tracking-wider">Current Lowest Bid</div>
    <div class="text-3xl font-bold text-green-600 tracking-tight">{{ formattedLowestBid }}</div>
    
    <div v-if="recentBids.length > 0" class="text-xs font-medium text-green-600 mt-1 flex items-center justify-center gap-1">
       <TrendingDown class="w-3 h-3" /> 
       ₹{{ (tender.estBudget - Math.min(...recentBids.map(b => b.total))).toLocaleString('en-IN') }} below budget
    </div>
  </div>

  <div class="mb-4">
    <label class="text-xs font-semibold text-gray-700 mb-2 block">Enter Your Bid Amount</label>
    <div class="flex gap-2 mb-3"> 
      <div class="relative flex-grow">
        <span class="absolute left-3 top-2.5 text-gray-400">₹</span>
        <input v-model="bidAmount" type="number" class="w-full pl-7 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-amber-400 focus:border-amber-400" placeholder="Enter amount">
      </div>
      <button 
         @click="placeBid"
         :disabled="!bidAmount || bidAmount <= 0 || isLoading"
        :class="[
            'px-4 py-2 bg-orange-400 text-white rounded-lg font-medium transition-all flex items-center gap-2',
            (!bidAmount || bidAmount <= 0 || isLoading || bidAmount > maxAllowedPrice) 
               ? 'opacity-40 cursor-not-allowed pointer-events-none select-none' 
               : 'opacity-100 hover:bg-orange-500 active:scale-95'
         ]"
         >
         <span v-if="isLoading">Placing...</span>
         <template v-else>
            Bid
         </template>
      </button>
    </div>

    <div class="min-h-[20px] mb-3">
      <p v-if="bidAmount > maxAllowedPrice" class="text-[11px] text-red-600 font-bold px-1 flex items-center gap-1">
        <AlertCircle class="w-3 h-3" /> 
        Must be ₹{{ maxAllowedPrice.toLocaleString('en-IN') }} or less to qualify
      </p>
    </div>

      <button 
   @click="bidAmount = quickBidAmount" 
   :disabled="quickBidAmount <= 0"
   class="w-full py-1.5 border border-gray-200 rounded-lg flex items-center justify-center gap-2 text-gray-700 hover:bg-gray-50 transition-colors text-sm disabled:opacity-50"
   >
   <ArrowDown class="w-4 h-4 text-gray-500" />
   Quick bid: ₹{{ quickBidAmount.toLocaleString('en-IN') }}
      </button>
  </div>

  <div class="mt-6">
    <h4 class="text-xs font-bold text-gray-900 mb-4 uppercase tracking-wider">Recent Bid Activity</h4>
    
    <div v-if="recentBids.length === 0" class="text-center py-4 text-xs text-gray-400 italic">
      No bids placed yet. Be the first!
    </div>

    <div v-for="(bid, idx) in recentBids" :key="idx" 
         class="flex items-center justify-between py-3 border-b border-gray-50 last:border-0"
         :class="{'bg-green-50 -mx-2 px-3 rounded-lg shadow-sm': idx === 0}">
      <div class="flex flex-col">
        <span class="font-bold text-sm" :class="idx === 0 ? 'text-green-700' : 'text-gray-700'">
          {{ bid.supplier === currentSupplier ? bid.supplier : 'Masked Supplier' }}
        </span>
        <span class="text-[10px] text-gray-400">
          {{ bid.time || 'Just now' }}
        </span>
      </div>
      <div class="text-right">
        <div class="font-bold" :class="idx === 0 ? 'text-green-600' : 'text-gray-900'">
          ₹{{ new Intl.NumberFormat('en-IN').format(bid.total) }}
        </div>
        <span v-if="idx === 0" class="text-[10px] font-bold text-green-500 uppercase">Current L1</span>
      </div>
    </div>
  </div>
</div>

 
            <div class="bg-indigo-900 rounded-xl p-6 text-white text-center shadow-lg">
    <h4 class="font-bold text-sm mb-2">Need Help?</h4>
    <p class="text-xs text-indigo-200 mb-4 leading-relaxed">
        Have questions about this tender? Contact our support team.
    </p>
    <button 
        @click="showSupportModal = true"
        class="w-full bg-white text-indigo-900 text-xs font-bold py-2 rounded-lg shadow-sm hover:bg-indigo-50 transition-colors flex items-center justify-center gap-2"
    >
        <MessageSquare class="w-4 h-4" /> 
        Contact Support
    </button>
  </div>

  <div v-if="showSupportModal" 
       class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
       @click.self="showSupportModal = false">
      
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden transform transition-all duration-300 scale-100">
          <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
              <h3 class="font-bold text-gray-900">Contact Information</h3>
              <button @click="showSupportModal = false" class="text-gray-400 hover:text-gray-600 transition-colors">
                  <X class="h-5 w-5" />
              </button>
          </div>

          <div class="p-6 space-y-6">
              <div>
                  <label class="text-[10px] uppercase tracking-widest font-bold text-indigo-600 mb-1 block">Contact Person</label>
                  <p class="text-gray-900 font-semibold text-lg">
                      {{ tenderDetails.custom_contact_person_display || 'Support Team' }}
                  </p>
              </div>

              <div>
                  <label class="text-[10px] uppercase tracking-widest font-bold text-indigo-600 mb-1 block">Office Address</label>
                  <div class="text-gray-600 text-sm leading-relaxed whitespace-pre-line bg-gray-50 p-4 rounded-xl border border-gray-100">
                      {{ tenderDetails.custom_contact_address_display || 'Address details not available.' }}
                  </div>
              </div>
          </div>

          <div class="px-6 py-4 bg-gray-50 border-t border-gray-100">
              <button 
                  @click="showSupportModal = false"
                  class="w-full px-4 py-2.5 bg-indigo-600 text-white text-sm font-bold rounded-lg hover:bg-indigo-700 transition-all shadow-md shadow-indigo-100"
              >
                  Close
              </button>
          </div>
      </div>
  </div>
 
          </div>
       </div>
     </div>
    </div>
  </div>
</template>
