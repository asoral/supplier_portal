<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { CheckCircle, Building2 } from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()
const register = authStore.signup

const formData = ref({
   companyName: '',
   contactPerson: '',
   gst: '',
   email: '',
   phone: '',
   address: '',
   password: '',
   confirmPassword: ''
})

const loading = ref(false)
const errorMsg = ref('')

const handleRegister = async (e) => {
  e.preventDefault()
  if (formData.value.password !== formData.value.confirmPassword) {
      alert("Passwords do not match");
      return;
  }
  
  loading.value = true
  errorMsg.value = ''

  try {
     await register({
        companyName: formData.value.companyName,
        contactPerson: formData.value.contactPerson,
        email: formData.value.email,
        phone: formData.value.phone,
        gst: formData.value.gst,
        password: formData.value.password
     })
     
     // On success, maybe show a success message or redirect to login
     alert("Registration successful! Please check your email or login.");
     router.push('/login')
  } catch (error) {
     console.error("Registration failed", error)
     errorMsg.value = error.message || "Registration failed"
  } finally {
     loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
     <!-- Header -->
    <div class="sm:mx-auto sm:w-full sm:max-w-md text-center mb-8">
       <div class="inline-flex items-center gap-2">
           <div class="h-8 w-8 flex items-center justify-center rounded-lg bg-indigo-600 text-white font-bold text-xl">T</div>
           <span class="font-bold text-gray-900 text-lg">TenderFlow</span>
       </div>
    </div>

    <div class="sm:mx-auto sm:w-full sm:max-w-[1000px]">
      <div class="bg-white shadow-xl sm:rounded-2xl overflow-hidden flex flex-col lg:flex-row">
         
         <!-- Left Side: Value Prop -->
         <div class="bg-slate-50 p-8 lg:p-12 lg:w-5/12 flex flex-col justify-center border-r border-gray-100">
            <h2 class="text-2xl font-bold text-gray-900 mb-6">Join Our Vendor Network</h2>
            <p class="text-gray-600 mb-8">Register today and start bidding on procurement opportunities from verified buyers.</p>
            
            <div class="space-y-6">
               <div class="flex gap-3">
                  <CheckCircle class="h-6 w-6 text-green-500 flex-shrink-0" />
                  <div>
                     <h3 class="font-semibold text-gray-900">Access to all active tenders</h3>
                     <p class="text-sm text-gray-500">Browse and bid on thousands of live opportunities.</p>
                  </div>
               </div>
               <div class="flex gap-3">
                  <CheckCircle class="h-6 w-6 text-green-500 flex-shrink-0" />
                  <div>
                     <h3 class="font-semibold text-gray-900">Real-time bid notifications</h3>
                     <p class="text-sm text-gray-500">Get instant alerts for relevant tenders and updates.</p>
                  </div>
               </div>
               <div class="flex gap-3">
                  <CheckCircle class="h-6 w-6 text-green-500 flex-shrink-0" />
                  <div>
                     <h3 class="font-semibold text-gray-900">Track your bid history</h3>
                     <p class="text-sm text-gray-500">Complete dashboard to manage all your submissions.</p>
                  </div>
               </div>
               <div class="flex gap-3">
                  <CheckCircle class="h-6 w-6 text-green-500 flex-shrink-0" />
                  <div>
                     <h3 class="font-semibold text-gray-900">Live bidding participation</h3>
                     <p class="text-sm text-gray-500">Enter dynamic reverse auctions for quick wins.</p>
                  </div>
               </div>
            </div>

            <div class="mt-12 bg-indigo-50 rounded-xl p-4 border border-indigo-100">
               <div class="text-xs font-semibold uppercase tracking-wide text-indigo-800 mb-2">Trusted By</div>
               <h3 class="text-lg font-bold text-gray-900">150+ Vendors</h3>
               <p class="text-xs text-gray-500">across manufacturing, trading, and services</p>
            </div>
         </div>
         
         <!-- Right Side: Form -->
         <div class="p-8 lg:p-12 lg:w-7/12">
            <div class="flex items-center gap-3 mb-6 pb-6 border-b border-gray-100">
               <div class="p-2 bg-indigo-100 rounded-lg text-indigo-600">
                  <Building2 class="h-6 w-6" />
               </div>
               <div>
                  <h3 class="text-lg font-bold text-gray-900">Vendor Registration</h3>
                  <p class="text-xs text-gray-500">Fill in your company details to create an account</p>
               </div>
            </div>

            <form @submit="handleRegister" class="space-y-4">
               <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Company Name *</label>
                     <input type="text" v-model="formData.companyName" required class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2 text-gray-900" placeholder="ABC Industries Pvt Ltd" />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Contact Person *</label>
                     <input type="text" v-model="formData.contactPerson" required class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2 text-gray-900" placeholder="John Doe" />
                  </div>
               </div>

               <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Email Address *</label>
                     <input type="email" v-model="formData.email" required class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2 text-gray-900" placeholder="contact@company.com" />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Phone Number *</label>
                     <input type="tel" v-model="formData.phone" required class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2 text-gray-900" placeholder="+91 98765 43210" />
                  </div>
               </div>

               <div>
                   <label class="block text-sm font-medium text-gray-700 mb-1">GST Number</label>
                   <input type="text" v-model="formData.gst" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2 text-gray-900" placeholder="22AAAAA0000A1Z5" />
               </div>

               <div>
                   <label class="block text-sm font-medium text-gray-700 mb-1">Registered Address *</label>
                   <textarea v-model="formData.address" required rows="2" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2 text-gray-900" placeholder="Full address with PIN code"></textarea>
               </div>

               <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Password *</label>
                     <input type="password" v-model="formData.password" required class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2 text-gray-900" placeholder="Min 8 characters" />
                  </div>
                  <div>
                     <label class="block text-sm font-medium text-gray-700 mb-1">Confirm Password *</label>
                     <input type="password" v-model="formData.confirmPassword" required class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2 text-gray-900" placeholder="Re-enter password" />
                  </div>
               </div>
               
               <div class="flex items-start">
                  <div class="flex h-5 items-center">
                    <input id="terms" name="terms" type="checkbox" required class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600" />
                  </div>
                  <div class="ml-3 text-sm">
                    <label for="terms" class="font-medium text-gray-700">I agree to the <a href="#" class="text-indigo-600 hover:text-indigo-500">Terms of Service</a> and <a href="#" class="text-indigo-600 hover:text-indigo-500">Privacy Policy</a></label>
                  </div>
               </div>
               
               <div v-if="errorMsg" class="text-red-500 text-sm text-center">{{ errorMsg }}</div>

               <button type="submit" :disabled="loading" class="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors">
                  <span v-if="loading">Creating Account...</span>
                  <span v-else>Create Vendor Account</span>
               </button>
               
               <div class="text-center text-sm text-gray-500 mt-4">
                  Already have an account? <router-link to="/login" class="font-bold text-indigo-600 hover:text-indigo-500">Sign In</router-link>
               </div>
            </form>
         </div>
      </div>
    </div>
  </div>
</template>
