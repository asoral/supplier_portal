import { createRouter, createWebHistory, createWebHashHistory } from "vue-router";
import HelloWorld from "../components/HelloWorld.vue";

const routes = [
  {
	path: "/",
	name: "HelloWorld",
	component: HelloWorld,
  },
//   {
// path: "/Home",
// 	name: "Home",
// 	component: Home,
//   },
//   {
//     path: '/signup',
//     name: 'Signup',
//     component: () => import('@/views/Signup.vue')
//   },
  {
    path: '/Home',
    name: 'Home',
    component: () => import('@/components/Home.vue')
  }
//   ,
//   {
//     path: '/CustomerRegistration',
//     name: 'CustomerRegistration',
//     component: () => import('@/components/CustomerRegistration.vue')
//   },
//   {
//     path: '/EmployeeRegistration',
//     name: 'EmployeeRegistration',
//     component: () => import('@/components/EmployeeRegistration.vue')
//   },
//   {
//     path: '/Catalog',
//     name: 'Catalog',
//     component: () => import('@/components/Catalog.vue')
//   },
//   {
//     path: '/Dashboard',
//     name: 'Dashboard',
//     component: () => import('@/components/Dashboard.vue')
//   },
//   {
//     path: '/Orders',
//     name: 'Orders',
//     component: () => import('@/components/Orders.vue')
//   },
//   {
//     path: '/Quotations',
//     name: 'Quotations',
//     component: () => import('@/components/Quotations.vue')
//   },
//   {
//     path: '/Invoices',
//     name: 'Invoices',
//     component: () => import('@/components/Invoices.vue')
//   },
//   {
//     path: '/Returns',
//     name: 'Returns',
//     component: () => import('@/components/Returns.vue')
//   },
//   {
//     path: '/MyAccount',
//     name: 'MyAccount',
//     component: () => import('@/components/MyAccount.vue')
//   },
//   {
//     path: '/Analytics',
//     name: 'Analytics',
//     component: () => import('@/components/Analytics.vue')
//   },
//   {
//     path: '/Support',
//     name: 'Support',
//     component: () => import('@/components/Support.vue')
//   },
// ,  
//   ...authRoutes,
];

const router = createRouter({
	history: createWebHistory("/supplier-portal"),
	routes,
})

export default router;
