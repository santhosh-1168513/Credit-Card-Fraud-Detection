/**
 * FraudGuard - Credit Card Fraud Detection System
 * Main JavaScript File
 * Author: Production Team
 * Version: 1.0.0
 */

// =====================================================
// GLOBAL VARIABLES
// =====================================================
let uploadedFile = null;
let csvData = [];
let analysisResults = [];
let currentFilter = 'all';

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

/**
 * Parse CSV file content
 * @param {string} content - CSV file content
 * @returns {Array} Parsed CSV data
 */
function parseCSV(content) {
    const lines = content.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim() === '') continue;
        
        const values = lines[i].split(',').map(v => v.trim());
        const row = {};
        
        headers.forEach((header, index) => {
            row[header] = values[index] || '';
        });
        
        data.push(row);
    }
    
    return data;
}

/**
 * Format currency
 * @param {number} amount - Amount to format
 * @returns {string} Formatted currency string
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

/**
 * Format date and time
 * @param {string} timestamp - Timestamp to format
 * @returns {string} Formatted date string
 */
function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Generate random fraud indicators for demo purposes
 * @returns {Array} Array of fraud indicators
 */
function generateFraudIndicators() {
    const indicators = [
        'Unusual transaction amount',
        'Suspicious merchant category',
        'Transaction from high-risk location',
        'Unusual time of transaction',
        'Multiple transactions in short period',
        'Card used in multiple locations',
        'Velocity check failed',
        'Amount exceeds normal spending pattern'
    ];
    
    // Randomly select 2-4 indicators
    const count = Math.floor(Math.random() * 3) + 2;
    const selected = [];
    const available = [...indicators];
    
    for (let i = 0; i < count; i++) {
        const index = Math.floor(Math.random() * available.length);
        selected.push(available[index]);
        available.splice(index, 1);
    }
    
    return selected;
}

/**
 * Calculate risk score based on transaction data (DEMO LOGIC)
 * In production, this would call an ML model API
 * @param {Object} transaction - Transaction data
 * @returns {number} Risk score (0-100)
 */
function calculateRiskScore(transaction) {
    let score = 0;
    const amount = parseFloat(transaction.amount) || 0;
    
    // Amount-based risk
    if (amount > 5000) score += 30;
    else if (amount > 2000) score += 20;
    else if (amount > 1000) score += 10;
    else if (amount < 10) score += 15;
    
    // Random factor to simulate ML model variability
    score += Math.random() * 40;
    
    // Location-based risk (simplified demo)
    const highRiskLocations = ['Nigeria', 'Russia', 'Ukraine', 'Unknown'];
    if (highRiskLocations.some(loc => transaction.location?.includes(loc))) {
        score += 25;
    }
    
    // Time-based risk (transactions between 1 AM - 5 AM)
    const timestamp = new Date(transaction.timestamp);
    const hour = timestamp.getHours();
    if (hour >= 1 && hour <= 5) {
        score += 15;
    }
    
    // Cap score at 100
    return Math.min(Math.round(score), 100);
}

/**
 * Determine fraud status based on risk score
 * @param {number} riskScore - Risk score
 * @returns {string} Fraud status
 */
function determineFraudStatus(riskScore) {
    if (riskScore >= 70) return 'fraud';
    if (riskScore >= 50) return 'warning';
    return 'legitimate';
}

/**
 * Get risk level label
 * @param {number} riskScore - Risk score
 * @returns {string} Risk level
 */
function getRiskLevel(riskScore) {
    if (riskScore >= 70) return 'High';
    if (riskScore >= 50) return 'Medium';
    return 'Low';
}

// =====================================================
// FILE UPLOAD FUNCTIONALITY
// =====================================================

/**
 * Initialize file upload functionality
 */
function initFileUpload() {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    
    if (!dropArea || !fileInput) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropArea.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFiles, false);
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function highlight(e) {
    document.getElementById('dropArea')?.classList.add('drag-over');
}

function unhighlight(e) {
    document.getElementById('dropArea')?.classList.remove('drag-over');
}

