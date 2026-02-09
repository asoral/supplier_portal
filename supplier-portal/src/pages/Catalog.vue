<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { 
  Package, Plus, Search, Filter, Edit2, Trash2, 
  TrendingUp, Clock, CheckCircle, AlertCircle, X 
} from 'lucide-vue-next'

// --- State ---
const activeTab = ref('My Catalog')
const tabs = ['My Catalog', 'Portal Items']
const searchQuery = ref('')
const loading = ref(true)
const products = ref([]) 
const currentSupplier = ref('')

// --- Modal State (ONLY ONE DECLARATION HERE) ---
const isAddProductModalOpen = ref(false)
const isEditing = ref(false)
const newProduct = ref({ 
   id: '',
  name: '', 
  sku: '', 
  category: '', 
  unit: '', 
  price: 0, 
  tax: '', 
  moq: '', 
  leadTime: '', 
  description: '' 
})

const openEditModal = (item) => { // Using 'item' here
  isEditing.value = true;
  
  newProduct.value = {
    id: item.id, 
    name: item.name,
    sku: item.sku,
    category: item.category,
    unit: item.unit || 'Nos',
    price: item.price,
    tax: item.tax,
    moq: item.min_order_qty || 1,
    // This was the line causing the error; it now correctly references 'item'
    leadTime: item.lead_time_days || 'N/A', 
    description: item.description
  };
  
  isAddProductModalOpen.value = true;
};

// --- Fetch Data ---
const authStore = useAuthStore()
const { secureFetch } = authStore

