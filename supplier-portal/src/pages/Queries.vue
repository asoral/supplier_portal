<script setup>
import { ref, computed } from 'vue'
import { MessageSquare, Clock, CheckCircle, FileQuestion, Plus, Search, FileText } from 'lucide-vue-next'

const activeTab = ref('My Queries')
const tabs = ['My Queries', 'Questionnaires']
const searchQuery = ref('')

const queries = ref([
  {
    id: 1,
    type: 'Query',
    title: 'Clarification on thickness tolerance',
    ref: 'Industrial Steel Plates - Grade A • TND-2024-001',
    status: 'Answered',
    question: 'Can you please confirm the acceptable tolerance for the 12mm thickness plates? Is it ±0.5mm or ±1mm?',
    response: 'The acceptable tolerance for 12mm plates is ±0.8mm as per IS 2062 standards.',
    responseDate: '24 Jan, 02:00 pm',
    submitted: '23 Jan, 10:30 am'
  },
  {
    id: 2,
    type: 'Query',
    title: 'Site visit scheduling',
    ref: 'Electrical Control Panels • TND-2024-004',
    status: 'Pending',
    question: 'We would like to schedule a site visit before submitting our bid. Please provide available dates.',
    response: null,
    submitted: '1 Feb, 09:15 am'
  },
  {
    id: 3,
    type: 'Query',
    title: 'Alternative brand acceptance',
    ref: 'CNC Machining Center • TND-2024-002',
    status: 'Answered',
    question: 'Will Mazak or DMG Mori be acceptable alternatives to the specified Fanuc control system?',
    response: 'Yes, Mazak, DMG Mori, and Okuma are acceptable alternatives with equivalent specifications.',
    responseDate: '29 Jan, 11:30 am',
    submitted: '28 Jan, 04:45 pm'
  },
  {
    id: 4,
    type: 'Questionnaire',
    title: 'Vendor Compliance Assessment',
    ref: 'Standard Vendor Qualification',
    status: 'Action Required',
    question: 'Please complete the mandatory compliance assessment regarding environmental standards and labor practices.',
    response: null,
    submitted: '2 Feb, 10:00 am',
    actionLabel: 'Start Questionnaire'
  },
  {
    id: 5,
    type: 'Questionnaire',
    title: 'Financial Capability Survey',
    ref: 'Annual Review 2024',
    status: 'Completed',
    question: 'Annual financial capability survey for registered vendors.',
    response: 'Submitted on 15 Jan, 2024',
    responseDate: '15 Jan, 03:30 pm',
    submitted: '15 Jan, 09:00 am',
    actionLabel: 'View Response'
  }
])

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
    (q.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    q.ref.toLowerCase().includes(searchQuery.value.toLowerCase()))
  )
})
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Queries & Questionnaires</h1>
        <p class="mt-1 text-sm text-gray-500">Submit queries about tenders and respond to questionnaires.</p>
      </div>
      <div class="flex gap-3">
         <button class="inline-flex items-center gap-2 rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
            <FileText class="h-4 w-4" /> Request Questionnaire
         </button>
         <button class="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
            <Plus class="h-4 w-4" /> New Query
         </button>
      </div>
    </div>

    <!-- Stats -->
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

    <!-- Search -->
    <div class="mb-6">
       <div class="relative max-w-sm">
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
    </div>

    <!-- List -->
    <div class="space-y-4">
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
                   <div v-if="query.type === 'Questionnaire' && query.status === 'Action Required'">
                       <button class="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">
                          {{ query.actionLabel }}
                       </button>
                   </div>
               </div>
                <p class="text-sm text-gray-500 mb-4">{{ query.ref }}</p>

                <div class="bg-gray-50 rounded-lg p-4 mb-3 text-sm text-gray-800 font-medium">
                   {{ query.question }}
                </div>

                <div v-if="query.response" class="bg-green-50 rounded-lg p-4 text-sm border border-green-100">
                   <div class="text-green-800 font-medium pb-1 mb-1 border-b border-green-200/50 flex justify-between">
                      <span>Response</span>
                      <span class="text-xs opacity-75">{{ query.responseDate }}</span>
                   </div>
                   <div class="text-green-900">
                      {{ query.response }}
                   </div>
                </div>

                <p class="text-xs text-gray-400 mt-2">Submitted: {{ query.submitted }}</p>
             </div>
          </div>
       </div>
    </div>

  </div>
</template>
