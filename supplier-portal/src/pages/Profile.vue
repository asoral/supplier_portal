<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  Building2, FileText, Award, Settings, MapPin, Calendar, CheckCircle,
  Star, Edit2, Download, Upload, Shield, Bell, Lock, Trash2,
  ShoppingBag, TrendingUp, FileCheck
} from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const activeTab = ref('Company')
const tabs = ['Company', 'Documents', 'Certifications', 'Settings']
const isLoading = ref(true)

// 1. Profile Data State (to be filled from Backend)
const profileData = ref(null)

// --- ADD THIS SECTION ---
const dashboardData = ref({
    stats: {
        total_bids: 0,
        orders_won: 0,
        win_rate: '0%',
        orders_won_value: '0.00'
    }
})
// 2. Form Data (now computed or reactive to profileData)
const formData = ref({
  companyName: '',
  businessType: '',
  gst: '',
  pan: '',
  contactEmail: '',
  contactPhone: '',
  website: '',
  address: '',
  about: '',
  employees: '',
  turnover: '',
  productCategories: []
})

const profileParams = computed(() => ({
  completion: profileCompletion.value,
  rating: 4.5, 
  joinedDate: (profileData.value && profileData.value.member_since) 
    ? new Date(profileData.value.member_since.replace(' ', 'T')).toLocaleDateString('en-IN', { 
        day: '2-digit', month: 'short', year: 'numeric' 
      }) 
    : '...', 
  // Get city from profileData address if it exists
  location: profileData.value?.address?.city || 'Location not set',
  industry: formData.value.businessType || 'Company',
  verified: true
}))

const memberSince = computed(() => {
    const rawDate = dashboardData.value.profile?.creation;
    if (!rawDate) return '...';
    
    // Fixes the "Invalid Date" error by converting to ISO format
    return new Date(rawDate.replace(' ', 'T')).toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
});

// Inside Profile.vue <script setup>
const isEditing = ref(false)

const toggleEdit = () => {
  if (isEditing.value) {
    // Logic to save data would go here
    saveProfileData() 
  }
  isEditing.value = !isEditing.value
}

const saveProfileData = async () => {
    // You can implement the API call to update the supplier record here later
    console.log("Saving data...", formData.value)
}

const fetchProfileData = async () => {
  isLoading.value = true
  try {
    const response = await authStore.secureFetch('/api/method/supplier_portal.api.get_supplier_profile')
    const result = await response.json()
    
    if (result.message) {
      const m = result.message
      profileData.value = m // Set this first
      
      // Update the entire object at once to prevent data loss
      formData.value = {
        companyName: m.supplier_name || '',
        businessType: m.business_type || '',
        gst: m.gst_number || '', // Note: Python function returned 'gst_number'
        pan: m.pan_number || '',  // Note: Python function returned 'pan_number'
        contactEmail: m.contact?.email_id || '',
        contactPhone: m.contact?.mobile_no || '',
        website: m.website || '',
        address: m.address?.address_line1 ? `${m.address.address_line1}, ${m.address.city}` : '',
        about: m.about_company || '',
        employees: m.employee_count || 'Not Specified',
        turnover: m.annual_turnover || 'Not Specified',
        AboutCompany:m.supplier_details,
        website:m.website,
        // ADDED HERE: This prevents the 'blank page' crash
        productCategories: m.product_categories ?? []
      }
    }
    
    const statsResponse = await authStore.secureFetch('/api/method/supplier_portal.api.get_dashboard_stats')
    const statsResult = await statsResponse.json()
    if (statsResult.message) {
        dashboardData.value = statsResult.message
    }
  } catch (e) {
    console.error("Profile Fetch Error:", e)
  } finally {
    isLoading.value = false
  }
}

const profileCompletion = computed(() => {
    if (!profileData.value) return 0;
    
    // Use the mapped formData values instead of raw profileData
    // because formData already handled the nesting logic
    const fields = [
        formData.value.companyName,
        formData.value.businessType,
        formData.value.address,
        formData.value.contactEmail,
        formData.value.gst
    ];
    
    const filled = fields.filter(f => f && f !== '' && f !== 'Not Specified').length;
    return Math.round((filled / fields.length) * 100);
});

const documents = ref([
  { name: 'Company Registration Certificate', date: '15 Jan 2024', type: 'pdf' },
  { name: 'GST Certificate', date: '15 Jan 2024', type: 'pdf' }
])

