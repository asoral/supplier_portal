<script setup>
import { ref } from 'vue'
import { Plus, Eye, Download, RotateCw, FileCode, CheckCircle, AlertTriangle, XCircle, Clock } from 'lucide-vue-next'

const completion = 71
const activeTab = ref('All Documents')
const tabs = ['All Documents', 'Registration', 'Certificates', 'Financial', 'Compliance']
const searchQuery = ref('')

const documents = ref([
 {
    id: 1,
    name: 'GST Registration Certificate',
    file: 'GST_Certificate_2024.pdf',
    size: '245 KB',
    uploaded: '15 Jan 2024',
    status: 'Valid',
    tags: ['Required']
  },
  {
    id: 2,
    name: 'PAN Card',
    file: 'PAN_Card.pdf',
    size: '156 KB',
    uploaded: '15 Jan 2024',
    status: 'Valid',
    tags: ['Required']
  },
  {
     id: 3,
     name: 'ISO 9001:2015 Certificate',
     file: 'ISO_9001_Certificate.pdf',
     size: '1.2 MB',
     uploaded: '20 Jan 2024',
     expires: '15 Dec 2025',
     status: 'Valid'
  },
  {
     id: 4,
     name: 'ISO 14001:2015 Certificate',
     file: 'ISO_14001_Certificate.pdf',
     size: '1.1 MB',
     uploaded: '20 Jan 2022',
     expires: '20 Mar 2024',
     status: 'Expiring Soon'
  },
  {
     id: 5,
     name: 'MSME Registration',
     file: 'MSME_Certificate.pdf',
     size: '320 KB',
     uploaded: '10 Jan 2024',
     expires: '10 Mar 2026',
     status: 'Valid',
     tags: ['Required']
  },
  {
     id: 6,
     name: 'Company Registration Certificate',
     file: 'Company_Registration.pdf',
     size: '890 KB',
     uploaded: '5 Jan 2024',
     status: 'Valid',
     tags: ['Required']
  },
  {
     id: 7,
     name: 'Bank Account Details',
     file: 'Bank_Details.pdf',
     size: '125 KB',
     uploaded: '10 Feb 2024',
     status: 'Pending Review',
     tags: ['Required']
  },
   {
     id: 8,
     name: 'Safety Compliance Certificate',
     file: 'Safety_compliance.pdf',
     size: '678 KB',
     uploaded: '20 Nov 2023',
     expires: '31 Dec 2023',
     status: 'Expired',
     tags: ['Required']
  }
])

