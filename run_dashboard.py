import os
import subprocess
import sys
import threading
import time

def run_dashboard():
    """Run the Streamlit dashboard"""
    try:
        dashboard_files = [
            'dashboard/app.py',           # Your existing app.py in dashboard folder
            'dashboard/dashboard_app.py', # If you create new one
            'dashboard_app.py'            # Fallback to root
        ]
        
        found_file = None
        for file in dashboard_files:
            if os.path.exists(file):
                found_file = file
                break
        
        if found_file:
            print("✅ Starting MCA Insights Dashboard...")
            print("📊 Dashboard will open at http://localhost:8501")
            subprocess.run([sys.executable, "-m", "streamlit", "run", found_file])
        else:
            print("❌ No dashboard file found in dashboard/ folder")
            
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

def run_api():
    """Run the Flask REST API"""
    try:
        api_files = [
            'dashboard/api.py',      # Your existing api.py in dashboard folder
            'api_server.py',         # Fallback
            'api.py'                 # Fallback
        ]
        
        found_file = None
        for file in api_files:
            if os.path.exists(file):
                found_file = file
                break
        
        if found_file:
            print("✅ Starting MCA REST API Server...")
            print("🌐 API will be available at http://localhost:5000")
            subprocess.run([sys.executable, found_file])
        else:
            print("❌ No API file found in dashboard/ folder")
            
    except Exception as e:
        print(f"❌ Error starting API: {e}")

def run_chatbot():
    """Run the Streamlit chatbot"""
    try:
        chatbot_files = [
            'ai/chatbot.py',         # Your existing chatbot.py in ai folder
            'ai/ragchat.py',         # Your ragchat as alternative
            'chatbot_app.py'         # Fallback
        ]
        
        found_file = None
        for file in chatbot_files:
            if os.path.exists(file):
                found_file = file
                break
        
        if found_file:
            print("✅ Starting MCA AI Chatbot...")
            print("🤖 Chatbot will open at http://localhost:8502")
            env = os.environ.copy()
            env['STREAMLIT_SERVER_PORT'] = '8502'
            subprocess.run([sys.executable, "-m", "streamlit", "run", found_file, "--server.port=8502"], env=env)
        else:
            print("❌ No chatbot file found in ai/ folder")
            
    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")

def run_summary():
    """Run the AI Summary Generator"""
    try:
        summary_files = [
            'ai/summarize.py',       # Your existing summarize.py in ai folder
            'summary_app.py',         # Fallback
            'ai/summary_generator.py' # Alternative
        ]
        
        found_file = None
        for file in summary_files:
            if os.path.exists(file):
                found_file = file
                break
        
        if found_file:
            print("✅ Starting AI Summary Generator...")
            print("📈 Summary Generator will open at http://localhost:8503")
            env = os.environ.copy()
            env['STREAMLIT_SERVER_PORT'] = '8503'
            subprocess.run([sys.executable, "-m", "streamlit", "run", found_file, "--server.port=8503"], env=env)
        else:
            print("❌ No summary file found in ai/ folder")
            
    except Exception as e:
        print(f"❌ Error starting summary generator: {e}")

def main():
    print("🎯 MCA Insights Engine - Interactive Features")
    print("==================================================")
    print("1. 📊 Dashboard (Streamlit) - http://localhost:8501")
    print("2. 🌐 REST API (Flask) - http://localhost:5000")
    print("3. 🤖 Chatbot (Streamlit) - http://localhost:8502") 
    print("4. 📈 AI Summary Generator - http://localhost:8503")
    print("5. 🚀 Start ALL Services")
    print()
    
    try:
        choice = input("Select option (1-5): ").strip()
        
        if choice == "1":
            run_dashboard()
        elif choice == "2":
            run_api()
        elif choice == "3":
            run_chatbot()
        elif choice == "4":
            run_summary()
        elif choice == "5":
            print("🚀 Starting ALL Services feature is currently under development.")
            print("Please select individual services (1-4) for now.")
            print("Exiting...")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please select 1-5.")
            
    except KeyboardInterrupt:
        print("\n👋 Exiting MCA Insights Engine. Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()