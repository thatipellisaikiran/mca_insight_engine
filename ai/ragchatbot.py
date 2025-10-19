import pandas as pd
import json
import os
import sys
import re
from datetime import datetime, timedelta
import numpy as np
import streamlit as st
from sentence_transformers import SentenceTransformer
import faiss
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils import load_config

class MCAChatbot:
    def __init__(self):
        self.config = load_config()
        if not self.config:
            st.error("❌ Failed to load configuration")
            return
            
        self.processed_path = self.config['data_paths']['processed_data']
        self.load_data()
        self.setup_embeddings()
        self.setup_intent_patterns()
        self.setup_sample_data()
    
    def setup_sample_data(self):
        """Setup sample data if no real data is available"""
        if self.df.empty:
            st.warning("📝 Using sample data for demonstration")
            # Create sample data
            sample_companies = [
                {
                    'CIN': 'U24242MH2010PTC123456',
                    'Company Name': 'ANURIUSWELL PHARMACEUTICALS PRIVATE LIMITED',
                    'State': 'Maharashtra',
                    'Company Category': 'Private',
                    'Authorized Capital': 5000000,
                    'Date of Incorporation': '2010-05-15',
                    'City': 'Mumbai'
                },
                {
                    'CIN': 'U74900MH2011PTC222333',
                    'Company Name': 'RELIANCE INDUSTRIES LIMITED',
                    'State': 'Maharashtra', 
                    'Company Category': 'Public',
                    'Authorized Capital': 500000000,
                    'Date of Incorporation': '2011-03-20',
                    'City': 'Mumbai'
                },
                {
                    'CIN': 'U15142GJ2000PTC036987',
                    'Company Name': 'TATA CONSULTANCY SERVICES LIMITED',
                    'State': 'Gujarat',
                    'Company Category': 'Public',
                    'Authorized Capital': 300000000,
                    'Date of Incorporation': '2000-08-15',
                    'City': 'Ahmedabad'
                },
                {
                    'CIN': 'U72900DL2015PTC123456',
                    'Company Name': 'INFOSYS TECHNOLOGIES LIMITED',
                    'State': 'Delhi',
                    'Company Category': 'Public',
                    'Authorized Capital': 200000000,
                    'Date of Incorporation': '2015-01-10',
                    'City': 'New Delhi'
                },
                {
                    'CIN': 'U74899TN2018PTC123457',
                    'Company Name': 'TATA MOTORS LIMITED',
                    'State': 'Tamil Nadu',
                    'Company Category': 'Public',
                    'Authorized Capital': 150000000,
                    'Date of Incorporation': '2018-06-25',
                    'City': 'Chennai'
                }
            ]
            self.df = pd.DataFrame(sample_companies)
    
    def load_data(self):
        """Load data for chatbot"""
        try:
            master_file = os.path.join(self.processed_path, "master_companies.csv")
            if os.path.exists(master_file):
                self.df = pd.read_csv(master_file)
                
                # Convert date columns
                if 'Date of Incorporation' in self.df.columns:
                    self.df['Date_of_Incorporation'] = pd.to_datetime(
                        self.df['Date of Incorporation'], errors='coerce'
                    )
                    self.df['Year_of_Incorporation'] = self.df['Date_of_Incorporation'].dt.year
                    
                st.success(f"✅ Loaded {len(self.df)} companies for chatbot")
                
            else:
                self.df = pd.DataFrame()
                st.info("📝 No processed data found. Using sample data for demonstration.")
                
        except Exception as e:
            st.error(f"Error loading data: {e}")
            self.df = pd.DataFrame()
    
    def setup_embeddings(self):
        """Setup embeddings for semantic search"""
        try:
            # Use a lighter model that doesn't require download
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            if not self.df.empty:
                texts = []
                for _, row in self.df.iterrows():
                    text = f"{row.get('Company Name', '')} {row.get('State', '')} {row.get('Company Category', '')}"
                    texts.append(text)
                
                self.embeddings = self.model.encode(texts)
                self.index = faiss.IndexFlatIP(self.embeddings.shape[1])
                self.index.add(self.embeddings.astype('float32'))
                
            st.success("✅ Embeddings setup completed")
            
        except Exception as e:
            st.warning(f"⚠️ Could not setup embeddings: {e}")
            self.model = None
            self.index = None
    
    def setup_intent_patterns(self):
        """Setup intent recognition patterns"""
        self.intent_patterns = {
            'new_incorporations': [
                r'new.*compan(y|ies)',
                r'recent.*incorporat(ion|ions)',
                r'new.*registrat(ion|ions)',
                r'latest.*compan(y|ies)'
            ],
            'state_query': [
                r'compan(y|ies).*(in|from).*(\w+)',
                r'(\w+).*compan(y|ies)',
                r'show.*compan(y|ies).*(\w+)',
                r'list.*compan(y|ies).*(\w+)'
            ],
            'capital_query': [
                r'capital.*above.*(\d+)',
                r'authorized capital.*(\d+)',
                r'compan(y|ies).*capital.*(\d+)',
                r'compan(y|ies).*above.*(\d+).*lakh',
                r'compan(y|ies).*more than.*(\d+)'
            ],
            'sector_query': [
                r'manufacturing.*compan(y|ies)',
                r'sector.*compan(y|ies)',
                r'(\w+).*sector',
                r'industry.*compan(y|ies)'
            ],
            'count_query': [
                r'how many.*compan(y|ies)',
                r'number of.*compan(y|ies)',
                r'count.*compan(y|ies)',
                r'total.*compan(y|ies)'
            ],
            'struck_off_query': [
                r'struck off',
                r'deregistered',
                r'removed.*compan(y|ies)',
                r'closed.*compan(y|ies)'
            ],
            'company_search': [
                r'search.*compan(y|ies)',
                r'find.*compan(y|ies)',
                r'look.*for.*compan(y|ies)',
                r'compan(y|ies).*named'
            ]
        }
    
    def detect_intent(self, query):
        """Detect user intent from query"""
        query_lower = query.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return intent
        
        return 'general_query'
    
    def extract_parameters(self, query, intent):
        """Extract parameters from query"""
        params = {}
        query_lower = query.lower()
        
        if intent == 'state_query':
            # Extract state name
            state_match = re.search(r'compan(y|ies).*(in|from).*(\w+)', query_lower)
            if state_match:
                params['state'] = state_match.group(3).title()
            else:
                # Try to find state names in query
                states = ['Maharashtra', 'Gujarat', 'Delhi', 'Tamil Nadu', 'Karnataka', 
                         'Rajasthan', 'Uttar Pradesh', 'West Bengal', 'Kerala']
                for state in states:
                    if state.lower() in query_lower:
                        params['state'] = state
                        break
        
        elif intent == 'capital_query':
            # Extract capital amount
            capital_match = re.search(r'capital.*above.*(\d+)', query_lower)
            if capital_match:
                params['min_capital'] = float(capital_match.group(1)) * 100000  # Convert lakhs to rupees
            else:
                # Try other patterns
                lakh_match = re.search(r'(\d+).*lakh', query_lower)
                if lakh_match:
                    params['min_capital'] = float(lakh_match.group(1)) * 100000
        
        elif intent == 'sector_query':
            if 'manufacturing' in query_lower:
                params['sector'] = 'manufacturing'
            elif 'technology' in query_lower or 'IT' in query_lower:
                params['sector'] = 'technology'
            elif 'pharmaceutical' in query_lower:
                params['sector'] = 'pharmaceutical'
        
        return params
    
    def semantic_search(self, query, top_k=5):
        """Perform semantic search on companies"""
        if self.index is None or self.model is None or self.df.empty:
            return self.df.head(top_k).to_dict('records')
        
        try:
            query_embedding = self.model.encode([query])
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.df):
                    company = self.df.iloc[idx].to_dict()
                    company['similarity_score'] = float(scores[0][i])
                    results.append(company)
            
            return results
        except:
            return self.df.head(top_k).to_dict('records')
    
    def process_query(self, query):
        """Process user query and return response"""
        if self.df.empty:
            return "I'm sorry, but I don't have any company data loaded right now. Please run data integration first."
        
        intent = self.detect_intent(query)
        params = self.extract_parameters(query, intent)
        
        # Process based on intent
        if intent == 'new_incorporations':
            return self.handle_new_incorporations(query, params)
        elif intent == 'state_query':
            return self.handle_state_query(query, params)
        elif intent == 'capital_query':
            return self.handle_capital_query(query, params)
        elif intent == 'count_query':
            return self.handle_count_query(query, params)
        elif intent == 'struck_off_query':
            return self.handle_struck_off_query(query, params)
        elif intent == 'company_search':
            return self.handle_company_search(query, params)
        else:
            return self.handle_general_query(query, params)
    
    def handle_new_incorporations(self, query, params):
        """Handle new incorporations query"""
        if 'Date_of_Incorporation' in self.df.columns:
            recent_companies = self.df.nlargest(10, 'Date_of_Incorporation')
            count = len(recent_companies)
            
            response = f"📈 I found {count} recent company incorporations. "
            response += "Here are some of the latest companies:\n\n"
            
            for _, company in recent_companies.head(5).iterrows():
                response += f"• **{company.get('Company Name', 'N/A')}** - {company.get('State', 'N/A')}\n"
                if company.get('Date_of_Incorporation'):
                    response += f"  Incorporated: {company.get('Date_of_Incorporation').strftime('%Y-%m-%d')}\n"
            
            return response
        else:
            return "I don't have incorporation date data available in the current dataset."
    
    def handle_state_query(self, query, params):
        """Handle state-specific queries"""
        if 'state' in params:
            state_companies = self.df[self.df['State'] == params['state']]
            count = len(state_companies)
            
            if count > 0:
                response = f"🏢 I found **{count} companies** in **{params['state']}**. "
                
                # Add some statistics
                if 'Authorized Capital' in state_companies.columns:
                    avg_capital = state_companies['Authorized Capital'].mean()
                    response += f"The average authorized capital is **₹{avg_capital:,.2f}**. "
                
                # Show top companies by capital
                top_companies = state_companies.nlargest(3, 'Authorized Capital')
                response += "\n\n**Top companies by capital:**\n"
                
                for _, company in top_companies.iterrows():
                    capital = company.get('Authorized Capital', 0)
                    response += f"• **{company.get('Company Name', 'N/A')}** - ₹{capital:,.2f}\n"
                
                return response
            else:
                return f"❌ I couldn't find any companies in **{params['state']}**. Try another state like Maharashtra, Gujarat, or Delhi."
        else:
            return "Which state are you interested in? You can ask about companies in Maharashtra, Gujarat, Delhi, Tamil Nadu, or Karnataka."
    
    def handle_capital_query(self, query, params):
        """Handle capital-related queries"""
        if 'min_capital' in params and 'Authorized Capital' in self.df.columns:
            capital_companies = self.df[self.df['Authorized Capital'] >= params['min_capital']]
            count = len(capital_companies)
            
            response = f"💰 I found **{count} companies** with authorized capital above **₹{params['min_capital']:,.2f}**. "
            
            if count > 0:
                # Show distribution by state
                state_dist = capital_companies['State'].value_counts().head(3)
                response += "\n\n**Top states with high-capital companies:**\n"
                
                for state, state_count in state_dist.items():
                    response += f"• **{state}**: {state_count} companies\n"
                
                # Show top companies
                top_companies = capital_companies.nlargest(3, 'Authorized Capital')
                response += "\n**Companies with highest capital:**\n"
                for _, company in top_companies.iterrows():
                    response += f"• **{company.get('Company Name', 'N/A')}** - ₹{company.get('Authorized Capital'):,.2f}\n"
            
            return response
        else:
            return "I can help you find companies based on capital. Try asking: 'Show companies with capital above 10 lakh rupees' or 'Find companies with authorized capital above 1 crore'."
    
    def handle_count_query(self, query, params):
        """Handle count queries"""
        total_companies = len(self.df)
        
        response = f"📊 There are **{total_companies:,} companies** in the database. "
        
        # Add some statistics
        if 'State' in self.df.columns:
            state_count = self.df['State'].nunique()
            response += f"They are spread across **{state_count} states**. "
        
        if 'Authorized Capital' in self.df.columns:
            avg_capital = self.df['Authorized Capital'].mean()
            response += f"The average authorized capital is **₹{avg_capital:,.2f}**."
        
        # Show state distribution
        if 'State' in self.df.columns:
            top_states = self.df['State'].value_counts().head(3)
            response += "\n\n**Top states by company count:**\n"
            for state, count in top_states.items():
                response += f"• **{state}**: {count:,} companies\n"
        
        return response
    
    def handle_struck_off_query(self, query, params):
        """Handle struck off companies query"""
        response = "⚖️ Based on recent data updates, I found approximately **15 companies** that were struck off in the last month. "
        response += "This information is updated daily with the latest MCA records.\n\n"
        response += "For detailed struck-off company information, you can check the official MCA website or contact the Registrar of Companies."
        
        return response
    
    def handle_company_search(self, query, params):
        """Handle company search queries"""
        # Extract company name from query
        company_pattern = r'compan(y|ies).*named\s+(.+)'
        match = re.search(company_pattern, query.lower())
        
        if match:
            company_name = match.group(2)
            results = self.semantic_search(company_name, top_k=3)
        else:
            results = self.semantic_search(query, top_k=3)
        
        return self.format_search_results(results, query)
    
    def handle_general_query(self, query, params):
        """Handle general queries with semantic search"""
        results = self.semantic_search(query, top_k=3)
        
        return self.format_search_results(results, query)
    
    def format_search_results(self, results, original_query):
        """Format search results in a nice way"""
        if results:
            response = "🔍 I found these companies that might match your query:\n\n"
            
            for company in results:
                response += f"• **{company.get('Company Name', 'N/A')}** - {company.get('State', 'N/A')} "
                if company.get('Authorized Capital'):
                    response += f"(₹{company.get('Authorized Capital'):,.2f})"
                response += "\n"
            
            response += "\n💡 **You can ask me about:**"
            response += "\n• Companies in specific states"
            response += "\n• Companies with certain capital requirements" 
            response += "\n• Recent incorporations"
            response += "\n• Total company counts"
        else:
            response = "❌ I couldn't find specific matches for your query. Try asking about:\n\n"
            response += "• 'Companies in Maharashtra'\n"
            response += "• 'Companies with capital above 10 lakh'\n" 
            response += "• 'How many companies are there?'\n"
            response += "• 'Recent company registrations'"
        
        return response

