<script setup>
import { ref, onMounted } from 'vue'
import { 
  ArrowRight, 
  CheckCircle, 
  Clock, 
  Trophy, 
  Users, 
  Zap, 
  ShieldCheck, 
  BarChart3, 
  Globe, 
  Target, 
  FileText,
  Hammer,
  Package,
  HardHat,
  Briefcase,
  PlayCircle,
  TrendingUp,
  Award
} from 'lucide-vue-next'

import { useRouter } from 'vue-router'
const activeTenders = ref([])
const isLoading = ref(true)
const fetchTenders = async () => {
  try {
    isLoading.value = true
    const response = await fetch('/api/method/supplier_portal.api.get_active_tenders?limit=6')
    const data = await response.json()
    activeTenders.value = data.message || []
  } catch (error) {
    console.error("Error fetching tenders:", error)
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchTenders()
})

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(value)
}

const router = useRouter()

const stats = [
  { name: 'Active Tenders', value: '24', change: '+12%', icon: FileText },
  { name: 'Registered Vendors', value: '150+', change: '+5%', icon: Users },
  { name: 'Orders Awarded', value: '12Cr+', change: '+20%', icon: Trophy },
  { name: 'Avg. Savings', value: '18%', change: '+3%', icon: TrendingUp },
]

const steps = [
  { id: 1, name: 'Post Requirement', description: 'Define your material needs with specs', icon: FileText },
  { id: 2, name: 'Receive Bids', description: 'Vendors submit competitive offers', icon: Users },
  { id: 3, name: 'Live Auction', description: 'Real-time bidding for best prices', icon: Zap },
  { id: 4, name: 'Award Order', description: 'Select winner and place order', icon: Award },
]

const categories = [
  { name: 'Raw Materials', count: 12, icon: Package },
  { name: 'Machinery', count: 5, icon: Hammer },
  { name: 'Consumables', count: 8, icon: Package }, // Using Package as fallback or specific icon
  { name: 'Electrical', count: 6, icon: Zap },
  { name: 'Safety', count: 4, icon: HardHat },
  { name: 'Services', count: 7, icon: Briefcase },
]

const features = [
  {
    name: 'Live Bidding',
    description: 'Real-time competition bidding with instant lowest bid visibility for maximum transparency.',
    icon: Zap,
    color: 'bg-orange-50 text-orange-600'
  },
  {
    name: 'Verified Vendors',
    description: 'All vendors are verified with complete documentation and compliance checks.',
    icon: ShieldCheck,
    color: 'bg-green-50 text-green-600'
  },
  {
    name: 'Streamlined Process',
    description: 'From requirement posting to order placement, everything in one unified platform.',
    icon: Clock,
    color: 'bg-blue-50 text-blue-600'
  },
  {
    name: 'Analytics & Insights',
    description: 'Track your participation, win rates, and optimize your bidding strategy.',
    icon: BarChart3,
    color: 'bg-purple-50 text-purple-600'
  },
  {
    name: 'Pan-India Network',
    description: 'Access vendors across all states with verified credentials and track records.',
    icon: Globe,
    color: 'bg-cyan-50 text-cyan-600'
  },
  {
    name: 'Smart Matching',
    description: 'AI-powered vendor recommendations based on your requirements and history.',
    icon: Target,
    color: 'bg-red-50 text-red-600'
  },
]

const testimonials = [
  {
    content: "TenderFlow has transformed how we manage our procurement. The live bidding feature ensures we always get the best prices.",
    author: "Rajesh Kumar",
    role: "Procurement Head, ABC Manufacturing"
  },
  {
    content: "As a vendor, the transparency and ease of bidding has helped us win more contracts. Highly recommended!",
    author: "Priya Sharma",
    role: "Director, XYZ Suppliers"
  },
  {
    content: "The analytics dashboard gives us insights we never had before. Our procurement efficiency has improved by 40%.",
    author: "Amit Patel",
    role: "CFO, Industrial Corp"
  }
]
</script>

