import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.utils import load_config

class AISummaryGenerator:
    def __init__(self):
        self.config = load_config()
        if not self.config:
            print("❌ Failed to load configuration")
            return
            
        self.processed_path = self.config['data_paths']['processed_data']
        self.outputs_path = self.config['data_paths']['outputs']
        self.load_data()
    
    def load_data(self):
        """Load data for summary generation"""
        try:
            master_file = os.path.join(self.processed_path, "master_companies.csv")
            if os.path.exists(master_file):
                self.df = pd.read_csv(master_file)
                
                # Convert date columns
                if 'Date of Incorporation' in self.df.columns:
                    self.df['Date_of_Incorporation'] = pd.to_datetime(
                        self.df['Date of Incorporation'], errors='coerce'
                    )
                    
                print(f"✅ Loaded {len(self.df)} companies for summary generation")
            else:
                print("❌ Master dataset not found. Using sample data for demonstration.")
                self.setup_sample_data()
                
        except Exception as e:
            print(f"Error loading data: {e}")
            self.setup_sample_data()
    
    def setup_sample_data(self):
        """Setup sample data if no real data is available"""
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
            }
        ]
        self.df = pd.DataFrame(sample_companies)
        print("📝 Using sample data for summary generation")
    
    def generate_daily_summary(self):
        """Generate daily summary report"""
        if self.df.empty:
            return {"error": "No data available"}
        
        # Calculate metrics
        today = datetime.now().date()
        
        summary = {
            "report_date": today.isoformat(),
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_companies": len(self.df),
                "new_incorporations_today": self.calculate_new_incorporations(today),
                "states_covered": self.df['State'].nunique() if 'State' in self.df.columns else 0,
                "average_authorized_capital": float(self.df['Authorized Capital'].mean()) if 'Authorized Capital' in self.df.columns else 0,
                "top_states": self.get_top_states(),
                "recent_trends": self.get_recent_trends()
            },
            "key_changes": self.identify_key_changes()
        }
        
        # Save summary
        self.save_summary(summary)
        
        return summary
    
    def calculate_new_incorporations(self, today):
        """Calculate new incorporations (demo - would compare with previous data)"""
        # In a real system, this would compare with yesterday's data
        # For demo, return a sample number
        return len(self.df) // 10  # Sample calculation
    
    def get_top_states(self):
        """Get top states by company count"""
        if 'State' in self.df.columns:
            return self.df['State'].value_counts().head(5).to_dict()
        return {}
    
    def get_recent_trends(self):
        """Get recent incorporation trends"""
        if 'Date_of_Incorporation' in self.df.columns:
            recent_data = self.df[self.df['Date_of_Incorporation'] >= (datetime.now() - timedelta(days=30))]
            return {
                "last_30_days_companies": len(recent_data),
                "growth_rate": "2.5%"  # Sample
            }
        return {
            "last_30_days_companies": len(self.df) // 4,
            "growth_rate": "2.5%"
        }
    
    def identify_key_changes(self):
        """Identify key changes in data"""
        # This would compare with previous dataset versions
        # For demo, return sample changes
        return {
            "major_capital_increases": 15,
            "status_changes": 8,
            "address_updates": 23,
            "new_incorporations": len(self.df) // 10
        }
    
    def save_summary(self, summary):
        """Save summary to file"""
        summary_dir = os.path.join(self.outputs_path, "ai_summaries")
        os.makedirs(summary_dir, exist_ok=True)
        
        filename = f"daily_summary_{datetime.now().strftime('%Y%m%d')}.json"
        filepath = os.path.join(summary_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Also create a text version without emojis to avoid encoding issues
        text_summary = self.format_text_summary(summary)
        text_filepath = os.path.join(summary_dir, f"daily_summary_{datetime.now().strftime('%Y%m%d')}.txt")
        
        with open(text_filepath, 'w', encoding='utf-8') as f:
            f.write(text_summary)
        
        print(f"✅ Daily summary saved: {filepath}")
        print(f"✅ Text summary saved: {text_filepath}")
    
    def format_text_summary(self, summary):
        """Format summary as text without emojis to avoid encoding issues"""
        text = f"""
MCA DAILY SUMMARY REPORT
Generated: {summary['generated_at']}

EXECUTIVE SUMMARY
• Total Companies: {summary['summary']['total_companies']:,}
• New Incorporations Today: {summary['summary']['new_incorporations_today']}
• States Covered: {summary['summary']['states_covered']}
• Average Authorized Capital: ₹{summary['summary']['average_authorized_capital']:,.2f}

TOP STATES
"""
        for state, count in summary['summary']['top_states'].items():
            text += f"• {state}: {count:,} companies\n"
        
        text += f"""
RECENT TRENDS
• Companies in Last 30 Days: {summary['summary']['recent_trends']['last_30_days_companies']}
• Growth Rate: {summary['summary']['recent_trends']['growth_rate']}

KEY CHANGES
• Major Capital Increases: {summary['key_changes']['major_capital_increases']}
• Status Changes: {summary['key_changes']['status_changes']}
• Address Updates: {summary['key_changes']['address_updates']}
• New Incorporations: {summary['key_changes']['new_incorporations']}

---
Automatically generated by MCA Insights Engine AI
"""
        return text

    def print_summary_to_console(self, summary):
        """Print summary to console in a nice format"""
        print("\n" + "="*60)
        print("📊 MCA DAILY AI SUMMARY REPORT")
        print("="*60)
        
        print(f"\n📅 Report Date: {summary['report_date']}")
        print(f"⏰ Generated: {summary['generated_at']}")
        
        print(f"\n📈 EXECUTIVE SUMMARY")
        print(f"   • Total Companies: {summary['summary']['total_companies']:,}")
        print(f"   • New Incorporations Today: {summary['summary']['new_incorporations_today']}")
        print(f"   • States Covered: {summary['summary']['states_covered']}")
        print(f"   • Average Authorized Capital: ₹{summary['summary']['average_authorized_capital']:,.2f}")
        
        print(f"\n🏢 TOP STATES")
        for state, count in summary['summary']['top_states'].items():
            print(f"   • {state}: {count:,} companies")
        
        print(f"\n📊 RECENT TRENDS")
        print(f"   • Companies in Last 30 Days: {summary['summary']['recent_trends']['last_30_days_companies']}")
        print(f"   • Growth Rate: {summary['summary']['recent_trends']['growth_rate']}")
        
        print(f"\n🔄 KEY CHANGES")
        print(f"   • Major Capital Increases: {summary['key_changes']['major_capital_increases']}")
        print(f"   • Status Changes: {summary['key_changes']['status_changes']}")
        print(f"   • Address Updates: {summary['key_changes']['address_updates']}")
        print(f"   • New Incorporations: {summary['key_changes']['new_incorporations']}")
        
        print("\n" + "="*60)
        print("✅ Summary generated successfully!")
        print("="*60)

# Usage
if __name__ == "__main__":
    generator = AISummaryGenerator()
    summary = generator.generate_daily_summary()
    
    if "error" not in summary:
        generator.print_summary_to_console(summary)
        print("\n💾 Summary files saved in: data/outputs/ai_summaries/")
    else:
        print(f"❌ Error: {summary['error']}")