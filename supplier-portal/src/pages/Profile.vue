<script setup>
import { ref } from 'vue'
import {
  Building2,
  FileText,
  Award,
  Settings,
  MapPin,
  Calendar,
  CheckCircle,
  Star,
  Edit2,
  Download,
  Upload,
  Shield,
  Bell,
  Lock,
  Trash2,
  ShoppingBag,
  TrendingUp,
  FileCheck
} from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const state = authStore
const activeTab = ref('Company')
const tabs = ['Company', 'Documents', 'Certifications', 'Settings']

// Mock Data
const profileParams = {
  completion: 85,
  rating: 4.5,
  reviews: 24,
  joinedDate: '15 Jun 2022',
  location: 'Pune, Maharashtra',
  industry: 'Manufacturing & Trading',
  verified: true
}

const quickStats = {
  totalBids: 6,
  ordersWon: 2,
  winRate: '33%',
  totalValue: '₹10,70,000'
}

// Form Data (pre-filled with mock or auth data)
const formData = ref({
  companyName: state.user?.company || 'ABC Industries Pvt Ltd',
  businessType: 'Manufacturing & Trading',
  gst: '27AABCU9603R1ZM',
  pan: 'AABCU9603R',
  contactEmail: state.user?.email || 'vendor@example.com',
  contactPhone: '+91 98765 43210',
  website: 'https://abcindustries.com',
  address: 'Plot 42, Industrial Area, Pune-2',
  about: 'ABC Industries is a leading supplier of industrial raw materials and safety equipment with over 15 years of experience in serving manufacturing companies across India.',
  employees: '50-100',
  turnover: '₹5-10 Cr'
})

const documents = ref([
  { name: 'Company Registration Certificate', date: '15 Jan 2024', type: 'pdf' },
  { name: 'GST Certificate', date: '15 Jan 2024', type: 'pdf' },
  { name: 'PAN Card', date: '15 Jan 2024', type: 'pdf' },
  { name: 'Bank Details', date: '10 Feb 2024', type: 'pdf' },
  { name: 'Product Catalog', date: '5 Mar 2024', type: 'pdf' }
])

const certifications = ref([
  { name: 'ISO 9001:2015', validUntil: '15 Dec 2025', status: 'Active' },
  { name: 'ISO 14001:2015', validUntil: '20 Aug 2025', status: 'Active' },
  { name: 'MSME Certified', validUntil: '10 Mar 2028', status: 'Active' },
  { name: 'GST Registered', validUntil: '', status: 'Active' },
])

