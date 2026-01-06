import { reactive, computed } from 'vue'

const state = reactive({
    user: null,
    cookie: null
})

// Initialize state from existing session if possible
// Initialize state from existing session if possible
// Helper to fetch full details
const fetchUserDetails = async (email) => {
    try {
        // 1. Fetch User details
        const userRes = await fetch(`/api/resource/User/${email}`);
        const userDoc = await userRes.json();
        const fullName = userDoc.data?.full_name || email;

        // 2. Fetch Supplier details (if connected)
        try {
            const supplierRes = await fetch(`/api/resource/Supplier?filters=[["email_id","=", "${email}"]]&fields=["name", "supplier_name"]`);
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

// Initialize state from existing session if possible
const init = async () => {
    try {
        const response = await fetch('/api/method/frappe.auth.get_logged_user', {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        })

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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usr: email, pwd: password })
        })

        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            const data = await response.json()

            if (data.message === 'Logged In') {
                state.user = await fetchUserDetails(email);
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
        await fetch('/api/method/logout', { method: 'POST' })
        state.user = null
    } catch (error) {
        console.error("Logout Error:", error)
    }
}

const register = async (data) => {
    try {
        // Use custom API for Vendor Registration
        const response = await fetch('/api/method/supplier_portal.api.register_vendor', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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
