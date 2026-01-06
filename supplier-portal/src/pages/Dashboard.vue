<script setup>
import { ref } from 'vue'
import { 
  Trophy, 
  FileText, 
  Clock, 
  TrendingUp,
  Receipt,
  MoreHorizontal,
  Download,
  CheckCircle,
  AlertCircle
} from 'lucide-vue-next'
import { useAuth } from '../auth.js'

const { state } = useAuth()

const stats = [
  { 
    name: 'Total Bids', 
    value: '6', 
    icon: FileText, 
    change: '15%', 
    changeType: 'increase' 
  },
  { 
    name: 'Orders Won', 
    value: '2', 
    icon: Trophy, 
    change: '25%', 
    changeType: 'increase' 
  },
  { 
    name: 'Pending Review', 
    value: '2', 
    icon: Clock, 
    change: '5%', 
    changeType: 'decrease' 
  },
  { 
    name: 'Win Rate', 
    value: '33%', 
    icon: TrendingUp, 
    change: '8%', 
    changeType: 'increase' 
  },
]

const recentBids = [
  { 
    title: 'Industrial Steel Plates - Grade A',
    amount: '₹33,50,000',
    date: '25 Jan 2024',
    rank: '#2',
    status: 'Shortlisted',
    statusColor: 'bg-blue-100 text-blue-800'
  },
  { 
    title: 'Electrical Control Panels',
    amount: '₹27,00,000',
    date: '28 Jan 2024',
    rank: '#3',
    status: 'Under Review',
    statusColor: 'bg-yellow-100 text-yellow-800'
  },
  { 
    title: 'Safety Equipment Batch 2024',
    amount: '₹4,50,000',
    date: '12 Feb 2024',
    rank: '#1',
    status: 'L1 Bidder',
    statusColor: 'bg-green-100 text-green-800'
  }
]

const activities = [
  {
    title: 'Submitted bid for Steel Plates',
    time: '2 hours ago',
    icon: FileText,
    iconColor: 'bg-blue-100 text-blue-600'
  },
  {
    title: 'Won Industrial Motors tender',
    time: '1 day ago',
    icon: Trophy,
    iconColor: 'bg-green-100 text-green-600'
  },
  {
    title: 'Shortlisted for Packaging Materials',
    time: '2 days ago',
    icon: Trophy,
    iconColor: 'bg-yellow-100 text-yellow-600'
  },
    {
    title: 'Submitted bid for Safety Equipment',
    time: '2 days ago',
    icon: FileText,
    iconColor: 'bg-blue-100 text-blue-600'
  }
]

const profileCompletion = 85
</script>

