<script setup>
import { ref } from 'vue'
import { Search, Book, Video, MessageSquare, ChevronDown, MessageCircle, Smartphone, FileText } from 'lucide-vue-next'

const activeTab = ref('FAQs')
const tabs = ['FAQs', 'User Guides', 'Videos', 'My Tickets', 'Contact Us']
const searchQuery = ref('')
const openFaq = ref(null)

const toggleFaq = (idx) => {
   if (openFaq.value === idx) {
      openFaq.value = null
   } else {
      openFaq.value = idx
   }
}

const helpCards = [
   { name: 'FAQs', desc: 'Browse common questions', icon: Smartphone, tab: 'FAQs' },
   { name: 'User Guides', desc: 'Step-by-step tutorials', icon: FileText, tab: 'User Guides' },
   { name: 'Video Tutorials', desc: 'Watch and learn', icon: Video, tab: 'Videos' },
   { name: 'Support Tickets', desc: 'Get personal help', icon: MessageSquare, tab: 'My Tickets' },
]

const faqs = [
   {
      category: 'Getting Started',
      items: [
         { q: 'How do I register as a vendor?', a: 'To register, click on the "Sign Up" button on the login page. Fill in your company details, upload necessary compliance documents (GST, PAN), and submit for approval. Once verified, you will receive an email with login credentials.' },
         { q: 'What documents are required for registration?', a: 'You typically need your GST Registration Certificate, PAN Card, Company Incorporation Certificate, and a Cancelled Cheque for bank verification.' },
         { q: 'How long does verification take?', a: 'Verification usually takes 24-48 business hours. You can track your status on the Dashboard.' }
      ]
   },
   {
      category: 'Bidding & Tenders',
      items: [
         { q: 'How do I submit a bid?', a: 'Navigate to "Active Tenders", select the tender you wish to bid on, and click "Place Bid". Enter your financial quote and upload technical documents.' },
         { q: 'Can I modify my bid after submission?', a: 'Yes, provided the tender deadline has not passed. Go to "My Bids", select the tender, and click "Modify Bid".' },
         { q: 'What is live bidding?', a: 'Live bidding allows vendors to place bids in real-time during a specific auction window. The lowest bid is often displayed (without vendor name) to encourage competitive pricing.' },
         { q: 'How do I save tenders for later?', a: 'Click the "Bookmark" icon on any tender card to save it to your "Saved Tenders" list.' }
      ]
   },
   {
      category: 'Orders & Deliveries',
      items: [
         { q: 'How do I acknowledge a purchase order?', a: 'Go to "Contracts", find the new PO, viewing the details and clicking "Acknowledge" to confirm acceptance.' },
         { q: 'How do I update delivery status?', a: 'Go to the "Deliveries" page, find the shipment, click "Update", and enter the current location or status milestone.' },
         { q: 'What happens if I can\'t meet the delivery deadline?', a: 'Immediately update the delivery status to "Delayed" and add a note explaining the reason. It is also recommended to raise a Query to inform the procurement team.' }
      ]
   },
   {
      category: 'Invoices & Payments',
      items: [
         { q: 'How do I submit an invoice?', a: 'Go to "Invoices", click "Upload Invoice", select the relevant PO, and upload your digital invoice copy.' },
         { q: 'When will I receive payment?', a: 'Payment terms are defined in your contract (e.g., Net 30). You can track payment status in the Invoices tab.' },
         { q: 'What is a debit note?', a: 'A debit note is issued if goods are returned or damaged, reducing the amount payable to you.' }
      ]
   },
   {
      category: 'Catalog & Products',
      items: [
         { q: 'How do I add products to my catalog?', a: 'Go to "My Catalog", click "Add Product", and fill in the SKU, description, and pricing details.' },
         { q: 'How do I update my rates?', a: 'Edit the product in your catalog. Note that rate changes may require approval depending on your contract terms.' }
      ]
   },
   {
      category: 'Integrations',
      items: [
         { q: 'How do I set up webhooks for my ERP?', a: 'Go to "Integrations" > "Webhooks", click "Create New", and enter your endpoint URL.' },
         { q: 'Where can I find my API key?', a: 'Go to "Integrations" > "API Keys" to generate and view your secret keys.' }
      ]
   }
]