const certifications = ref([
  { name: 'ISO 9001:2015', validUntil: '15 Dec 2025', status: 'Active' },
  { name: 'GST Registered', validUntil: '', status: 'Active' },
])

const settings = ref({
  newTender: true,
  bidStatus: true,
  deadlines: true,
  orderUpdates: false,
  weeklyDigest: false
})

onMounted(fetchProfileData)
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
             <span class="flex items-center gap-1"><Calendar class="h-4 w-4" /> Member since {{memberSince}}</span>
          </div>
        </div>
        
        <div>
   <button 
      @click="isEditing = !isEditing"
      :class="[
        isEditing 
          ? 'bg-green-600 text-white border-green-600 hover:bg-green-700' 
          : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
      ]"
      class="flex items-center gap-2 px-4 py-2 border rounded-lg text-sm font-medium shadow-sm transition-all"
   >
      <component :is="isEditing ? CheckCircle : Edit2" class="h-4 w-4" />
      {{ isEditing ? 'Save Changes' : 'Edit Profile' }}
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
                  <span class="text-sm font-bold text-gray-900">{{ dashboardData.stats?.total_bids || 0 }}</span>
               </div>
               <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                     <div class="p-2 bg-gray-50 rounded-lg">
                        <Award class="h-4 w-4 text-gray-500" />
                     </div>
                     <span class="text-sm text-gray-600">Orders Won</span>
                  </div>
                  <span class="text-sm font-bold text-green-600">{{ dashboardData.stats?.orders_won || 0 }}</span>
               </div>
               <div class="flex items-center justify-between">
                  <div class="flex items-center gap-3">
                     <div class="p-2 bg-gray-50 rounded-lg">
                        <TrendingUp class="h-4 w-4 text-gray-500" />
                     </div>
                     <span class="text-sm text-gray-600">Win Rate</span>
                  </div>
                  <span class="text-sm font-bold text-gray-900">{{ dashboardData.stats?.win_rate || '0%' }}</span>
               </div>
               <div class="pt-3 border-t border-gray-100 flex items-center justify-between">
                  <div class="flex items-center gap-3">
                     <div class="p-2 bg-gray-50 rounded-lg">
                        <FileCheck class="h-4 w-4 text-gray-500" />
                     </div>
                     <span class="text-xs text-gray-600">Total Value Won</span>
                  </div>
                  <span class="text-sm font-bold text-gray-900">₹{{ dashboardData.stats?.orders_won_value || '0.00' }}</span>
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
                     <input type="text" v-model="formData.companyName" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Business Type</label>
                     <input type="text" v-model="formData.businessType" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">GST Number</label>
                     <input type="text" v-model="formData.gst" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">PAN Number</label>
                     <input type="text" v-model="formData.pan" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" />
                  </div>
               </div>
               
               <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">About Company</label>
                  <textarea rows="3" v-model="formData.about" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all"></textarea>
               </div>
               
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Annual Turnover</label>
                     <input type="text" v-model="formData.turnover" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Employee Count</label>
                     <input type="text" v-model="formData.employees" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" />
                  </div>
                </div>

               <div class="border-t border-gray-100 pt-6">
                  <h4 class="text-sm font-bold text-gray-900 mb-4 flex items-center gap-2"><User class="h-4 w-4 text-gray-400" /> Contact Information</h4>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                        <input type="email" v-model="formData.contactEmail" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" />
                     </div>
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                        <input type="text" v-model="formData.contactPhone" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" />
                     </div>
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Website</label>
                        <input type="text" v-model="formData.website" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" />
                     </div>
                     <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Location</label>
                        <input type="text" v-model="profileParams.location" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all"/>
                     <div class="md:col-span-2">
                        <label class="block text-sm font-medium text-gray-700 mb-1">Full Address</label>
                        <textarea rows="2" v-model="formData.address" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all"></textarea>
                     </div>
                     </div>
                  </div>
               </div>
            </form>
            <div class="bg-white p-6 rounded-xl border border-gray-200 mt-6">
               <h3 class="text-sm font-bold text-gray-900 mb-4">Product Categories</h3>
               <div class="flex flex-wrap gap-2">
                  <span v-for="cat in formData.productCategories" :key="cat" 
                        class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium border border-gray-200">
                     {{ cat }}
                  </span>
               </div>
            </div>
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
