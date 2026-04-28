(function () {
    function getCookie(name) {
        const escapedName = String(name || '').replace(/[-.]/g, '\\$&');
        const match = document.cookie.match(new RegExp('(?:^|; )' + escapedName + '=([^;]*)'));
        return match ? decodeURIComponent(match[1]) : '';
    }

    function getCsrfToken() {
        return getCookie('csrftoken');
    }

    function buildRequestBody(data) {
        if (!data) {
            return null;
        }

        if (data instanceof URLSearchParams) {
            return data.toString();
        }

        const params = new URLSearchParams();
        Object.keys(data).forEach(function (key) {
            params.set(key, String(data[key]));
        });
        return params.toString();
    }

    async function requestJson(url, options) {
        const opts = options || {};
        const method = (opts.method || 'GET').toUpperCase();
        const headers = Object.assign({
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
        }, opts.headers || {});

        const fetchOptions = {
            method: method,
            headers: headers,
            credentials: opts.credentials || 'same-origin',
        };

        if (method !== 'GET' && method !== 'HEAD') {
            if (!headers['Content-Type']) {
                headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8';
            }
            if (!headers['X-CSRFToken'] && opts.csrf !== false) {
                headers['X-CSRFToken'] = getCsrfToken();
            }
            fetchOptions.body = buildRequestBody(opts.data);
        }

        let response;
        try {
            response = await fetch(url, fetchOptions);
        } catch (error) {
            const networkError = new Error('network_error');
            networkError.cause = error;
            throw networkError;
        }

        if (!response.ok) {
            const responseError = new Error('http_error');
            responseError.status = response.status;
            throw responseError;
        }

        try {
            return await response.json();
        } catch (error) {
            const parseError = new Error('parse_error');
            parseError.cause = error;
            throw parseError;
        }
    }

    function ensureStatusElement(root) {
        if (!root) {
            return null;
        }

        let statusElement = root.querySelector('.ajax-status');
        if (!statusElement) {
            statusElement = document.createElement('p');
            statusElement.className = 'ajax-status';
            root.insertAdjacentElement('afterbegin', statusElement);
        }

        return statusElement;
    }

    function renderLoading(root, text) {
        const statusElement = ensureStatusElement(root);
        if (!statusElement) {
            return;
        }

        statusElement.className = 'ajax-status ajax-status-loading';
        statusElement.textContent = text || 'loading...';
    }

    function renderError(root, text) {
        const statusElement = ensureStatusElement(root);
        if (!statusElement) {
            return;
        }

        statusElement.className = 'ajax-status ajax-status-error';
        statusElement.textContent = text || 'request failed';
    }

    function clearStatus(root) {
        if (!root) {
            return;
        }

        const statusElement = root.querySelector('.ajax-status');
        if (statusElement) {
            statusElement.remove();
        }
    }

    window.AjaxUtils = {
        getCookie: getCookie,
        getCsrfToken: getCsrfToken,
        requestJson: requestJson,
        renderLoading: renderLoading,
        renderError: renderError,
        clearStatus: clearStatus,
    };
})();
