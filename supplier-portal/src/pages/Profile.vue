<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  Building2, FileText, Award, Settings, MapPin, Calendar, CheckCircle,
  Star, Edit2, Download, Upload, Shield, Bell, Lock, Trash2,
  ShoppingBag, TrendingUp, FileCheck, X, UploadCloud, Eye, Loader2
} from 'lucide-vue-next'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()
const activeTab = ref('Company')
const tabs = ['Company', 'Documents', 'Certifications', 'Settings']
const isLoading = ref(true)

const isDocModalOpen = ref(false)
const uploading = ref(false)
const newDoc = ref({ name: '', file: null, expiry_date: '' })

const handleDocFileChange = (e) => {
  newDoc.value.file = e.target.files[0]
}

const handleUpload = async () => {
  if (activeTab.value === 'Certifications') {
    await uploadCertificate()
  } else {
    await uploadDocument()
  }
}

const uploadDocument = async () => {
  if (!newDoc.value.name || !newDoc.value.file) {
    return alert("Please provide a document name and select a file.")
  }

  uploading.value = true
  try {
    const base64Content = await getBase64(newDoc.value.file)
    const response = await authStore.secureFetch('/api/method/supplier_portal.api.upload_supplier_document', {
      method: 'POST',
      body: JSON.stringify({
        doc_name: newDoc.value.name,
        filename: newDoc.value.file.name,
        filedata: base64Content
      })
    })

    const res = await response.json()
    if (res.message === "success") {
      await fetchProfileData() 
      closeModal()
    }
  } catch (error) {
    console.error("Upload failed:", error)
    alert("Error uploading document")
  } finally {
    uploading.value = false
  }
}

const uploadCertificate = async () => {
  if (!newDoc.value.name || !newDoc.value.file) {
    return alert("Please provide certificate name and file.")
  }

  uploading.value = true
  try {
    const base64Content = await getBase64(newDoc.value.file)
    
    const response = await authStore.secureFetch('/api/method/supplier_portal.api.upload_supplier_certificate', {
      method: 'POST',
      body: JSON.stringify({
        doc_name: newDoc.value.name,
        filename: newDoc.value.file.name,
        filedata: base64Content,
        expiry_date: newDoc.value.expiry_date
      })
    })

    const res = await response.json()
    if (res.message === "success") {
      await fetchProfileData() 
      closeModal()
    }
  } catch (error) {
    console.error("Upload failed:", error)
    alert("Error uploading certificate")
  } finally {
    uploading.value = false
  }
}

const deleteCertificate = async (certName) => {
    if (!confirm("Are you sure you want to delete this certificate?")) return;

    try {
        const getCookie = (name) => {
            let r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        };

        const params = new URLSearchParams();
        params.append('certificate_name', certName);

        const response = await fetch('/api/method/supplier_portal.api.delete_supplier_certificate', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Frappe-CSRF-Token': window.csrf_token || getCookie('sid')
            },
            body: params
        });
        
        const result = await response.json();
        
        if (result.message === "success") {
            if (typeof supplierData !== 'undefined' && supplierData.value) {
                supplierData.value.custom_supplier_certificates = supplierData.value.custom_supplier_certificates.filter(
                    c => c.supplier_certificate_name !== certName
                );
            } 
            else if (typeof profileData !== 'undefined' && profileData.value) {
                profileData.value.custom_supplier_certificates = profileData.value.custom_supplier_certificates.filter(
                    c => c.supplier_certificate_name !== certName
                );
            }
            else if (typeof formData !== 'undefined' && formData.value.custom_supplier_certificates) {
                formData.value.custom_supplier_certificates = formData.value.custom_supplier_certificates.filter(
                    c => c.supplier_certificate_name !== certName
                );
            }
            else {
                if (typeof fetchProfileData === 'function') {
                    fetchProfileData();
                }
            }
        }
    } catch (error) {
        console.error("Delete request failed:", error);
    }
};

