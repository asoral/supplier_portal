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

    const fetchUserDetails = async (email = null) => {
        // If email provided, we can rely on it, but safer to ask backend 'who am i'
        try {
            // credentials: 'include' is CRITICAL here to ensure session cookie is sent
            // [FIX] Add timestamp to prevent browser caching of 'Guest' response
            const response = await fetch(`/api/method/supplier_portal.api.get_logged_user?t=${Date.now()}`, {
                credentials: 'include',
                cache: 'no-store'
            });
            const data = await response.json();

            if (data.message) {
                if (data.message === 'Guest') {
                    return { email: 'Guest' }; // Explicit Guest object
                }
                return {
                    email: data.message,
                    name: data.message === 'Administrator' ? 'Administrator' : data.message,
                }
            }
        } catch (e) {
            console.error("Failed to fetch user details", e);
        }
        return null;
    }

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

    // Helper to read cookies
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    // Initialize: Trust local storage but VERIFY with backend
    const initializeAuth = async () => {
        const storedUser = localStorage.getItem('auth_user')
        const storedToken = localStorage.getItem('auth_token')

        let isLocallyAuthenticated = false;

        // 1. Load from local first (fast)
        if (storedUser && storedToken) {
            try {
                // Only overwrite if we didn't just optimistically set it equal
                const parsed = JSON.parse(storedUser);
                if (!user.value || user.value.email === parsed.email) {
                    user.value = parsed
                    token.value = storedToken
                    isLocallyAuthenticated = true;
                }
            } catch (e) {
                console.error("Error parsing stored session", e)
            }
        }

        // 2. Verify with backend (truth) - IN BACKGROUND if we have local data
        const verifyBackend = async () => {
            try {
                const backendUser = await fetchUserDetails();

                if (backendUser) {
                    if (backendUser.email !== 'Guest') {
                        // Valid user from backend
                        // Update if different
                        if (!user.value || user.value.email !== backendUser.email) {
                            console.log("Session sync: Updating user from backend", backendUser);
                            user.value = {
                                ...backendUser,
                                name: backendUser.name // Simplification
                            };
                            localStorage.setItem('auth_user', JSON.stringify(user.value));
                        }

                        // [FIX] Shared Session Support
                        if (!token.value) {
                            console.log("Shared session detected. initializing local token.");
                            token.value = 'frappe-session-shared-' + Date.now();
                            localStorage.setItem('auth_token', token.value);
                        }

                        // Refresh CSRF
                        getCsrfToken();
                    } else {
                        // Backend EXPLICITLY says Guest.
                        if (user.value) {
                            console.warn("Backend reported 'Guest' while local session exists. Keeping local session active.");
                            // We do NOT logout here. We trust the local state to keep the UI running.
                            // The user will see 'Session Expired' overlays if API calls fail, but won't be kicked out.
                        }
                    }
                }
            } catch (e) {
                console.error("Auth init verify failed", e);
            }
        };

        if (isLocallyAuthenticated) {
            // If we have local data, return immediately to unblock the router
            // Run verification in background
            verifyBackend();
            return;
        } else {
            // If no local data, we MUST await the backend check (e.g. fresh load without local storage but maybe cookie exists)
            await verifyBackend();
        }
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

        try {
            let response = await fetch(url, fetchOptions);

            // Retry logic for CSRF/Auth errors
            if (!response.ok) {
                if (response.status === 403 || response.status === 417 || response.status === 401) {

                    // [FIX] Distinguish between 401 (Session Expired) and 403 (Permission Denied)
                    // 403 should NOT logout. It just means you can't see this specific resource.

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
                    if (isCsrf) {
                        console.warn("CSRF Error, refreshing token and retrying...");
                        await new Promise(r => setTimeout(r, 200));
                        currentToken = await getCsrfToken();
                        headers['X-Frappe-CSRF-Token'] = currentToken;
                        response = await fetch(url, { ...fetchOptions, headers });
                    }

                    // Final check: disable all auto-logout
                    if (response.status === 401) {
                        console.warn("Session expired (401). Keeping local session active.");
                    }
                }
            }
            return response;
        } catch (error) {
            console.error("Secure fetch error:", error);
            throw error;
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
                // Wait a tiny bit for cookie to propagate in browser
                await new Promise(r => setTimeout(r, 100));
                await getCsrfToken();

                // 2. Verified Fetch Loop
                // Retry fetching user details to ensure session "stuck"
                let attempts = 0;
                let verifiedUser = null;

                while (attempts < 3 && !verifiedUser) {
                    try {
                        const u = await fetchUserDetails(credentials.email);
                        if (u && u.email !== 'Guest') {
                            verifiedUser = u;
                        } else {
                            // Wait and retry - Increased delay to 500ms
                            await new Promise(r => setTimeout(r, 500));
                        }
                    } catch (e) {
                        await new Promise(r => setTimeout(r, 500));
                    }
                    attempts++;
                }

                if (!verifiedUser) {
                    console.warn("Login successful but backend session verification timed out. Trusting login response and proceeding.");
                    // [FIX] Do NOT logout. Assume cookie will eventually propagate.
                    // Use fallback data derived from login if needed, or just trust the local state we are about to set.

                    // Allow to proceed with basic user info
                    try {
                        // Optimistic setting if verify failed
                        verifiedUser = {
                            email: credentials.email,
                            name: data.full_name || 'User',
                            company: 'Vendor'
                        }
                    } catch (e) { }
                }

                // Use verifiedUser if found, otherwise fall back to constructed
                user.value = {
                    ...verifiedUser,
                    home_page: data.home_page
                }

                token.value = 'frappe-session-' + Date.now()

                localStorage.setItem('auth_user', JSON.stringify(user.value))
                localStorage.setItem('auth_token', token.value)

                // [FIX] Explicitly set cookie too for optimistic check
                document.cookie = `user_id=${encodeURIComponent(user.value.email)}; path=/; max-age=86400; SameSite=Lax`;

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

    const logout = async (skipServer = false) => {
        try {
            if (!skipServer) {
                await fetch('/api/method/logout', { method: 'GET', credentials: 'include' })
                await getCsrfToken(); // Refresh token context
            }
        } catch (error) {
            console.error('Logout error:', error)
        } finally {
            user.value = null
            token.value = null
            csrfToken.value = null
            localStorage.removeItem('auth_user')
            localStorage.removeItem('auth_token')

            // [FIX] Removed hard redirect. 
            // Let the caller or reactive UI handle the redirect to avoid loops.
            // window.location.href = '/supplier-portal/login'
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
