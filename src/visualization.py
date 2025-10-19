import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import sys
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Now import from src
from src.utils import load_config

class DataVisualizer:
    def __init__(self, config):
        self.config = config
        self.outputs_path = config['data_paths']['outputs']
        self.visualizations_path = os.path.join(self.outputs_path, 'visualizations')
        
        # Create visualizations directory
        os.makedirs(self.visualizations_path, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8')
        self.colors = sns.color_palette('viridis')
        print(f"📁 Visualizations will be saved to: {self.visualizations_path}")
    
    def load_analysis_data(self):
        """Load analysis data for visualization"""
        insights_path = os.path.join(self.outputs_path, 'insights', 'detailed_analysis.json')
        
        if os.path.exists(insights_path):
            try:
                with open(insights_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error loading analysis data: {e}")
        else:
            print(f"ℹ️  Analysis file not found: {insights_path}")
        return None
    
    def create_state_distribution_chart(self, analysis_data):
        """Create state-wise company distribution chart"""
        try:
            if 'state_distribution' in analysis_data and analysis_data['state_distribution']:
                state_data = analysis_data['state_distribution']
                
                plt.figure(figsize=(12, 8))
                states = list(state_data.keys())
                counts = list(state_data.values())
                
                bars = plt.bar(states, counts, color=self.colors)
                plt.title('Company Distribution by State', fontsize=16, fontweight='bold')
                plt.xlabel('States', fontsize=12)
                plt.ylabel('Number of Companies', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                
                # Add value labels on bars
                for bar, count in zip(bars, counts):
                    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                            f'{count:,}', ha='center', va='bottom')
                
                plt.tight_layout()
                plt.savefig(os.path.join(self.visualizations_path, 'state_distribution.png'), 
                           dpi=300, bbox_inches='tight')
                plt.close()
                
                print("✅ Created: state_distribution.png")
            else:
                print("⚠️  No state distribution data available")
        except Exception as e:
            print(f"❌ Error creating state distribution chart: {e}")
    
    def create_sample_visualizations(self):
        """Create sample visualizations when no analysis data exists"""
        print("🎨 Creating sample visualizations...")
        
        try:
            # Sample data
            states = ['Maharashtra', 'Gujarat', 'Delhi', 'Tamil Nadu', 'Karnataka']
            company_counts = [1560, 1240, 890, 1120, 780]
            
            # Bar chart
            plt.figure(figsize=(12, 8))
            bars = plt.bar(states, company_counts, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'])
            plt.title('Sample: Company Distribution by State', fontsize=16, fontweight='bold')
            plt.xlabel('States')
            plt.ylabel('Number of Companies')
            plt.xticks(rotation=45, ha='right')
            
            for bar, count in zip(bars, company_counts):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                        f'{count:,}', ha='center', va='bottom')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.visualizations_path, 'sample_state_distribution.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
            # Pie chart
            plt.figure(figsize=(10, 8))
            plt.pie(company_counts, labels=states, autopct='%1.1f%%', startangle=90)
            plt.title('Sample: State-wise Company Distribution', fontweight='bold')
            plt.savefig(os.path.join(self.visualizations_path, 'sample_pie_chart.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
            # Summary chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            ax1.bar(['Total Companies'], [sum(company_counts)], color='#3498db')
            ax1.set_title('Total Companies', fontweight='bold')
            ax1.set_ylabel('Count')
            ax1.text(0, sum(company_counts) + 50, f'{sum(company_counts):,}', 
                    ha='center', va='bottom', fontweight='bold')
            
            ax2.bar(['States Covered'], [len(states)], color='#2ecc71')
            ax2.set_title('Geographical Coverage', fontweight='bold')
            ax2.set_ylabel('Count')
            ax2.text(0, len(states) + 0.3, f'{len(states)} states', 
                    ha='center', va='bottom', fontweight='bold')
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.visualizations_path, 'sample_summary.png'), dpi=300, bbox_inches='tight')
            plt.close()
            
            print("✅ Created sample visualizations")
            
        except Exception as e:
            print(f"❌ Error creating sample visualizations: {e}")
    
    def create_analysis_report(self):
        """Create comprehensive analysis report with visualizations"""
        analysis_data = self.load_analysis_data()
        
        if analysis_data:
            print("📊 Creating Visualizations from Analysis Data...")
            self.create_state_distribution_chart(analysis_data)
        else:
            print("ℹ️  No analysis data found. Creating sample visualizations...")
            self.create_sample_visualizations()
        
        # Create a report file
        try:
            report_content = f"""
MCA INSIGHTS ENGINE - VISUALIZATION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

VISUALIZATIONS CREATED:
- state_distribution.png - Company distribution across states
- sample_state_distribution.png - Sample data visualization
- sample_pie_chart.png - Sample pie chart
- sample_summary.png - Sample summary metrics

Output Location: {self.visualizations_path}

NOTES:
- Run the analysis pipeline first for actual data visualizations
- Sample visualizations are created when analysis data is not available
"""
            report_file = os.path.join(self.visualizations_path, 'visualization_report.txt')
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            print("✅ Created: visualization_report.txt")
            print(f"🎉 All visualizations saved to: {self.visualizations_path}")
            
        except Exception as e:
            print(f"❌ Error creating report: {e}")

def main():
    """Main function to run visualizations"""
    try:
        # Get the project root directory
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, 'config', 'config.yaml')
        
        print(f"🔍 Looking for config at: {config_path}")
        
        if not os.path.exists(config_path):
            print(f"❌ Config file not found at: {config_path}")
            print("💡 Creating default config file...")
            
            # Create config directory and file
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            default_config = {
                'data_paths': {
                    'raw_data': 'C:/mca_insights_engine/dataset/raw',
                    'processed_data': 'C:/mca_insights_engine/dataset/processed',
                    'outputs': 'C:/mca_insights_engine/dataset/outputs'
                },
                'merge_settings': {
                    'remove_duplicates': True,
                    'validate_quality': True
                },
                'logging': {
                    'level': 'INFO'
                }
            }
            
            import yaml
            with open(config_path, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
            
            print(f"✅ Created default config: {config_path}")
            config = default_config
        else:
            config = load_config(config_path)
        
        if config:
            print("📊 MCA Insights Engine - Visualization Module")
            print("=" * 50)
            visualizer = DataVisualizer(config)
            visualizer.create_analysis_report()
        else:
            print("❌ Failed to load configuration")
            
    except Exception as e:
        print(f"❌ Error in visualization main: {e}")
        print("💡 Try running from project root: python src/visualization.py")

if __name__ == "__main__":
    main()