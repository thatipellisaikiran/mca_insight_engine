import pandas as pd
import numpy as np
import logging
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self, config):
        self.config = config
        self.processed_data_path = config['data_paths']['processed_data']
        self.outputs_path = config['data_paths']['outputs']
        
    def load_master_data(self):
        """Load the master merged dataset"""
        master_file = os.path.join(self.processed_data_path, 'master_companies.csv')
        
        if not os.path.exists(master_file):
            logger.error("Master dataset not found. Run data integration first.")
            return None
        
        try:
            df = pd.read_csv(master_file)
            logger.info(f"Loaded master dataset: {len(df)} records, {len(df.columns)} columns")
            return df
        except Exception as e:
            logger.error(f"Error loading master dataset: {str(e)}")
            return None
    
    def basic_descriptive_analysis(self, df):
        """Perform basic descriptive analysis"""
        analysis_results = {
            'analysis_timestamp': datetime.now().isoformat(),
            'basic_stats': {},
            'state_analysis': {},
            'capital_analysis': {},
            'temporal_analysis': {},
            'company_category_analysis': {}
        }
        
        # Basic statistics - FIXED: Initialize all required keys
        analysis_results['basic_stats']['total_companies'] = len(df)
        analysis_results['basic_stats']['total_states'] = df['State'].nunique() if 'State' in df.columns else 0
        analysis_results['basic_stats']['total_columns'] = len(df.columns)
        
        # State-wise analysis
        if 'State' in df.columns:
            state_stats = df['State'].value_counts().to_dict()
            analysis_results['state_analysis']['company_count_by_state'] = state_stats
            analysis_results['state_analysis']['top_states'] = dict(list(state_stats.items())[:5])
        
        # Capital analysis - FIXED: Handle empty/missing data
        if 'Authorized Capital' in df.columns:
            capital_data = df['Authorized Capital'].dropna()
            if len(capital_data) > 0:
                capital_stats = {
                    'total_authorized_capital': float(capital_data.sum()),
                    'average_authorized_capital': float(capital_data.mean()),
                    'median_authorized_capital': float(capital_data.median()),
                    'max_authorized_capital': float(capital_data.max()),
                    'min_authorized_capital': float(capital_data.min()),
                    'records_with_capital_data': len(capital_data)
                }
            else:
                capital_stats = {
                    'total_authorized_capital': 0,
                    'average_authorized_capital': 0,
                    'median_authorized_capital': 0,
                    'max_authorized_capital': 0,
                    'min_authorized_capital': 0,
                    'records_with_capital_data': 0
                }
            analysis_results['capital_analysis']['authorized_capital'] = capital_stats
        
        if 'Paid-up Capital' in df.columns:
            paidup_data = df['Paid-up Capital'].dropna()
            if len(paidup_data) > 0:
                paidup_stats = {
                    'total_paidup_capital': float(paidup_data.sum()),
                    'average_paidup_capital': float(paidup_data.mean()),
                    'median_paidup_capital': float(paidup_data.median()),
                    'max_paidup_capital': float(paidup_data.max()),
                    'min_paidup_capital': float(paidup_data.min()),
                    'records_with_paidup_data': len(paidup_data)
                }
            else:
                paidup_stats = {
                    'total_paidup_capital': 0,
                    'average_paidup_capital': 0,
                    'median_paidup_capital': 0,
                    'max_paidup_capital': 0,
                    'min_paidup_capital': 0,
                    'records_with_paidup_data': 0
                }
            analysis_results['capital_analysis']['paidup_capital'] = paidup_stats
        
        # Company category analysis
        if 'Company Category' in df.columns:
            category_stats = df['Company Category'].value_counts().to_dict()
            analysis_results['company_category_analysis'] = category_stats
        
        # Data quality metrics
        analysis_results['data_quality'] = {
            'total_records': len(df),
            'records_with_missing_data': df.isna().any(axis=1).sum(),
            'completeness_percentage': round((1 - df.isna().mean().mean()) * 100, 2)
        }
        
        return analysis_results
    
    def advanced_capital_analysis(self, df):
        """Perform advanced capital analysis"""
        capital_analysis = {}
        
        if 'Authorized Capital' in df.columns and 'State' in df.columns:
            # State-wise capital analysis - FIXED: Handle empty data
            capital_data = df[['State', 'Authorized Capital']].dropna()
            if len(capital_data) > 0:
                state_capital = capital_data.groupby('State')['Authorized Capital'].agg([
                    'sum', 'mean', 'median', 'count'
                ]).round(2)
                
                # Convert to dictionary format
                capital_analysis['state_wise_capital'] = state_capital.to_dict('index')
                
                # Capital distribution analysis
                capital_bins = [0, 100000, 1000000, 10000000, float('inf')]
                bin_labels = ['Small (<1L)', 'Medium (1L-10L)', 'Large (10L-1Cr)', 'Very Large (>1Cr)']
                
                capital_data['Capital_Size_Category'] = pd.cut(
                    capital_data['Authorized Capital'], 
                    bins=capital_bins, 
                    labels=bin_labels,
                    right=False
                )
                
                capital_distribution = capital_data['Capital_Size_Category'].value_counts().to_dict()
                capital_analysis['capital_size_distribution'] = capital_distribution
            else:
                capital_analysis['state_wise_capital'] = {}
                capital_analysis['capital_size_distribution'] = {}
        
        return capital_analysis
    
    def temporal_analysis(self, df):
        """Analyze trends over time"""
        temporal_analysis = {}
        
        if 'Date of Incorporation' in df.columns:
            # Convert to datetime if not already
            df['Year_of_Incorporation'] = pd.to_datetime(
                df['Date of Incorporation'], errors='coerce'
            ).dt.year
            
            # Remove NaN years
            valid_years = df['Year_of_Incorporation'].dropna()
            
            if len(valid_years) > 0:
                # Year-wise company registration
                yearly_registrations = valid_years.value_counts().sort_index().to_dict()
                temporal_analysis['yearly_registrations'] = yearly_registrations
                
                # Recent trends (last 10 years)
                current_year = datetime.now().year
                recent_years = {int(k): int(v) for k, v in yearly_registrations.items() 
                              if k >= current_year - 10 and pd.notna(k)}
                temporal_analysis['recent_trends'] = recent_years
                
                # Overall trend statistics
                temporal_analysis['trend_stats'] = {
                    'earliest_year': int(valid_years.min()),
                    'latest_year': int(valid_years.max()),
                    'total_years_covered': len(yearly_registrations)
                }
            else:
                temporal_analysis['yearly_registrations'] = {}
                temporal_analysis['recent_trends'] = {}
                temporal_analysis['trend_stats'] = {
                    'earliest_year': None,
                    'latest_year': None,
                    'total_years_covered': 0
                }
        
        return temporal_analysis
    
    def generate_insights(self, df, basic_analysis, capital_analysis, temporal_analysis):
        """Generate business insights from analysis"""
        insights = {
            'key_findings': [],
            'recommendations': [],
            'anomalies_detected': [],
            'generation_timestamp': datetime.now().isoformat()
        }
        
        # Key findings from basic analysis
        total_companies = basic_analysis['basic_stats']['total_companies']
        insights['key_findings'].append(f"Total companies analyzed: {total_companies:,}")
        
        if 'state_analysis' in basic_analysis and 'company_count_by_state' in basic_analysis['state_analysis']:
            state_counts = basic_analysis['state_analysis']['company_count_by_state']
            if state_counts:
                top_state = max(state_counts.items(), key=lambda x: x[1])
                insights['key_findings'].append(f"Top state by company count: {top_state[0]} with {top_state[1]:,} companies")
        
        # Capital insights
        if 'capital_analysis' in basic_analysis and 'authorized_capital' in basic_analysis['capital_analysis']:
            capital_stats = basic_analysis['capital_analysis']['authorized_capital']
            if capital_stats['records_with_capital_data'] > 0:
                avg_capital = capital_stats['average_authorized_capital']
                insights['key_findings'].append(f"Average authorized capital: ₹{avg_capital:,.2f}")
        
        # Temporal insights
        if 'recent_trends' in temporal_analysis and temporal_analysis['recent_trends']:
            recent_years = temporal_analysis['recent_trends']
            if recent_years:
                latest_year = max(recent_years.keys())
                latest_count = recent_years[latest_year]
                insights['key_findings'].append(f"Latest year ({latest_year}) registrations: {latest_year} companies")
        
        # Data quality insights
        if 'data_quality' in basic_analysis:
            quality = basic_analysis['data_quality']
            insights['key_findings'].append(f"Data completeness: {quality['completeness_percentage']}%")
        
        # Recommendations
        insights['recommendations'].append("Consider focusing on states with high company density for business expansion")
        insights['recommendations'].append("Analyze capital-intensive companies for potential investment opportunities")
        insights['recommendations'].append("Review data quality and consider data enrichment for missing values")
        
        # Anomalies
        if 'data_quality' in basic_analysis and basic_analysis['data_quality']['records_with_missing_data'] > 0:
            missing_count = basic_analysis['data_quality']['records_with_missing_data']
            insights['anomalies_detected'].append(f"{missing_count} records have missing data that may need attention")
        
        return insights
    
    def save_analysis_results(self, analysis_results, insights):
        """Save all analysis results"""
        # Create output directories
        insights_dir = os.path.join(self.outputs_path, 'insights')
        reports_dir = os.path.join(self.outputs_path, 'reports')
        os.makedirs(insights_dir, exist_ok=True)
        os.makedirs(reports_dir, exist_ok=True)
        
        try:
            # Save detailed analysis
            analysis_file = os.path.join(insights_dir, 'detailed_analysis.json')
            with open(analysis_file, 'w') as f:
                json.dump(analysis_results, f, indent=2, default=str)
            
            # Save insights
            insights_file = os.path.join(insights_dir, 'business_insights.json')
            with open(insights_file, 'w') as f:
                json.dump(insights, f, indent=2)
            
            # Save summary report
            summary_report = {
                'report_generated': datetime.now().isoformat(),
                'total_companies_analyzed': analysis_results['basic_analysis']['basic_stats']['total_companies'],
                'total_states': analysis_results['basic_analysis']['basic_stats']['total_states'],
                'data_completeness': analysis_results['basic_analysis']['data_quality']['completeness_percentage'],
                'key_insights': insights['key_findings'][:3],  # Top 3 insights
                'total_recommendations': len(insights['recommendations'])
            }
            
            summary_file = os.path.join(reports_dir, 'summary_report.json')
            with open(summary_file, 'w') as f:
                json.dump(summary_report, f, indent=2)
            
            logger.info(f"✅ Analysis results saved:")
            logger.info(f"   - Detailed analysis: {analysis_file}")
            logger.info(f"   - Business insights: {insights_file}")
            logger.info(f"   - Summary report: {summary_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving analysis results: {str(e)}")
            return False
    
    def run_complete_analysis(self):
        """Execute complete analysis pipeline"""
        logger.info("🔍 Starting Complete Analysis Pipeline")
        logger.info("=" * 50)
        
        try:
            # Load data
            df = self.load_master_data()
            if df is None or df.empty:
                logger.error("❌ No data available for analysis")
                return False
            
            logger.info(f"📊 Dataset loaded: {len(df)} records, {len(df.columns)} columns")
            
            # Perform analyses
            logger.info("📈 Performing basic descriptive analysis...")
            basic_analysis = self.basic_descriptive_analysis(df)
            
            logger.info("💰 Performing capital analysis...")
            capital_analysis = self.advanced_capital_analysis(df)
            
            logger.info("📅 Performing temporal analysis...")
            temporal_analysis = self.temporal_analysis(df)
            
            # Combine all analyses - FIXED: Proper structure
            analysis_results = {
                'basic_analysis': basic_analysis,
                'capital_analysis': capital_analysis,
                'temporal_analysis': temporal_analysis,
                'analysis_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_records_analyzed': len(df),
                    'analysis_version': '1.0'
                }
            }
            
            # Generate insights
            logger.info("💡 Generating business insights...")
            insights = self.generate_insights(df, basic_analysis, capital_analysis, temporal_analysis)
            
            # Save results
            logger.info("💾 Saving analysis results...")
            success = self.save_analysis_results(analysis_results, insights)
            
            if success:
                logger.info("🎉 Analysis Pipeline Completed Successfully!")
                # Print summary
                print(f"\n📊 ANALYSIS SUMMARY:")
                print(f"   Companies Analyzed: {len(df):,}")
                print(f"   States Covered: {basic_analysis['basic_stats']['total_states']}")
                print(f"   Data Completeness: {basic_analysis['data_quality']['completeness_percentage']}%")
                print(f"   Key Insights Generated: {len(insights['key_findings'])}")
                print(f"   Output Location: {self.outputs_path}")
            else:
                logger.error("❌ Failed to save analysis results")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Analysis pipeline failed: {str(e)}")
            return False