<template>
  <div class="bg-gray-50">
    <!-- Hero Section -->
    <div class="relative bg-white pt-16 pb-20 lg:pt-24 lg:pb-28 overflow-hidden">
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center z-10">
        
        <!-- Top Badges -->
        <div class="flex justify-center gap-4 mb-8">
           <span class="inline-flex items-center rounded-full bg-gray-50 px-3 py-1 text-xs font-medium text-gray-600 ring-1 ring-inset ring-gray-500/10">
              <ShieldCheck class="w-3 h-3 mr-1" /> Trusted by 500+ Vendors
           </span>
            <span class="inline-flex items-center rounded-full bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700 ring-1 ring-inset ring-indigo-700/10">
              <Zap class="w-3 h-3 mr-1" /> New with AI Matching
           </span>
        </div>

        <h1 class="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl mb-6">
          <span class="block">Procurement Made</span>
          <span class="block text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Transparent</span>
          <span class="block">& Effortlessly Efficient</span>
        </h1>
        <p class="mt-4 max-w-2xl mx-auto text-xl text-gray-500">
          Your comprehensive tender management portal. Publish requirements, receive competitive bids in real-time, and build lasting vendor relationships — all in one place.
        </p>
        <div class="mt-8 flex justify-center gap-4">
          <button @click="router.push('/tenders')" class="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 md:text-lg transition-all hover:scale-105 shadow-lg shadow-indigo-200">
            Explore Active Tenders
          </button>
        </div>

        <!-- Trust Indicators -->
        <div class="mt-8 flex justify-center gap-6 text-sm text-gray-400">
           <span class="flex items-center"><CheckCircle class="w-4 h-4 mr-1.5 text-green-500" /> Free to Register</span>
           <span class="flex items-center"><CheckCircle class="w-4 h-4 mr-1.5 text-green-500" /> No Hidden Fees</span>
           <span class="flex items-center"><CheckCircle class="w-4 h-4 mr-1.5 text-green-500" /> 24/7 Support</span>
        </div>
      </div>
      
      <!-- Background Gradient Decoration -->
       <div class="absolute top-0 left-1/2 w-full -translate-x-1/2 h-full z-0 overflow-hidden pointer-events-none">
          <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-50 blur-3xl opacity-50"></div>
          <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-purple-50 blur-3xl opacity-50"></div>
       </div>
    </div>

    <!-- Stats Section -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-16 relative z-20">
       <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div v-for="stat in stats" :key="stat.name" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 flex flex-col items-start hover:shadow-md transition-shadow">
             <div class="flex justify-between w-full mb-4">
                <span class="text-sm font-medium text-gray-500">{{ stat.name }}</span>
                <div class="p-2 bg-gray-50 rounded-lg">
                   <component :is="stat.icon" class="w-5 h-5 text-gray-400" />
                </div>
             </div>
             <div class="flex items-end gap-3 w-full">
                <span class="text-3xl font-bold text-gray-900">{{ stat.value }}</span>
                <span class="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full mb-1">{{ stat.change }}</span>
             </div>
          </div>
       </div>
    </div>

    <!-- How It Works -->
    <div class="py-24 bg-white mt-16">
       <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span class="inline-block py-1 px-3 rounded-full bg-gray-100 text-gray-600 text-xs font-semibold uppercase tracking-wide mb-4">Simple Process</span>
          <h2 class="text-3xl font-extrabold text-gray-900 mb-16">How TenderFlow Works</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-4 gap-12 relative">
             <div v-for="(step, index) in steps" :key="step.name" class="relative flex flex-col items-center">
                <!-- Connector Line -->
                <div v-if="index < steps.length - 1" class="hidden md:block absolute top-8 left-[60%] w-[80%] h-[2px] bg-gradient-to-r from-indigo-200 to-gray-100 z-0"></div>
                
                <div class="transform transition-transform hover:scale-110 duration-300 relative z-10 bg-white">
                   <div class="w-16 h-16 rounded-2xl bg-indigo-600 text-white flex items-center justify-center shadow-lg shadow-indigo-200 mb-6 relative">
                      <component :is="step.icon" class="w-8 h-8" />
                      <div class="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-white border-2 border-indigo-600 text-indigo-600 flex items-center justify-center text-xs font-bold">
                         {{ step.id }}
                      </div>
                   </div>
                </div>
                <h3 class="text-lg font-bold text-gray-900 mb-2">{{ step.name }}</h3>
                <p class="text-sm text-gray-500 max-w-[200px]">{{ step.description }}</p>
             </div>
          </div>
       </div>
    </div>

    <!-- Categories -->
    <div class="py-24 bg-gray-50/50">
       <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex justify-between items-end mb-12">
             <div>
                <span class="inline-block py-1 px-3 rounded-full bg-gray-100 text-gray-600 text-xs font-semibold uppercase tracking-wide mb-2">Categories</span>
                <h2 class="text-3xl font-extrabold text-gray-900">Browse by Category</h2>
             </div>
             <a href="#" class="hidden md:flex items-center text-indigo-600 font-semibold hover:text-indigo-500">
                View All Categories <ArrowRight class="w-4 h-4 ml-2" />
             </a>
          </div>

          <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
             <div v-for="category in categories" :key="category.name" @click="router.push({ path: '/tenders', query: { category: category.name } })" class="bg-white rounded-xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-all cursor-pointer group text-center">
                <div class="w-12 h-12 mx-auto bg-gray-50 rounded-full flex items-center justify-center mb-4 group-hover:bg-indigo-50 group-hover:scale-110 transition-all">
                   <component :is="category.icon" class="w-6 h-6 text-gray-400 group-hover:text-indigo-600" />
                </div>
                <h3 class="font-semibold text-gray-900 mb-1">{{ category.name }}</h3>
                <p class="text-xs text-gray-500">{{ category.count }} active tenders</p>
             </div>
          </div>
       </div>
    </div>

   <div class="py-24 bg-white border-y border-gray-100">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex justify-between items-end mb-12">
      <div>
        <div class="flex items-center gap-2 mb-2">
          <div class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-red-50 text-[10px] font-bold text-red-500 uppercase tracking-wider border border-red-100">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-red-500"></span>
            </span>
            Live Now
          </div>
        </div>
        <h2 class="text-4xl font-extrabold text-gray-900">Active Tenders</h2>
        <p class="mt-2 text-gray-500">Browse current opportunities and submit your competitive bids</p>
      </div>
      <button @click="router.push('/tenders')" class="hidden md:flex items-center text-indigo-600 font-semibold hover:text-indigo-500 transition-colors">
        View All <ArrowRight class="w-4 h-4 ml-2" />
      </button>
    </div>

    <div v-if="isLoading" class="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div v-for="i in 3" :key="i" class="h-64 bg-gray-50 animate-pulse rounded-2xl border border-gray-100"></div>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div v-for="tender in activeTenders" :key="tender.name" 
           class="group bg-white rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-xl hover:border-indigo-100 transition-all duration-300 flex flex-col">
        
        <div class="flex justify-between items-start mb-6">
          <div class="flex flex-wrap gap-2">
             <span class="px-2 py-1 bg-gray-100 text-gray-600 text-[10px] font-bold rounded uppercase">
                {{ tender.custom_rfq_category || 'General' }}
             </span>
             <span class="px-2 py-1 bg-blue-50 text-blue-600 text-[10px] font-bold rounded uppercase">
                {{ tender.status }}
             </span>
          </div>
          <div v-if="tender.custom_enable_live_bidding" class="flex items-center gap-1 text-red-500 text-[10px] font-bold uppercase">
             <Zap class="w-3 h-3 fill-current" /> Live Bidding
          </div>
        </div>

        <h3 class="text-xl font-bold text-gray-900 mb-2 truncate group-hover:text-indigo-600 transition-colors">
          {{ tender.custom_rfq_subject }}
        </h3>
        
        <div class="space-y-4 mb-8 mt-4">
          <div class="flex flex-col">
             <span class="text-xs text-gray-400 uppercase font-medium">Total Budget</span>
             <span class="font-extrabold text-gray-900 text-xl">₹{{ tender.custom_total_budget_?.toLocaleString('en-IN') }}</span>
          </div>
          
          <div class="flex justify-between items-center py-3 border-t border-gray-50">
             <div class="flex items-center gap-2 text-sm text-gray-500">
                <Clock class="w-4 h-4 text-gray-400" />
                <span>Deadline:</span>
             </div>
             <span class="text-sm font-bold text-gray-900">{{ tender.custom_bid_submission_last_date }}</span>
          </div>
        </div>

        <button @click="router.push(`/tenders/${tender.name}`)" 
                class="mt-auto w-full py-3 bg-indigo-600 text-white rounded-xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-100 active:scale-95">
          View & Bid
        </button>
      </div>
    </div>

    <div v-if="!isLoading && activeTenders.length === 0" class="text-center py-12">
       <p class="text-gray-400 italic">No active tenders available at the moment.</p>
    </div>
  </div>
