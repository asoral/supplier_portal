import { reactive, computed } from 'vue'

const state = reactive({
    user: null,
    csrfToken: null
})

// Helper to fetch full details
const fetchUserDetails = async (email) => {
    try {
        // 1. Fetch User details
        const userRes = await fetch(`/api/resource/User/${email}`, { credentials: 'include' });
        const userDoc = await userRes.json();
        const fullName = userDoc.data?.full_name || email;

        // 2. Fetch Supplier details (if connected)
        try {
            const supplierRes = await fetch(`/api/resource/Supplier?filters=[["email_id","=", "${email}"]]&fields=["name", "supplier_name"]`, { credentials: 'include' });
            const supplierData = await supplierRes.json();

            let company = 'Vendor';
            if (supplierData.data && supplierData.data.length > 0) {
                company = supplierData.data[0].supplier_name;
            }

            return {
                name: fullName,
                email: email,
                company: company
            };
        } catch (sErr) {
            return { name: fullName, email, company: 'Vendor' };
        }

    } catch (e) {
        console.error("Error fetching user details", e);
        return { name: email.split('@')[0], email, company: 'Vendor' };
    }
}

// Function to extract CSRF token from document cookies as fallback
const getCsrfFromCookie = () => {
    if (document.cookie && document.cookie.includes('sid')) {
        // This is a naive check. Real token is usually not in cookie for SPA unless customized.
        // But often X-Frappe-CSRF-Token header is enough if captured.
    }
    return null;
}

// Initialize state from existing session if possible
const init = async () => {
    try {
        const response = await fetch('/api/method/frappe.auth.get_logged_user', {
            method: 'GET',
            credentials: 'include',
            headers: { 'Accept': 'application/json' }
        })

        // Capture CSRF Token from response header
        const csrfToken = response.headers.get('X-Frappe-CSRF-Token');
        if (csrfToken) {
            state.csrfToken = csrfToken;
        }

        const contentType = response.headers.get("content-type");
        if (response.ok && contentType && contentType.indexOf("application/json") !== -1) {
            const data = await response.json()
            if (data.message && data.message !== 'Guest') {
                // Fetch full user details
                state.user = await fetchUserDetails(data.message);
                return
            }
        }
    } catch (e) {
        // Not logged in or network error, ignore
    }
}

const isLoggedIn = computed(() => !!state.user && state.user.email !== 'Guest')

const login = async (email, password) => {
    try {
        const response = await fetch('/api/method/login', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...(state.csrfToken ? { 'X-Frappe-CSRF-Token': state.csrfToken } : {})
            },
            body: JSON.stringify({ usr: email, pwd: password })
        })

        // Capture CSRF if updated
        const csrfToken = response.headers.get('X-Frappe-CSRF-Token');
        if (csrfToken) {
            state.csrfToken = csrfToken;
        }

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            const data = await response.json()

            if (data.message === 'Logged In') {
                state.user = await fetchUserDetails(email);
                // Re-init to ensure we have fresh token/state
                await init();
                return state.user
            } else {
                throw new Error(data.message || 'Login failed')
            }
        } else {
            // Likely an HTML error page (403/500)
            if (!response.ok) {
                throw new Error(`Server Error: ${response.status}`)
            }
            throw new Error("Invalid server response")
        }
    } catch (error) {
        console.error("Login Error:", error)
        throw error
    }
}

const logout = async () => {
    try {
        await fetch('/api/method/logout', {
            method: 'GET',
            credentials: 'include'
        })
    } catch (error) {
        console.error("Logout Error (ignoring):", error)
    } finally {
        state.user = null
        state.csrfToken = null
    }
}

const register = async (data) => {
    try {
        // Use custom API for Vendor Registration
        const response = await fetch('/api/method/supplier_portal.api.register_vendor', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...(state.csrfToken ? { 'X-Frappe-CSRF-Token': state.csrfToken } : {})
            },
            body: JSON.stringify({
                company_name: data.companyName,
                email: data.email,
                contact_person: data.contactPerson,
                phone: data.phone,
                gst: data.gst,
                password: data.password
            })
        })

        // Frappe might return 200 OK but with an internal exception text if debug is on, 
        // but generally returns JSON.
        const result = await response.json()

        // Check for success or error based on our python return
        if (result.message && result.message.status === 'success') {
            return { success: true, message: result.message.message }
        } else {
            // If we returned {status: "failed", message: "..."}
            const errMsg = (result.message && result.message.message) || result.message || 'Registration failed'
            throw new Error(errMsg)
        }

    } catch (error) {
        console.error("Registration Error:", error)
        throw error
    }
}

// Call init on load
init()

export const useAuth = () => {
    return {
        state,
        isLoggedIn,
        login,
        logout,
        register
    }
}
