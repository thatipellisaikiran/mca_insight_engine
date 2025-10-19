import pandas as pd
import numpy as np
import os
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DataIntegrator:
    def __init__(self, config):
        self.config = config
        self.raw_data_path = config['data_paths']['raw_data']
        self.processed_data_path = config['data_paths']['processed_data']
        self.change_log = {}
        
    def discover_datasets(self):
        """Discover and list all available datasets"""
        datasets_info = {}
        
        state_files = {
            'maharashtra': 'maharashtra.xlsx',
            'gujarat': 'gujarat.xlsx', 
            'delhi': 'delhi.xlsx',
            'tamil_nadu': 'tamilnadu.xlsx',
            'karnataka': 'karnataka.xlsx'
        }
        
        for state, filename in state_files.items():
            file_path = os.path.join(self.raw_data_path, filename)
            if os.path.exists(file_path):
                datasets_info[state] = {
                    'file_path': file_path,
                    'exists': True,
                    'size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2)
                }
            else:
                datasets_info[state] = {
                    'file_path': file_path,
                    'exists': False
                }
                logger.warning(f"File not found: {file_path}")
        
        return datasets_info
    
    def load_single_dataset(self, file_path, state_name):
        """Load a single dataset with comprehensive error handling"""
        try:
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path}")
                return None
            
            logger.info(f"✅ Loaded {state_name}: {len(df)} records, {len(df.columns)} columns")
            return df
            
        except Exception as e:
            logger.error(f"❌ Failed to load {state_name}: {str(e)}")
            return None
    
    def analyze_dataset_columns(self, datasets):
        """Analyze and compare columns across all datasets"""
        column_analysis = {}
        
        for state, df in datasets.items():
            if df is not None:
                column_analysis[state] = {
                    'columns': list(df.columns),
                    'data_types': df.dtypes.astype(str).to_dict(),
                    'sample_data': df.head(3).to_dict('records')
                }
        
        return column_analysis
    
    def create_column_mapping(self, column_analysis):
        """Create intelligent column mapping based on analysis"""
        # Common MCA data column patterns
        standard_columns = {
            'CIN': ['cin', 'corporate identification number', 'company cin'],
            'Company Name': ['company name', 'name', 'company_name'],
            'Registered Office Address': ['registered office address', 'address', 'registered_address'],
            'State': ['state', 'company state'],
            'City': ['city', 'company city'],
            'PIN': ['pin', 'pincode', 'pin code'],
            'Company Category': ['company category', 'category'],
            'Company Subcategory': ['company subcategory', 'subcategory'],
            'Class of Company': ['class of company', 'class'],
            'Authorized Capital': ['authorized capital', 'auth_capital'],
            'Paid-up Capital': ['paid-up capital', 'paidup_capital'],
            'Date of Incorporation': ['date of incorporation', 'incorporation_date'],
            'Date of Last AGM': ['date of last agm', 'last_agm_date'],
            'Date of Balance Sheet': ['date of balance sheet', 'balance_sheet_date']
        }
        
        column_mapping = {}
        
        for state, analysis in column_analysis.items():
            state_mapping = {}
            actual_columns = [col.lower() for col in analysis['columns']]
            
            for standard_col, possible_names in standard_columns.items():
                for possible_name in possible_names:
                    if possible_name in actual_columns:
                        idx = actual_columns.index(possible_name)
                        original_col = analysis['columns'][idx]
                        state_mapping[original_col] = standard_col
                        break
            
            column_mapping[state] = state_mapping
        
        return column_mapping
    
    def standardize_datasets(self, datasets, column_mapping):
        """Standardize all datasets using column mapping"""
        standardized_datasets = {}
        
        for state, df in datasets.items():
            if df is not None and state in column_mapping:
                # Rename columns
                df_standardized = df.rename(columns=column_mapping[state])
                
                # Add missing standard columns
                standard_columns = [
                    'CIN', 'Company Name', 'Registered Office Address', 'State',
                    'City', 'PIN', 'Company Category', 'Company Subcategory',
                    'Class of Company', 'Authorized Capital', 'Paid-up Capital',
                    'Date of Incorporation', 'Date of Last AGM', 'Date of Balance Sheet'
                ]
                
                for col in standard_columns:
                    if col not in df_standardized.columns:
                        df_standardized[col] = np.nan
                
                # Add metadata
                df_standardized['Data_Source_State'] = state.title()
                df_standardized['Data_Load_Timestamp'] = datetime.now()
                
                standardized_datasets[state] = df_standardized
                logger.info(f"✅ Standardized {state}: now has {len(df_standardized.columns)} columns")
        
        return standardized_datasets
    
    def clean_and_transform(self, datasets):
        """Clean and transform data for consistency"""
        cleaned_datasets = {}
        
        for state, df in datasets.items():
            df_clean = df.copy()
            
            # Clean text fields
            text_columns = ['Company Name', 'Registered Office Address', 'City', 'State']
            for col in text_columns:
                if col in df_clean.columns:
                    df_clean[col] = df_clean[col].astype(str).str.strip().str.title()
            
            # Convert numeric columns
            if 'Authorized Capital' in df_clean.columns:
                df_clean['Authorized Capital'] = pd.to_numeric(
                    df_clean['Authorized Capital'], errors='coerce'
                )
            
            if 'Paid-up Capital' in df_clean.columns:
                df_clean['Paid-up Capital'] = pd.to_numeric(
                    df_clean['Paid-up Capital'], errors='coerce'
                )
            
            # Convert date columns
            date_columns = ['Date of Incorporation', 'Date of Last AGM', 'Date of Balance Sheet']
            for date_col in date_columns:
                if date_col in df_clean.columns:
                    df_clean[date_col] = pd.to_datetime(df_clean[date_col], errors='coerce')
            
            # Ensure state consistency
            if 'State' in df_clean.columns:
                df_clean['State'] = state.title()
            
            cleaned_datasets[state] = df_clean
        
        return cleaned_datasets
    
    def merge_datasets(self, datasets):
        """Merge all datasets into a single master dataset"""
        all_dataframes = []
        
        for state, df in datasets.items():
            # Select only common columns that exist
            common_columns = [
                'CIN', 'Company Name', 'Registered Office Address', 'State', 'City',
                'PIN', 'Company Category', 'Company Subcategory', 'Class of Company',
                'Authorized Capital', 'Paid-up Capital', 'Date of Incorporation',
                'Date of Last AGM', 'Date of Balance Sheet', 'Data_Source_State',
                'Data_Load_Timestamp'
            ]
            
            available_columns = [col for col in common_columns if col in df.columns]
            df_subset = df[available_columns].copy()
            all_dataframes.append(df_subset)
        
        if all_dataframes:
            master_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
            logger.info(f"✅ Merged {len(all_dataframes)} datasets into master with {len(master_df)} records")
        else:
            master_df = pd.DataFrame()
            logger.error("❌ No datasets to merge")
        
        return master_df
    
    def remove_duplicates(self, df):
        """Remove duplicate records using multiple strategies"""
        initial_count = len(df)
        
        # Strategy 1: Remove exact duplicates
        df_deduped = df.drop_duplicates()
        
        # Strategy 2: Remove based on CIN (most reliable)
        if 'CIN' in df_deduped.columns:
            df_deduped = df_deduped.drop_duplicates(subset=['CIN'], keep='first')
        
        # Strategy 3: Remove based on Company Name + State
        elif 'Company Name' in df_deduped.columns and 'State' in df_deduped.columns:
            df_deduped = df_deduped.drop_duplicates(
                subset=['Company Name', 'State'], 
                keep='first'
            )
        
        final_count = len(df_deduped)
        duplicates_removed = initial_count - final_count
        
        logger.info(f"✅ Removed {duplicates_removed} duplicate records")
        self.change_log['duplicates_removed'] = duplicates_removed
        
        return df_deduped
    
    def validate_data_quality(self, df):
        """Comprehensive data quality validation"""
        quality_report = {
            'validation_timestamp': datetime.now().isoformat(),
            'total_records': len(df),
            'total_columns': len(df.columns),
            'data_completeness': {},
            'data_quality_issues': {}
        }
        
        # Check completeness for key columns
        key_columns = ['CIN', 'Company Name', 'State']
        for col in key_columns:
            if col in df.columns:
                missing_count = df[col].isna().sum()
                completeness_pct = round((1 - missing_count / len(df)) * 100, 2)
                quality_report['data_completeness'][col] = {
                    'missing_count': missing_count,
                    'completeness_percentage': completeness_pct
                }
        
        # Check data quality issues
        if 'Authorized Capital' in df.columns:
            negative_capital = (df['Authorized Capital'] < 0).sum()
            if negative_capital > 0:
                quality_report['data_quality_issues']['negative_authorized_capital'] = negative_capital
        
        # State distribution
        if 'State' in df.columns:
            quality_report['state_distribution'] = df['State'].value_counts().to_dict()
        
        # Overall completeness score
        overall_completeness = round((1 - df.isna().mean().mean()) * 100, 2)
        quality_report['overall_completeness_score'] = overall_completeness
        
        logger.info(f"✅ Data quality validation completed: {overall_completeness}% completeness")
        
        return quality_report
    
    def save_results(self, df, quality_report):
        """Save merged data and quality reports"""
        # Save master dataset
        master_file = os.path.join(self.processed_data_path, 'master_companies.csv')
        df.to_csv(master_file, index=False)
        
        # Save quality report
        quality_file = os.path.join(self.processed_data_path, 'data_quality_report.json')
        with open(quality_file, 'w') as f:
            json.dump(quality_report, f, indent=2, default=str)
        
        # Save change log
        self.change_log['merge_timestamp'] = datetime.now().isoformat()
        self.change_log['quality_report'] = quality_report
        
        change_log_file = os.path.join(self.processed_data_path, 'change_log.json')
        with open(change_log_file, 'w') as f:
            json.dump(self.change_log, f, indent=2, default=str)
        
        logger.info(f"✅ Results saved:")
        logger.info(f"   - Master data: {master_file}")
        logger.info(f"   - Quality report: {quality_file}")
        logger.info(f"   - Change log: {change_log_file}")
        
        return master_file
    
    def run_complete_pipeline(self):
        """Execute the complete data integration pipeline"""
        logger.info("🚀 Starting Complete Data Integration Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 1: Discover datasets
            logger.info("📁 Step 1: Discovering datasets...")
            datasets_info = self.discover_datasets()
            logger.info(f"Discovered {len([d for d in datasets_info.values() if d['exists']])} datasets")
            
            # Step 2: Load all datasets
            logger.info("📥 Step 2: Loading datasets...")
            datasets = {}
            for state, info in datasets_info.items():
                if info['exists']:
                    df = self.load_single_dataset(info['file_path'], state)
                    if df is not None:
                        datasets[state] = df
            
            if not datasets:
                logger.error("❌ No datasets loaded successfully. Pipeline stopped.")
                return None
            
            # Step 3: Analyze columns
            logger.info("🔍 Step 3: Analyzing column structure...")
            column_analysis = self.analyze_dataset_columns(datasets)
            
            # Step 4: Create column mapping
            logger.info("🔄 Step 4: Creating column mappings...")
            column_mapping = self.create_column_mapping(column_analysis)
            
            # Step 5: Standardize datasets
            logger.info("📊 Step 5: Standardizing datasets...")
            standardized_datasets = self.standardize_datasets(datasets, column_mapping)
            
            # Step 6: Clean and transform
            logger.info("🧹 Step 6: Cleaning and transforming data...")
            cleaned_datasets = self.clean_and_transform(standardized_datasets)
            
            # Step 7: Merge datasets
            logger.info("🔄 Step 7: Merging datasets...")
            merged_df = self.merge_datasets(cleaned_datasets)
            
            if merged_df.empty:
                logger.error("❌ Merged dataset is empty. Pipeline stopped.")
                return None
            
            # Step 8: Remove duplicates
            logger.info("🚫 Step 8: Removing duplicates...")
            deduped_df = self.remove_duplicates(merged_df)
            
            # Step 9: Validate data quality
            logger.info("✅ Step 9: Validating data quality...")
            quality_report = self.validate_data_quality(deduped_df)
            
            # Step 10: Save results
            logger.info("💾 Step 10: Saving results...")
            result_path = self.save_results(deduped_df, quality_report)
            
            logger.info("🎉 Data Integration Pipeline Completed Successfully!")
            logger.info("=" * 60)
            
            return result_path
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {str(e)}")
            return None