<script setup>
import { BarChart3, CheckCircle2, Clock, DollarSign, FileText } from 'lucide-vue-next'

const stats = [
  { name: 'Total Orders Won', value: '12', icon: CheckCircle2, change: '+2', changeType: 'increase' },
  { name: 'Active Bids', value: '5', icon: Clock, change: '-1', changeType: 'decrease' },
  { name: 'Total Bid Value', value: '₹2.4M', icon: DollarSign, change: '+12%', changeType: 'increase' },
  { name: 'Profile Strength', value: '85%', icon: FileText, change: 'Good', changeType: 'neutral' },
]

const recentActivity = [
  { id: 1, type: 'Bid Submitted', tender: 'Supply of Steel Plates', time: '2 hours ago', status: 'Pending' },
  { id: 2, type: 'Tender Won', tender: 'Office Stationery Supply', time: '1 day ago', status: 'Success' },
  { id: 3, type: 'New Document Req', tender: 'Safety Equipment', time: '2 days ago', status: 'Action Required' },
]
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-3xl font-bold tracking-tight text-gray-900 mb-8">Vendor Dashboard</h1>
    
    <!-- Stats Grid -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
      <div v-for="item in stats" :key="item.name" class="relative overflow-hidden rounded-lg bg-white px-4 pt-5 pb-12 shadow sm:px-6 sm:pt-6">
        <dt>
          <div class="absolute rounded-md bg-indigo-500 p-3">
            <component :is="item.icon" class="h-6 w-6 text-white" aria-hidden="true" />
          </div>
          <p class="ml-16 truncate text-sm font-medium text-gray-500">{{ item.name }}</p>
        </dt>
        <dd class="ml-16 flex items-baseline pb-1 sm:pb-7">
          <p class="text-2xl font-semibold text-gray-900">{{ item.value }}</p>
          <p v-if="item.changeType !== 'neutral'" :class="[item.changeType === 'increase' ? 'text-green-600' : 'text-red-600', 'ml-2 flex items-baseline text-sm font-semibold']">
            {{ item.change }}
          </p>
        </dd>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Activity Feed -->
      <div class="bg-white rounded-lg shadow sm:rounded-lg">
        <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 class="text-base font-semibold leading-6 text-gray-900">Recent Activity</h3>
        </div>
        <ul role="list" class="divide-y divide-gray-200">
          <li v-for="activity in recentActivity" :key="activity.id" class="px-4 py-4 sm:px-6">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-3">
                 <div class="h-2 w-2 rounded-full" :class="{
                   'bg-yellow-400': activity.status === 'Pending',
                   'bg-green-400': activity.status === 'Success',
                   'bg-red-400': activity.status === 'Action Required'
                 }"></div>
                 <div>
                    <p class="text-sm font-medium text-indigo-600 truncate">{{ activity.tender }}</p>
                    <p class="text-sm text-gray-500">{{ activity.type }}</p>
                 </div>
              </div>
              <div class="ml-2 flex-shrink-0 flex flex-col items-end">
                <p class="text-xs text-gray-500">{{ activity.time }}</p>
                <p class="text-xs font-medium px-2 py-0.5 rounded mt-1" :class="{
                   'bg-yellow-100 text-yellow-800': activity.status === 'Pending',
                   'bg-green-100 text-green-800': activity.status === 'Success',
                   'bg-red-100 text-red-800': activity.status === 'Action Required'
                }">{{ activity.status }}</p>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- Quick Actions / Profile Strength -->
      <div class="bg-white rounded-lg shadow sm:rounded-lg p-6">
         <h3 class="text-base font-semibold leading-6 text-gray-900 mb-4">Complete Your Profile</h3>
         <div class="mb-4">
            <div class="flex justify-between text-sm font-medium text-gray-900 mb-1">
               <span>Profile Strength</span>
               <span>85%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5">
               <div class="bg-indigo-600 h-2.5 rounded-full" style="width: 85%"></div>
            </div>
         </div>
         <div class="bg-blue-50 border-l-4 border-blue-400 p-4 mb-4">
            <div class="flex">
               <div class="flex-shrink-0">
                  <FileText class="h-5 w-5 text-blue-400" />
               </div>
               <div class="ml-3">
                  <p class="text-sm text-blue-700">
                     Upload your <strong>GST Certificate</strong> to participate in government tenders.
                  </p>
               </div>
            </div>
         </div>
         <button class="w-full rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500">Update Documents</button>
      </div>
    </div>
  </div>
</template>
