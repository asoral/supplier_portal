<script setup>
import { ref, computed, onMounted } from 'vue'
import { MessageSquare, Clock, CheckCircle, FileQuestion, Plus, Search, FileText, X, Send } from 'lucide-vue-next'
import { createToast } from 'mosha-vue-toastify'
import 'mosha-vue-toastify/dist/style.css'

// --- State Management ---
const activeTab = ref('My Queries')
const tabs = ['My Queries', 'Questionnaires']
const searchQuery = ref('')
const isLoading = ref(true)
const queries = ref([]) // Stores live data from RFQ Query doctype
const tendersList = ref([]) // Stores dynamic RFQ IDs

// Modal & Form State
const isQueryModalOpen = ref(false)
const newQuery = ref({ tender: '', subject: '', description: '' })

// Questionnaire State
const isRequestModalOpen = ref(false)
const newRequest = ref({ tender: '', type: '', reason: '' })
const questionnaireTypes = ['Compliance Assessment', 'Technical Assessment']

// --- Logic: Data Fetching ---

// 1. Fetch live queries and questionnaires from backend
const fetchQueries = async () => {
  isLoading.value = true
  try {
    const headers = { 'X-Requested-With': 'XMLHttpRequest' };
    
    // Fetch both in parallel
    const [queriesRes, questRes] = await Promise.all([
        fetch('/api/method/supplier_portal.api.get_my_queries', { credentials: 'include', headers }),
        fetch('/api/method/supplier_portal.api.get_my_questionnaires', { credentials: 'include', headers })
    ]);

    const queriesData = await queriesRes.json();
    const questData = await questRes.json();

    const qList = (queriesData.message || []).map(q => ({
      id: q.name,
      type: 'Query',
      title: q.subject,
      ref: q.rfq, 
      status: q.status,
      question: q.query,
      response: q.response,
      responseDate: q.response ? 'Answered' : null,
      submitted: new Date(q.creation).toLocaleDateString('en-IN', { 
        day: '2-digit', month: 'short', year: 'numeric' 
      })
    }));

    const qstList = (questData.message || []).map(q => ({
      id: q.name,
      type: 'Questionnaire',
      title: q.subject, // 'Compliance Assessment' etc.
      ref: q.rfq,
      status: q.status,
      question: q.query, // The 'reason'
      response: q.response,
      responseDate: q.response ? 'Answered' : null,
      submitted: new Date(q.creation).toLocaleDateString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric'
      })
    }));

    queries.value = [...qList, ...qstList];

  } catch (error) {
    console.error("Failed to fetch data:", error)
    createToast('Failed to load data', { type: 'danger' })
  } finally {
    isLoading.value = false
  }
}

// 2. Fetch valid Tenders dynamically
const fetchTenders = async () => {
  try {
    const response = await fetch('/api/resource/Request for Quotation?' + new URLSearchParams({
      fields: JSON.stringify(["name"]),
      limit_page_length: 50
    }), { credentials: 'include' })
    
    const result = await response.json()
    tendersList.value = (result.data || []).map(t => t.name)
  } catch (error) {
    console.error("Failed to fetch tenders:", error)
  }
}

// --- Logic: Form Submissions ---

// Submit new query to Frappe
const isSubmitting = ref(false)

const getLatestCsrfToken = async () => {
    try {
        const response = await fetch('/api/method/supplier_portal.api.get_csrf_token', { 
            credentials: 'include',
            cache: 'no-store'
        });
        const data = await response.json();
        
        if (data.message) {
            window.csrf_token = data.message;
            return data.message;
        }
    } catch (e) {
        console.error("Failed to refresh CSRF token", e);
    }
    return window.csrf_token;
}

const secureFetch = async (url, options = {}) => {
    let token = window.csrf_token;
    if (!token || token === "None") {
        token = await getLatestCsrfToken();
    }
    
    // Merge headers carefully
    const headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Frappe-CSRF-Token': token,
        ...(options.headers || {})
    };

    // Ensure credentials are included
    const fetchOptions = {
        ...options,
        headers,
        credentials: 'include'
    };

    let response = await fetch(url, fetchOptions);
    
    if (!response.ok) {
         try {
             // We clone to check error type
             const clone = response.clone();
             const err = await clone.json();
             
             if (err.exc_type === 'CSRFTokenError' || response.status === 403 || response.status === 417 || response.status === 400) {
                 console.warn("CSRF Error, retrying...", err.exc_type);
                 
                 // Wait a moment and force get new token
                 await new Promise(r => setTimeout(r, 500));
                 token = await getLatestCsrfToken();
                 
                 // Update header with new token
                 headers['X-Frappe-CSRF-Token'] = token;
                 
                 // Retry with new headers
                 response = await fetch(url, {
                     ...fetchOptions,
                     headers
                 });
             }
         } catch(e) { }
    }
    return response;
}

