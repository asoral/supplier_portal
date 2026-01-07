<script setup>
import { ref } from 'vue'
import { Webhook, Key, FileText, CheckCircle, XCircle, Plus, Copy, Play, Eye, EyeOff, RotateCw, AlertTriangle, Code, Terminal, Activity, ArrowUpRight, Clock, ShieldCheck } from 'lucide-vue-next'

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
// API Key Logic
const showApiKey = ref(false)
const showSecret = ref(false)
const apiKey = 'sk_live_51M0...923k'
const webhookSecret = 'whsec_...82n1'

const logs = ref([
 { id: 1, event: 'order.created', timestamp: '2024-01-15 14:30:00', status: 'success', duration: '145ms' },
 { id: 2, event: 'invoice.received', timestamp: '2024-01-15 10:15:00', status: 'success', duration: '89ms' },
 { id: 3, event: 'delivery.scheduled', timestamp: '2024-01-14 16:45:00', status: 'failed', duration: '5000ms' },
 { id: 4, event: 'order.updated', timestamp: '2024-01-14 11:20:00', status: 'success', duration: '112ms' },
 { id: 5, event: 'payment.created', timestamp: '2024-01-13 09:30:00', status: 'success', duration: '78ms' }
])

const endpoints = [
 { method: 'POST', path: '/api/v1/products', desc: 'Update product catalog' },
 { method: 'POST', path: '/api/v1/rates', desc: 'Update pricing and rates' },
 { method: 'POST', path: '/api/v1/deliveries', desc: 'Update delivery schedules' },
 { method: 'POST', path: '/api/v1/invoices', desc: 'Submit invoice documents' },
 { method: 'POST', path: '/api/v1/stock', desc: 'Update stock availability' },
 { method: 'GET', path: '/api/v1/orders', desc: 'Fetch pending orders' }
]

