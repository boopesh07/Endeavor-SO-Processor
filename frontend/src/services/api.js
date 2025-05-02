import axios from 'axios';

const API_URL = '/api';

// Create axios instance
const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Extract data from PDF
export const extractFromPDF = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/extract', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

// Create a new sales order
export const createSalesOrder = async (fileName, lineItems) => {
    const formData = new FormData();
    formData.append('file_name', fileName);
    formData.append('line_items', JSON.stringify(lineItems));

    const response = await api.post('/sales-orders', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

// Get all sales orders
export const getAllSalesOrders = async () => {
    const response = await api.get('/sales-orders');
    return response.data;
};

// Get a specific sales order
export const getSalesOrder = async (id) => {
    const response = await api.get(`/sales-orders/${id}`);
    return response.data;
};

// Match all items in a sales order
export const matchSalesOrderItems = async (id) => {
    const response = await api.post(`/sales-orders/${id}/match`);
    return response.data;
};

// Batch match multiple items using the external API
export const matchBatchItems = async (queries, limit = 5) => {
    // The actual external API endpoint
    const MATCH_BATCH_API_URL = 'https://endeavor-interview-api-gzwki.ondigitalocean.app/match/batch';

    try {
        const response = await axios.post(`${MATCH_BATCH_API_URL}?limit=${limit}`, {
            queries: queries
        });

        return response.data.results;
    } catch (error) {
        console.error('Error in batch matching:', error);
        throw error;
    }
};

// Get matches for a specific item
export const getMatchesForItem = async (orderId, itemName, limit = 5) => {
    // For the extraction page, we don't have an orderId yet, so call the external API directly
    if (!orderId) {
        // The actual external API endpoint
        const MATCH_SINGLE_API_URL = 'https://endeavor-interview-api-gzwki.ondigitalocean.app/match';

        try {
            const response = await axios.get(`${MATCH_SINGLE_API_URL}?query="${itemName}"&limit=${limit}`);
            return response.data;
        } catch (error) {
            console.error('Error in single item matching:', error);
            throw error;
        }
    }

    // For existing sales orders, use our backend API
    const response = await api.get(`/sales-orders/${orderId}/match-item`, {
        params: { item_name: itemName, limit },
    });
    return response.data;
};

// Update a sales order
export const updateSalesOrder = async (id, updates) => {
    const response = await api.patch(`/sales-orders/${id}`, updates);
    return response.data;
};

// Update a specific line item
export const updateLineItem = async (orderId, itemIndex, updates) => {
    const response = await api.patch(`/sales-orders/${orderId}/line-items/${itemIndex}`, updates);
    return response.data;
};

// Get a sales order CSV download URL
export const getSalesOrderCsvUrl = (id) => {
    return `${API_URL}/sales-orders/${id}/csv`;
};

// Download a sales order CSV directly
export const downloadSalesOrderCsv = async (id) => {
    try {
        // Use fetch API for direct file download
        const response = await fetch(`${API_URL}/sales-orders/${id}/csv`, {
            method: 'GET',
            headers: {
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Get the blob data
        const blob = await response.blob();

        // Create a download link and trigger it
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `sales_order_${id}.csv`;
        document.body.appendChild(a);
        a.click();

        // Clean up
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        return true;
    } catch (error) {
        console.error('Error downloading CSV:', error);
        throw error;
    }
}; 