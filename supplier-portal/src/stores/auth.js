import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const token = ref(null)

    const isAuthenticated = computed(() => !!token.value && !!user.value)

    // Helper to fetch full details (from original auth.js)
    const fetchUserDetails = async (email) => {
        try {
            // 1. Fetch User details
            const userRes = await fetch(`/api/resource/User/${email}?t=${Date.now()}`, { credentials: 'include', cache: 'no-store' });
            const userDoc = await userRes.json();
            const fullName = userDoc.data?.full_name || email;

            // 2. Fetch Supplier details (if connected)
            try {
                // Use custom API to get supplier based on child table linkage
                const supplierRes = await fetch(`/api/method/supplier_portal.api.get_supplier_details`, { credentials: 'include' });
                const supplierData = await supplierRes.json();

                let company = 'Vendor';
                let supplierId = null;

                if (supplierData.message && Object.keys(supplierData.message).length > 0) {
                    company = supplierData.message.supplier_name;
                    supplierId = supplierData.message.name;
                }

                return {
                    name: fullName,
                    email: email,
                    company: company,
                    supplierId: supplierId
                };
            } catch (sErr) {
                console.warn("Supplier fetch error", sErr);
                return { name: fullName, email, company: 'Vendor' };
            }

        } catch (e) {
            console.error("Error fetching user details", e);
            return { name: email.split('@')[0], email, company: 'Vendor' };
        }
    }

    const login = async (credentials) => {
        try {
            const response = await fetch('/api/method/login', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    usr: credentials.email,
                    pwd: credentials.password
                })
            })

            const data = await response.json()

            if (response.ok && data.message === 'Logged In') {
                // Fetch full details including Company Name (Custom logic retained for functionality)
                const fullUser = await fetchUserDetails(credentials.email);

                user.value = {
                    ...fullUser, // Includes name, email, company, supplierId
                    home_page: data.home_page
                }
                token.value = 'frappe-session-' + Date.now()

                // Store in localStorage for persistence
                localStorage.setItem('auth_user', JSON.stringify(user.value))
                localStorage.setItem('auth_token', token.value)

                return true
            } else {
                return false
            }
        } catch (error) {
            console.error('Login error:', error)
            return false
        }
    }

    const signup = async (userData) => {
        // Use custom API for Vendor Registration (from original auth.js)
        try {
            const response = await fetch('/api/method/supplier_portal.api.register_vendor', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    company_name: userData.companyName,
                    email: userData.email,
                    contact_person: userData.contactPerson,
                    phone: userData.phone,
                    gst: userData.gst,
                    password: userData.password
                })
            })

            const result = await response.json()

            if (result.message && result.message.status === 'success') {
                return { success: true, message: result.message.message }
            } else {
                const errMsg = (result.message && result.message.message) || result.message || 'Registration failed'
                throw new Error(errMsg)
            }
        } catch (error) {
            console.error("Registration Error:", error)
            throw error;
        }
    }

    const logout = async () => {
        try {
            // User requested POST for logout
            await fetch('/api/method/logout', {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
        } catch (error) {
            console.error('Logout error:', error)
        } finally {
            user.value = null
            token.value = null

            // Clear localStorage
            localStorage.removeItem('auth_user')
            localStorage.removeItem('auth_token')

            // Force reload to clear any memory states or router guards
            window.location.href = '/login'
        }
    }

    // Auto-check auth when tab becomes visible (handles cross-tab login/logout)
    if (typeof window !== 'undefined') {
        window.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                initializeAuth()
            }
        })
    }

    const initializeAuth = async () => {
        // 1. Always check the true server state first (with cache busting)
        try {
            const response = await fetch(`/api/method/frappe.auth.get_logged_user?t=${Date.now()}`, {
                credentials: 'include',
                cache: 'no-store',
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });

            if (response.ok) {
                const data = await response.json();
                const serverUser = data.message;

                // Case A: Server says we are logged in (not Guest)
                if (serverUser && serverUser !== 'Guest') {
                    // If we don't have user data in memory, or if it doesn't match, fetch and update
                    if (!user.value || user.value.email !== serverUser) {
                        const fullUser = await fetchUserDetails(serverUser);
                        user.value = {
                            ...fullUser,
                            home_page: '/app' // Default or fetch if needed
                        }
                        token.value = 'frappe-session-active' // Presence of token indicates auth

                        // Update persistence
                        localStorage.setItem('auth_user', JSON.stringify(user.value))
                        localStorage.setItem('auth_token', token.value)
                    }
                    return; // Sync complete
                }

                // Case B: Server says 'Guest' -> We must be logged out
                // If we have local state, clear it (Sync Logout)
                if (user.value || localStorage.getItem('auth_user')) {
                    console.log("Server reports Guest, clearing local session.");
                    user.value = null
                    token.value = null
                    localStorage.removeItem('auth_user')
                    localStorage.removeItem('auth_token')
                    // Optional: Redirect to login if currently on a protected route?
                    // router.push('/login') // requires router access
                }
            } else {
                // Response not OK (e.g. 500 error), assume logged out or keep state?
                // Safer to do nothing or retry, but if 401/403, definitely logout.
                if (response.status === 401 || response.status === 403) {
                    user.value = null;
                    token.value = null;
                    localStorage.removeItem('auth_user');
                    localStorage.removeItem('auth_token');
                }
            }

        } catch (e) {
            console.warn("Auth check failed, falling back to local state if offline", e);
            // Fallback: If network error, maybe trust local storage? 
            const storedUser = localStorage.getItem('auth_user')
            const storedToken = localStorage.getItem('auth_token')
            if (storedUser && storedToken) {
                user.value = JSON.parse(storedUser)
                token.value = storedToken
            }
        }
    }

    return {
        user,
        token,
        isAuthenticated,
        login,
        signup,
        logout,
        initializeAuth
    }
})