const copyToClipboard = (text) => {
  // Mock copy
  console.log('Copied:', text)
}
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

    <!-- API Keys Tab -->
    <div v-show="activeTab === 'API Keys'" class="space-y-6">
      <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
        <h2 class="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2"><Key class="h-5 w-5 text-indigo-600"/> API Credentials</h2>
        <div class="space-y-6">
           <div>
              <label class="block text-sm font-medium leading-6 text-gray-900">API Key</label>
              <div class="mt-2 flex rounded-md shadow-sm">
                 <div class="relative flex-grow focus-within:z-10">
                    <input type="text" readonly :value="showApiKey ? apiKey : '•'.repeat(24)" class="block w-full rounded-none rounded-l-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-mono">
                 </div>
                 <button @click="showApiKey = !showApiKey" type="button" class="relative -ml-px inline-flex items-center gap-x-1.5 px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    <component :is="showApiKey ? EyeOff : Eye" class="h-4 w-4 text-gray-400" />
                 </button>
                 <button @click="copyToClipboard(apiKey)" type="button" class="relative -ml-px inline-flex items-center gap-x-1.5 px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    <Copy class="h-4 w-4 text-gray-400" />
                 </button>
                 <button type="button" class="relative -ml-px inline-flex items-center gap-x-1.5 rounded-r-md px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    <RotateCw class="h-4 w-4 text-gray-400" /> Regenerate
                 </button>
              </div>
              <p class="mt-2 text-xs text-gray-500">Use this key in the <code class="text-xs bg-gray-100 px-1 rounded">Authorization</code> header.</p>
           </div>
           
           <div>
              <label class="block text-sm font-medium leading-6 text-gray-900">Webhook Signing Secret</label>
               <div class="mt-2 flex rounded-md shadow-sm">
                 <div class="relative flex-grow focus-within:z-10">
                    <input type="text" readonly :value="showSecret ? webhookSecret : '•'.repeat(24)" class="block w-full rounded-none rounded-l-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 font-mono">
                 </div>
                 <button @click="showSecret = !showSecret" type="button" class="relative -ml-px inline-flex items-center gap-x-1.5 px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    <component :is="showSecret ? EyeOff : Eye" class="h-4 w-4 text-gray-400" />
                 </button>
                 <button @click="copyToClipboard(webhookSecret)" type="button" class="relative -ml-px inline-flex items-center gap-x-1.5 rounded-r-md px-3 py-2 text-sm font-semibold text-gray-900 ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                    <Copy class="h-4 w-4 text-gray-400" />
                 </button>
              </div>
              <p class="mt-2 text-xs text-gray-500">Use this secret to verify webhook payloads are from us.</p>
           </div>
        </div>
      </div>
      
       <div class="rounded-md bg-yellow-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <AlertTriangle class="h-5 w-5 text-yellow-400" aria-hidden="true" />
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-yellow-800">Keep your credentials secure</h3>
            <div class="mt-2 text-sm text-yellow-700">
              <p>Never share your API keys in public repositories or client-side code. Regenerate keys immediately if you suspect they've been compromised.</p>
            </div>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <h2 class="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2"><ArrowUpRight class="h-5 w-5 text-indigo-600"/> Push Data to Portal</h2>
          <p class="text-sm text-gray-500 mb-6">Use our REST API to push product catalogs, rates, and delivery updates to the vendor portal.</p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
             <div v-for="ep in endpoints" :key="ep.path" class="border border-gray-200 rounded-lg p-3 hover:border-indigo-300 transition-colors">
                <div class="flex items-center gap-2 mb-1">
                   <span class="text-xs font-bold px-2 py-0.5 rounded bg-gray-100 text-gray-700 font-mono">{{ ep.method }}</span>
                   <span class="text-xs font-mono text-indigo-600">{{ ep.path }}</span>
                </div>
                <div class="text-xs text-gray-500">{{ ep.desc }}</div>
             </div>
          </div>
      </div>
    </div>

    <!-- Logs Tab -->
    <div v-show="activeTab === 'Logs'" class="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div class="border-b border-gray-200 px-6 py-4">
             <h2 class="text-base font-semibold text-gray-900">Webhook Delivery Logs</h2>
             <p class="text-sm text-gray-500">Recent webhook deliveries and their status</p>
        </div>
        <ul role="list" class="divide-y divide-gray-200">
           <li v-for="log in logs" :key="log.id" class="px-6 py-4 hover:bg-gray-50 transition-colors">
              <div class="flex items-center justify-between">
                 <div class="flex items-center gap-3">
                    <CheckCircle v-if="log.status === 'success'" class="h-5 w-5 text-green-500" />
                    <XCircle v-else class="h-5 w-5 text-red-500" />
                    <div>
                       <div class="text-sm font-medium text-gray-900 font-mono">{{ log.event }}</div>
                       <div class="text-xs text-gray-500">{{ log.timestamp }}</div>
                    </div>
                 </div>
                 <div class="text-right">
                    <span class="inline-flex items-center rounded-md px-2 py-1 text-xs font-medium uppercase ring-1 ring-inset" :class="log.status === 'success' ? 'bg-blue-50 text-blue-700 ring-blue-700/10' : 'bg-red-50 text-red-700 ring-red-600/10'">{{ log.status }}</span>
                    <div class="text-xs text-gray-400 mt-1">{{ log.duration }}</div>
                 </div>
              </div>
           </li>
        </ul>
    </div>

    <!-- Documentation Tab -->
    <div v-show="activeTab === 'Documentation'" class="bg-white rounded-lg border border-gray-200 p-8 shadow-sm">
        <div class="max-w-3xl mx-auto space-y-10">
           <div>
              <h2 class="text-2xl font-bold text-gray-900 mb-4">Integration Guide</h2>
              <p class="text-gray-600">Step-by-step instructions to integrate your systems with our vendor portal.</p>
           </div>
           
           <div class="space-y-8">
              <div class="relative pl-10">
                 <div class="absolute left-0 top-0 flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-white font-bold text-sm">1</div>
                 <h3 class="text-lg font-semibold text-gray-900">Get Your API Credentials</h3>
                 <p class="mt-2 text-gray-600 text-sm">Navigate to the <span class="font-semibold text-gray-900">API Keys</span> tab to get your API key and webhook signing secret.</p>
              </div>

               <div class="relative pl-10">
                 <div class="absolute left-0 top-0 flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-white font-bold text-sm">2</div>
                 <h3 class="text-lg font-semibold text-gray-900">Configure Webhooks</h3>
                 <p class="mt-2 text-gray-600 text-sm">Set up webhook endpoints in your ERP system to receive real-time updates for orders, invoices, and deliveries.</p>
              </div>

               <div class="relative pl-10">
                 <div class="absolute left-0 top-0 flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-white font-bold text-sm">3</div>
                 <h3 class="text-lg font-semibold text-gray-900">Verify Webhook Signatures</h3>
                 <p class="mt-2 text-gray-600 text-sm mb-3">Use the webhook signing secret to verify that incoming webhooks are authentic.</p>
                 <div class="bg-gray-900 rounded-lg p-4 overflow-x-auto text-xs text-gray-300 font-mono">
                    <pre>const signature = req.headers['x-webhook-signature'];
const isValid = verifySignature(payload, signature, webhookSecret);</pre>
                 </div>
              </div>

               <div class="relative pl-10">
                 <div class="absolute left-0 top-0 flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-white font-bold text-sm">4</div>
                 <h3 class="text-lg font-semibold text-gray-900">Push Data to Portal</h3>
                 <p class="mt-2 text-gray-600 text-sm mb-3">Use our REST API to push product catalogs, rates, and delivery updates from your ERP.</p>
                 <div class="bg-gray-900 rounded-lg p-4 overflow-x-auto text-xs text-gray-300 font-mono">
                    <pre>curl -X POST https://portal.example.com/api/v1/products \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sku": "PROD-001", "name": "Widget", "rate": 150.00}'</pre>
                 </div>
              </div>
           </div>

           <div class="border-t border-gray-200 pt-8">
              <h3 class="text-sm font-semibold text-gray-900 mb-4">Supported ERP Systems</h3>
              <div class="flex gap-4">
                 <span class="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">ERPNext</span>
                 <span class="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">SAP</span>
                 <span class="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">Oracle</span>
                 <span class="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">Microsoft Dynamics</span>
                 <span class="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">Tally</span>
                 <span class="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">Zoho</span>
                 <span class="inline-flex items-center rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">QuickBooks</span>
              </div>
           </div>
        </div>
    </div>

  </div>
</template>
