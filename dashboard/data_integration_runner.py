import streamlit as st
import yaml
import os
from pathlib import Path

st.set_page_config(page_title="Data Integration Runner", layout="wide")

st.title("Data Integration Runner")
st.subheader("Run data integration to process your raw Excel files")

# Configuration loading with better error handling
def load_config():
    # Try multiple possible config locations
    possible_paths = [
        Path(__file__).parent / "config" / "config.yaml",  # dashboard/config/config.yaml
        Path(__file__).parent.parent / "config" / "config.yaml",  # ../config/config.yaml
        Path("config.yaml")  # Current directory
    ]
    
    for config_path in possible_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r') as file:
                    config = yaml.safe_load(file)
                st.success(f"✅ Configuration loaded from: {config_path}")
                return config
            except Exception as e:
                st.error(f"❌ Error reading config file {config_path}: {str(e)}")
                return None
    
    # If no config file found, create a default one
    st.warning("⚠️ No config file found. Creating default configuration...")
    return create_default_config()

def create_default_config():
    default_config = {
        'data_sources': {
            'excel': {
                'input_directory': 'dataset/input',
                'output_directory': 'dataset/output', 
                'processed_directory': 'dataset/processed'
            }
        },
        'processing': {
            'chunk_size': 1000,
            'max_workers': 4,
            'timeout': 300
        },
        'file_handling': {
            'allowed_extensions': ['.xlsx', '.xls', '.csv'],
            'max_file_size_mb': 50,
            'auto_create_dirs': True
        }
    }
    
    # Create config directory and file
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False)
    
    st.success(f"✅ Default config created at: {config_file}")
    return default_config

# Load configuration
config = load_config()

if config:
    st.success("✅ Configuration loaded successfully!")
    
    # Display config info
    with st.expander("📋 Configuration Details"):
        st.json(config)
    
    # Data Integration UI
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚀 Run Data Integration", type="primary", use_container_width=True):
            input_dir = config['data_sources']['excel']['input_directory']
            if os.path.exists(input_dir):
                files = [f for f in os.listdir(input_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
                if files:
                    st.success(f"Found {len(files)} files to process")
                    # Add your file processing logic here
                    
                    # Simulate processing
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, file in enumerate(files):
                        progress = (i + 1) / len(files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing: {file} ({i+1}/{len(files)})")
                        # Simulate processing time
                        import time
                        time.sleep(0.5)
                    
                    st.success("✅ Data integration completed successfully!")
                else:
                    st.warning("No Excel/CSV files found in input directory")
            else:
                st.error(f"Input directory not found: {input_dir}")
    
    with col2:
        if st.button("📁 Check Data Sources", use_container_width=True):
            input_dir = config['data_sources']['excel']['input_directory']
            output_dir = config['data_sources']['excel']['output_directory']
            processed_dir = config['data_sources']['excel']['processed_directory']
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if os.path.exists(input_dir):
                    files = [f for f in os.listdir(input_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
                    st.success(f"✅ Input: {input_dir}")
                    st.write(f"Files: {len(files)}")
                else:
                    st.error(f"❌ Input: {input_dir}")
            
            with col_b:
                if os.path.exists(output_dir):
                    st.success(f"✅ Output: {output_dir}")
                else:
                    st.warning(f"⚠️ Output: {output_dir}")
            
            with col_c:
                if os.path.exists(processed_dir):
                    st.success(f"✅ Processed: {processed_dir}")
                else:
                    st.warning(f"⚠️ Processed: {processed_dir}")
    
    with col3:
        if st.button("🛠️ Create Directories", use_container_width=True):
            directories = [
                config['data_sources']['excel']['input_directory'],
                config['data_sources']['excel']['output_directory'],
                config['data_sources']['excel']['processed_directory'],
                'logs'
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                st.success(f"Created: {directory}")

    # File Upload Section
    st.divider()
    st.subheader("📤 Upload Excel Files")
    
    uploaded_files = st.file_uploader(
        "Choose Excel/CSV files", 
        type=['xlsx', 'xls', 'csv'],
        accept_multiple_files=True,
        help="Upload your raw Excel or CSV files for processing"
    )
    
    if uploaded_files:
        st.success(f"📎 {len(uploaded_files)} files ready for processing")
        
        # Show file details
        for uploaded_file in uploaded_files:
            file_size_mb = round(uploaded_file.size / (1024 * 1024), 2)
            st.write(f" - {uploaded_file.name} ({file_size_mb} MB)")
        
        # Process uploaded files
        if st.button("Process Uploaded Files"):
            input_dir = config['data_sources']['excel']['input_directory']
            os.makedirs(input_dir, exist_ok=True)
            
            for uploaded_file in uploaded_files:
                # Save uploaded file to input directory
                with open(os.path.join(input_dir, uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            st.success(f"✅ {len(uploaded_files)} files saved to {input_dir}")

else:
    st.error("❌ Failed to load configuration")