// --- Fetch Data ---
const fetchProducts = async () => {
  loading.value = true;
  try {
    const response = await secureFetch('/api/method/supplier_portal.api.get_catalog_items');
    if (!response.ok) throw new Error('Network response was not ok');
    const data = await response.json();

    if (data && data.message) {
      products.value = data.message.items || [];
      currentSupplier.value = data.message.current_supplier || '';
    }
  } catch (error) {
    console.error("Failed to load products:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchProducts();
});

// --- Computed Filtering ---
const filteredProducts = computed(() => {
  if (!products.value) return [];
  return products.value.filter(item => {
    const matchesSearch = !searchQuery.value || 
      item.name?.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      item.sku?.toLowerCase().includes(searchQuery.value.toLowerCase());

    if (!matchesSearch) return false;

    if (activeTab.value === 'My Catalog') {
      return item.is_my_item === true;
    } else {
      return item.is_purchase_item == 1 && item.is_my_item === false;
    }
  });
});

const openAddModal = () => {
  if (!authStore.user) {
      alert("Please login to manage products.");
      return;
  }
  isEditing.value = false;
  // Resetting all fields, especially id, to ensure a fresh entry
  newProduct.value = { 
    id: '', 
    name: '', 
    sku: '', 
    category: '', 
    unit: '', 
    price: 0, 
    tax: '', 
    moq: '', 
    leadTime: '', 
    description: '' 
  };
  isAddProductModalOpen.value = true;
};

const closeAddModal = () => {
  isAddProductModalOpen.value = false;
};

const submitProduct = async () => {
  if (!newProduct.value.name || !newProduct.value.price) {
    alert("Please enter both product name and price");
    return;
  }

  try {
    loading.value = true;
    
    // We only use the catalog update path now
    const method = '/api/method/supplier_portal.api.update_catalog_item';

    const payload = {
      item_id: newProduct.value.id, 
      name: newProduct.value.name,
      price: newProduct.value.price,
      moq: newProduct.value.moq,
      leadTime: newProduct.value.leadTime,
      description: newProduct.value.description,
      tax: newProduct.value.tax 
    };

    const response = await secureFetch(method, {
      method: 'POST',
      body: JSON.stringify(payload) 
    });

    const result = await response.json();
    
    // Result handling based on Frappe return
    if (result.message === "success") {
      closeAddModal();
      await fetchProducts(); // Refresh the list
      alert("Product updated successfully!");
    } else {
      alert("Error: " + (result.message?.message || "Failed to update product"));
    }
  } catch (error) {
    console.error("Update failed:", error);
    alert("An error occurred during submission.");
  } finally {
    loading.value = false;
  }
};

const addToMyCatalog = async (product) => {
  if (!authStore.user) {
      alert("Please login to add items to your catalog.");
      return;
  }
  try {
    const response = await secureFetch('/api/method/supplier_portal.api.add_to_catalog', {
      method: 'POST',
      body: JSON.stringify({ item_id: product.id })
    });
    const data = await response.json();
    if (data.message === "success") {
      product.is_my_item = true; // Moves item to 'My Catalog' instantly
      alert(`${product.name} added to your catalog!`);
    } else {
       alert("Failed: " + (data.message || "Unknown error"));
    }
  } catch (error) {
    console.error("Failed to add item:", error);
  }
};

const deleteProduct = async (productId) => {
  if (!confirm("Are you sure you want to remove this item?")) return;

  try {
    const response = await secureFetch('/api/method/supplier_portal.api.remove_from_catalog', {
      method: 'POST',
      body: JSON.stringify({ item_id: productId }) // This matches the Python argument
    });
    
    const data = await response.json();
    if (data.message === "success") {
      await fetchProducts(); // Refresh the list
    }
  } catch (err) {
    console.error("Delete request failed:", err);
  }
};

// --- Stats ---
const stats = computed(() => [
  { 
    name: 'Total Products', 
    value: products.value.filter(p => p.is_my_item).length, 
    icon: Package, color: 'text-indigo-600', bg: 'bg-indigo-50' 
  },
  { 
    name: 'Active Items', 
    value: products.value.filter(p => p.is_my_item && p.status === 'active').length, 
    icon: CheckCircle, color: 'text-green-600', bg: 'bg-green-50' 
  },
  { 
    name: 'Pending Approval', 
    value: products.value.filter(p => p.is_my_item && p.status === 'pending').length, 
    icon: Clock, color: 'text-orange-600', bg: 'bg-orange-50' 
  },
  { 
    name: 'Matched Tenders', 
    value: products.value.reduce((acc, p) => p.is_my_item ? acc + (p.matches || 0) : acc, 0), 
    icon: TrendingUp, color: 'text-blue-600', bg: 'bg-blue-50' 
  },
]);
</script>

<template>
  <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-gray-900">Product Catalog</h1>
        <p class="mt-1 text-sm text-gray-500">Manage your product catalog and pricing.</p>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-4 mb-8">
       <div v-for="stat in stats" :key="stat.name" class="rounded-lg bg-white px-4 py-5 shadow sm:p-6 border border-gray-100 flex items-center gap-4">
          <div :class="[stat.bg, 'rounded-md p-3']">
             <component :is="stat.icon" :class="[stat.color, 'h-6 w-6']" />
          </div>
          <div>
             <dt class="truncate text-sm font-medium text-gray-500">{{ stat.name }}</dt>
             <dd class="mt-1 text-2xl font-semibold tracking-tight text-gray-900">{{ stat.value }}</dd>
          </div>
       </div>
    </div>

    <div class="mb-6">
       <div class="flex space-x-2">
          <button
             v-for="tab in tabs"
             :key="tab"
             @click="activeTab = tab"
             :class="[
                activeTab === tab 
                   ? 'bg-indigo-50 text-indigo-700 ring-1 ring-inset ring-indigo-700/10 font-semibold' 
                   : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50',
                'rounded-md px-4 py-2 text-sm font-medium transition-colors'
             ]"
          >
             {{ tab }}
          </button>
       </div>
    </div>

    <div class="flex flex-col sm:flex-row gap-4 mb-6">
       <div class="relative flex-grow">
          <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
             <Search class="h-4 w-4 text-gray-400" />
          </div>
          <input 
            v-model="searchQuery"
            type="text" 
            class="block w-full rounded-md border-0 py-2 pl-10 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6 shadow-sm"
            placeholder="Search products..." 
          />
       </div>
       <button class="inline-flex items-center justify-center gap-2 rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50">
          <Filter class="h-4 w-4 text-gray-500" />
          Filters
       </button>
    </div>

    <div v-if="loading" class="flex flex-col items-center justify-center py-20 bg-white rounded-xl border border-gray-200">
       <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-600 mb-4"></div>
       <p class="text-gray-500">Fetching products...</p>
    </div>

    <div v-else class="space-y-4">
       <div v-if="filteredProducts.length === 0" class="text-center py-20 bg-white rounded-xl border-2 border-dashed border-gray-200">
          <Package class="mx-auto h-12 w-12 text-gray-300 mb-4" />
          <h3 class="text-sm font-semibold text-gray-900">No products found</h3>
          <p class="mt-1 text-sm text-gray-500">Try adjusting your search or filters.</p>
       </div>

      <div v-for="product in filteredProducts" :key="product.id">
          <div v-if="activeTab === 'My Catalog'" class="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
             <div class="flex flex-col lg:flex-row gap-6">
                <div class="flex-shrink-0">
                   <div class="h-16 w-16 rounded-lg bg-gray-50 flex items-center justify-center border border-gray-100">
                      <Package class="h-8 w-8 text-gray-400" />
                   </div>
                </div>

                <div class="flex-grow">
                   <div class="flex flex-wrap items-center gap-2 mb-1">
                      <h3 class="text-lg font-bold text-gray-900">{{ product.name }}</h3>
                      <span class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset bg-green-50 text-green-700 ring-green-600/20">
                         {{ product.status }}
                      </span>
                      <span v-if="product.matches" class="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700 ring-1 ring-inset ring-blue-700/10">
                         <TrendingUp class="h-3 w-3" /> {{ product.matches }} matches
                      </span>
                   </div>
                   <div class="text-sm text-gray-500 mb-2">
                       <span class="font-bold text-gray-700">SKU:</span> {{ product.sku || 'N/A' }}
                       <span class="mx-2 text-gray-300">•</span>
                       <span class="font-bold text-gray-700">Category:</span> {{ product.category }}
                       <span class="mx-2 text-gray-300">•</span>
                       <span class="font-bold text-gray-700">Unit:</span> {{ product.unit || 'Nos' }}
                   </div>
                   <p class="text-sm text-gray-600 leading-relaxed">{{ product.description }}</p>
                </div>

                <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 min-w-[320px] border-t lg:border-t-0 lg:border-l border-gray-100 pt-4 lg:pt-0 lg:pl-8">
    
    <div class="text-right flex-shrink-0">
        <div class="text-xl font-bold text-gray-900">₹{{ Number(product.price).toLocaleString() }}</div>
        <div class="text-[14px] text-gray-400 font-medium">+ {{ product.tax }}</div>
    </div>

    <div class="text-right text-[14px] text-gray-500 leading-tight min-w-[80px]">
        <div class="flex justify-end gap-1">
            <span class="text-gray-400">Lead:</span> 
            <span class="font-medium text-gray-700">{{ product.leadTime }}</span>
        </div>
        <div class="flex justify-end gap-1">
            <span class="text-gray-400">MOQ:</span> 
            <span class="font-medium text-gray-700">{{ product.moq }}</span>
        </div>
    </div>

   <div class="flex lg:flex-row gap-1 items-center">
    <button @click="openEditModal(product)" 
            class="p-2 text-blue-600 hover:bg-blue-50 rounded-md transition-colors">
        <Edit2 class="h-4 w-4" />
    </button>
    
    <button @click="deleteProduct(product.id)" 
            class="p-2 text-red-500 hover:bg-red-50 rounded-md transition-colors">
        <Trash2 class="h-4 w-4" />
    </button>