const submitQuery = async () => {
  if (!newQuery.value.subject || !newQuery.value.description || !newQuery.value.tender) {
    createToast("Please fill in all fields.", { type: 'warning' });
    return;
  }

  isSubmitting.value = true
  try {
    const response = await secureFetch('/api/method/supplier_portal.api.create_rfq_query', {
      method: 'POST',
      body: JSON.stringify({
        subject: newQuery.value.subject,
        rfq: newQuery.value.tender, 
        query: newQuery.value.description
      }),
      credentials: 'include'
    });

    if (response.ok) {
        const resData = await response.json();
        createToast('Query submitted successfully', { type: 'success' })
        
        // Close modal immediately for better UX
        closeModal();
        newQuery.value = { subject: '', tender: '', description: '' };
        
        // Refresh data in background
        fetchQueries(); 
    } else {
      const error = await response.json();
      console.error("Submission failed:", error);
      createToast(error.message || 'Submission failed', { type: 'danger' })
    }
  } catch (err) {
    console.error("Network error:", err);
    createToast('Network error occurred. Please try again.', { type: 'danger' })
  } finally {
    isSubmitting.value = false
  }
}

const isSubmittingRequest = ref(false)

const submitRequest = async () => {
    if (!newRequest.value.tender || !newRequest.value.type || !newRequest.value.reason) {
        createToast("Please fill in all fields.", { type: 'warning' });
        return;
    }

    isSubmittingRequest.value = true
    try {
        const response = await secureFetch('/api/method/supplier_portal.api.create_rfq_questionnaire', {
            method: 'POST',
            body: JSON.stringify({
                rfq: newRequest.value.tender,
                subject: newRequest.value.type,
                query: newRequest.value.reason
            }),
            credentials: 'include'
        });

        if (response.ok) {
            createToast('Questionnaire requested successfully', { type: 'success' });
            closeRequestModal();
            newRequest.value = { tender: '', type: '', reason: '' };
            fetchQueries(); // Refresh list
        } else {
            const error = await response.json();
            createToast(error.message || 'Request failed', { type: 'danger' });
        }
    } catch (err) {
        console.error("Network error:", err);
        createToast('Network error occurred.', { type: 'danger' });
    } finally {
        isSubmittingRequest.value = false
    }
}

// --- Logic: Computed Properties ---