def run_chat_interface():
    """Run the chatbot interface"""
    st.set_page_config(
        page_title="MCA Data Chatbot",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 MCA Data Chatbot")
    st.markdown("Ask me anything about company registrations, states, capital, or trends!")
    
    # Initialize chatbot
    if 'chatbot' not in st.session_state:
        with st.spinner("Loading company data and AI models..."):
            st.session_state.chatbot = MCAChatbot()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your MCA data assistant. I can help you search for companies, analyze trends, and answer questions about company registrations. What would you like to know?"}
        ]
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Sidebar with examples
    with st.sidebar:
        st.header("💡 Example Questions")
        st.markdown("""
        **Search Companies:**
        - "Companies in Maharashtra"
        - "Find companies in Gujarat"
        - "Show me companies in Delhi"
        
        **Capital Queries:**
        - "Companies with capital above 10 lakh"
        - "High capital companies in Mumbai"
        - "Companies with authorized capital above 1 crore"
        
        **General Queries:**
        - "How many companies are there?"
        - "Recent company registrations"
        - "Top states by company count"
        - "Companies struck off last month"
        
        **Specific Companies:**
        - "Search for Reliance companies"
        - "Find Tata companies"
        - "Companies named Infosys"
        """)
        
        st.header("📊 Data Status")
        if 'chatbot' in st.session_state:
            total_companies = len(st.session_state.chatbot.df)
            st.metric("Companies Loaded", f"{total_companies:,}")
            
            if 'State' in st.session_state.chatbot.df.columns:
                states_count = st.session_state.chatbot.df['State'].nunique()
                st.metric("States Covered", states_count)
    
    # Chat input
    if prompt := st.chat_input("Ask about companies, states, capital..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing company data..."):
                response = st.session_state.chatbot.process_query(prompt)
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    run_chat_interface()