const userGuides = [
  { title: 'Vendor Registration Guide', desc: 'Complete walkthrough of the registration process.', time: '5 min read' },
  { title: 'Bidding Sytem Overview', desc: 'How to place and manage your bids effectively.', time: '8 min read' },
  { title: 'Invoice Submission', desc: 'Step-by-step guide to digital invoicing.', time: '4 min read' },
  { title: 'Managing Your Catalog', desc: 'Add and update products in your vendor catalog.', time: '6 min read' }
]

const videos = [
  { title: 'Platform Tour 2024', duration: '2:30', thumb: 'bg-indigo-100' },
  { title: 'How to Submit a Bid', duration: '5:45', thumb: 'bg-blue-100' },
  { title: 'Updating Company Profile', duration: '3:15', thumb: 'bg-green-100' },
  { title: 'Understanding Contracts', duration: '4:20', thumb: 'bg-orange-100' }
]

const tickets = [
  { id: 'SPT-2024-001', subject: 'Login issue on mobile app', status: 'Open', date: '2 Feb, 2024' },
  { id: 'SPT-2024-002', subject: 'Document upload failure', status: 'Resolved', date: '28 Jan, 2024' },
  { id: 'SPT-2023-899', subject: 'Clarification on tender terms', status: 'Closed', date: '15 Dec, 2023' }
]
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
     <!-- Central Search Header -->
     <div class="text-center max-w-2xl mx-auto mb-12">
        <h1 class="text-3xl font-bold tracking-tight text-gray-900 mb-4">How can we help you?</h1>
        <div class="relative">
           <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4">
              <Search class="h-5 w-5 text-gray-400" />
           </div>
           <input 
             v-model="searchQuery"
             type="text" 
             class="block w-full rounded-lg border-0 py-4 pl-12 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-200 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-lg sm:leading-6"
             placeholder="Search for answers..."
           />
        </div>
     </div>

     <!-- Top Cards -->
     <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <div 
          v-for="card in helpCards" 
          :key="card.name" 
          @click="activeTab = card.tab"
          class="bg-white rounded-xl border border-gray-200 p-6 text-center hover:shadow-lg transition-shadow cursor-pointer group"
          :class="{ 'ring-2 ring-indigo-600 ring-offset-2': activeTab === card.tab }"
        >
           <div class="mx-auto h-12 w-12 rounded-full bg-indigo-50 flex items-center justify-center mb-4 group-hover:bg-indigo-100 transition-colors">
              <component :is="card.icon" class="h-6 w-6 text-indigo-600" />
           </div>
           <h3 class="text-lg font-semibold text-gray-900">{{ card.name }}</h3>
           <p class="text-sm text-gray-500 mt-1">{{ card.desc }}</p>
        </div>
     </div>

     <!-- Tabs -->
    <div class="border-b border-gray-200 mb-8">
      <nav class="-mb-px flex space-x-8 overflow-x-auto" aria-label="Tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          @click="activeTab = tab"
          :class="[
            activeTab === tab
              ? 'border-indigo-500 text-indigo-600'
              : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700',
            'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium transition-colors'
          ]"
        >
          {{ tab }}
        </button>
      </nav>
    </div>

    <!-- FAQ Accordions -->
    <div v-if="activeTab === 'FAQs'" class="space-y-6">
       <div v-for="(section, sIdx) in faqs" :key="section.category" class="bg-white rounded-xl border border-gray-200 overflow-hidden">
          <div class="bg-gray-50 px-6 py-4 border-b border-gray-100">
             <h2 class="text-lg font-semibold text-gray-900">{{ section.category }}</h2>
          </div>
          <div class="divide-y divide-gray-100">
             <div v-for="(item, iIdx) in section.items" :key="iIdx" class="w-full">
                <button 
                  @click="toggleFaq(`${sIdx}-${iIdx}`)"
                  class="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors focus:outline-none"
                >
                   <span class="font-medium text-gray-900 text-sm">{{ item.q }}</span>
                   <ChevronDown 
                     class="h-5 w-5 text-gray-400 transition-transform duration-200"
                     :class="openFaq === `${sIdx}-${iIdx}` ? 'rotate-180 text-indigo-600' : ''"
                   />
                </button>
                <div 
                   v-show="openFaq === `${sIdx}-${iIdx}`"
                   class="px-6 pb-4 text-sm text-gray-600 bg-gray-50/30"
                >
                   {{ item.a }}
                </div>
             </div>
          </div>
       </div>
    </div>

    <!-- User Guides -->
    <div v-else-if="activeTab === 'User Guides'" class="grid grid-cols-1 md:grid-cols-2 gap-6">
       <div v-for="guide in userGuides" :key="guide.title" class="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-all cursor-pointer group">
          <div class="flex items-start gap-4">
             <div class="rounded-lg bg-indigo-50 p-3 group-hover:bg-indigo-100 transition-colors">
                <Book class="h-6 w-6 text-indigo-600" />
             </div>
             <div>
                <h3 class="text-base font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ guide.title }}</h3>
                <p class="text-sm text-gray-500 mt-1 mb-2">{{ guide.desc }}</p>
                <span class="text-xs font-medium text-gray-400">{{ guide.time }}</span>
             </div>
          </div>
       </div>
    </div>

    <!-- Videos -->
    <div v-else-if="activeTab === 'Videos'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
       <div v-for="video in videos" :key="video.title" class="bg-white rounded-xl border border-gray-200 overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group">
          <div :class="[video.thumb, 'aspect-video flex items-center justify-center relative']">
             <div class="h-12 w-12 rounded-full bg-white/90 flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                <Video class="h-5 w-5 text-indigo-600 ml-1" />
             </div>
             <span class="absolute bottom-2 right-2 px-2 py-1 bg-black/70 text-white text-xs rounded font-medium">{{ video.duration }}</span>
          </div>
          <div class="p-4">
             <h3 class="text-sm font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">{{ video.title }}</h3>
          </div>
       </div>
    </div>

    <!-- My Tickets -->
    <div v-else-if="activeTab === 'My Tickets'" class="bg-white rounded-xl border border-gray-200 overflow-hidden">
       <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
             <thead class="bg-gray-50">
                <tr>
                   <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ticket ID</th>
                   <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                   <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                   <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                </tr>
             </thead>
             <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="ticket in tickets" :key="ticket.id" class="hover:bg-gray-50">
                   <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">{{ ticket.id }}</td>
                   <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ ticket.subject }}</td>
                   <td class="px-6 py-4 whitespace-nowrap text-sm">
                      <span :class="['px-2 py-1 text-xs font-medium rounded-full', 
                         ticket.status === 'Open' ? 'bg-blue-50 text-blue-700' : 
                         ticket.status === 'Resolved' ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-700']">
                         {{ ticket.status }}
                      </span>
                   </td>
                   <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ ticket.date }}</td>
                </tr>
             </tbody>
          </table>
       </div>
       <div class="p-4 border-t border-gray-200 bg-gray-50 flex justify-center">
          <button class="text-sm font-medium text-indigo-600 hover:text-indigo-500 flex items-center gap-2">
             <MessageCircle class="h-4 w-4" /> Create New Ticket
          </button>
       </div>
    </div>

    <!-- Contact Us -->
    <div v-else-if="activeTab === 'Contact Us'" class="max-w-2xl mx-auto">
       <div class="bg-indigo-50 rounded-xl p-8 text-center">
          <h3 class="text-xl font-bold text-gray-900 mb-2">Still need help?</h3>
          <p class="text-sm text-gray-600 mb-6">Our support team is available Mon-Fri, 9am - 6pm EST.</p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
             <button class="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">
                <MessageSquare class="h-4 w-4" /> Chat with Support
             </button>
             <button class="inline-flex items-center justify-center gap-2 rounded-lg bg-white px-6 py-3 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
                Email Us
             </button>
          </div>
       </div>
    </div>

  </div>
</template>