const deleteDocument = async (docName) => {
    if (!confirm("Are you sure you want to delete this document?")) return;

    try {
        const getCookie = (name) => {
            let r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
            return r ? r[1] : undefined;
        };

        const params = new URLSearchParams();
        params.append('doc_entry_name', docName);

        const response = await fetch('/api/method/supplier_portal.api.delete_supplier_document', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-Frappe-CSRF-Token': window.csrf_token || getCookie('sid')
            },
            body: params
        });
        
        const result = await response.json();
        
        if (result.message === "success") {
            const dataObj = typeof supplierData !== 'undefined' ? supplierData : 
                            typeof profileData !== 'undefined' ? profileData : null;

            if (dataObj && dataObj.value.custom_supplier_documents) {
                dataObj.value.custom_supplier_documents = dataObj.value.custom_supplier_documents.filter(
                    doc => doc.name !== docName
                );
            }
        }
    } catch (error) {
        console.error("Document delete failed:", error);
    }
};

const closeModal = () => {
  isDocModalOpen.value = false
  newDoc.value = { name: '', file: null, expiry_date: '' }
}

const previewDocument = (fileUrl) => {
  if (!fileUrl) return alert("No file attached to this document.");
  const url = fileUrl.startsWith('http') ? fileUrl : window.location.origin + fileUrl;
  window.open(url, '_blank');
};

const profileData = ref(null)
const dashboardData = ref({
    stats: { total_bids: 0, orders_won: 0, win_rate: '0%', orders_won_value: '0.00' }
})

const formData = ref({
  companyName: '', businessType: '', gst: '', pan: '', contactEmail: '',
  contactPhone: '', website: '', address: '', about: '', employees: '',
  turnover: '', productCategories: [], AboutCompany: ''
})

const documents = computed(() => {
  return profileData.value?.custom_supplier_documents || []
})

const certifications = computed(() => {
  return profileData.value?.custom_supplier_certificates || []
})

const formatDate = (dateStr) => {
  if (!dateStr) return '';
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric'
  });
}

const profileParams = computed(() => ({
  completion: profileCompletion.value,
  rating: 4.5, 
  joinedDate: (profileData.value && profileData.value.member_since) 
    ? new Date(profileData.value.member_since.replace(' ', 'T')).toLocaleDateString('en-IN', { 
        day: '2-digit', month: 'short', year: 'numeric' 
      }) 
    : '...', 
  location: profileData.value?.address?.city || 'Location not set',
  industry: formData.value.businessType || 'Company',
  verified: true
}))

const memberSince = computed(() => {
    const rawDate = profileData.value?.creation;
    if (!rawDate) return '...';
    return new Date(rawDate.replace(' ', 'T')).toLocaleDateString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric'
    });
});

const profileCompletion = computed(() => {
  if (!profileData.value) return 0;

  const fields = [
    { value: profileData.value.supplier_name, weight: 10 },
    { value: profileData.value.gst_number, weight: 10 },
    { value: profileData.value.pan_number, weight: 10 },
    { value: profileData.value.website, weight: 10 },
    { value: profileData.value.supplier_details, weight: 15 },
    { value: profileData.value.address?.address_line1, weight: 15 },
    { value: profileData.value.contact?.mobile_no, weight: 10 },
    { value: profileData.value.custom_supplier_documents?.length > 0, weight: 10 },
    { value: profileData.value.custom_supplier_certificates?.length > 0, weight: 10 }
  ];

  const total = fields.reduce((acc, field) => {
    const isComplete = Array.isArray(field.value) ? field.value.length > 0 : !!field.value;
    return acc + (isComplete ? field.weight : 0);
  }, 0);

  return Math.min(total, 100);
});

const isEditing = ref(false)
const toggleEdit = () => {
  if (isEditing.value) saveProfileData() 
  isEditing.value = !isEditing.value
}

const saveProfileData = async () => {
    console.log("Saving data...", formData.value)
}

const getBase64 = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result.split(',')[1])
    reader.onerror = error => reject(error)
  })
}

