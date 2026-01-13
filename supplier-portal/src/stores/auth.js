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
                // Fetch full details including Company Name
                const fullUser = await fetchUserDetails(credentials.email);

                user.value = {
                    ...fullUser,
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
                // Auto login after signup? Or return success.
                // The original code just returned success message.
                return { success: true, message: result.message.message }
            } else {
                const errMsg = (result.message && result.message.message) || result.message || 'Registration failed'
                throw new Error(errMsg)
            }
        } catch (error) {
            console.error("Registration Error:", error)
            // Fallback to mock for testing if server fails? No, better to fail real API.
            // But user's snippet had a mock signup. I will stick to Real API if possible, 
            // but if the user demanded the snippet exactly, I might have issues.
            // The user said "thsi api use", implying the structure.
            // I'll return false/error.
            throw error;
        }
    }

    const logout = async () => {
        try {
            await fetch('/api/method/logout', {
                method: 'GET',
                credentials: 'include',
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

                // Case A: Server says we are logged in
                if (data.message && data.message !== 'Guest') {
                    // If we don't have user data in memory, or if it doesn't match, fetch and update
                    if (!user.value || user.value.email !== data.message) {
                        const fullUser = await fetchUserDetails(data.message);
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
            }

            // Case B: Server says 'Guest' or request failed -> Clear everything
            // This handles the "Vice Versa" case: Logged out in Desk -> Auto logs out in Portal
            user.value = null
            token.value = null
            localStorage.removeItem('auth_user')
            localStorage.removeItem('auth_token')

        } catch (e) {
            console.warn("Auth check failed, falling back to local state if offline", e);
            // Fallback: If network error, maybe trust local storage? 
            // Better to stay safe and assume not authenticated if we can't reach server?
            // unique decision: trust local if offline, but mostly we assume online.
            // For now, let's just leave it. If checking user fails, we might be offline. 
            // Loading 'auth_user' from storage is a risk if session expired.
            // But let's load it just in case, but user might experience 403s on APIs.
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