const getStatusColor = (status) => {
   switch(status) {
      case 'Valid': return 'bg-green-50 text-green-700 ring-green-600/20'
      case 'Expiring Soon': return 'bg-orange-50 text-orange-700 ring-orange-600/20'
      case 'Pending Review': return 'bg-gray-50 text-gray-600 ring-gray-600/20'
      case 'Expired': return 'bg-red-50 text-red-700 ring-red-600/20'
      default: return 'bg-gray-50 text-gray-600'
   }
}
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
     <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900 flex items-center gap-2">
           <FileCode class="h-8 w-8 text-indigo-600" />
           Document Center
        </h1>
        <p class="mt-1 text-sm text-gray-500">Manage your compliance documents, certificates, and registrations.</p>
      </div>
      <button class="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 flex items-center gap-2">
         <Plus class="h-4 w-4" /> Upload Document
      </button>
    </div>

    <!-- Compliance Stats -->
    <div class="bg-white rounded-lg border border-gray-200 p-6 mb-8">
       <div class="mb-4">
          <h2 class="text-base font-semibold text-gray-900">Compliance Status</h2>
          <p class="text-sm text-gray-500">Your document compliance overview</p>
       </div>
       <div class="flex flex-col md:flex-row gap-8 items-center">
          <div class="flex-grow w-full">
             <div class="flex justify-between text-sm font-medium mb-2">
                <span>Required Documents Completion</span>
                <span>5/7</span>
             </div>
             <div class="w-full bg-gray-200 rounded-full h-2.5">
                <div class="bg-blue-600 h-2.5 rounded-full" :style="`width: ${completion}%`"></div>
             </div>
             <p class="text-xs text-gray-500 mt-2">{{ completion }}% of required documents submitted.</p>
          </div>
          <div class="grid grid-cols-2 gap-4 w-full md:w-auto min-w-[300px]">
             <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <CheckCircle class="h-5 w-5 text-green-500" />
                <div>
                   <div class="text-sm font-bold text-gray-900">6</div>
                   <div class="text-xs text-gray-500">Valid</div>
                </div>
             </div>
              <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <AlertTriangle class="h-5 w-5 text-orange-500" />
                <div>
                   <div class="text-sm font-bold text-gray-900">2</div>
                   <div class="text-xs text-gray-500">Expiring Soon</div>
                </div>
             </div>
              <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <XCircle class="h-5 w-5 text-red-500" />
                <div>
                   <div class="text-sm font-bold text-gray-900">1</div>
                   <div class="text-xs text-gray-500">Expired</div>
                </div>
             </div>
              <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <Clock class="h-5 w-5 text-blue-500" />
                <div>
                   <div class="text-sm font-bold text-gray-900">1</div>
                   <div class="text-xs text-gray-500">Pending</div>
                </div>
             </div>
          </div>
       </div>
    </div>

    <!-- Controls -->
     <div class="mb-6 space-y-4">
         <input 
            v-model="searchQuery"
            type="text" 
            class="block w-full sm:w-80 rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 pl-3"
            placeholder="Search documents..." 
         />
         <div class="flex flex-wrap gap-2">
            <button
               v-for="tab in tabs"
               :key="tab"
               @click="activeTab = tab"
               :class="[
                  activeTab === tab ? 'bg-gray-100 text-gray-900' : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50',
                  'rounded-md px-3 py-1.5 text-sm font-medium transition-colors'
               ]"
            >
               {{ tab }}
            </button>
         </div>
     </div>

    <!-- List -->
    <div class="space-y-3">
       <div v-for="doc in documents" :key="doc.id" class="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 bg-white rounded-lg border border-gray-200 shadow-sm hover:border-gray-300 transition-colors">
          <div class="flex gap-4 items-start">
             <div class="bg-indigo-50 p-2 rounded-lg">
                <FileCode class="h-6 w-6 text-indigo-600" />
             </div>
             <div>
                <div class="flex flex-wrap items-center gap-2">
                   <h3 class="font-medium text-gray-900">{{ doc.name }}</h3>
                   <span :class="['inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset', getStatusColor(doc.status)]">
                      {{ doc.status }}
                   </span>
                   <span v-for="tag in doc.tags" :key="tag" class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
                      {{ tag }}
                   </span>
                </div>
                <div class="flex items-center gap-4 mt-1 text-xs text-gray-500">
                   <span>{{ doc.file }} • {{ doc.size }}</span>
                   <span class="flex items-center gap-1">
                      <Clock class="h-3 w-3" /> Uploaded: {{ doc.uploaded }}
                   </span>
                   <span v-if="doc.expires" class="flex items-center gap-1" :class="doc.status === 'Expiring Soon' ? 'text-orange-600' : doc.status === 'Expired' ? 'text-red-600' : ''">
                      <Clock class="h-3 w-3" /> Expires: {{ doc.expires }}
                   </span>
                </div>
             </div>
          </div>
          <div class="flex items-center gap-2 mt-4 sm:mt-0 self-end sm:self-center">
             <button class="p-1.5 text-gray-400 hover:text-gray-600"><Eye class="h-4 w-4" /></button>
             <button class="p-1.5 text-gray-400 hover:text-gray-600"><Download class="h-4 w-4" /></button>
             <button v-if="doc.status === 'Expiring Soon' || doc.status === 'Expired'" class="inline-flex items-center gap-1 rounded bg-white px-2 py-1 text-xs font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                <RotateCw class="h-3 w-3" /> Renew
             </button>
          </div>
       </div>
    </div>

  </div>
</template>