</div>

    <!-- Features -->
    <div class="py-24 bg-white">
       <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="text-center mb-16">
             <span class="inline-block py-1 px-3 rounded-full bg-gray-100 text-gray-600 text-xs font-semibold uppercase tracking-wide mb-4">Platform Features</span>
             <h2 class="text-3xl font-extrabold text-gray-900">Why Choose TenderFlow?</h2>
             <p class="mt-4 max-w-2xl mx-auto text-gray-500">A modern procurement platform designed for efficiency and transparency.</p>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
             <div v-for="feature in features" :key="feature.name" class="p-8 rounded-2xl border border-gray-100 bg-white hover:border-gray-200 transition-colors">
                <div :class="['w-12 h-12 rounded-lg flex items-center justify-center mb-6', feature.color]">
                   <component :is="feature.icon" class="w-6 h-6" />
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-3">{{ feature.name }}</h3>
                <p class="text-gray-500 leading-relaxed">{{ feature.description }}</p>
             </div>
          </div>
       </div>
    </div>
    
    <!-- Testimonials -->
     <div class="py-24 bg-gray-50/50">
       <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <span class="inline-block py-1 px-3 rounded-full bg-gray-100 text-gray-600 text-xs font-semibold uppercase tracking-wide mb-4">Testimonials</span>
          <h2 class="text-3xl font-extrabold text-gray-900 mb-16">Trusted by Industry Leaders</h2>
          
          <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
             <div v-for="(testimonial, idx) in testimonials" :key="idx" class="bg-white p-8 rounded-2xl shadow-sm border border-gray-100">
                <div class="flex gap-1 text-amber-400 mb-4">
                   <span v-for="i in 5" :key="i">★</span>
                </div>
                <p class="text-gray-600 italic mb-6">"{{ testimonial.content }}"</p>
                <div>
                   <h4 class="font-bold text-gray-900">{{ testimonial.author }}</h4>
                   <p class="text-xs text-gray-500">{{ testimonial.role }}</p>
                </div>
             </div>
          </div>
       </div>
    </div>


    <!-- CTA Section -->
    <div class="relative py-16">
       <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-3xl p-12 text-center text-white shadow-2xl relative overflow-hidden">
             <!-- Decorative circles -->
             <div class="absolute top-0 right-0 -mt-10 -mr-10 w-40 h-40 bg-white opacity-10 rounded-full blur-2xl"></div>
             <div class="absolute bottom-0 left-0 -mb-10 -ml-10 w-40 h-40 bg-white opacity-10 rounded-full blur-2xl"></div>

             <span class="inline-block py-1 px-3 rounded-full bg-white/20 border border-white/30 text-white text-xs font-semibold uppercase tracking-wide mb-6">Get Started Today</span>
             <h2 class="text-3xl md:text-4xl font-bold mb-4">Ready to Start Bidding?</h2>
             <p class="text-indigo-100 mb-8 max-w-xl mx-auto text-lg">Join our vendor network today and access exclusive procurement opportunities from verified buyers across India.</p>
             
             <div class="flex flex-col sm:flex-row justify-center gap-4">
                <button @click="router.push('/register')" class="px-8 py-3 bg-white text-indigo-600 font-bold rounded-md hover:bg-gray-50 transition-colors">
                   Register Now — It's Free
                </button>
                <button class="px-8 py-3 bg-indigo-500/30 border border-white/30 text-white font-semibold rounded-md hover:bg-indigo-500/40 transition-colors backdrop-blur-sm">
                   Contact Sales
                </button>
             </div>
          </div>
       </div>
    </div>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 pt-16 pb-8">
       <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-8 mb-12">
             <div class="col-span-2">
                <div class="flex items-center gap-2 mb-4">
                   <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white font-bold">T</div>
                   <span class="text-xl font-bold text-gray-900">TenderFlow</span>
                </div>
                <p class="text-sm text-gray-500 max-w-xs leading-relaxed">
                   Streamline your procurement process with our comprehensive tender management and vendor collaboration platform. Fair, transparent, and efficient.
                </p>
             </div>
             
             <div>
                <h4 class="font-bold text-gray-900 mb-4 text-sm">Quick Links</h4>
                <ul class="space-y-3 text-sm text-gray-500">
                   <li><a href="#" class="hover:text-indigo-600">Active Tenders</a></li>
                   <li><a href="#" class="hover:text-indigo-600">Vendor Registration</a></li>
                   <li><a href="#" class="hover:text-indigo-600">Vendor Dashboard</a></li>
                </ul>
             </div>

             <div>
                <h4 class="font-bold text-gray-900 mb-4 text-sm">Support</h4>
                <ul class="space-y-3 text-sm text-gray-500">
                   <li><a href="#" class="hover:text-indigo-600">Help Center</a></li>
                   <li><a href="#" class="hover:text-indigo-600">Terms & Conditions</a></li>
                   <li><a href="#" class="hover:text-indigo-600">Privacy Policy</a></li>
                </ul>
             </div>
          </div>
          
          <div class="border-t border-gray-100 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
             <p class="text-xs text-gray-400">© 2024 TenderFlow. All rights reserved.</p>
          </div>
       </div>
    </footer>


  </div>
</template>

<style>
/* Additional custom styles if needed for specific glowing effects */
</style>
