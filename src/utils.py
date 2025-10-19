import os
import pandas as pd
import logging
from datetime import datetime
import yaml
import json
import sys

def setup_logging(log_level='INFO', log_file=None):
    """Setup logging configuration"""
    if log_file is None:
        log_file = f'logs/mca_engine_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Level: {log_level}, File: {log_file}")
    return logger

def load_config(config_path='config/config.yaml'):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        logging.info(f"Configuration loaded from {config_path}")
        return config
    except FileNotFoundError:
        logging.error(f"Configuration file not found: {config_path}")
        return None
    except Exception as e:
        logging.error(f"Error loading config from {config_path}: {e}")
        return None

def create_directories(config):
    """Create necessary directories"""
    directories = [
        config['data_paths']['raw_data'],
        config['data_paths']['processed_data'],
        config['data_paths']['outputs'],
        'logs',
        'tests',
        'docs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logging.info(f"Created/verified directory: {directory}")

def get_file_info(directory_path):
    """Get information about files in directory"""
    files_info = []
    
    if os.path.exists(directory_path):
        for file in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                file_info = {
                    'filename': file,
                    'file_path': file_path,
                    'size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2),
                    'extension': os.path.splitext(file)[1],
                    'modified_time': datetime.fromtimestamp(os.path.getmtime(file_path))
                }
                files_info.append(file_info)
    
    return files_info

def validate_dataframe(df, dataset_name):
    """Validate dataframe structure and quality"""
    validation_report = {
        'dataset_name': dataset_name,
        'timestamp': datetime.now().isoformat(),
        'total_records': len(df),
        'total_columns': len(df.columns),
        'columns': list(df.columns),
        'missing_values': df.isna().sum().to_dict(),
        'data_types': df.dtypes.astype(str).to_dict(),
        'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2)
    }
    
    return validation_report

def save_dataframe_to_excel(df, file_path, sheet_name='Data'):
    """Save dataframe to Excel with proper formatting"""
    try:
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_len, 50)
        
        logging.info(f"DataFrame saved to Excel: {file_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving to Excel {file_path}: {e}")
        return False

def get_dataframe_info(df, name="Dataset"):
    """Get comprehensive information about dataframe"""
    info = {
        'name': name,
        'shape': df.shape,
        'columns': list(df.columns),
        'data_types': df.dtypes.astype(str).to_dict(),
        'memory_usage_mb': round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2),
        'missing_values': df.isnull().sum().to_dict()
    }
    return info

def preview_dataset(file_path, n_rows=5):
    """Preview a dataset"""
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path, nrows=n_rows)
        else:
            df = pd.read_csv(file_path, nrows=n_rows)
        
        print(f"Preview of {os.path.basename(file_path)}:")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
        print("\n" + "="*50)
        
        return df.columns.tolist()
    except Exception as e:
        print(f"Error previewing {file_path}: {e}")
        return None

def save_json(data, file_path, indent=2):
    """Save data to JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=indent, default=str)
        logging.info(f"JSON data saved: {file_path}")
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {file_path}: {e}")
        return False

def load_json(file_path):
    """Load data from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logging.info(f"JSON data loaded: {file_path}")
        return data
    except Exception as e:
        logging.error(f"Error loading JSON from {file_path}: {e}")
        return None

def check_file_exists(file_path):
    """Check if file exists and return size info"""
    if os.path.exists(file_path):
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        return True, size_mb
    return False, 0

def print_section_header(title):
    """Print a formatted section header"""
    print(f"\n{'-'*60}")
    print(f"📋 {title}")
    print(f"{'-'*60}")

def print_step(step_number, step_name):
    """Print step information"""
    print(f"\n🔹 STEP {step_number}: {step_name}")
    print(f"{'-'*40}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")