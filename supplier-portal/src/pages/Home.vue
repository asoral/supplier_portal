<script setup>
import { ArrowRight, CheckCircle, Clock, Trophy, Users } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const router = useRouter()

const features = [
  {
    name: 'Real-time Notifications',
    description: 'Get instant alerts for new tenders matching your profile.',
    icon: Clock,
  },
  {
    name: 'Transparent Bidding',
    description: 'Participate in live auctions with complete visibility.',
    icon: Users,
  },
  {
    name: 'Award Tracking',
    description: 'Track your order status and payment milestones.',
    icon: Trophy,
  },
]

const steps = [
  { id: 1, name: 'Post Requirement', description: 'Buyers post detailed requirements.' },
  { id: 2, name: 'Receive Bids', description: 'Vendors submit competitive quotes.' },
  { id: 3, name: 'Live Auction', description: 'Real-time negotiation phase.' },
  { id: 4, name: 'Award Order', description: 'Best value vendor gets the contract.' },
]
</script>

<template>
  <div class="bg-white">
    <!-- Hero Section -->
    <div class="relative isolate px-6 pt-14 lg:px-8 hero-gradient overflow-hidden">
      <div class="mx-auto max-w-2xl py-32 sm:py-48 lg:py-56 text-center">
        <h1 class="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
          Streamline Your Procurement with
          <span class="gradient-text">TenderFlow</span>
        </h1>
        <p class="mt-6 text-lg leading-8 text-gray-600">
          The most advanced vendor management and e-procurement platform. 
          Connect with top suppliers, manage bids in real-time, and award contracts efficiently.
        </p>
        <div class="mt-10 flex items-center justify-center gap-x-6">
          <button
            @click="router.push('/register')"
            class="rounded-md bg-indigo-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all hover:scale-105"
          >
            Get Started
          </button>
          <button 
             @click="router.push('/tenders')"
             class="text-sm font-semibold leading-6 text-gray-900 flex items-center gap-1 hover:gap-2 transition-all"
          >
            View Active Tenders <ArrowRight class="h-4 w-4" />
          </button>
        </div>
      </div>
      
      <!-- Decorative background blur -->
      <div class="absolute inset-x-0 top-[calc(100%-13rem)] -z-10 transform-gpu overflow-hidden blur-3xl sm:top-[calc(100%-30rem)]" aria-hidden="true">
        <div class="relative left-[calc(50%+3rem)] aspect-[1155/678] w-[36.125rem] -translate-x-1/2 bg-gradient-to-tr from-[#ff80b5] to-[#9089fc] opacity-30 sm:left-[calc(50%+36rem)]" style="clip-path: polygon(74.1% 44.1%, 100% 61.6%, 97.5% 26.9%, 85.5% 0.1%, 80.7% 2%, 72.5% 32.5%, 60.2% 62.4%, 52.4% 68.1%, 47.5% 58.3%, 45.2% 34.5%, 27.5% 76.7%, 0.1% 64.9%, 17.9% 100%, 27.6% 76.8%, 76.1% 97.7%, 74.1% 44.1%)" />
      </div>
    </div>

    <!-- Features Section -->
    <div class="mx-auto max-w-7xl px-6 lg:px-8 py-24 sm:py-32">
      <div class="mx-auto max-w-2xl lg:text-center">
        <h2 class="text-base font-semibold leading-7 text-indigo-600">Faster Procurement</h2>
        <p class="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
          Everything you need to manage tenders
        </p>
        <p class="mt-6 text-lg leading-8 text-gray-600">
          Our platform simplifies the entire procurement lifecycle from requisition to payment.
        </p>
      </div>
      <div class="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
        <dl class="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-3 lg:gap-y-16">
          <div v-for="feature in features" :key="feature.name" class="relative pl-16">
            <dt class="text-base font-semibold leading-7 text-gray-900">
              <div class="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600">
                <component :is="feature.icon" class="h-6 w-6 text-white" aria-hidden="true" />
              </div>
              {{ feature.name }}
            </dt>
            <dd class="mt-2 text-base leading-7 text-gray-600">{{ feature.description }}</dd>
          </div>
        </dl>
      </div>
    </div>

    <!-- Steps Section -->
    <div class="bg-gray-50 py-24 sm:py-32">
      <div class="mx-auto max-w-7xl px-6 lg:px-8">
        <div class="mx-auto max-w-2xl lg:text-center mb-16">
          <h2 class="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">How TenderFlow Works</h2>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div v-for="(step, index) in steps" :key="step.id" class="relative flex flex-col items-center text-center">
             <div class="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-600 text-white font-bold text-xl mb-4 relative z-10">
               {{ step.id }}
             </div>
             <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ step.name }}</h3>
             <p class="text-sm text-gray-600">{{ step.description }}</p>
             
             <!-- Connector Line -->
             <div v-if="index < steps.length - 1" class="hidden md:block absolute top-6 left-1/2 w-full h-0.5 bg-gray-300 -z-0" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