<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="bg-white border-b border-gray-200">
      <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div class="md:flex md:items-center md:justify-between">
          <div class="min-w-0 flex-1">
            <div class="flex items-center gap-3 mb-2">
                <div class="h-12 w-12 rounded-lg bg-indigo-600 flex items-center justify-center text-white text-xl font-bold">
                    {{ state.user?.name?.charAt(0) || 'U' }}
                </div>
                <div>
                     <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl sm:tracking-tight">
                    Welcome back!
                    </h2>
                     <div class="flex items-center gap-2 text-sm text-gray-500">
                        {{ state.user?.company || 'Company Name' }}
                        <span class="inline-flex items-center rounded-full bg-green-50 px-2 py-0.5 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                            <CheckCircle class="mr-1 h-3 w-3" />
                            Verified
                        </span>
                     </div>
                </div>
            </div>
            <p class="mt-1 text-sm text-gray-500">Track your bids and performance metrics.</p>
          </div>
          <div class="mt-4 flex md:ml-4 md:mt-0">
            <button type="button" class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50" @click="$router.push('/profile')">
              <User class="-ml-0.5 mr-1.5 h-5 w-5 text-gray-400" aria-hidden="true" />
              Profile
            </button>
            <button type="button" class="ml-3 inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600" @click="$router.push('/tenders')">
              Browse Tenders
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      
      <!-- Stats -->
      <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <div v-for="item in stats" :key="item.name" class="overflow-hidden rounded-xl bg-white p-6 shadow-sm ring-1 ring-gray-900/5 transition-all hover:shadow-md">
          <div class="flex items-center justify-between">
             <div>
                <dt class="truncate text-sm font-medium text-gray-500">{{ item.name }}</dt>
                <dd class="mt-2 text-3xl font-semibold tracking-tight text-gray-900">{{ item.value }}</dd>
             </div>
             <div class="p-3 bg-gray-50 rounded-lg">
                <component :is="item.icon" class="h-6 w-6 text-indigo-600" />
             </div>
          </div>
          <div class="mt-4 flex items-center text-sm">
             <span :class="[
                item.changeType === 'increase' ? 'text-green-600' : 'text-red-600',
                'font-medium flex items-center'
             ]">
                {{ item.changeType === 'increase' ? '↑' : '↓' }} {{ item.change }}
             </span>
             <span class="ml-2 text-gray-400">vs last month</span>
          </div>
        </div>
      </div>

      <!-- Tabs (Visual Only for now) -->
      <div class="border-b border-gray-200 mb-8">
        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
          <a href="#" class="border-indigo-500 text-indigo-600 whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium" aria-current="page">Overview</a>
          <a href="#" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium">My Bids</a>
          <a href="#" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium">Analytics</a>
        </nav>
      </div>

      <div class="grid grid-cols-1 gap-8 lg:grid-cols-3">
        <!-- Left Column -->
        <div class="lg:col-span-2 space-y-8">
           <!-- Value Cards -->
           <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="bg-white rounded-xl p-6 shadow-sm ring-1 ring-gray-900/5">
                 <div class="flex items-center gap-4">
                    <div class="h-10 w-10 rounded-full bg-blue-50 flex items-center justify-center">
                       <span class="text-blue-600 font-bold">₹</span>
                    </div>
                    <div>
                       <p class="text-sm font-medium text-gray-500">Total Bid Value</p>
                       <p class="text-xl font-bold text-gray-900">₹1,57,70,000</p>
                    </div>
                 </div>
              </div>
              <div class="bg-white rounded-xl p-6 shadow-sm ring-1 ring-gray-900/5">
                 <div class="flex items-center gap-4">
                    <div class="h-10 w-10 rounded-full bg-green-50 flex items-center justify-center">
                       <Trophy class="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                        <p class="text-sm font-medium text-gray-500">Orders Won Value</p>
                        <p class="text-xl font-bold text-gray-900">₹10,70,000</p>
                    </div>
                 </div>
              </div>
           </div>

           <!-- Recent Bids -->
           <div class="bg-white rounded-xl shadow-sm ring-1 ring-gray-900/5">
              <div class="flex items-center justify-between border-b border-gray-100 px-6 py-4">
                 <div class="flex items-center gap-2">
                    <FileText class="h-5 w-5 text-indigo-600" />
                    <h3 class="font-semibold text-gray-900">Recent Bids</h3>
                 </div>
                 <a href="#" class="text-sm font-semibold text-indigo-600 hover:text-indigo-500 flex items-center">
                    View All <span aria-hidden="true" class="ml-1">→</span>
                 </a>
              </div>
              <ul role="list" class="divide-y divide-gray-100">
                 <li v-for="bid in recentBids" :key="bid.title" class="px-6 py-4 hover:bg-gray-50 transition-colors">
                    <div class="flex items-center justify-between gap-x-6">
                       <div class="min-w-0">
                          <div class="flex items-start gap-x-3">
                             <p class="text-sm font-semibold leading-6 text-gray-900">{{ bid.title }}</p>
                          </div>
                          <div class="mt-1 flex items-center gap-x-2 text-xs leading-5 text-gray-500">
                             <p>{{ bid.amount }}</p>
                             <svg viewBox="0 0 2 2" class="h-0.5 w-0.5 fill-current"><circle cx="1" cy="1" r="1" /></svg>
                             <p>{{ bid.date }}</p>
                          </div>
                       </div>
                       <div class="flex flex-none items-center gap-x-4">
                          <span class="font-medium text-amber-500 text-sm">{{ bid.rank }}</span>
                          <span :class="[bid.statusColor, 'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-gray-500/10']">
                             {{ bid.status }}
                          </span>
                       </div>
                    </div>
                 </li>
              </ul>
           </div>
        </div>

        <!-- Right Column -->
        <div class="space-y-8">
           <!-- Profile Strength -->
           <div class="bg-white rounded-xl p-6 shadow-sm ring-1 ring-gray-900/5">
              <h3 class="font-semibold text-gray-900 mb-4">Profile Strength</h3>
              <div class="flex items-center gap-6">
                 <div class="relative h-20 w-20 flex-shrink-0">
                    <svg class="h-full w-full -rotate-90 transform" viewBox="0 0 36 36">
                       <path class="text-gray-100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-width="4" />
                       <path class="text-indigo-600" :stroke-dasharray="`${profileCompletion}, 100`" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
                    </svg>
                    <div class="absolute inset-0 flex items-center justify-center flex-col">
                       <span class="text-sm font-bold text-gray-900">{{ profileCompletion }}%</span>
                    </div>
                 </div>
                 <div>
                    <p class="text-sm text-gray-600 mb-2">Complete your profile to increase visibility</p>
                    <a href="#" class="text-sm font-semibold text-indigo-600 hover:text-indigo-500">Complete Now →</a>
                 </div>
              </div>
           </div>

           <!-- Recent Activity -->
           <div class="bg-white rounded-xl shadow-sm ring-1 ring-gray-900/5">
              <div class="p-4 border-b border-gray-100">
                 <h3 class="font-semibold text-gray-900 flex items-center gap-2">
                    <TrendingUp class="h-4 w-4 text-gray-400" />
                    Recent Activity
                 </h3>
              </div>
              <div class="p-4">
                 <ul role="list" class="space-y-6">
                    <li v-for="(activity, activityIdx) in activities" :key="activityIdx" class="relative flex gap-x-4">
                       <div class="absolute left-0 top-0 flex w-6 justify-center -bottom-6" v-if="activityIdx !== activities.length - 1">
                          <div class="w-px bg-gray-200" />
                       </div>
                       <div :class="[activity.iconColor, 'relative flex h-8 w-8 flex-none items-center justify-center rounded-lg bg-gray-50']">
                          <component :is="activity.icon" class="h-4 w-4" aria-hidden="true" />
                       </div>
                       <div class="flex-auto py-0.5">
                          <p class="text-sm font-medium text-gray-900 leading-snug">{{ activity.title }}</p>
                          <p class="text-xs text-gray-500 mt-1">{{ activity.time }}</p>
                       </div>
                    </li>
                 </ul>
              </div>
           </div>
        </div>
      </div>
    </div>
  </div>
</template>
