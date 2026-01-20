import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const token = ref(null)
    const csrfToken = ref(null)

    // Synchronously restore from local storage if available
    try {
        const storedUser = localStorage.getItem('auth_user')
        const storedToken = localStorage.getItem('auth_token')
        if (storedUser && storedToken) {
            user.value = JSON.parse(storedUser)
            token.value = storedToken
        }
    } catch (e) {
        console.error("Failed to restore session from local storage", e)
    }

    const isAuthenticated = computed(() => !!token.value && !!user.value)

    const getCsrfToken = async () => {
        try {
            // If we have a valid global token (e.g. pushed by server), use it first? 
            // Ideally fetching fresh is safer.
            const response = await fetch('/api/method/supplier_portal.api.get_csrf_token', {
                credentials: 'include',
                cache: 'no-store'
            });
            const data = await response.json();
            if (data.message) {
                csrfToken.value = data.message;
                window.csrf_token = data.message; // Sync with global for legacy scripts
                return data.message;
            }
        } catch (e) {
            console.error("Failed to fetch CSRF token", e);
        }
        return csrfToken.value || window.csrf_token;
    }

    // Robust Fetch wrapper
    const secureFetch = async (url, options = {}) => {
        let currentToken = csrfToken.value || window.csrf_token;
        if (!currentToken || currentToken === "None") {
            currentToken = await getCsrfToken();
        }

        const headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-Frappe-CSRF-Token': currentToken,
            ...(options.headers || {})
        };

        const fetchOptions = {
            ...options,
            headers,
            credentials: 'include'
        };

        let response = await fetch(url, fetchOptions);

        // Retry logic for CSRF/Auth errors
        if (!response.ok) {
            if (response.status === 403 || response.status === 417 || response.status === 401) {
                // Try to parse error to see if it's specifically CSRF
                let isCsrf = false;
                try {
                    const clone = response.clone();
                    const err = await clone.json();
                    if (err.exc_type === 'CSRFTokenError' || (response.status === 403 && err.message?.includes('CSRF'))) {
                        isCsrf = true;
                    }
                } catch (e) { }

                // If it looks like a token issue (or generic 403 which acts like one), retry once
                if (isCsrf || response.status === 403) {
                    console.warn("Potential CSRF/Permission Error, refreshing token and retrying...");
                    await new Promise(r => setTimeout(r, 200));
                    currentToken = await getCsrfToken();
                    headers['X-Frappe-CSRF-Token'] = currentToken;
                    response = await fetch(url, { ...fetchOptions, headers });
                }
            }
        }
        return response;
    }

    // Helper to fetch full details
    const fetchUserDetails = async (email) => {
        try {
            const userRes = await secureFetch(`/api/resource/User/${email}?t=${Date.now()}`);
            const userDoc = await userRes.json();
            const fullName = userDoc.data?.full_name || email;

            try {
                const supplierRes = await secureFetch(`/api/method/supplier_portal.api.get_supplier_details`);
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
                // 1. Refresh CSRF Token immediately after login
                await getCsrfToken();

                // 2. Verify Session
                const verifyRes = await secureFetch(`/api/method/supplier_portal.api.get_logged_user?t=${Date.now()}`);
                const verifyData = await verifyRes.json();

                if (!verifyData.message || verifyData.message === 'Guest') {
                    throw new Error('Session establishment failed.');
                }

                // 3. Fetch details
                const fullUser = await fetchUserDetails(credentials.email);

                user.value = {
                    ...fullUser,
                    home_page: data.home_page
                }
                token.value = 'frappe-session-' + Date.now()

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
        try {
            const response = await fetch('/api/method/supplier_portal.api.register_vendor', {
                method: 'POST',
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
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
            await fetch('/api/method/logout', { method: 'GET', credentials: 'include' })
            await getCsrfToken(); // Refresh token context
        } catch (error) {
            console.error('Logout error:', error)
        } finally {
            user.value = null
            token.value = null
            csrfToken.value = null
            localStorage.removeItem('auth_user')
            localStorage.removeItem('auth_token')
            window.location.href = '/supplier-portal/login'
        }
    }

    const initializeAuth = async () => {
        try {
            // Pre-load CSRF token safely
            await getCsrfToken();

            const response = await fetch(`/api/method/supplier_portal.api.get_logged_user?t=${Date.now()}`, {
                credentials: 'include',
                cache: 'no-store',
                headers: { 'Accept': 'application/json', 'Cache-Control': 'no-cache' }
            });

            if (response.ok) {
                const data = await response.json();
                const serverUser = data.message;

                // Case 1: Server says we are logged in
                if (serverUser && serverUser !== 'Guest') {
                    if (!user.value || user.value.email !== serverUser) {
                        const fullUser = await fetchUserDetails(serverUser);
                        user.value = { ...fullUser, home_page: '/supplier-portal/dashboard' }
                        token.value = 'frappe-session-active'
                        localStorage.setItem('auth_user', JSON.stringify(user.value))
                        localStorage.setItem('auth_token', token.value)
                    }
                    return;
                }

                // Case 2: Server explicitly says "Guest", but we think we are logged in.
                if (user.value || localStorage.getItem('auth_user')) {
                    console.warn("Server reports Guest, performing double-check...");

                    // Wait 1 second and retry just in case it's a transient glitch
                    await new Promise(r => setTimeout(r, 1000));

                    try {
                        const retryRes = await fetch(`/api/method/supplier_portal.api.get_logged_user?t=${Date.now()}`, {
                            credentials: 'include',
                            cache: 'no-store'
                        });
                        const retryData = await retryRes.json();
                        if (retryData.message && retryData.message !== 'Guest') {
                            console.log("Double-check success! Session recovered.");
                            return; // Session is actually fine
                        }
                    } catch (e) { }

                    console.log("Server confirmed Guest after retry, clearing local session.");
                    user.value = null
                    token.value = null
                    localStorage.removeItem('auth_user')
                    localStorage.removeItem('auth_token')
                    window.location.href = '/supplier-portal/login'
                }
            }
        } catch (e) {
            // Case 3: Network error or other failure. Do NOT logout. 
            // Assume session might still be valid.
            console.warn("Auth check failed (network/backend), preserving local state for now.", e);
            const storedUser = localStorage.getItem('auth_user')
            const storedToken = localStorage.getItem('auth_token')
            if (storedUser && storedToken && !user.value) {
                user.value = JSON.parse(storedUser)
                token.value = storedToken
            }
        }
    }



    return {
        user,
        token,
        csrfToken,
        isAuthenticated,
        login,
        signup,
        logout,
        initializeAuth,
        secureFetch,
        getCsrfToken
    }
})
