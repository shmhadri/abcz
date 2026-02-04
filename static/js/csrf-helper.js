/**
 * CSRF Token Helper for Django
 * Add this to any template that makes fetch POST requests
 */

// Get CSRF token from cookie
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

// Get CSRF token
const csrftoken = getCookie('csrftoken');

/**
 * Helper function for POST requests with CSRF token
 * Usage:
 *   postWithCSRF('/api/endpoint/', {key: 'value'})
 *     .then(data => console.log(data))
 *     .catch(err => console.error(err));
 */
function postWithCSRF(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    }).then(response => {
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Request failed');
            });
        }
        return response.json();
    });
}