// Dynamic Stats calculation
const stats = computed(() => {
  const totalQueries = queries.value.filter(q => q.type === 'Query').length
  const pending = queries.value.filter(q => q.type === 'Query' && q.status === 'Pending').length
  const answered = queries.value.filter(q => q.type === 'Query' && q.status === 'Answered').length
  const questionnaires = queries.value.filter(q => q.type === 'Questionnaire').length

  return [
    { name: 'Total Queries', value: totalQueries.toString(), icon: MessageSquare, color: 'text-blue-600', bg: 'bg-blue-50' },
    { name: 'Pending', value: pending.toString(), icon: Clock, color: 'text-orange-600', bg: 'bg-orange-50' },
    { name: 'Answered', value: answered.toString(), icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' },
    { name: 'Questionnaires', value: questionnaires.toString(), icon: FileQuestion, color: 'text-indigo-600', bg: 'bg-indigo-50' },
  ]
})

const filteredQueries = computed(() => {
  const queryType = activeTab.value === 'My Queries' ? 'Query' : 'Questionnaire'
  return queries.value.filter(q => 
    q.type === queryType &&
    (q.title?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    q.ref?.toLowerCase().includes(searchQuery.value.toLowerCase()))
  )
})

// Template update for button
/*
<div class="mt-6">
    <button @click="submitRequest" :disabled="isSubmittingRequest" type="button" class="inline-flex w-full justify-center rounded-lg bg-indigo-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 gap-2 items-center transition-all disabled:opacity-50 disabled:cursor-not-allowed">
    <svg v-if="isSubmittingRequest" class="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    {{ isSubmittingRequest ? 'Submitting...' : 'Submit Request' }}
    </button>
</div>
*/

// --- Modal Controls ---
const openModal = () => isQueryModalOpen.value = true
const closeModal = () => {
  isQueryModalOpen.value = false
  newQuery.value = { tender: '', subject: '', description: '' }
}

const openRequestModal = () => isRequestModalOpen.value = true
const closeRequestModal = () => isRequestModalOpen.value = false

// --- Lifecycle ---
onMounted(() => {
  fetchQueries();
  fetchTenders(); // Load dynamic list for the dropdown
})
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Queries & Questionnaires</h1>
        <p class="mt-1 text-sm text-gray-500">Submit queries about tenders and respond to questionnaires.</p>
      </div>
      <div class="flex gap-3">
         <button @click="openRequestModal" class="inline-flex items-center gap-2 rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            <FileText class="h-4 w-4" /> Request Questionnaire
         </button>
         <button @click="openModal" class="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
            <Plus class="h-4 w-4" /> New Query
         </button>
      </div>
    </div>

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

    <div class="mb-6 flex items-center justify-between">
       <div class="relative max-w-sm flex-grow">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
             <Search class="h-4 w-4 text-gray-400" />
          </div>
          <input 
            v-model="searchQuery"
            type="text" 
            class="block w-full rounded-md border-0 py-2 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 shadow-sm"
            placeholder="Search queries..." 
          />
       </div>
       <div v-if="isLoading" class="ml-4">
          <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-indigo-600"></div>
       </div>
    </div>

    <div v-if="!isLoading" class="space-y-4">
       <div v-if="filteredQueries.length === 0" class="text-center py-12 bg-white rounded-lg border border-dashed border-gray-300">
          <MessageSquare class="mx-auto h-12 w-12 text-gray-400" />
          <h3 class="mt-2 text-sm font-semibold text-gray-900">No records found</h3>
          <p class="mt-1 text-sm text-gray-500">Submit a new query to see it listed here.</p>
       </div>

       <div v-for="query in filteredQueries" :key="query.id" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
          <div class="flex items-start gap-4">
             <div class="mt-1">
                <div v-if="query.status === 'Answered'" class="rounded-full bg-green-100 p-2">
                   <CheckCircle class="h-5 w-5 text-green-600" />
                </div>
                <div v-else class="rounded-full bg-orange-100 p-2">
                   <Clock class="h-5 w-5 text-orange-600" />
                </div>
             </div>
             
             <div class="flex-grow">
               <div class="flex justify-between items-start">
                   <div class="flex items-center gap-3 mb-1">
                      <h3 class="text-base font-semibold text-gray-900">{{ query.title }}</h3>
                      <span :class="['inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset', 
                         query.status === 'Answered' || query.status === 'Completed' ? 'bg-green-50 text-green-700 ring-green-600/20' : 
                         query.status === 'Action Required' ? 'bg-indigo-50 text-indigo-700 ring-indigo-600/20' :
                         'bg-orange-50 text-orange-700 ring-orange-600/20']">
                         {{ query.status }}
                      </span>
                   </div>
                   <div class="text-xs font-mono text-gray-400">{{ query.id }}</div>
               </div>
               
                <p class="text-sm text-gray-500 mb-4">{{ query.ref }}</p>

                <div class="bg-gray-50 rounded-lg p-4 mb-3 text-sm text-gray-800 font-medium whitespace-pre-wrap">
                   {{ query.question }}
                </div>

                <div v-if="query.response" class="bg-green-50 rounded-lg p-4 text-sm border border-green-100">
                   <div class="text-green-800 font-medium pb-1 mb-1 border-b border-green-200/50 flex justify-between">
                      <span>Response</span>
                      <span class="text-xs opacity-75">{{ query.responseDate }}</span>
                   </div>
                   <div class="text-green-900 prose prose-sm max-w-none" v-html="query.response"></div>
                </div>

                <p class="text-xs text-gray-400 mt-2">Submitted: {{ query.submitted }}</p>
             </div>
          </div>
       </div>
    </div>

    <div v-if="isQueryModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6" role="dialog" aria-modal="true">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeModal"></div>
      
      <div class="relative transform overflow-hidden rounded-xl bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
        <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
          <button type="button" class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none" @click="closeModal">
            <span class="sr-only">Close</span>
            <X class="h-5 w-5" aria-hidden="true" />
          </button>
        </div>
        
        <div>
          <h3 class="text-lg font-bold leading-6 text-gray-900 mb-6" id="modal-title">Submit New Query</h3>
          <div class="space-y-4">
             <div>
               <label for="tender" class="block text-sm font-semibold text-gray-900 mb-1.5">Select Tender</label>
               <select id="tender" v-model="newQuery.tender" class="block w-full rounded-lg border-0 py-2.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                 <option value="" disabled selected>Select tender</option>
                 <option v-for="tender in tendersList" :key="tender" :value="tender">{{ tender }}</option>
               </select>
             </div>

             <div>
               <label for="subject" class="block text-sm font-semibold text-gray-900 mb-1.5">Subject</label>
               <input type="text" id="subject" v-model="newQuery.subject" placeholder="Brief subject of your query" class="block w-full rounded-lg border-0 py-2.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
             </div>

             <div>
               <label for="query" class="block text-sm font-semibold text-gray-900 mb-1.5">Your Query</label>
               <textarea id="query" rows="4" v-model="newQuery.description" placeholder="Describe your query in detail..." class="block w-full rounded-lg border-0 py-2.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"></textarea>
             </div>
          </div>
          
          <div class="mt-6">
             <button @click="submitQuery" :disabled="isSubmitting" type="button" class="inline-flex w-full justify-center rounded-lg bg-indigo-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 gap-2 items-center transition-all disabled:opacity-50 disabled:cursor-not-allowed">
               <svg v-if="isSubmitting" class="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                   <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                   <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
               </svg>
               <Send v-else class="h-4 w-4" /> 
               {{ isSubmitting ? 'Submitting...' : 'Submit Query' }}
             </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isRequestModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6" role="dialog" aria-modal="true">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeRequestModal"></div>
      
      <div class="relative transform overflow-hidden rounded-xl bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
        <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
          <button type="button" class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none" @click="closeRequestModal">
            <span class="sr-only">Close</span>
            <X class="h-5 w-5" aria-hidden="true" />
          </button>
        </div>
        
        <div>
          <h3 class="text-lg font-bold leading-6 text-gray-900 mb-6" id="modal-title">Request Questionnaire</h3>
          <div class="space-y-4">
             <div>
               <label for="req-tender" class="block text-sm font-semibold text-gray-900 mb-1.5">Select Tender</label>
               <select id="req-tender" v-model="newRequest.tender" class="block w-full rounded-lg border-0 py-2.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                 <option value="" disabled selected>Select tender</option>
                 <option v-for="tender in tendersList" :key="tender" :value="tender">{{ tender }}</option>
               </select>
             </div>

             <div>
               <label for="req-type" class="block text-sm font-semibold text-gray-900 mb-1.5">Type of Questionnaire</label>
               <select id="req-type" v-model="newRequest.type" class="block w-full rounded-lg border-0 py-2.5 pl-3 pr-10 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6">
                 <option value="" disabled selected>Select type</option>
                 <option v-for="qType in questionnaireTypes" :key="qType" :value="qType">{{ qType }}</option>
               </select>
             </div>

             <div>
               <label for="req-reason" class="block text-sm font-semibold text-gray-900 mb-1.5">Reason for Request</label>
               <textarea id="req-reason" rows="4" v-model="newRequest.reason" placeholder="Explain why you need this questionnaire..." class="block w-full rounded-lg border-0 py-2.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"></textarea>
             </div>
          </div>
          
          <div class="mt-6">
             <button @click="submitRequest" :disabled="isSubmittingRequest" type="button" class="inline-flex w-full justify-center rounded-lg bg-indigo-600 px-3 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 gap-2 items-center transition-all disabled:opacity-50 disabled:cursor-not-allowed">
               <svg v-if="isSubmittingRequest" class="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                   <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                   <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
               </svg>
               {{ isSubmittingRequest ? 'Submitting...' : 'Submit Request' }}
             </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>