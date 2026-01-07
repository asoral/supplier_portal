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
  AlertCircle,
  Eye,
  User,
  PieChart,
  BarChart3
} from 'lucide-vue-next'
import { useAuth } from '../auth.js'

const { state } = useAuth()
const activeTab = ref('Overview')

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

const bidHistory = [
  { 
    title: 'Industrial Steel Plates - Grade A',
    id: 'TND-2024-001',
    amount: '₹33,50,000',
    date: '25 Jan 2024',
    submitted: '25 Jan 2024',
    rank: '#2',
    status: 'Shortlisted',
    statusColor: 'bg-blue-100 text-blue-800'
  },
  { 
    title: 'Electrical Control Panels',
    id: 'TND-2024-004',
    amount: '₹27,00,000',
    date: '28 Jan 2024',
    submitted: '28 Jan 2024',
    rank: '#3',
    status: 'Under Review',
    statusColor: 'bg-yellow-100 text-yellow-800'
  },
  { 
    title: 'Safety Equipment Annual Supply',
    id: 'TND-2024-005',
    amount: '₹7,50,000',
    date: '20 Jan 2024',
    submitted: '20 Jan 2024',
    rank: '#1',
    status: 'Won',
    statusColor: 'bg-green-100 text-green-800'
  },
  {
    title: 'Welding Consumables Q4',
    id: 'TND-2023-089',
    amount: '₹4,50,000',
    date: '10 Dec 2023',
    submitted: '10 Dec 2023',
    rank: '#4',
    status: 'Not Selected',
    statusColor: 'bg-red-100 text-red-800'
  },
  {
    title: 'CNC Machining Center',
    id: 'TND-2024-002',
    amount: '₹82,00,000',
    date: '29 Jan 2024',
    submitted: '29 Jan 2024',
    rank: '-',
    status: 'Submitted',
    statusColor: 'bg-gray-100 text-gray-800'
  },
  {
    title: 'Office Furniture Supply',
    id: 'TND-2023-078',
    amount: '₹3,20,000',
    date: '15 Nov 2023',
    submitted: '15 Nov 2023',
    rank: '#1',
    status: 'Won',
    statusColor: 'bg-green-100 text-green-800'
  }
]

const performanceCategories = [
  { name: 'Raw Materials', won: 2, total: 5, percentage: 40, color: 'bg-purple-600' },
  { name: 'Machinery', won: 1, total: 3, percentage: 33, color: 'bg-indigo-600' },
  { name: 'Consumables', won: 2, total: 4, percentage: 50, color: 'bg-blue-600' },
  { name: 'Electrical', won: 1, total: 2, percentage: 50, color: 'bg-violet-600' }
]

