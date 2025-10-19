MCA Insights Engine  

Overview  
MCA Insights Engine is a comprehensive Python application that processes, analyzes, and provides insights into Indian company data from the Ministry of Corporate Affairs (MCA). The system consolidates state-wise company data, detects changes, enriches information, and provides interactive dashboards with AI-powered features.  

Features  
• Data Integration: Merge and clean state-wise MCA data  
• Change Detection: Track daily company changes and updates  
• Data Enrichment: Enhance company data with external sources  
• Interactive Dashboard: Web-based data exploration and visualization  
• REST API: Programmatic access to company data  
• AI Chatbot: Natural language query interface  
• AI Summary Generator: Automated report generation  

Installation  

Prerequisites  
• Python 3.8 or higher  
• pip package manager  

Steps  
1. Clone the repository  
   git clone <repository-url>  
   cd mca_insights_engine

2. Install required dependencies  
   pip install -r requirements.txt

3. Prepare your data files  
   Place companies.csv, directors.csv, and charges.csv in the data/raw/ directory  

Quick Start  

Starting the Application  
Run the main launcher:  
   python run_dashboard.py

This will present you with the following options:  

🎯 MCA Insights Engine - Interactive Features  
==================================================  
1. 📊 Dashboard (Streamlit) - http://localhost:8501  
2. 🌐 REST API (Flask) - http://localhost:5000  
3. 🤖 Chatbot (Streamlit) - http://localhost:8502  
4. 📈 AI Summary Generator - http://localhost:8503  
5. 🚀 Start ALL Services  

Select option (1-5):  

Access Points  
• Main Dashboard: http://localhost:8501  
• REST API: http://localhost:5000  
• AI Chatbot: http://localhost:8502  
• AI Summary Generator: http://localhost:8503  

Project Structure  
mca_insights_engine/  
├── run_dashboard.py              → Main application launcher  
├── ai/                           → AI components (chatbot, summarization)  
├── dashboard/                    → Web dashboard and API  
├── data/                         → Data storage (raw, processed, outputs)  
├── utils/                        → Configuration and utilities  
├── src/                          → Core business logic  
└── logs/                         → Application logs  

API Documentation  

REST Endpoints  
GET /api/companies             → Retrieve all companies  
GET /api/company/<cin>         → Get company by CIN  
GET /api/search?q=<name>       → Search companies by name  
GET /api/companies?state=<s>   → Filter by state  
GET /api/companies?status=<s>  → Filter by company status  

Example API Usage  
curl http://localhost:5000/api/company/U72900MH2000PTC124845  
curl "http://localhost:5000/api/search?q=Tech Solutions"  
curl http://localhost:5000/api/states  

AI Features  

Chatbot Examples  
• "Show new incorporations in Maharashtra"  
• "List manufacturing companies with high capital"  
• "How many companies were struck off last month?"  
• "Show company trends by state"  

Summary Generation  
• Daily change reports  
• Key metrics extraction  
• Trend analysis summaries  
• Exportable report formats  

Configuration  
Edit utils/config.py to customize:  
• Data source paths  
• Analysis parameters  
• Visualization settings  
• API endpoints  

Troubleshooting  

Common Issues  

Port already in use:  
sudo lsof -t -i tcp:5000 | xargs kill -9  

Missing dependencies:  
pip install -r requirements.txt  

Data file errors:  
• Ensure CSV files are in data/raw/ directory  
• Check file names match expected patterns  
• Verify CSV format and encoding  

Module import errors:  
• Run commands from project root directory  
• Check Python path and environment  

Logs  
Check the logs/ directory for detailed error information and application logs.  

Support  
For issues and questions:  
• Check the logs in logs/ directory  
• Verify data files are in correct format  
• Ensure all dependencies are installed  
• Run from the project root directory  

Conclusion  
MCA Insights Engine provides a unified, AI-driven approach to understanding and analyzing Indian company data. By combining data processing, visualization, and intelligent insights, it simplifies corporate data exploration and reporting. The system’s modular design ensures scalability, extensibility, and ease of integration with future enhancements and datasets.