function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFileSelection(files[0]);
}

function handleFiles(e) {
    const files = e.target.files;
    handleFileSelection(files[0]);
}

/**
 * Handle file selection
 * @param {File} file - Selected file
 */
function handleFileSelection(file) {
    if (!file) return;
    
    // Validate file type
    if (!file.name.endsWith('.csv')) {
        alert('Please upload a CSV file');
        return;
    }
    
    uploadedFile = file;
    
    // Display file info
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    if (fileInfo && fileName && fileSize) {
        fileName.textContent = file.name;
        fileSize.textContent = (file.size / 1024).toFixed(2) + ' KB';
        fileInfo.classList.remove('d-none');
    }
    
    // Enable analyze button
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.disabled = false;
    }
    
    // Read file to get row count
    const reader = new FileReader();
    reader.onload = function(e) {
        const content = e.target.result;
        const lines = content.trim().split('\n');
        const rowCount = document.getElementById('fileRows');
        if (rowCount) {
            rowCount.textContent = (lines.length - 1) + ' rows';
        }
    };
    reader.readAsText(file);
}

/**
 * Clear selected file
 */
function clearFile() {
    uploadedFile = null;
    csvData = [];
    
    const fileInfo = document.getElementById('fileInfo');
    const fileInput = document.getElementById('fileInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (fileInfo) fileInfo.classList.add('d-none');
    if (fileInput) fileInput.value = '';
    if (analyzeBtn) analyzeBtn.disabled = true;
}

// =====================================================
// SAMPLE DATA GENERATION
// =====================================================

/**
 * Generate sample transaction data
 * @returns {string} CSV formatted sample data
 */
function generateSampleData() {
    const merchants = ['Amazon', 'Walmart', 'Target', 'Best Buy', 'Starbucks', 'Shell Gas', 'McDonalds', 'Apple Store'];
    const locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Miami', 'Seattle', 'Boston', 'Denver'];
    const sampleData = [];
    
    // Add CSV header
    sampleData.push('transaction_id,amount,merchant,location,timestamp,card_number');
    
    // Generate 20 sample transactions
    for (let i = 1; i <= 20; i++) {
        const transactionId = 'TXN' + String(i).padStart(4, '0');
        const amount = (Math.random() * 2000 + 10).toFixed(2);
        const merchant = merchants[Math.floor(Math.random() * merchants.length)];
        const location = locations[Math.floor(Math.random() * locations.length)];
        
        // Generate random timestamp within last 30 days
        const now = new Date();
        const randomDays = Math.floor(Math.random() * 30);
        const randomHours = Math.floor(Math.random() * 24);
        const randomMinutes = Math.floor(Math.random() * 60);
        const timestamp = new Date(now.getTime() - (randomDays * 24 * 60 * 60 * 1000) - (randomHours * 60 * 60 * 1000) - (randomMinutes * 60 * 1000));
        
        const cardNumber = '****' + Math.floor(Math.random() * 9000 + 1000);
        
        sampleData.push(`${transactionId},${amount},${merchant},${location},${timestamp.toISOString()},${cardNumber}`);
    }
    
    return sampleData.join('\n');
}

/**
 * Use sample data for analysis
 */
function useSampleData() {
    const sampleCSV = generateSampleData();
    const blob = new Blob([sampleCSV], { type: 'text/csv' });
    const file = new File([blob], 'sample_transactions.csv', { type: 'text/csv' });
    
    handleFileSelection(file);
}

// =====================================================
// FRAUD ANALYSIS FUNCTIONALITY
// =====================================================

/**
 * Analyze transactions for fraud
 */
async function analyzeTransactions() {
    if (!uploadedFile) {
        alert('Please upload a CSV file first');
        return;
    }
    
    // Hide upload card and show progress
    const uploadCard = document.querySelector('.card');
    const progressSection = document.getElementById('progressSection');
    
    if (uploadCard && progressSection) {
        uploadCard.classList.add('d-none');
        progressSection.classList.remove('d-none');
    }
    
    // Read file content
    const reader = new FileReader();
    reader.onload = async function(e) {
        const content = e.target.result;
        csvData = parseCSV(content);
        
        // Simulate analysis process
        await performAnalysis(csvData);
    };
    reader.readAsText(uploadedFile);
}

/**
 * Perform fraud analysis on transactions
 * @param {Array} transactions - Transaction data
 */
async function performAnalysis(transactions) {
    analysisResults = [];
    const totalCount = transactions.length;
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const processedCount = document.getElementById('processedCount');
    const totalCountEl = document.getElementById('totalCount');
    
    if (totalCountEl) totalCountEl.textContent = totalCount;
    
    const stages = [
        'Initializing fraud detection model...',
        'Loading transaction data...',
        'Analyzing transaction patterns...',
        'Calculating risk scores...',
        'Finalizing results...'
    ];
    
    // Process each transaction
    for (let i = 0; i < transactions.length; i++) {
        const transaction = transactions[i];
        
        // Update progress
        const progress = ((i + 1) / totalCount) * 100;
        if (progressBar) {
            progressBar.style.width = progress + '%';
            progressBar.textContent = Math.round(progress) + '%';
        }
        
        if (processedCount) processedCount.textContent = i + 1;
        
        // Update stage text
        const stageIndex = Math.floor((i / totalCount) * stages.length);
        if (progressText && stages[stageIndex]) {
            progressText.textContent = stages[stageIndex];
        }
        
        // Calculate risk score (this would call ML model in production)
        const riskScore = calculateRiskScore(transaction);
        const status = determineFraudStatus(riskScore);
        const indicators = status === 'fraud' ? generateFraudIndicators() : [];
        
        analysisResults.push({
            ...transaction,
            riskScore,
            status,
            indicators,
            riskLevel: getRiskLevel(riskScore)
        });
        
        // Simulate processing time
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    // Save results and redirect
    saveResults();
    setTimeout(() => {
        window.location.href = 'results.html';
    }, 1000);
}

/**
 * Save analysis results to memory
 * In production, this would save to a backend/database
 */
function saveResults() {
    // Store in memory (will persist during session)
    window.analysisResults = analysisResults;
    window.analysisTimestamp = new Date().toISOString();
}

// =====================================================
// RESULTS PAGE FUNCTIONALITY
// =====================================================

/**
 * Initialize results page
 */
function initResultsPage() {
    // Load results from memory
    const results = window.analysisResults;
    
    if (!results || results.length === 0) {
        // No results found, redirect to upload page
        window.location.href = 'upload.html';
        return;
    }
    
    displayResults(results);
}

/**
 * Display analysis results
 * @param {Array} results - Analysis results
 */
function displayResults(results) {
    // Update timestamp
    const dateTime = document.getElementById('dateTime');
    if (dateTime) {
        dateTime.textContent = formatDateTime(window.analysisTimestamp || new Date());
    }
    
    // Calculate statistics
    const totalTransactions = results.length;
    const fraudCount = results.filter(r => r.status === 'fraud').length;
    const legitimateCount = results.filter(r => r.status === 'legitimate' || r.status === 'warning').length;
    const fraudRate = ((fraudCount / totalTransactions) * 100).toFixed(1);
    
    // Update summary cards
    document.getElementById('totalTransactions').textContent = totalTransactions;
    document.getElementById('legitimateCount').textContent = legitimateCount;
    document.getElementById('fraudCount').textContent = fraudCount;
    document.getElementById('fraudRate').textContent = fraudRate + '%';
    
    // Display status alert
    displayStatusAlert(fraudCount, totalTransactions);
    
    // Populate results table
    populateResultsTable(results);
}

/**
 * Display overall status alert
 * @param {number} fraudCount - Number of fraud transactions
 * @param {number} totalCount - Total transactions
 */
function displayStatusAlert(fraudCount, totalCount) {
    const statusAlert = document.getElementById('statusAlert');
    const statusIcon = document.getElementById('statusIcon');
    const statusTitle = document.getElementById('statusTitle');
    const statusMessage = document.getElementById('statusMessage');
    
    if (!statusAlert) return;
    
    statusAlert.classList.remove('d-none');
    
    if (fraudCount === 0) {
        statusAlert.className = 'alert alert-success d-none';
        statusAlert.classList.remove('d-none');
        statusIcon.className = 'bi bi-check-circle-fill fs-2 me-3';
        statusTitle.textContent = 'No Fraud Detected';
        statusMessage.textContent = `All ${totalCount} transactions appear to be legitimate. No suspicious activity detected.`;
    } else {
        statusAlert.className = 'alert alert-danger d-none';
        statusAlert.classList.remove('d-none');
        statusIcon.className = 'bi bi-exclamation-triangle-fill fs-2 me-3';
        statusTitle.textContent = 'Fraud Detected';
        statusMessage.textContent = `${fraudCount} potentially fraudulent transaction(s) detected out of ${totalCount} total transactions. Please review flagged transactions immediately.`;
    }
}

/**
 * Populate results table with transaction data
 * @param {Array} results - Analysis results
 */
function populateResultsTable(results) {
    const tableBody = document.getElementById('resultsTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    results.forEach((transaction, index) => {
        const row = document.createElement('tr');
        row.setAttribute('data-status', transaction.status);
        
        const statusClass = transaction.status === 'fraud' ? 'status-fraud' : 
                           transaction.status === 'warning' ? 'status-warning' : 
                           'status-legitimate';
        
        const riskClass = transaction.riskScore >= 70 ? 'risk-high' :
                         transaction.riskScore >= 50 ? 'risk-medium' :
                         'risk-low';
        
        row.innerHTML = `
            <td class="px-4">${transaction.transaction_id || 'N/A'}</td>
            <td>${formatCurrency(parseFloat(transaction.amount) || 0)}</td>
            <td>${transaction.merchant || 'N/A'}</td>
            <td>${transaction.location || 'N/A'}</td>
            <td>${formatDateTime(transaction.timestamp)}</td>
            <td class="${riskClass}">
                <strong>${transaction.riskScore}%</strong>
                <small class="d-block">${transaction.riskLevel}</small>
            </td>
            <td>
                <span class="badge ${statusClass}">
                    ${transaction.status === 'fraud' ? 'Fraud' : transaction.status === 'warning' ? 'Warning' : 'Legitimate'}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewTransactionDetails(${index})">
                    <i class="bi bi-eye"></i>
                </button>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
}

/**
 * Filter results based on status
 * @param {string} filter - Filter type ('all', 'fraud', 'legitimate')
 */
function filterResults(filter) {
    currentFilter = filter;
    const rows = document.querySelectorAll('#resultsTableBody tr');
    const noResults = document.getElementById('noResults');
    let visibleCount = 0;
    
    rows.forEach(row => {
        const status = row.getAttribute('data-status');
        
        if (filter === 'all') {
            row.style.display = '';
            visibleCount++;
        } else if (filter === 'fraud' && status === 'fraud') {
            row.style.display = '';
            visibleCount++;
        } else if (filter === 'legitimate' && (status === 'legitimate' || status === 'warning')) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });
    
    // Show/hide no results message
    if (noResults) {
        if (visibleCount === 0) {
            noResults.classList.remove('d-none');
        } else {
            noResults.classList.add('d-none');
        }
    }
}

/**
 * View detailed transaction information
 * @param {number} index - Transaction index
 */
function viewTransactionDetails(index) {
    const results = window.analysisResults;
    if (!results || !results[index]) return;
    
    const transaction = results[index];
    
    // Populate modal with transaction details
    document.getElementById('modalTransactionId').textContent = transaction.transaction_id || 'N/A';
    document.getElementById('modalAmount').textContent = formatCurrency(parseFloat(transaction.amount) || 0);
    document.getElementById('modalMerchant').textContent = transaction.merchant || 'N/A';
    document.getElementById('modalCard').textContent = transaction.card_number || 'N/A';
    document.getElementById('modalLocation').textContent = transaction.location || 'N/A';
    document.getElementById('modalTimestamp').textContent = formatDateTime(transaction.timestamp);
    
    // Update risk score
    const modalRiskScore = document.getElementById('modalRiskScore');
    const modalRiskBar = document.getElementById('modalRiskBar');
    
    modalRiskScore.textContent = transaction.riskScore + '%';
    modalRiskBar.style.width = transaction.riskScore + '%';
    modalRiskBar.className = 'progress-bar';
    
    if (transaction.riskScore >= 70) {
        modalRiskBar.classList.add('bg-danger');
    } else if (transaction.riskScore >= 50) {
        modalRiskBar.classList.add('bg-warning');
    } else {
        modalRiskBar.classList.add('bg-success');
    }
    
    // Update status
    const modalStatus = document.getElementById('modalStatus');
    const statusClass = transaction.status === 'fraud' ? 'badge-danger' : 
                       transaction.status === 'warning' ? 'badge-warning' : 
                       'badge-success';
    modalStatus.className = 'badge ' + statusClass;
    modalStatus.textContent = transaction.status === 'fraud' ? 'Fraud Detected' : 
                             transaction.status === 'warning' ? 'Warning' : 
                             'Legitimate';
    
    // Update fraud indicators
    const modalIndicators = document.getElementById('modalIndicators');
    modalIndicators.innerHTML = '';
    
    if (transaction.indicators && transaction.indicators.length > 0) {
        transaction.indicators.forEach(indicator => {
            const li = document.createElement('li');
            li.className = 'text-danger';
            li.innerHTML = `<i class="bi bi-exclamation-circle me-2"></i>${indicator}`;
            modalIndicators.appendChild(li);
        });
    } else {
        modalIndicators.innerHTML = '<li class="text-success"><i class="bi bi-check-circle me-2"></i>No fraud indicators detected</li>';
    }
    
    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('transactionModal'));
    modal.show();
}

/**
 * Export results to CSV or PDF
 * @param {string} format - Export format ('csv' or 'pdf')
 */
function exportResults(format) {
    const results = window.analysisResults;
    if (!results || results.length === 0) {
        alert('No results to export');
        return;
    }
    
    if (format === 'csv') {
        exportToCSV(results);
    } else if (format === 'pdf') {
        alert('PDF export functionality would be implemented with a PDF library in production.\nFor now, please use the browser\'s print function (Ctrl+P) to save as PDF.');
        window.print();
    }
}

/**
 * Export results to CSV file
 * @param {Array} results - Analysis results
 */
function exportToCSV(results) {
    const headers = ['Transaction ID', 'Amount', 'Merchant', 'Location', 'Timestamp', 'Card Number', 'Risk Score', 'Status'];
    const csvContent = [headers.join(',')];
    
    results.forEach(transaction => {
        const row = [
            transaction.transaction_id || '',
            transaction.amount || '',
            transaction.merchant || '',
            transaction.location || '',
            transaction.timestamp || '',
            transaction.card_number || '',
            transaction.riskScore || '',
            transaction.status || ''
        ];
        csvContent.push(row.join(','));
    });
    
    // Create and download file
    const blob = new Blob([csvContent.join('\n')], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `fraud_analysis_results_${new Date().getTime()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// =====================================================
// PAGE INITIALIZATION
// =====================================================

/**
 * Initialize application based on current page
 */
document.addEventListener('DOMContentLoaded', function() {
    const currentPage = window.location.pathname.split('/').pop();
    
    // Initialize based on current page
    if (currentPage === 'upload.html' || currentPage === '') {
        initFileUpload();
    } else if (currentPage === 'results.html') {
        initResultsPage();
    }
    
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Make functions globally accessible
window.clearFile = clearFile;
window.useSampleData = useSampleData;
window.analyzeTransactions = analyzeTransactions;
window.filterResults = filterResults;
window.viewTransactionDetails = viewTransactionDetails;
window.exportResults = exportResults;