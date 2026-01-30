import http.server
import socketserver
import urllib.parse
import requests
import re
import time
import os
from datetime import datetime

PORT = int(os.environ.get('PORT', 8080))

class MetarHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        print(f"Request: {self.path}")
        if self.path == '/':
            self.home_page()
        elif self.path.startswith('/download?'):
            self.process_download_request()
        elif self.path.startswith('/file/'):
            self.send_file()
        elif self.path.startswith('/batch?'):
            self.process_batch_request()
        else:
            self.send_error(404, f"Not found: {self.path}")

    def home_page(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>METAR/TAF Smart Downloader | AJAY</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: #333;
                }
                
                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                }
                
                .glass-card {
                    background: rgba(255, 255, 255, 0.97);
                    backdrop-filter: blur(20px);
                    border-radius: 24px;
                    padding: 50px;
                    box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    margin-bottom: 30px;
                }
                
                .header {
                    text-align: center;
                    margin-bottom: 50px;
                    padding-bottom: 30px;
                    border-bottom: 2px solid rgba(102, 126, 234, 0.1);
                }
                
                .header h1 {
                    font-size: 3.5rem;
                    background: linear-gradient(90deg, #667eea, #764ba2);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 15px;
                    font-weight: 800;
                    letter-spacing: -0.5px;
                }
                
                .header p {
                    color: #666;
                    font-size: 1.3rem;
                    max-width: 800px;
                    margin: 0 auto;
                    line-height: 1.6;
                }
                
                .main-content {
                    display: grid;
                    grid-template-columns: 1fr 1.2fr;
                    gap: 50px;
                    margin-bottom: 40px;
                }
                
                .left-panel {
                    display: flex;
                    flex-direction: column;
                    gap: 40px;
                }
                
                .right-panel {
                    background: rgba(248, 249, 250, 0.8);
                    border-radius: 20px;
                    padding: 35px;
                    border: 1px solid rgba(224, 224, 224, 0.5);
                }
                
                .form-section {
                    background: white;
                    padding: 35px;
                    border-radius: 20px;
                    border: 1px solid #e0e0e0;
                    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
                }
                
                .section-title {
                    display: flex;
                    align-items: center;
                    margin-bottom: 25px;
                    color: #333;
                    font-size: 1.4rem;
                    font-weight: 700;
                }
                
                .section-title .icon {
                    margin-right: 15px;
                    font-size: 1.8rem;
                }
                
                .input-group {
                    margin-bottom: 30px;
                }
                
                .input-label {
                    display: block;
                    margin-bottom: 12px;
                    color: #555;
                    font-weight: 600;
                    font-size: 1.1rem;
                }
                
                .input-field {
                    width: 100%;
                    padding: 18px 20px;
                    border: 2px solid #e0e0e0;
                    border-radius: 14px;
                    font-size: 1.1rem;
                    transition: all 0.3s ease;
                    background: white;
                    font-family: inherit;
                }
                
                .input-field:focus {
                    border-color: #667eea;
                    outline: none;
                    box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.15);
                    transform: translateY(-1px);
                }
                
                .radio-group {
                    display: flex;
                    gap: 20px;
                    margin: 20px 0;
                }
                
                .radio-option {
                    flex: 1;
                }
                
                .radio-input {
                    display: none;
                }
                
                .radio-label {
                    display: block;
                    padding: 25px;
                    background: #f8f9fa;
                    border: 2px solid #e0e0e0;
                    border-radius: 14px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    font-weight: 600;
                    text-align: center;
                    font-size: 1.1rem;
                }
                
                .radio-input:checked + .radio-label {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    border-color: #667eea;
                    transform: translateY(-3px);
                    box-shadow: 0 12px 25px rgba(102, 126, 234, 0.25);
                }
                
                .report-type-group {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin: 25px 0;
                }
                
                .report-type-card {
                    background: white;
                    padding: 30px;
                    border-radius: 18px;
                    border: 2px solid #e0e0e0;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }
                
                .report-type-card:hover {
                    border-color: #667eea;
                    transform: translateY(-3px);
                    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
                }
                
                .report-type-card.selected {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                    border-color: #667eea;
                    transform: translateY(-3px);
                    box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
                }
                
                .report-type-icon {
                    font-size: 3rem;
                    margin-bottom: 15px;
                }
                
                .report-type-name {
                    font-size: 1.4rem;
                    font-weight: 700;
                    margin-bottom: 8px;
                }
                
                .report-type-desc {
                    font-size: 0.95rem;
                    opacity: 0.9;
                    line-height: 1.4;
                }
                
                .quick-stations {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    margin: 30px 0;
                }
                
                .station-card {
                    background: white;
                    padding: 25px;
                    border-radius: 16px;
                    border: 2px solid #e0e0e0;
                    text-align: center;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                
                .station-card:hover {
                    border-color: #667eea;
                    transform: translateY(-3px);
                    box-shadow: 0 12px 25px rgba(0, 0, 0, 0.08);
                }
                
                .station-code {
                    font-size: 2.2rem;
                    font-weight: 800;
                    color: #667eea;
                    margin-bottom: 8px;
                    letter-spacing: 1px;
                }
                
                .station-name {
                    color: #666;
                    font-size: 1rem;
                    font-weight: 500;
                }
                
                .highlight {
                    background: linear-gradient(135deg, #fff9e6, #fff3cd);
                    border: 2px solid #ffc107;
                    transform: translateY(-2px);
                    box-shadow: 0 10px 20px rgba(255, 193, 7, 0.15);
                }
                
                .action-section {
                    margin-top: 40px;
                }
                
                .button-group {
                    display: flex;
                    gap: 25px;
                    margin-top: 40px;
                }
                
                .btn {
                    flex: 1;
                    padding: 25px;
                    border: none;
                    border-radius: 16px;
                    font-size: 1.3rem;
                    font-weight: 700;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 15px;
                    letter-spacing: 0.5px;
                }
                
                .btn-primary {
                    background: linear-gradient(135deg, #667eea, #764ba2);
                    color: white;
                }
                
                .btn-primary:hover {
                    transform: translateY(-4px);
                    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.4);
                }
                
                .btn-secondary {
                    background: #f8f9fa;
                    color: #555;
                    border: 2px solid #e0e0e0;
                }
                
                .btn-secondary:hover {
                    background: #e9ecef;
                    transform: translateY(-3px);
                    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
                }
                
                .info-panel {
                    background: white;
                    border-radius: 20px;
                    padding: 35px;
                    border: 1px solid #e0e0e0;
                    margin-bottom: 30px;
                }
                
                .info-title {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #333;
                    margin-bottom: 25px;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }
                
                .info-content {
                    color: #666;
                    line-height: 1.7;
                    font-size: 1.05rem;
                }
                
                .info-content ul {
                    margin: 20px 0;
                    padding-left: 25px;
                }
                
                .info-content li {
                    margin-bottom: 12px;
                }
                
                .sample-output {
                    background: #f8f9fa;
                    border-radius: 15px;
                    padding: 25px;
                    margin-top: 25px;
                    border: 1px solid #e0e0e0;
                }
                
                .sample-title {
                    font-weight: 600;
                    color: #555;
                    margin-bottom: 15px;
                    font-size: 1.1rem;
                }
                
                .sample-code {
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.95rem;
                    line-height: 1.5;
                    overflow-x: auto;
                    border: 1px solid #e0e0e0;
                }
                
                .status-bar {
                    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                    padding: 30px;
                    border-radius: 20px;
                    text-align: center;
                    border: 1px solid rgba(224, 224, 224, 0.5);
                    margin-top: 40px;
                }
                
                .status-bar p {
                    color: #666;
                    font-size: 1.1rem;
                    line-height: 1.6;
                }
                
                .loading {
                    display: none;
                    text-align: center;
                    padding: 60px;
                    background: white;
                    border-radius: 20px;
                    margin: 40px 0;
                    border: 1px solid #e0e0e0;
                }
                
                .spinner {
                    width: 70px;
                    height: 70px;
                    border: 6px solid #f3f3f3;
                    border-top: 6px solid #667eea;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 30px;
                }
                
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                .footer {
                    text-align: center;
                    color: rgba(255, 255, 255, 0.8);
                    margin-top: 40px;
                    font-size: 0.95rem;
                }
                
                /* Responsive adjustments */
                @media (max-width: 1200px) {
                    .main-content {
                        grid-template-columns: 1fr;
                        gap: 40px;
                    }
                    
                    .header h1 {
                        font-size: 3rem;
                    }
                }
                
                @media (max-width: 768px) {
                    .glass-card {
                        padding: 30px;
                    }
                    
                    .header h1 {
                        font-size: 2.5rem;
                    }
                    
                    .button-group {
                        flex-direction: column;
                    }
                    
                    .report-type-group {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="glass-card">
                    <div class="header">
                        <h1>🌤️ METAR/TAF Downloader</h1>
                        <p>Professional Aviation Weather Data Download Tool | Developed by AJAY YADAV (IMD GOA)</p>
                    </div>
                    
                    <div class="main-content">
                        <div class="left-panel">
                            <!-- Report Type Selection -->
                            <div class="form-section">
                                <div class="section-title">
                                    <span class="icon">📋</span>
                                    <span>Report Type Selection</span>
                                </div>
                                <div class="report-type-group">
                                    <div class="report-type-card selected" onclick="selectReportType('METAR')" id="metarCard">
                                        <div class="report-type-icon">🌤️</div>
                                        <div class="report-type-name">METAR</div>
                                        <div class="report-type-desc">Aviation Routine Weather Report</div>
                                    </div>
                                    <div class="report-type-card" onclick="selectReportType('TAF')" id="tafCard">
                                        <div class="report-type-icon">📡</div>
                                        <div class="report-type-name">TAF</div>
                                        <div class="report-type-desc">Terminal Aerodrome Forecast</div>
                                    </div>
                                </div>
                                <input type="hidden" id="reportType" name="reportType" value="METAR">
                            </div>
                            
                            <!-- Station Information -->
                            <div class="form-section">
                                <div class="section-title">
                                    <span class="icon">📍</span>
                                    <span>Station Configuration</span>
                                </div>
                                <div class="input-group">
                                    <label class="input-label">ICAO Station Code (4 Letters)</label>
                                    <input type="text" class="input-field" id="station" name="station" value="VOGA" 
                                           maxlength="4" required pattern="[A-Z]{4}" 
                                           placeholder="Enter 4-letter ICAO code (e.g., VOGA)">
                                </div>
                                <div class="quick-stations">
                                    <div class="station-card highlight" onclick="setStation('VOGA')">
                                        <div class="station-code">VOGA</div>
                                        <div class="station-name">GOA International (MOPA)</div>
                                    </div>
                                    <div class="station-card" onclick="setStation('VOMM')">
                                        <div class="station-code">VOMM</div>
                                        <div class="station-name">Chennai International</div>
                                    </div>
                                    <div class="station-card" onclick="setStation('VABB')">
                                        <div class="station-code">VABB</div>
                                        <div class="station-name">Mumbai International</div>
                                    </div>
                                    <div class="station-card" onclick="setStation('VIDP')">
                                        <div class="station-code">VIDP</div>
                                        <div class="station-name">Delhi International</div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Time Period -->
                            <div class="form-section">
                                <div class="section-title">
                                    <span class="icon">📅</span>
                                    <span>Time Period Selection</span>
                                </div>
                                <div class="input-group">
                                    <label class="input-label">Year</label>
                                    <input type="number" class="input-field" id="year" name="year" 
                                           value="2024" min="2000" max="2026" required>
                                </div>
                                <div class="radio-group">
                                    <div class="radio-option">
                                        <input type="radio" id="single" name="mode" value="single" checked class="radio-input">
                                        <label for="single" class="radio-label">📁 Single Month Download</label>
                                    </div>
                                    <div class="radio-option">
                                        <input type="radio" id="all" name="mode" value="all" class="radio-input">
                                        <label for="all" class="radio-label">📦 All 12 Months (Batch)</label>
                                    </div>
                                </div>
                                <div id="monthSelection">
                                    <div class="input-group">
                                        <label class="input-label">Select Month</label>
                                        <select class="input-field" id="month" name="month">
                                            <option value="01">January</option>
                                            <option value="02">February</option>
                                            <option value="03">March</option>
                                            <option value="04">April</option>
                                            <option value="05">May</option>
                                            <option value="06">June</option>
                                            <option value="07">July</option>
                                            <option value="08">August</option>
                                            <option value="09">September</option>
                                            <option value="10">October</option>
                                            <option value="11">November</option>
                                            <option value="12">December</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="right-panel">
                            <!-- Information Panel -->
                            <div class="info-panel">
                                <div class="info-title">
                                    <span>ℹ️</span>
                                    <span>Application Information</span>
                                </div>
                                <div class="info-content">
                                    <p>This tool allows you to download METAR and TAF weather reports from OGIMET database with automatic cleaning and formatting.</p>
                                    
                                    <strong>Key Features:</strong>
                                    <ul>
                                        <li><strong>Dual Report Type:</strong> Download both METAR and TAF reports</li>
                                        <li><strong>Intelligent Cleaning:</strong> Automatic timestamp removal and formatting</li>
                                        <li><strong>Batch Processing:</strong> Download all 12 months at once</li>
                                        <li><strong>Quick Stations:</strong> One-click access to major Indian airports</li>
                                        <li><strong>Professional Output:</strong> Clean, formatted text files ready for analysis</li>
                                    </ul>
                                    
                                    <div class="sample-output">
                                        <div class="sample-title">Sample Output Format:</div>
                                        <div class="sample-code" id="sampleOutput">
                                            <!-- Sample will be populated by JavaScript -->
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Action Buttons -->
                            <div class="action-section">
                                <div class="button-group">
                                    <button type="button" class="btn btn-primary" onclick="startDownload()">
                                        <span>🚀</span>
                                        <span>START DOWNLOAD</span>
                                    </button>
                                    <button type="button" class="btn btn-secondary" onclick="resetForm()">
                                        <span>↻</span>
                                        <span>RESET FORM</span>
                                    </button>
                                </div>
                            </div>
                            
                            <!-- Loading Section -->
                            <div id="loading" class="loading">
                                <div class="spinner"></div>
                                <h3>Processing Your Request...</h3>
                                <p id="statusText">Downloading weather data. Please wait while we process your request.</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Status Bar -->
                    <div class="status-bar">
                        <p>
                            <strong>📊 Processing Information:</strong> Downloads may take 30-60 seconds depending on data volume.<br>
                            <strong>👨‍💻 Developer:</strong> AJAY YADAV (IMD GOA)<br>
                            <strong>📧 Contact:</strong> ajaypahe02@gmail.com
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p>METAR/TAF Downloader v2.0 | Designed for Desktop Use | © 2024</p>
                </div>
            </div>
            
            <script>
                // Initialize sample output based on selected report type
                function updateSampleOutput() {
                    const reportType = document.getElementById('reportType').value;
                    const sampleDiv = document.getElementById('sampleOutput');
                    
                    if (reportType === 'METAR') {
                        sampleDiv.innerHTML = `METAR VOGA 010000Z 15006KT 3500 HZ NSC 28/22 Q1012 NOSIG=<br>
METAR VOGA 010030Z 15005KT 3500 HZ NSC 28/23 Q1012 NOSIG=<br>
METAR VOGA 010100Z 16006KT 3500 HZ NSC 28/22 Q1012 NOSIG=`;
                    } else {
                        sampleDiv.innerHTML = `TAF VOGA 070800Z 0709/0718 09015KT 5000 HZ FU NSC<br>
&nbsp;&nbsp;&nbsp;&nbsp;BECMG 0710/0712 31008KT<br>
&nbsp;&nbsp;&nbsp;&nbsp;BECMG 0714/0716 03007KT 3000 HZ FU=<br>
TAF VOGA 071400Z 0715/0724 03006KT 3000 HZ NSC<br>
&nbsp;&nbsp;&nbsp;&nbsp;BECMG 0721/0723 09006KT=`;
                    }
                }
                
                function selectReportType(type) {
                    document.getElementById('reportType').value = type;
                    
                    // Update UI
                    document.getElementById('metarCard').classList.remove('selected');
                    document.getElementById('tafCard').classList.remove('selected');
                    
                    if (type === 'METAR') {
                        document.getElementById('metarCard').classList.add('selected');
                    } else {
                        document.getElementById('tafCard').classList.add('selected');
                    }
                    
                    // Update station highlights
                    document.querySelectorAll('.station-card').forEach(card => {
                        card.classList.remove('highlight');
                        if (card.querySelector('.station-code').textContent === 'VOGA') {
                            card.classList.add('highlight');
                        }
                    });
                    
                    // Update sample output
                    updateSampleOutput();
                }
                
                function setStation(code) {
                    document.getElementById('station').value = code;
                    
                    // Update highlight
                    document.querySelectorAll('.station-card').forEach(card => {
                        card.classList.remove('highlight');
                    });
                    event.currentTarget.classList.add('highlight');
                }
                
                function updateMonthVisibility() {
                    const singleMode = document.getElementById('single').checked;
                    const monthDiv = document.getElementById('monthSelection');
                    monthDiv.style.display = singleMode ? 'block' : 'none';
                }
                
                function startDownload() {
                    const reportType = document.getElementById('reportType').value;
                    const station = document.getElementById('station').value.toUpperCase();
                    const year = document.getElementById('year').value;
                    const mode = document.querySelector('input[name="mode"]:checked').value;
                    const month = mode === 'single' ? document.getElementById('month').value : '00';
                    
                    if (station.length !== 4) {
                        alert('Please enter a valid 4-letter ICAO station code');
                        return;
                    }
                    
                    // Show loading
                    document.getElementById('loading').style.display = 'block';
                    document.querySelectorAll('.form-section, .action-section').forEach(el => {
                        el.style.opacity = '0.5';
                        el.style.pointerEvents = 'none';
                    });
                    
                    // Update status
                    const statusText = document.getElementById('statusText');
                    const monthNames = {
                        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
                        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
                        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
                    };
                    
                    if (mode === 'all') {
                        statusText.textContent = `Downloading ALL 12 months of ${reportType} data for ${station} station (Year: ${year})...`;
                    } else {
                        const monthName = monthNames[month] || month;
                        statusText.textContent = `Downloading ${reportType} data for ${station} station (${monthName} ${year})...`;
                    }
                    
                    // Redirect to download page
                    if (mode === 'all') {
                        window.location.href = `/batch?station=${station}&year=${year}&type=${reportType}`;
                    } else {
                        window.location.href = `/download?station=${station}&year=${year}&month=${month}&type=${reportType}`;
                    }
                }
                
                function resetForm() {
                    document.getElementById('reportType').value = 'METAR';
                    document.getElementById('station').value = 'VOGA';
                    document.getElementById('year').value = '2024';
                    document.getElementById('single').checked = true;
                    document.getElementById('month').value = '01';
                    
                    // Update UI
                    selectReportType('METAR');
                    updateMonthVisibility();
                    
                    // Reset highlights
                    document.querySelectorAll('.station-card').forEach(card => {
                        card.classList.remove('highlight');
                        if (card.querySelector('.station-code').textContent === 'VOGA') {
                            card.classList.add('highlight');
                        }
                    });
                }
                
                // Initialize
                document.addEventListener('DOMContentLoaded', function() {
                    selectReportType('METAR');
                    updateMonthVisibility();
                    updateSampleOutput();
                    
                    document.querySelectorAll('input[name="mode"]').forEach(radio => {
                        radio.addEventListener('change', updateMonthVisibility);
                    });
                    
                    // Add keyboard shortcuts
                    document.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter' && e.ctrlKey) {
                            startDownload();
                            e.preventDefault();
                        }
                        if (e.key === 'Escape') {
                            resetForm();
                        }
                    });
                });
            </script>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def process_download_request(self):
        """Handle single month download"""
        query = self.path.split('?')[1] if '?' in self.path else ''
        params = urllib.parse.parse_qs(query)
        station = params.get('station', ['VOGA'])[0].upper()
        year = params.get('year', ['2024'])[0]
        month = params.get('month', ['01'])[0]
        report_type = params.get('type', ['METAR'])[0].upper()
        
        print(f"{report_type} download: {station} {year}-{month}")
        
        # Download data
        result = self.download_single_month(station, year, month, report_type)
        
        # Show result
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = self.create_single_result_page(result, station, year, month, report_type)
        self.wfile.write(html.encode('utf-8'))

    def process_batch_request(self):
        """Handle all months download"""
        query = self.path.split('?')[1] if '?' in self.path else ''
        params = urllib.parse.parse_qs(query)
        station = params.get('station', ['VOGA'])[0].upper()
        year = params.get('year', ['2024'])[0]
        report_type = params.get('type', ['METAR'])[0].upper()
        
        print(f"Batch {report_type} download: {station} {year} (all months)")
        
        # Start batch download
        results = self.download_all_months(station, year, report_type)
        
        # Show result
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        html = self.create_batch_result_page(results, station, year, report_type)
        self.wfile.write(html.encode('utf-8'))

    def download_single_month(self, station, year, month, report_type):
        """Download single month with original cleaning"""
        result = {
            'success': False,
            'filename': '',
            'reports': 0,
            'error': '',
            'raw_data': '',
            'clean_data': '',
            'report_type': report_type
        }
        
        try:
            print(f"Downloading {report_type} {station} {year}-{month}...")
            
            # Get data with original cleaning
            clean_data, raw_data = self.get_weather_data(station, year, month, report_type)
            
            if clean_data and len(clean_data.strip()) > 0:
                # Save file with CORRECT naming (original format)
                if report_type == 'METAR':
                    filename = f"METAR{year}{month}.txt"
                else:  # TAF
                    filename = f"TAF{year}{month}.txt"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(clean_data)
                
                # Count reports - count each TAF issuance
                if report_type == 'TAF':
                    # Count TAF lines (lines starting with TAF)
                    lines = clean_data.strip().split('\n')
                    report_count = len([l for l in lines if l.strip() and 'TAF' in l])
                else:
                    lines = clean_data.strip().split('\n')
                    report_count = len([l for l in lines if l.strip()])
                
                result['success'] = True
                result['filename'] = filename
                result['reports'] = report_count
                result['raw_data'] = raw_data
                result['clean_data'] = clean_data
                
                print(f"✅ Saved {report_count} {report_type} reports to {filename}")
            else:
                result['error'] = f"No {report_type} data found"
                print(f"❌ No {report_type} data found")
                
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Exception: {e}")
        
        return result

    def download_all_months(self, station, year, report_type):
        """Download all 12 months in batches"""
        results = []
        file_prefix = 'METAR' if report_type == 'METAR' else 'TAF'
        folder_name = f"{file_prefix}_{station}_{year}"
        os.makedirs(folder_name, exist_ok=True)
        
        month_days = {
            '01': '31', '02': '28', '03': '31', '04': '30',
            '05': '31', '06': '30', '07': '31', '08': '31',
            '09': '30', '10': '31', '11': '30', '12': '31'
        }
        
        month_names = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }
        
        is_leap = int(year) % 4 == 0
        
        # Process in batches of 3 (like original)
        all_months = list(range(1, 13))
        batches = [all_months[i:i+3] for i in range(0, len(all_months), 3)]
        
        for batch_idx, batch in enumerate(batches):
            print(f"\n📦 {report_type} Batch {batch_idx + 1}/{len(batches)}")
            
            for month_num in batch:
                month = f"{month_num:02d}"
                month_name = month_names.get(month, f"Month {month}")
                
                if month == '02' and is_leap:
                    end_day = '29'
                else:
                    end_day = month_days.get(month, '31')
                
                print(f"  {month_name}...", end="", flush=True)
                
                try:
                    clean_data, _ = self.get_weather_data(station, year, month, report_type, end_day)
                    
                    if clean_data and len(clean_data.strip()) > 0:
                        # CORRECT file naming (original format)
                        filename = os.path.join(folder_name, f"{file_prefix}{year}{month}.txt")
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(clean_data)
                        
                        # Count reports
                        if report_type == 'TAF':
                            lines = clean_data.strip().split('\n')
                            report_count = len([l for l in lines if l.strip() and 'TAF' in l])
                        else:
                            lines = clean_data.strip().split('\n')
                            report_count = len([l for l in lines if l.strip()])
                        
                        results.append({
                            'month': month,
                            'month_name': month_name,
                            'filename': filename,
                            'reports': report_count,
                            'success': True
                        })
                        
                        print(f"✅ {report_count} reports")
                    else:
                        results.append({
                            'month': month,
                            'month_name': month_name,
                            'filename': '',
                            'reports': 0,
                            'success': False,
                            'error': f'No {report_type} data'
                        })
                        print("❌")
                        
                except Exception as e:
                    results.append({
                        'month': month,
                        'month_name': month_name,
                        'filename': '',
                        'reports': 0,
                        'success': False,
                        'error': str(e)
                    })
                    print(f"❌ Error: {e}")
                
                time.sleep(1)  # Increased delay
            
            # Delay between batches
            if batch_idx < len(batches) - 1:
                print("  Waiting 3 seconds before next batch...")
                time.sleep(3)
        
        return {
            'station': station,
            'year': year,
            'report_type': report_type,
            'folder': folder_name,
            'results': results,
            'total_success': sum(1 for r in results if r['success']),
            'total_reports': sum(r['reports'] for r in results if r['success'])
        }

    def get_weather_data(self, station, year, month, report_type='METAR', end_day=None):
        """Get METAR or TAF data with original cleaning"""
        if not end_day:
            month_days = {
                '01': '31', '02': '28', '03': '31', '04': '30',
                '05': '31', '06': '30', '07': '31', '08': '31',
                '09': '30', '10': '31', '11': '30', '12': '31'
            }
            
            if month == '02' and int(year) % 4 == 0:
                end_day = '29'
            else:
                end_day = month_days.get(month, '31')
        
        # Create session
        session = requests.Session()
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        try:
            # Get cookies
            session.get('https://www.ogimet.com/display_metars2.php?lang=en', 
                       headers=headers, timeout=10)
            time.sleep(0.5)
        except:
            pass
        
        # Set report type (METAR=SA, TAF=FC)
        tipo = 'FC' if report_type == 'TAF' else 'SA'
        
        # Form data
        form_data = {
            'lugar': station,
            'tipo': tipo,
            'ord': 'DIR',
            'nil': 'NO',
            'fmt': 'txt',
            'ano': year,
            'mes': month,
            'day': '01',
            'hora': '00',
            'min': '00',
            'anof': year,
            'mesf': month,
            'dayf': end_day,
            'horaf': '23',
            'minf': '59',
            'send': 'send',
            'enviar': 'Send',
            'lang': 'en'
        }
        
        post_headers = headers.copy()
        post_headers.update({
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://www.ogimet.com/display_metars2.php?lang=en',
        })
        
        try:
            response = session.post(
                'https://www.ogimet.com/display_metars2.php',
                data=form_data,
                headers=post_headers,
                timeout=60
            )
            
            raw_data = response.text
            
            # Apply cleaning based on report type
            if report_type == 'TAF':
                clean_data = self.clean_taf_text_original(raw_data)
            else:
                clean_data = self.clean_metar_text_original(raw_data)
            
            return clean_data, raw_data
            
        except Exception as e:
            print(f"  Request error: {e}")
            return "", f"Request error: {e}"

    def clean_metar_text_original(self, text):
        """ORIGINAL METAR cleaning - remove timestamps"""
        lines = text.split('\n')
        clean_reports = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                continue
            
            # Skip HTML/comments
            if line.startswith(('<', '#', '<!--')):
                continue
            
            # Only process METAR/SPECI lines
            if 'METAR' in line or 'SPECI' in line:
                # Remove timestamps - KEY FEATURE!
                if re.match(r'^\d{10,14}\s+', line):
                    line = re.sub(r'^\d{10,14}\s+', '', line)
                elif '->' in line:
                    line = line.split('->', 1)[1].strip()
                
                line = ' '.join(line.split())
                
                # Validate it's a proper METAR
                if len(line) > 20 and re.search(r'\d{6}Z', line):
                    clean_reports.append(line)
        
        # Sort by time
        def get_time(report):
            match = re.search(r'(\d{6})Z', report)
            return match.group(1) if match else '000000'
        
        clean_reports.sort(key=get_time)
        
        return '\n'.join(clean_reports)

    def clean_taf_text_original(self, text):
        """ORIGINAL TAF cleaning - remove leading timestamps, keep BECMG/TEMPO"""
        lines = text.split('\n')
        clean_tafs = []
        current_taf = []
        in_taf = False
        
        for line in lines:
            line = line.rstrip()  # Only remove trailing spaces
            
            if not line:
                continue
            
            # Skip HTML/comments
            if line.startswith(('<', '#', '<!--')):
                continue
            
            # Check if this is a TAF line (timestamp followed by TAF)
            if re.match(r'^\d{12}\s+(TAF|TAF\s+AMD|TAF\s+COR)', line):
                # Save previous TAF if exists
                if current_taf:
                    clean_taf = self.process_taf_lines(current_taf)
                    if clean_taf:
                        clean_tafs.append(clean_taf)
                    current_taf = []
                
                # Start new TAF - REMOVE leading timestamp
                clean_line = re.sub(r'^\d{12}\s+', '', line)
                current_taf.append(clean_line)
                in_taf = True
            
            # If we're in a TAF and line continues it
            elif in_taf and (line.startswith(' ') or line.startswith('\t') or 
                            line.startswith('BECMG') or line.startswith('TEMPO') or 
                            line.startswith('FM') or line.startswith('PROB')):
                # Check if this is a continuation of current TAF
                current_taf.append(line.strip())
            
            # If line doesn't continue TAF
            elif in_taf and not (line.startswith(' ') or line.startswith('\t')):
                # End current TAF
                if current_taf:
                    clean_taf = self.process_taf_lines(current_taf)
                    if clean_taf:
                        clean_tafs.append(clean_taf)
                    current_taf = []
                in_taf = False
        
        # Add last TAF if exists
        if current_taf:
            clean_taf = self.process_taf_lines(current_taf)
            if clean_taf:
                clean_tafs.append(clean_taf)
        
        # Sort by time (extract from TAF line)
        def get_taf_time(taf):
            first_line = taf.split('\n')[0]
            match = re.search(r'(\d{6})Z', first_line)
            return match.group(1) if match else '000000'
        
        clean_tafs.sort(key=get_taf_time)
        
        return '\n'.join(clean_tafs)

    def process_taf_lines(self, taf_lines):
        """Process and clean TAF lines"""
        if not taf_lines:
            return ""
        
        # Join lines with single space
        clean_taf = ' '.join(taf_lines)
        
        # Remove extra spaces
        clean_taf = re.sub(r'\s+', ' ', clean_taf)
        
        # Ensure proper format
        if 'TAF' in clean_taf and re.search(r'\d{6}Z', clean_taf):
            return clean_taf
        return ""

    def create_single_result_page(self, result, station, year, month, report_type):
        """Create result page for single month"""
        month_names = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }
        
        month_name = month_names.get(month, month)
        report_type_lower = report_type.lower()
        
        # Desktop-optimized result page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Download Result | METAR/TAF Downloader</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: #333;
                }}
                
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                
                .result-card {{
                    background: rgba(255, 255, 255, 0.97);
                    backdrop-filter: blur(20px);
                    border-radius: 24px;
                    padding: 50px;
                    box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }}
                
                .result-header {{
                    text-align: center;
                    margin-bottom: 50px;
                    padding-bottom: 30px;
                    border-bottom: 2px solid rgba(102, 126, 234, 0.1);
                }}
                
                .result-icon {{
                    font-size: 5rem;
                    margin-bottom: 25px;
                }}
                
                .success .result-icon {{
                    color: #10b981;
                }}
                
                .error .result-icon {{
                    color: #ef4444;
                }}
                
                .result-title {{
                    font-size: 3rem;
                    font-weight: 800;
                    margin-bottom: 15px;
                    color: #333;
                }}
                
                .result-subtitle {{
                    color: #666;
                    font-size: 1.3rem;
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 25px;
                    margin: 50px 0;
                }}
                
                .stat-card {{
                    background: white;
                    padding: 35px;
                    border-radius: 20px;
                    text-align: center;
                    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.08);
                    border: 1px solid #e0e0e0;
                    transition: transform 0.3s ease;
                }}
                
                .stat-card:hover {{
                    transform: translateY(-5px);
                }}
                
                .stat-value {{
                    font-size: 3rem;
                    font-weight: 800;
                    color: #667eea;
                    margin-bottom: 15px;
                }}
                
                .stat-label {{
                    color: #666;
                    font-size: 1.1rem;
                    font-weight: 600;
                }}
                
                .preview-section {{
                    background: #f8f9fa;
                    border-radius: 20px;
                    padding: 40px;
                    margin: 50px 0;
                    border: 1px solid #e0e0e0;
                }}
                
                .preview-title {{
                    font-size: 1.8rem;
                    font-weight: 700;
                    margin-bottom: 25px;
                    color: #333;
                    display: flex;
                    align-items: center;
                    gap: 15px;
                }}
                
                .preview-content {{
                    background: white;
                    padding: 30px;
                    border-radius: 15px;
                    max-height: 500px;
                    overflow-y: auto;
                    font-family: 'Courier New', monospace;
                    font-size: 15px;
                    line-height: 1.6;
                    border: 1px solid #e0e0e0;
                }}
                
                .action-buttons {{
                    display: flex;
                    gap: 30px;
                    margin-top: 50px;
                }}
                
                .action-btn {{
                    flex: 1;
                    padding: 28px;
                    border: none;
                    border-radius: 18px;
                    font-size: 1.4rem;
                    font-weight: 700;
                    cursor: pointer;
                    text-decoration: none;
                    text-align: center;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 18px;
                }}
                
                .download-btn {{
                    background: linear-gradient(135deg, #10b981, #059669);
                    color: white;
                }}
                
                .download-btn:hover {{
                    transform: translateY(-4px);
                    box-shadow: 0 20px 40px rgba(16, 185, 129, 0.4);
                }}
                
                .back-btn {{
                    background: #f8f9fa;
                    color: #555;
                    border: 2px solid #e0e0e0;
                }}
                
                .back-btn:hover {{
                    background: #e9ecef;
                    transform: translateY(-3px);
                    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
                }}
                
                .note-box {{
                    background: linear-gradient(135deg, #fff9e6, #fff3cd);
                    border: 2px solid #ffc107;
                    padding: 25px;
                    border-radius: 15px;
                    margin-top: 30px;
                    color: #856404;
                    font-size: 1.1rem;
                    line-height: 1.6;
                }}
                
                .error-details {{
                    background: #f8d7da;
                    color: #721c24;
                    padding: 30px;
                    border-radius: 15px;
                    margin: 40px 0;
                    border: 1px solid #f5c6cb;
                }}
                
                @media (max-width: 1024px) {{
                    .stats-grid {{
                        grid-template-columns: repeat(2, 1fr);
                    }}
                    
                    .action-buttons {{
                        flex-direction: column;
                    }}
                }}
                
                @media (max-width: 768px) {{
                    .result-card {{
                        padding: 30px;
                    }}
                    
                    .result-title {{
                        font-size: 2.5rem;
                    }}
                    
                    .stats-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="result-card {'success' if result['success'] else 'error'}">
                    <div class="result-header">
                        <div class="result-icon">
                            {'✅' if result['success'] else '❌'}
                        </div>
                        <h1 class="result-title">
                            {'Download Successful!' if result['success'] else 'Download Failed'}
                        </h1>
                        <p class="result-subtitle">
                            {report_type} Report | Station: {station} | Month: {month_name} {year}
                        </p>
                    </div>
        """
        
        if result['success']:
            html += f"""
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">{result['reports']}</div>
                            <div class="stat-label">{report_type} Reports</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{month_name}</div>
                            <div class="stat-label">Month</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{year}</div>
                            <div class="stat-label">Year</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">{report_type}</div>
                            <div class="stat-label">Report Type</div>
                        </div>
                    </div>
                    
                    <div class="preview-section">
                        <div class="preview-title">
                            📄 Cleaned {report_type} File Preview
                        </div>
                        <div class="preview-content">
            """
            
            # Show cleaned content
            if result['clean_data']:
                # Show first 25 lines
                lines = result['clean_data'].split('\n')
                for i, line in enumerate(lines[:25]):
                    html += f"{line}<br>"
                if len(lines) > 25:
                    html += f"<br><em>... and {len(lines) - 25} more lines</em>"
            else:
                html += "Preview not available"
            
            html += f"""
                        </div>
                        <div class="note-box">
                            <strong>📝 Processing Information:</strong><br>
                            {'✓ TAF cleaning: Leading timestamps removed, BECMG/TEMPO preserved' if report_type == 'TAF' else '✓ METAR cleaning: Timestamps removed, only clean METAR/SPECI reports'}<br>
                            <strong>📁 File saved as:</strong> {result['filename']}<br>
                            <strong>🔧 Report type:</strong> {'TAF (tipo=FC)' if report_type == 'TAF' else 'METAR (tipo=SA)'}
                        </div>
                    </div>
                    
                    <div class="action-buttons">
                        <a href="/file/{result['filename']}" class="action-btn download-btn">
                            📥 Download {report_type} File
                        </a>
                        <a href="/" class="action-btn back-btn">
                            ← Back to Downloader
                        </a>
                    </div>
            """
        else:
            html += f"""
                    <div class="error-details">
                        <h3 style="margin-bottom: 20px; font-size: 1.5rem;">❌ Download Error</h3>
                        <p style="font-size: 1.2rem; margin-bottom: 20px;"><strong>Error Details:</strong> {result['error']}</p>
                        
                        <h4 style="margin: 25px 0 15px; font-size: 1.3rem;">Troubleshooting Steps:</h4>
                        <ul style="margin-left: 25px; font-size: 1.1rem;">
                            <li>Verify station code is correct (4 uppercase letters)</li>
                            <li>Check internet connection</li>
                            <li>Try a different station or time period</li>
                            <li>Ensure year is between 2000-2026</li>
                        </ul>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 35px; border-radius: 20px; margin: 40px 0;">
                        <h3 style="margin-bottom: 25px; font-size: 1.5rem;">Quick Test Stations:</h3>
                        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                            <a href="/download?station=VOGA&year=2024&month=01&type={report_type_lower}" 
                               style="background: #667eea; color: white; padding: 22px; border-radius: 15px; text-decoration: none; text-align: center; font-weight: 600; font-size: 1.2rem;">
                                VOGA (Priority Test)
                            </a>
                            <a href="/download?station=VOMM&year=2024&month=01&type={report_type_lower}" 
                               style="background: #e0e0e0; color: #333; padding: 22px; border-radius: 15px; text-decoration: none; text-align: center; font-weight: 600; font-size: 1.2rem;">
                                VOMM Chennai
                            </a>
                            <a href="/download?station=VABB&year=2024&month=01&type={report_type_lower}" 
                               style="background: #e0e0e0; color: #333; padding: 22px; border-radius: 15px; text-decoration: none; text-align: center; font-weight: 600; font-size: 1.2rem;">
                                VABB Mumbai
                            </a>
                            <a href="/download?station=VIDP&year=2024&month=01&type={report_type_lower}" 
                               style="background: #e0e0e0; color: #333; padding: 22px; border-radius: 15px; text-decoration: none; text-align: center; font-weight: 600; font-size: 1.2rem;">
                                VIDP Delhi
                            </a>
                        </div>
                    </div>
                    
                    <div class="action-buttons">
                        <a href="/" class="action-btn back-btn" style="flex: 1;">
                            ← Try Again
                        </a>
                    </div>
            """
        
        html += """
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

    def create_batch_result_page(self, results, station, year, report_type):
        """Create result page for batch download"""
        report_type_lower = report_type.lower()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Batch Download Complete | METAR/TAF Downloader</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 40px 20px;
                    color: #333;
                }}
                
                .container {{
                    max-width: 1400px;
                    margin: 0 auto;
                }}
                
                .result-card {{
                    background: rgba(255, 255, 255, 0.97);
                    backdrop-filter: blur(20px);
                    border-radius: 24px;
                    padding: 50px;
                    box-shadow: 0 25px 80px rgba(0, 0, 0, 0.3);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 50px;
                    padding-bottom: 30px;
                    border-bottom: 2px solid rgba(102, 126, 234, 0.1);
                }}
                
                .header h1 {{
                    font-size: 3.5rem;
                    font-weight: 800;
                    color: #333;
                    margin-bottom: 15px;
                }}
                
                .header p {{
                    color: #666;
                    font-size: 1.4rem;
                }}
                
                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 25px;
                    margin: 50px 0;
                }}
                
                .summary-card {{
                    background: white;
                    padding: 35px;
                    border-radius: 20px;
                    text-align: center;
                    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.08);
                    border: 1px solid #e0e0e0;
                    transition: transform 0.3s ease;
                }}
                
                .summary-card:hover {{
                    transform: translateY(-5px);
                }}
                
                .success-value {{
                    color: #10b981;
                }}
                
                .total-value {{
                    color: #667eea;
                }}
                
                .summary-value {{
                    font-size: 3rem;
                    font-weight: 800;
                    margin-bottom: 15px;
                }}
                
                .summary-label {{
                    color: #666;
                    font-size: 1.1rem;
                    font-weight: 600;
                }}
                
                .month-grid {{
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 20px;
                    margin: 50px 0;
                }}
                
                .month-card {{
                    background: white;
                    padding: 25px;
                    border-radius: 16px;
                    border: 2px solid #e0e0e0;
                    text-align: center;
                    transition: all 0.3s ease;
                }}
                
                .month-card:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
                }}
                
                .month-success {{
                    border-color: #10b981;
                    background: #f0f9f4;
                }}
                
                .month-failed {{
                    border-color: #ef4444;
                    background: #fef2f2;
                }}
                
                .month-name {{
                    font-weight: 700;
                    margin-bottom: 10px;
                    font-size: 1.2rem;
                }}
                
                .month-reports {{
                    font-size: 2rem;
                    color: #667eea;
                    margin-bottom: 10px;
                    font-weight: 800;
                }}
                
                .action-buttons {{
                    display: flex;
                    gap: 30px;
                    margin-top: 50px;
                }}
                
                .action-btn {{
                    flex: 1;
                    padding: 28px;
                    border: none;
                    border-radius: 18px;
                    font-size: 1.4rem;
                    font-weight: 700;
                    cursor: pointer;
                    text-decoration: none;
                    text-align: center;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 18px;
                }}
                
                .download-btn {{
                    background: linear-gradient(135deg, #10b981, #059669);
                    color: white;
                }}
                
                .download-btn:hover {{
                    transform: translateY(-4px);
                    box-shadow: 0 20px 40px rgba(16, 185, 129, 0.4);
                }}
                
                .back-btn {{
                    background: #f8f9fa;
                    color: #555;
                    border: 2px solid #e0e0e0;
                }}
                
                .back-btn:hover {{
                    background: #e9ecef;
                    transform: translateY(-3px);
                    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
                }}
                
                .note-box {{
                    background: linear-gradient(135deg, #fff9e6, #fff3cd);
                    border: 2px solid #ffc107;
                    padding: 25px;
                    border-radius: 15px;
                    margin-top: 40px;
                    color: #856404;
                    font-size: 1.1rem;
                    line-height: 1.6;
                }}
                
                @media (max-width: 1200px) {{
                    .month-grid {{
                        grid-template-columns: repeat(3, 1fr);
                    }}
                }}
                
                @media (max-width: 900px) {{
                    .summary-grid {{
                        grid-template-columns: repeat(2, 1fr);
                    }}
                    
                    .month-grid {{
                        grid-template-columns: repeat(2, 1fr);
                    }}
                    
                    .action-buttons {{
                        flex-direction: column;
                    }}
                }}
                
                @media (max-width: 600px) {{
                    .result-card {{
                        padding: 30px;
                    }}
                    
                    .header h1 {{
                        font-size: 2.5rem;
                    }}
                    
                    .summary-grid {{
                        grid-template-columns: 1fr;
                    }}
                    
                    .month-grid {{
                        grid-template-columns: 1fr;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="result-card">
                    <div class="header">
                        <h1>📦 {report_type} Batch Download Complete</h1>
                        <p>{station} - {year} (All 12 Months)</p>
                    </div>
                    
                    <div class="summary-grid">
                        <div class="summary-card">
                            <div class="summary-value success-value">{results['total_success']}/12</div>
                            <div class="summary-label">Successful Months</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-value total-value">{results['total_reports']:,}</div>
                            <div class="summary-label">Total {report_type} Reports</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-value">{station}</div>
                            <div class="summary-label">Station Code</div>
                        </div>
                        <div class="summary-card">
                            <div class="summary-value">{report_type}</div>
                            <div class="summary-label">Report Type</div>
                        </div>
                    </div>
                    
                    <h3 style="margin-bottom: 30px; font-size: 1.8rem; color: #333;">Monthly Download Results:</h3>
                    <div class="month-grid">
        """
        
        # Add month cards
        for result in results['results']:
            status_class = 'month-success' if result['success'] else 'month-failed'
            html += f"""
                        <div class="month-card {status_class}">
                            <div class="month-name">{result['month_name']}</div>
                            <div class="month-reports">
                                {result['reports'] if result['success'] else '❌'}
                            </div>
                            <div style="font-size: 1rem; color: #666; margin-top: 10px;">
                                {result['month']} | {report_type}
                            </div>
                        </div>
            """
        
        # Different note for METAR vs TAF
        if report_type == 'TAF':
            note_text = "✓ TAF processing: Leading timestamps removed, BECMG/TEMPO preserved"
        else:
            note_text = "✓ METAR processing: Timestamps removed, only clean METAR/SPECI reports"
        
        html += f"""
                    </div>
                    
                    <div class="note-box">
                        <strong>📊 Batch Processing Summary:</strong><br>
                        {note_text}<br>
                        <strong>📁 Folder created:</strong> {results['folder']}<br>
                        <strong>⏱️ Processing:</strong> Downloaded in batches of 3 months<br>
                        <strong>🔧 Report type:</strong> {'TAF (tipo=FC)' if report_type == 'TAF' else 'METAR (tipo=SA)'}
                    </div>
                    
                    <div class="action-buttons">
                        <a href="/file/{results['folder']}" class="action-btn download-btn">
                            📥 Download All Files (ZIP)
                        </a>
                        <a href="/" class="action-btn back-btn">
                            ← New Download
                        </a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

    def send_file(self):
        """Serve file or folder for download"""
        path = self.path[6:]  # Remove '/file/'
        
        if os.path.isdir(path):
            # Create zip of folder
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(path):
                    for file in files:
                        if file.endswith('.txt'):
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(path))
                            zipf.write(file_path, arcname)
            
            zip_buffer.seek(0)
            self.send_response(200)
            self.send_header('Content-type', 'application/zip')
            self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(path)}.zip"')
            self.send_header('Content-Length', str(zip_buffer.getbuffer().nbytes))
            self.end_headers()
            self.wfile.write(zip_buffer.getvalue())
            
        elif os.path.exists(path):
            # Serve single file
            self.send_response(200)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(path)}"')
            
            with open(path, 'rb') as f:
                file_content = f.read()
            
            self.send_header('Content-Length', str(len(file_content)))
            self.end_headers()
            self.wfile.write(file_content)
        else:
            self.send_error(404, "File not found")

# Start server
print("=" * 70)
print("🌤️ METAR/TAF DESKTOP WEB APP")
print("=" * 70)
print(f"Server running on: http://localhost:{PORT}")
print("Features:")
print(" • Desktop-optimized professional UI")
print(" • Dual panel layout with information section")
print(" • METAR and TAF download options")
print(" • VOGA priority station with quick selection")
print(" • Single month & All months (batch) download")
print(" • METAR: Timestamps removed")
print(" • TAF: Leading timestamps removed, BECMG/TEMPO preserved")
print(" • File naming: METARYYYYMM.txt / TAFYYYYMM.txt")
print(" • Batch processing (3 months at a time with delays)")
print(" • Keyboard shortcuts (Ctrl+Enter, Escape)")
print("=" * 70)

try:
    with socketserver.TCPServer(("", PORT), MetarHandler) as httpd:
        httpd.serve_forever()
except KeyboardInterrupt:
    print("\nServer stopped.")
except Exception as e:
    print(f"Error: {e}")