</div>
</div>

             </div>
          </div>

          <div v-else class="rounded-lg border border-gray-200 bg-white p-4 shadow-sm flex items-center gap-4 hover:border-indigo-200 transition-colors">
             <div class="h-12 w-12 rounded bg-gray-50 flex items-center justify-center flex-shrink-0">
                <Package class="h-6 w-6 text-gray-400" />
             </div>
             <div class="flex-grow">
                <h3 class="text-sm font-bold text-gray-900">{{ product.name }}</h3>
                <p class="text-xs text-gray-500">Category: {{ product.category }} • Unit: {{ product.unit }}</p>
             </div>
            <button @click="addToMyCatalog(product)" class="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md text-sm font-semibold text-gray-700 hover:bg-gray-50 transition whitespace-nowrap">
               <Plus class="h-4 w-4" /> Add to My Catalog
            </button>
          </div>
       </div>

    </div>

    <div v-if="isAddProductModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="w-full max-w-2xl rounded-xl bg-white shadow-2xl overflow-hidden">
        <div class="flex items-center justify-between border-b border-gray-100 px-6 py-4">
          <h3 class="text-lg font-bold text-gray-900">{{ isEditing ? 'Edit Product' : 'Add New Product' }}</h3>
          <button @click="closeAddModal" class="text-gray-400 hover:text-gray-500">
            <X class="h-5 w-5" />
          </button>
        </div>
        <div class="p-6 max-h-[80vh] overflow-y-auto">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="col-span-1">
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">Product Name</label>
              <input v-model="newProduct.name" type="text" placeholder="Enter product name" class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
            </div>
            <div class="col-span-1">
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">SKU</label>
              <input v-model="newProduct.sku" type="text" placeholder="Enter SKU" class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
            </div>
            <div class="col-span-1">
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">Category</label>
              <input v-model="newProduct.category" type="text" placeholder="e.g. Hardware" class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
            </div>
            <div class="col-span-1">
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">Unit of Measure</label>
              <input v-model="newProduct.unit" type="text" placeholder="e.g. Nos" class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
            </div>
            <div class="col-span-1">
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">Base Price (₹)</label>
              <input v-model="newProduct.price" type="number" class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
            </div>
            <div class="col-span-1">
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">GST Rate (%)</label>
              <select v-model="newProduct.tax" class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                <option value="18%">18%</option>
                <option value="12%">12%</option>
                <option value="5%">5%</option>
              </select>
            </div>
            <div class="col-span-1">
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">MOQ</label>
              <input v-model="newProduct.moq" type="number" class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
            </div>
            <div class="col-span-1">
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">Lead Time (Days)</label>
              <input v-model="newProduct.leadTime" type="text" placeholder="Delivery lead time" class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
            </div>
            <div class="col-span-2">
              <label class="block text-xs font-bold uppercase tracking-wider text-gray-500 mb-1">Specifications</label>
              <textarea v-model="newProduct.description" rows="3" placeholder="Enter product specifications..." class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"></textarea>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-6 py-4 flex justify-end gap-3">
          <button @click="closeAddModal" class="px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-100 rounded-md">Cancel</button>
          <button @click="submitProduct" class="px-6 py-2 bg-indigo-600 text-sm font-semibold text-white rounded-md hover:bg-indigo-500 shadow-sm">
            {{ isEditing ? 'Update Catalog' : 'Add to Catalog' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>