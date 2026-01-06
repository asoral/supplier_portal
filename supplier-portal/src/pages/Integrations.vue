<script setup>
import { ref } from 'vue'
import { Webhook, Key, FileText, CheckCircle, XCircle, Plus, Copy, Play } from 'lucide-vue-next'

const activeTab = ref('Webhooks')
const tabs = ['Webhooks', 'API Keys', 'Logs', 'Documentation']

const configuredWebhooks = ref([
 {
    id: 1,
    name: 'ERP Order Sync',
    url: 'https://erp.company.com/api/webhooks/orders',
    status: 'active',
    events: ['order.created', 'order.updated'],
    lastTriggered: '2024-03-12 14:30:00',
    successRate: 98.5
  },
  {
    id: 2,
    name: 'Invoice Notification',
    url: 'https://accounting.company.com/webhooks/invoices',
    status: 'active',
    events: ['invoice.received', 'payment.created'],
    lastTriggered: '2024-03-12 10:15:00',
    successRate: 100
  },
   {
    id: 3,
    name: 'Delivery Updates',
    url: 'https://logistics.company.com/api/delivery-webhook',
    status: 'inactive',
    events: ['delivery.scheduled', 'delivery.completed'],
    lastTriggered: '2024-03-10 09:00:00',
    successRate: 85.2
  }
])

const eventOptions = [
  { label: 'Orders', options: ['order.created', 'order.updated', 'order.cancelled'] },
  { label: 'Invoices', options: ['invoice.received', 'invoice.paid', 'invoice.overdue'] },
  { label: 'Payments', options: ['payment.created', 'payment.received', 'debit_note.created'] },
  { label: 'Deliveries', options: ['delivery.scheduled', 'delivery.dispatched', 'delivery.completed'] },
  { label: 'Catalog', options: ['product.added', 'product.updated', 'rate.changed'] },
   { label: 'Tenders', options: ['tender.invited', 'bid.submitted', 'bid.awarded'] }
]
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <div class="mb-8">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">System Integrations</h1>
        <p class="mt-1 text-sm text-gray-500">Connect your ERP, accounting, and logistics systems with our vendor portal using webhooks and APIs.</p>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 mb-6">
      <nav class="-mb-px flex space-x-8 overflow-x-auto" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          @click="activeTab = tab"
          :class="[
            activeTab === tab
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium flex items-center gap-2'
          ]"
        >
          <Webhook v-if="tab === 'Webhooks'" class="h-4 w-4" />
          <Key v-if="tab === 'API Keys'" class="h-4 w-4" />
          <FileText v-if="tab === 'Logs' || tab === 'Documentation'" class="h-4 w-4" />
          {{ tab }}
        </button>
      </nav>
    </div>

    <div v-show="activeTab === 'Webhooks'" class="space-y-8">
       <!-- Create Form -->
       <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <div class="flex items-center gap-2 mb-4">
             <div class="bg-indigo-50 p-1.5 rounded">
                <Plus class="h-4 w-4 text-indigo-600" />
             </div>
             <h2 class="text-base font-semibold text-gray-900">Create New Webhook</h2>
          </div>
          <p class="text-sm text-gray-500 mb-6">Configure a new endpoint to receive real-time updates from the vendor portal.</p>
          
          <div class="space-y-6">
             <div>
                <label class="block text-sm font-medium leading-6 text-gray-900">Webhook URL</label>
                <div class="mt-2">
                   <input type="text" class="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" placeholder="https://your-erp.com/api/webhooks">
                </div>
             </div>

             <div>
                <label class="block text-sm font-medium leading-6 text-gray-900 mb-2">Select Events to Subscribe</label>
                <div class="space-y-4">
                   <div v-for="group in eventOptions" :key="group.label">
                      <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{{ group.label }}</h3>
                      <div class="flex flex-wrap gap-2">
                         <button v-for="event in group.options" :key="event" class="rounded-full bg-gray-50 px-3 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-200 hover:bg-gray-100 cursor-pointer transition-colors">
                            {{ event }}
                         </button>
                      </div>
                   </div>
                </div>
             </div>
             
             <div class="pt-2">
                <button type="button" class="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600">Create Webhook</button>
             </div>
          </div>
       </div>

       <!-- List -->
       <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
           <div class="mb-4">
             <h2 class="text-base font-semibold text-gray-900">Configured Webhooks</h2>
             <p class="text-sm text-gray-500">Manage your existing webhook endpoints.</p>
          </div>
          
          <div class="space-y-4">
             <div v-for="hook in configuredWebhooks" :key="hook.id" class="rounded-lg border border-gray-200 p-4 hover:border-gray-300 transition-colors">
                <div class="flex items-start justify-between">
                   <div>
                      <div class="flex items-center gap-2">
                         <h3 class="text-sm font-medium text-gray-900">{{ hook.name }}</h3>
                         <span class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset" :class="hook.status === 'active' ? 'bg-blue-50 text-blue-700 ring-blue-700/10' : 'bg-gray-50 text-gray-600 ring-gray-500/10'">{{ hook.status }}</span>
                      </div>
                      <div class="mt-1 text-xs font-mono text-gray-500 bg-gray-50 inline-block px-1 rounded">{{ hook.url }}</div>
                      
                      <div class="mt-3 flex flex-wrap gap-2">
                         <span v-for="event in hook.events" :key="event" class="inline-flex items-center rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-600/10">
                            {{ event }}
                         </span>
                      </div>
                      
                      <div class="mt-3 flex items-center gap-4 text-xs text-gray-500">
                         <span>Last triggered: {{ hook.lastTriggered }}</span>
                         <span class="text-green-600">Success rate: {{ hook.successRate }}%</span>
                      </div>
                   </div>
                   
                   <div class="flex items-center gap-3">
                       <button class="inline-flex items-center gap-1 rounded bg-white px-2.5 py-1.5 text-xs font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                         <Play class="h-3 w-3" /> Test
                      </button>
                      <div class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2" :class="hook.status === 'active' ? 'bg-indigo-600' : 'bg-gray-200'" role="switch">
                         <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="hook.status === 'active' ? 'translate-x-5' : 'translate-x-0'"></span>
                      </div>
                   </div>
                </div>
             </div>
          </div>
       </div>
    </div>
  </div>
</template>
