<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../auth.js'
import { Lock, Mail, Info } from 'lucide-vue-next'

const router = useRouter()
const { login } = useAuth()
const email = ref('supplier@techsolutions.com')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async (e) => {
  e.preventDefault()
  loading.value = true
  errorMsg.value = ''
  try {
     await login(email.value, password.value)
     router.push('/dashboard')
  } catch (error) {
     console.error("Login failed", error)
     errorMsg.value = 'Invalid login credentials'
  } finally {
     loading.value = false
  }
}

const fillDemo = () => {
   email.value = 'supplier@techsolutions.com'
   password.value = '123456'
}
</script>

<template>
  <div class="flex min-h-screen flex-col items-center pt-20 bg-gray-50 pb-12">
    <!-- Header -->
    <div class="w-full max-w-md mb-8 flex justify-between items-center px-4">
       <div class="flex items-center gap-2">
          <div class="h-8 w-8 flex items-center justify-center rounded-lg bg-indigo-600 text-white font-bold text-xl">T</div>
          <span class="font-bold text-gray-900 text-lg">TenderFlow</span>
       </div>
    </div>

    <!-- Login Card -->
    <div class="w-full max-w-md bg-white rounded-xl shadow-sm border border-gray-100 p-8">
       <div class="text-center mb-8">
          <div class="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 text-white mb-4 shadow-indigo-100 shadow-lg">
             <Lock class="h-6 w-6" />
          </div>
          <h2 class="text-2xl font-bold text-gray-900">Welcome Back</h2>
          <p class="mt-2 text-sm text-gray-500">Sign in to your vendor account to manage bids</p>
       </div>

       <!-- Demo Alert -->
       <div class="mb-6 rounded-lg bg-indigo-50 p-4 border border-indigo-100">
          <div class="flex">
             <div class="flex-shrink-0">
                <Info class="h-5 w-5 text-indigo-400" aria-hidden="true" />
             </div>
             <div class="ml-3">
                <h3 class="text-sm font-medium text-indigo-800">Demo Mode</h3>
                <div class="mt-2 text-sm text-indigo-700">
                   <p>Use the pre-filled credentials or click below to auto-fill demo login. <button @click="fillDemo" class="font-bold underline cursor-pointer hover:text-indigo-900">Fill Demo Credentials</button></p>
                </div>
             </div>
          </div>
       </div>

       <form @submit="handleLogin" class="space-y-5">
          <div>
             <label for="email" class="block text-sm font-medium text-gray-900 mb-1">Email Address</label>
             <input id="email" type="email" v-model="email" required class="block w-full rounded-lg border-0 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 bg-gray-50" />
          </div>

          <div>
             <div class="flex items-center justify-between mb-1">
                <label for="password" class="block text-sm font-medium text-gray-900">Password</label>
                <a href="#" class="text-sm font-semibold text-indigo-600 hover:text-indigo-500">Forgot password?</a>
             </div>
             <input id="password" type="password" v-model="password" required class="block w-full rounded-lg border-0 py-2.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 bg-gray-50" />
          </div>
          
          <div v-if="errorMsg" class="text-red-500 text-sm text-center">{{ errorMsg }}</div>

          <button type="submit" :disabled="loading" class="flex w-full justify-center rounded-lg bg-indigo-600 px-3 py-2.5 text-sm font-semibold leading-6 text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all hover:scale-[1.01] shadow-indigo-200">
             <span v-if="loading">Signing in...</span>
             <span v-else>Sign In</span>
          </button>
       </form>

       <div class="mt-6 text-center text-sm text-gray-500">
          Don't have an account? 
          <router-link to="/register" class="font-semibold text-indigo-600 hover:text-indigo-500">Register as Vendor</router-link>
       </div>
    </div>
  </div>
</template>