const monthlyPerformance = [
  { month: 'Jan', count: 2, growth: '+10%' },
  { month: 'Feb', count: 3, growth: '+15%' },
  { month: 'Mar', count: 4, growth: '+20%' },
  { month: 'Apr', count: 5, growth: '+25%' }
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
          <a href="#" @click.prevent="activeTab = 'Overview'" :class="[activeTab === 'Overview' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']" aria-current="page">Overview</a>
          <a href="#" @click.prevent="activeTab = 'My Bids'" :class="[activeTab === 'My Bids' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']">My Bids</a>
          <a href="#" @click.prevent="activeTab = 'Analytics'" :class="[activeTab === 'Analytics' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700', 'whitespace-nowrap border-b-2 py-4 px-1 text-sm font-medium']">Analytics</a>
        </nav>
      </div>

      <!-- Overview View -->
      <div v-if="activeTab === 'Overview'" class="grid grid-cols-1 gap-8 lg:grid-cols-3">
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
                 <a href="#" @click.prevent="activeTab = 'My Bids'" class="text-sm font-semibold text-indigo-600 hover:text-indigo-500 flex items-center">
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

      <!-- My Bids View -->
      <div v-else-if="activeTab === 'My Bids'" class="bg-white rounded-xl shadow-sm ring-1 ring-gray-900/5 p-6">
         <!-- Bids Table Header -->
         <div class="flex items-center justify-between mb-6">
            <h3 class="font-semibold text-gray-900 flex items-center gap-2">
               <TrendingUp class="h-5 w-5 text-indigo-600" />
               Complete Bid History
            </h3>
            <button class="flex items-center text-sm font-medium text-gray-600 hover:text-gray-900 border border-gray-300 rounded-lg px-3 py-1.5 hover:bg-gray-50">
               <Download class="h-4 w-4 mr-2" /> Export
            </button>
         </div>
         
         <!-- Bids Table -->
         <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
               <thead>
                  <tr>
                     <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-xs font-semibold text-gray-500 sm:pl-0">Tender</th>
                     <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-gray-500">Your Bid</th>
                     <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-gray-500">Submitted</th>
                     <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-gray-500">Rank</th>
                     <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-gray-500">Status</th>
                     <th scope="col" class="px-3 py-3.5 text-left text-xs font-semibold text-gray-500">Action</th>
                  </tr>
               </thead>
               <tbody class="divide-y divide-gray-100">
                  <tr v-for="bid in bidHistory" :key="bid.id" class="hover:bg-gray-50 transition-colors">
                     <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-0">
                        <div>{{ bid.title }}</div>
                        <div class="text-xs text-gray-400 mt-0.5">{{ bid.id }}</div>
                     </td>
                     <td class="whitespace-nowrap px-3 py-4 text-sm font-semibold text-gray-900">{{ bid.amount }}</td>
                     <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ bid.submitted }}</td>
                     <td class="whitespace-nowrap px-3 py-4 text-sm font-medium text-amber-500">{{ bid.rank }}</td>
                     <td class="whitespace-nowrap px-3 py-4 text-sm">
                        <span :class="[bid.statusColor, 'inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset ring-gray-500/10']">
                           {{ bid.status }}
                        </span>
                     </td>
                     <td class="whitespace-nowrap px-3 py-4 text-sm">
                        <button class="text-gray-400 hover:text-indigo-600 flex items-center gap-1 transition-colors">
                           <Eye class="h-4 w-4" /> View
                        </button>
                     </td>
                  </tr>
               </tbody>
            </table>
         </div>
      </div>
      
      <!-- Analytics View -->
      <!-- Analytics View -->
      <div v-else-if="activeTab === 'Analytics'" class="grid grid-cols-1 gap-8 lg:grid-cols-3">
         <!-- Left Column (Analytics) -->
         <div class="lg:col-span-2 space-y-8">
            <!-- Performance by Category -->
            <div class="bg-white rounded-xl shadow-sm ring-1 ring-gray-900/5 p-6">
               <h3 class="font-semibold text-gray-900 mb-6 flex items-center gap-2">
                  <PieChart class="h-5 w-5 text-indigo-600" />
                  Performance by Category
               </h3>
               <div class="space-y-6">
                  <div v-for="category in performanceCategories" :key="category.name">
                     <div class="flex justify-between text-sm mb-1">
                        <span class="font-medium text-gray-900">{{ category.name }}</span>
                        <span class="text-gray-500">{{ category.won }}/{{ category.total }} won ({{ category.percentage }}%)</span>
                     </div>
                     <div class="w-full bg-gray-100 rounded-full h-2">
                        <div class="h-2 rounded-full transition-all duration-500" :class="category.color" :style="{ width: `${category.percentage}%` }"></div>
                     </div>
                  </div>
               </div>
            </div>

            <!-- Monthly Performance -->
            <div class="bg-white rounded-xl shadow-sm ring-1 ring-gray-900/5 p-6">
               <h3 class="font-semibold text-gray-900 mb-6 flex items-center gap-2">
                  <BarChart3 class="h-5 w-5 text-indigo-600" />
                  Monthly Performance
               </h3>
               <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div v-for="month in monthlyPerformance" :key="month.month" class="bg-gray-50 rounded-lg p-4 text-center">
                     <div class="text-sm font-medium text-gray-500 mb-1">{{ month.month }}</div>
                     <div class="text-2xl font-bold text-gray-900 mb-1">{{ month.count }}</div>
                     <div class="text-xs font-semibold text-green-600 flex items-center justify-center gap-0.5">
                        <span>↑</span> {{ month.growth }}
                     </div>
                  </div>
               </div>
            </div>
         </div>

         <!-- Right Column (Reused) -->
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