const settings = ref({
  newTender: true,
  bidStatus: true,
  deadlines: true,
  orderUpdates: false,
  weeklyDigest: false
})
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    
    <!-- Header Card -->
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
      <div class="flex flex-col md:flex-row gap-6 items-start">
        <!-- Logo -->
        <div class="h-24 w-24 rounded-xl bg-indigo-600 flex items-center justify-center flex-shrink-0">
          <span class="text-3xl font-bold text-white uppercase">{{ formData.companyName.charAt(0) }}</span>
        </div>
        
        <div class="flex-grow">
          <div class="flex flex-col md:flex-row md:items-center gap-3 mb-2">
            <h1 class="text-2xl font-bold text-gray-900">{{ formData.companyName }}</h1>
            <span v-if="profileParams.verified" class="inline-flex items-center gap-1 rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
              <CheckCircle class="h-3 w-3" /> Verified
            </span>
          </div>
          
          <p class="text-base text-gray-600 mb-4">{{ profileParams.industry }}</p>
          
          <div class="flex flex-wrap gap-4 text-sm text-gray-500">
             <span class="flex items-center gap-1"><MapPin class="h-4 w-4" /> {{ profileParams.location }}</span>
             <span class="flex items-center gap-1"><Calendar class="h-4 w-4" /> Member since {{ profileParams.joinedDate }}</span>
          </div>
        </div>
        
        <div>
           <button class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 bg-white shadow-sm">
              <Edit2 class="h-4 w-4" /> Edit Profile
           </button>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <!-- Persistent Sidebar -->
      <div class="space-y-6">
         <!-- Profile Completion -->
         <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4">Profile Completion</h3>
            <div class="flex items-center gap-4">
              <div class="relative h-16 w-16 flex-shrink-0">
                 <svg class="h-full w-full" viewBox="0 0 36 36">
                    <path
                      class="text-gray-200"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="3"
                    />
                    <path
                      class="text-indigo-600"
                      :stroke-dasharray="`${profileParams.completion}, 100`"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="3"
                    />
                 </svg>
                 <div class="absolute inset-0 flex items-center justify-center text-sm font-bold text-gray-900">
                    {{ profileParams.completion }}%
                 </div>
              </div>
              <div>
                 <p class="text-xs text-gray-500 mb-1">Complete your profile to increase visibility</p>
                 <a href="#" class="text-xs font-medium text-indigo-600 hover:text-indigo-500">Complete Now →</a>
              </div>
            </div>
         </div>

         <!-- Ratings -->
         <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2"><Star class="h-4 w-4 text-orange-400 fill-orange-400" /> Vendor Ratings</h3>
            <div class="text-center mb-4">
               <div class="text-4xl font-bold text-gray-900 mb-2">{{ profileParams.rating }}</div>
               <div class="flex justify-center gap-1 mb-2">
                  <Star v-for="i in 5" :key="i" class="h-4 w-4" :class="i <= Math.round(profileParams.rating) ? 'text-orange-400 fill-orange-400' : 'text-gray-200'" />
               </div>
               <p class="text-xs text-gray-500">Based on {{ profileParams.reviews }} reviews</p>
            </div>
            
            <div class="space-y-3">
               <div>
                  <div class="flex items-center justify-between text-xs mb-1">
                     <span class="text-gray-500">Delivery</span>
                     <span class="font-medium text-gray-900">4.7</span>
                  </div>
                  <div class="w-full bg-gray-100 rounded-full h-1.5">
                     <div class="bg-orange-400 h-1.5 rounded-full" style="width: 94%"></div>
                  </div>
               </div>
               <div>
                  <div class="flex items-center justify-between text-xs mb-1">
                     <span class="text-gray-500">Quality</span>
                     <span class="font-medium text-gray-900">4.3</span>
                  </div>
                  <div class="w-full bg-gray-100 rounded-full h-1.5">
                     <div class="bg-orange-400 h-1.5 rounded-full" style="width: 86%"></div>
                  </div>
               </div>
               <div>
                  <div class="flex items-center justify-between text-xs mb-1">
                     <span class="text-gray-500">Communication</span>
                     <span class="font-medium text-gray-900">4.6</span>
                  </div>
                  <div class="w-full bg-gray-100 rounded-full h-1.5">
                     <div class="bg-orange-400 h-1.5 rounded-full" style="width: 92%"></div>
                  </div>
               </div>
            </div>
         </div>
         
         <!-- Quick Stats -->
         <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-sm font-semibold text-gray-900 mb-4">Quick Stats</h3>
            <div class="space-y-4">
               <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                     <div class="p-2 bg-gray-50 rounded-lg">
                        <ShoppingBag class="h-4 w-4 text-gray-500" />
                     </div>
                     <span class="text-sm text-gray-600">Total Bids</span>
                  </div>
                  <span class="text-sm font-bold text-gray-900">{{ quickStats.totalBids }}</span>
               </div>
               <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                     <div class="p-2 bg-gray-50 rounded-lg">
                        <Award class="h-4 w-4 text-gray-500" />
                     </div>
                     <span class="text-sm text-gray-600">Orders Won</span>
                  </div>
                  <span class="text-sm font-bold text-green-600">{{ quickStats.ordersWon }}</span>
               </div>
               <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                     <div class="p-2 bg-gray-50 rounded-lg">
                        <TrendingUp class="h-4 w-4 text-gray-500" />
                     </div>
                     <span class="text-sm text-gray-600">Win Rate</span>
                  </div>
                  <span class="text-sm font-bold text-gray-900">{{ quickStats.winRate }}</span>
               </div>
               <div class="pt-3 border-t border-gray-100 flex items-center justify-between">
                  <div class="flex items-center gap-3">
                     <div class="p-2 bg-gray-50 rounded-lg">
                        <FileCheck class="h-4 w-4 text-gray-500" />
                     </div>
                     <span class="text-xs text-gray-600">Total Value Won</span>
                  </div>
                  <span class="text-sm font-bold text-gray-900">{{ quickStats.totalValue }}</span>
               </div>
            </div>
         </div>
      </div>

      <!-- Main Content Column -->
      <div class="lg:col-span-2">
         <!-- Tabs -->
         <div class="bg-gray-50/50 rounded-xl p-1 mb-6 flex space-x-1">
            <button
               v-for="tab in tabs"
               :key="tab"
               @click="activeTab = tab"
               :class="[
                  activeTab === tab
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 hover:bg-white/50',
                  'flex-1 rounded-lg py-2.5 text-sm font-medium transition-all duration-200'
               ]"
            >
               {{ tab }}
            </button>
         </div>

         <!-- Company Tab -->
         <div v-show="activeTab === 'Company'" class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-fade-in">
            <h3 class="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2"><Building2 class="h-5 w-5 text-gray-400" /> Company Information</h3>
            
            <form class="space-y-6">
               <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                     <input type="text" v-model="formData.companyName" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 bg-gray-50 sm:text-sm sm:leading-6" disabled />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Business Type</label>
                     <input type="text" v-model="formData.businessType" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">GST Number</label>
                     <input type="text" v-model="formData.gst" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                  </div>
                   <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">PAN Number</label>
                     <input type="text" v-model="formData.pan" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                  </div>
               </div>
               
               <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">About Company</label>
                  <textarea rows="3" v-model="formData.about" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"></textarea>
               </div>
               
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Annual Turnover</label>
                     <input type="text" v-model="formData.turnover" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Employee Count</label>
                     <input type="text" v-model="formData.employees" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                  </div>
                </div>

               <div class="border-t border-gray-100 pt-6">
                  <h4 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2"><User class="h-4 w-4 text-gray-400" /> Contact Information</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input type="email" v-model="formData.contactEmail" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                     </div>
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                        <input type="text" v-model="formData.contactPhone" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                     </div>
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
                        <input type="text" v-model="formData.website" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6" />
                     </div>
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                        <input type="text" disabled :value="profileParams.location" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 bg-gray-50 sm:text-sm sm:leading-6" />
                     </div>
                     <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Full Address</label>
                        <textarea rows="2" v-model="formData.address" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset ring-gray-200 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"></textarea>
                     </div>
                  </div>
               </div>

            </form>
         </div>

         <!-- Documents Tab -->
         <div v-show="activeTab === 'Documents'" class="space-y-6 animate-fade-in">
             <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div class="flex items-center justify-between mb-6">
                   <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2"><FileText class="h-4 w-4 text-gray-500" /> Uploaded Documents</h3>
                   <button class="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500">
                      <Upload class="h-3 w-3" /> Upload New
                   </button>
                </div>

                <div class="space-y-3">
                   <div v-for="(doc, idx) in documents" :key="idx" class="flex items-center justify-between p-4 rounded-lg border border-gray-100 hover:border-indigo-100 hover:bg-indigo-50/30 transition-colors group">
                      <div class="flex items-center gap-4">
                         <div class="h-10 w-10 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-600">
                            <FileText class="h-5 w-5" />
                         </div>
                         <div>
                            <p class="text-sm font-medium text-gray-900">{{ doc.name }}</p>
                            <p class="text-xs text-gray-500">Uploaded on {{ doc.date }}</p>
                         </div>
                      </div>
                      <div class="flex items-center gap-2">
                         <button class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-white rounded-full transition-colors"><View class="h-4 w-4" /></button>
                         <button class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-white rounded-full transition-colors"><Download class="h-4 w-4" /></button>
                      </div>
                   </div>
                </div>
             </div>
         </div>

         <!-- Certifications Tab -->
         <div v-show="activeTab === 'Certifications'" class="space-y-6 animate-fade-in">
             <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div class="flex items-center justify-between mb-6">
                   <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2"><Award class="h-4 w-4 text-gray-500" /> Certifications & Compliance</h3>
                   <button class="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500">
                      <Upload class="h-3 w-3" /> Add Certificate
                   </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div v-for="(cert, idx) in certifications" :key="idx" class="p-4 rounded-lg border border-gray-200 hover:border-indigo-200 transition-colors">
                      <div class="flex items-start justify-between mb-2">
                         <div class="flex items-center gap-2">
                            <Award class="h-5 w-5 text-indigo-600" />
                            <span class="text-sm font-medium text-gray-900">{{ cert.name }}</span>
                         </div>
                         <span class="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">{{ cert.status }}</span>
                      </div>
                      <p class="text-xs text-gray-500 ml-7" v-if="cert.validUntil">Valid until {{ cert.validUntil }}</p>
                   </div>
                </div>
             </div>
         </div>

         <!-- Settings Tab -->
         <div v-show="activeTab === 'Settings'" class="space-y-6 animate-fade-in">
             <!-- Notification Preferences -->
             <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 class="text-sm font-bold text-gray-900 mb-6 flex items-center gap-2"><Bell class="h-4 w-4 text-gray-500" /> Notification Preferences</h3>
                <div class="space-y-4">
                   <div class="flex items-center justify-between">
                      <div>
                         <p class="text-sm font-medium text-gray-900">New tender in my categories</p>
                         <p class="text-xs text-gray-500">Get notified when new tenders are published</p>
                      </div>
                      <div class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none" :class="settings.newTender ? 'bg-indigo-600' : 'bg-gray-200'" @click="settings.newTender = !settings.newTender">
                         <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="settings.newTender ? 'translate-x-5' : 'translate-x-0'"></span>
                      </div>
                   </div>
                    <div class="flex items-center justify-between">
                      <div>
                         <p class="text-sm font-medium text-gray-900">Bid status updates</p>
                         <p class="text-xs text-gray-500">Updates on your submitted bids</p>
                      </div>
                      <div class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none" :class="settings.bidStatus ? 'bg-indigo-600' : 'bg-gray-200'" @click="settings.bidStatus = !settings.bidStatus">
                         <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="settings.bidStatus ? 'translate-x-5' : 'translate-x-0'"></span>
                      </div>
                   </div>
                    <div class="flex items-center justify-between">
                      <div>
                         <p class="text-sm font-medium text-gray-900">Tender deadline reminders</p>
                         <p class="text-xs text-gray-500">Reminder 24 hours before deadline</p>
                      </div>
                      <div class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none" :class="settings.deadlines ? 'bg-indigo-600' : 'bg-gray-200'" @click="settings.deadlines = !settings.deadlines">
                         <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="settings.deadlines ? 'translate-x-5' : 'translate-x-0'"></span>
                      </div>
                   </div>
                    <div class="flex items-center justify-between">
                      <div>
                         <p class="text-sm font-medium text-gray-900">Order updates</p>
                         <p class="text-xs text-gray-500">Notifications about awarded orders</p>
                      </div>
                      <div class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none" :class="settings.orderUpdates ? 'bg-indigo-600' : 'bg-gray-200'" @click="settings.orderUpdates = !settings.orderUpdates">
                         <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="settings.orderUpdates ? 'translate-x-5' : 'translate-x-0'"></span>
                      </div>
                   </div>
                    <div class="flex items-center justify-between">
                      <div>
                         <p class="text-sm font-medium text-gray-900">Weekly digest</p>
                         <p class="text-xs text-gray-500">Summary of opportunities every week</p>
                      </div>
                      <div class="relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none" :class="settings.weeklyDigest ? 'bg-indigo-600' : 'bg-gray-200'" @click="settings.weeklyDigest = !settings.weeklyDigest">
                         <span class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out" :class="settings.weeklyDigest ? 'translate-x-5' : 'translate-x-0'"></span>
                      </div>
                   </div>
                </div>
             </div>
             
             <!-- Security Settings -->
             <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                 <h3 class="text-sm font-bold text-gray-900 mb-6 flex items-center gap-2"><Shield class="h-4 w-4 text-gray-500" /> Security Settings</h3>
                 <div class="space-y-6">
                    <div class="flex items-center justify-between pb-4 border-b border-gray-100">
                       <div>
                          <p class="text-sm font-medium text-gray-900">Two-Factor Authentication</p>
                          <p class="text-xs text-gray-500">Add an extra layer of security</p>
                       </div>
                       <button class="px-3 py-1.5 rounded-md border border-gray-200 text-xs font-medium text-gray-700 hover:bg-gray-50">Enable</button>
                    </div>
                     <div class="flex items-center justify-between pb-4 border-b border-gray-100">
                       <div>
                          <p class="text-sm font-medium text-gray-900">Change Password</p>
                          <p class="text-xs text-gray-500">Update your account password</p>
                       </div>
                       <button class="px-3 py-1.5 rounded-md border border-gray-200 text-xs font-medium text-gray-700 hover:bg-gray-50">Change</button>
                    </div>
                     <div class="flex items-center justify-between">
                       <div>
                          <p class="text-sm font-medium text-red-600">Delete Account</p>
                          <p class="text-xs text-gray-500">Permanently delete your account</p>
                       </div>
                       <button class="px-3 py-1.5 rounded-md bg-red-600 text-xs font-medium text-white hover:bg-red-700">Delete</button>
                    </div>
                 </div>
             </div>
         </div>

      </div>
      
    </div>

  </div>
</template>
