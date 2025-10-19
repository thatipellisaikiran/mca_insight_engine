🧩 MCA Insights Engine
Overview

MCA Insights Engine is a comprehensive Python application that processes, analyzes, and provides insights into Indian company data from the Ministry of Corporate Affairs (MCA).
It consolidates state-wise company data, detects changes, enriches information, and provides interactive dashboards with AI-powered insights.

🚀 Features
🗂️ Data Integration

Merge and clean company datasets

Extract state-wise and status-wise company information

Automate data updates from MCA sources

🧠 AI Features

NLP-based company insights

Chatbot-style question answering

Intelligent summary generation and key metric extraction

⚙️ API Endpoints
GET /api/companies?state=--     → Filter by state
GET /api/companies?status=--    → Filter by company status

🧪 Example API Usage
curl "http://localhost:5000/api/company/U72900MH2000PTC124845"
curl "http://localhost:5000/api/search?q=Tech Solutions"
curl "http://localhost:5000/api/states"

💬 Chatbot Examples

"Show new incorporations in Maharashtra"

"List manufacturing companies with high capital"

"How many companies were struck off last month?"

"Show company trends by state"

📊 Summary Generation

Daily change reports

Key metrics extraction

Trend analysis summaries

Exportable report formats (CSV, PDF, etc.)

🧰 Tech Stack

Python

Flask / FastAPI

Pandas & NumPy

LangChain / LLM APIs (for AI insights)

Plotly / Streamlit (for dashboards)

📁 Project Structure
mca_insight_engine/
│
├── data/                     # Source and processed datasets
├── api/                      # API and routing scripts
├── analytics/                # Insight and summary generation
├── chatbot/                  # AI and chatbot logic
├── utils/                    # Helper functions
├── README.md                 # Project documentation
└── requirements.txt          # Dependencies

🏁 How to Run
# Clone repository
git clone https://github.com/<your-username>/mca_insight_engine.git

# Navigate to folder
cd mca_insight_engine

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

📈 Conclusion

The MCA Insights Engine serves as an intelligent analysis platform for Indian company data — integrating datasets, detecting patterns, and delivering insights through AI-driven automation and analytics.