const fetchProfileData = async () => {
  isLoading.value = true
  try {
    const response = await authStore.secureFetch('/api/method/supplier_portal.api.get_supplier_profile')
    const result = await response.json()
    
    if (result.message) {
      const m = result.message
      profileData.value = m
      
      formData.value = {
        companyName: m.supplier_name || '',
        businessType: m.business_type || '',
        gst: m.gst_number || '',
        pan: m.pan_number || '',
        contactEmail: m.contact?.email_id || '',
        contactPhone: m.contact?.mobile_no || '',
        businessPhone: m.address?.phone || '',
        website: m.website || '',
        address: m.address?.address_line1 ? `${m.address.address_line1}, ${m.address.city}` : '',
        AboutCompany: m.supplier_details || '',
        employees: m.employee_count || 'Not Specified',
        turnover: m.annual_turnover || 'Not Specified',
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

const settings = ref({
  newTender: true, bidStatus: true, deadlines: true, orderUpdates: false, weeklyDigest: false
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
                  <textarea rows="3" v-model="formData.AboutCompany" :disabled="!isEditing" :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all"></textarea>
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
                        <input 
                           type="text" 
                           v-model="profileData.address.phone" 
                           :disabled="!isEditing" 
                           :class="[!isEditing ? 'bg-gray-50 ring-gray-200' : 'bg-white ring-indigo-600 ring-2']" 
                           class="block w-full rounded-md border-0 py-2 text-gray-900 ring-1 ring-inset sm:text-sm sm:leading-6 transition-all" 
                           placeholder="No office phone set"
                     />
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
          <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
            <FileText class="h-4 w-4 text-gray-500" /> Uploaded Documents
          </h3>
          <button @click="isDocModalOpen = true" class="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500 transition-all">
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
                   <p class="text-sm font-medium text-gray-900">{{ doc.document_name }}</p>
                   <p class="text-xs text-gray-500">Uploaded on {{ doc.date }}</p>
                </div>
             </div>
             <div class="flex items-center gap-2">
                <button 
                     @click="deleteDocument(doc.name)" 
                     class="p-2 text-gray-400 hover:text-red-500 transition-colors"
                     title="Delete Document"
                  >
                     <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                     </svg>
                  </button>
                <a :href="doc.file" download class="p-2 text-gray-400 hover:text-indigo-600 hover:bg-white rounded-full transition-colors">
                  <Download class="h-4 w-4" />
                </a>
             </div>
          </div>
          
          <div v-if="!documents.length" class="text-center py-10 border-2 border-dashed border-gray-100 rounded-xl text-gray-400 text-sm">
             No documents uploaded yet.
          </div>
       </div>
    </div>
</div>

         <!-- Certifications Tab -->
         <div v-show="activeTab === 'Certifications'" class="space-y-6 animate-fade-in">
    <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
       <div class="flex items-center justify-between mb-6">
          <h3 class="text-sm font-bold text-gray-900 flex items-center gap-2">
            <Award class="h-4 w-4 text-gray-500" /> Certifications & Compliance
          </h3>
          <button @click="isDocModalOpen = true" class="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-xs font-semibold text-white shadow-sm hover:bg-indigo-500">
             <Upload class="h-3 w-3" /> Add Certificate
          </button>
       </div>

       <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div v-for="(cert, idx) in certifications" :key="idx" 
     class="p-4 rounded-xl border border-gray-100 bg-white hover:border-indigo-100 transition-all shadow-sm group relative">
    
    <div class="flex items-start justify-between">
        <div class="flex items-start gap-3">
            <div class="mt-1 p-2 rounded-lg bg-indigo-50 text-indigo-600">
                <Shield class="h-5 w-5" />
            </div>
            
            <div class="space-y-1">
                <div class="flex items-center gap-2">
                    <span class="text-sm font-bold text-gray-900 leading-none">
                     {{ cert.supplier_certificate_name || cert.supplier_certificate || 'Unnamed Certificate' }}
                  </span>
                </div>
                
                <div class="flex items-center gap-1.5 text-xs text-gray-500">
                    <Calendar class="h-3 w-3" />
                    {{ cert.expiry_date ? 'Valid until ' + formatDate(cert.expiry_date) : 'Life-time Validity' }}
                </div>
            </div>
        </div>

        <span class="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-[10px] font-bold text-green-700 ring-1 ring-inset ring-green-600/20">
            <button 
                  @click="deleteCertificate(cert.supplier_certificate_name)"
                  class="p-2 text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-200"
                  title="Delete Certificate"
               >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
               </button>
        </span>
    </div>
    </div>
          
          <div v-if="!certifications.length" class="col-span-full text-center py-10 border-2 border-dashed border-gray-100 rounded-xl text-gray-400 text-sm">
             No certifications found.
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
  <div v-if="isDocModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
  <div class="fixed inset-0 bg-gray-500/75 backdrop-blur-sm" @click="isDocModalOpen = false"></div>
  
  <div class="relative bg-white rounded-xl shadow-xl w-full max-w-md p-6 overflow-hidden animate-in fade-in zoom-in duration-200">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-bold text-gray-900">Upload New Document</h3>
      <button @click="isDocModalOpen = false" class="text-gray-400 hover:text-gray-500">
        <X class="h-5 w-5" />
      </button>
    </div>

    <div class="space-y-5">
      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Document Name</label>
        <input 
          v-model="newDoc.name" 
          type="text" 
          placeholder="e.g. GST Certificate"
          class="w-full rounded-lg border-gray-200 text-sm focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
        />
      </div>

      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Attachment</label>
        <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-200 border-dashed rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors">
          <div class="space-y-1 text-center">
            <UploadCloud class="mx-auto h-10 w-10 text-gray-400" />
            <div class="flex text-sm text-gray-600 justify-center">
              <label class="relative cursor-pointer font-semibold text-indigo-600 hover:text-indigo-500">
                <span>Select a file</span>
                <input type="file" class="sr-only" @change="handleDocFileChange" />
              </label>
            </div>
            <p v-if="newDoc.file" class="text-xs text-indigo-600 font-bold mt-2">
              {{ newDoc.file.name }}
            </p>
            <p v-else class="text-xs text-gray-400">PDF, PNG, JPG up to 10MB</p>
          </div>
        </div>
      </div>

      <button 
        @click="uploadDocument" 
        :disabled="uploading"
        class="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-bold text-sm shadow-sm hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
      >
        <Loader2 v-if="uploading" class="h-4 w-4 animate-spin" />
        {{ uploading ? 'Uploading...' : 'Upload Document' }}
      </button>
    </div>
  </div>
</div>

<div v-if="isDocModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
  <div class="fixed inset-0 bg-gray-500/75 backdrop-blur-sm" @click="isDocModalOpen = false"></div>
  
  <div class="relative bg-white rounded-xl shadow-xl w-full max-w-md p-6 overflow-hidden animate-in fade-in zoom-in duration-200">
    <div class="flex justify-between items-center mb-6">
      <h3 class="text-lg font-bold text-gray-900">
        {{ activeTab === 'Certifications' ? 'Upload New Certificate' : 'Upload New Document' }}
      </h3>
      <button @click="isDocModalOpen = false" class="text-gray-400 hover:text-gray-500">
        <X class="h-5 w-5" />
      </button>
    </div>

    <div class="space-y-5">
      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Certificate Name</label>
        <input 
          v-model="newDoc.name" 
          type="text" 
          placeholder="e.g. ISO 9001 Certificate"
          class="w-full rounded-lg border-gray-200 text-sm focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
        />
      </div>

      <div v-if="activeTab === 'Certifications'">
        <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Expiry Date (Optional)</label>
        <input 
          v-model="newDoc.expiry_date" 
          type="date" 
          class="w-full rounded-lg border-gray-200 text-sm focus:ring-2 focus:ring-indigo-600 focus:border-transparent"
        />
      </div>

      <div>
        <label class="block text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Attachment</label>
        <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-200 border-dashed rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors">
          <div class="space-y-1 text-center">
            <UploadCloud class="mx-auto h-10 w-10 text-gray-400" />
            <div class="flex text-sm text-gray-600 justify-center">
              <label class="relative cursor-pointer font-semibold text-indigo-600 hover:text-indigo-500">
                <span>Select a file</span>
                <input type="file" class="sr-only" @change="handleDocFileChange" />
              </label>
            </div>
            <p v-if="newDoc.file" class="text-xs text-indigo-600 font-bold mt-2">{{ newDoc.file.name }}</p>
            <p v-else class="text-xs text-gray-400">PDF, PNG, JPG up to 10MB</p>
          </div>
        </div>
      </div>

      <button 
        @click="activeTab === 'Certifications' ? uploadCertificate() : uploadDocument()" 
        :disabled="uploading"
        class="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-bold text-sm shadow-sm hover:bg-indigo-700 disabled:bg-gray-300 transition-all flex items-center justify-center gap-2"
      >
        <Loader2 v-if="uploading" class="h-4 w-4 animate-spin" />
        {{ uploading ? 'Uploading...' : (activeTab === 'Certifications' ? 'Upload Certificate' : 'Upload Document') }}
      </button>
    </div>
  </div>
</div>

</template>
