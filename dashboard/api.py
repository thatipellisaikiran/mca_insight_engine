from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime
import urllib.parse

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Generate sample MCA data
def generate_sample_data():
    np.random.seed(42)
    industries = ['Technology', 'Manufacturing', 'Services', 'Healthcare', 'Finance', 'Retail', 'Real Estate']
    states = ['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'Uttar Pradesh', 'West Bengal']
    
    companies = []
    for i in range(200):
        inc_date = f"202{np.random.randint(2,5)}-{np.random.randint(1,13):02d}-{np.random.randint(1,28):02d}"
        companies.append({
            'id': i + 1,
            'cin': f'U72900MH202{np.random.randint(2,5)}PTC{np.random.randint(100000, 999999)}',
            'name': f'Company {i} Private Limited',
            'industry': np.random.choice(industries),
            'state': np.random.choice(states),
            'authorized_capital': int(np.random.lognormal(14, 1.2)),
            'paid_up_capital': int(np.random.lognormal(13, 1.0)),
            'incorporation_date': inc_date,
            'status': np.random.choice(['Active', 'Active', 'Active', 'Dormant', 'Under Process'], 
                                     p=[0.65, 0.15, 0.10, 0.05, 0.05]),
            'director_count': np.random.randint(1, 8),
            'email': f'info@company{i}.com',
            'address': f'{np.random.randint(1, 100)} Street, {np.random.choice(states)}'
        })
    
    # Add some pharmaceutical companies for better search results
    pharma_companies = [
        {
            'id': 1001,
            'cin': 'U24230MH2020PTC123456',
            'name': 'SKYI FKUR WISH YOU INB PHARMACEUTICAL PRIVATE LIMITED',
            'industry': 'Healthcare',
            'state': 'Maharashtra',
            'authorized_capital': 50000000,
            'paid_up_capital': 25000000,
            'incorporation_date': '2020-05-15',
            'status': 'Active',
            'director_count': 4,
            'email': 'contact@skyipharma.com',
            'address': 'Plot No. 45, MIDC, Mumbai, Maharashtra'
        },
        {
            'id': 1002, 
            'cin': 'U24230MH2019PTC654321',
            'name': 'SUN PHARMACEUTICAL INDUSTRIES LIMITED',
            'industry': 'Healthcare',
            'state': 'Maharashtra', 
            'authorized_capital': 2500000000,
            'paid_up_capital': 1500000000,
            'incorporation_date': '2019-03-20',
            'status': 'Active',
            'director_count': 7,
            'email': 'info@sunpharma.com',
            'address': 'Western Express Highway, Goregaon, Mumbai'
        },
        {
            'id': 1003,
            'cin': 'U24230GJ2018PTC789012',
            'name': 'ZYDUS PHARMACEUTICALS PRIVATE LIMITED',
            'industry': 'Healthcare',
            'state': 'Gujarat',
            'authorized_capital': 1500000000,
            'paid_up_capital': 1000000000,
            'incorporation_date': '2018-07-10',
            'status': 'Active',
            'director_count': 5,
            'email': 'contact@zydus.com',
            'address': 'Zydus Tower, Ahmedabad, Gujarat'
        }
    ]
    
    companies.extend(pharma_companies)
    return companies

companies_data = generate_sample_data()

@app.route('/')
def home():
    return jsonify({
        "message": "MCA Insights REST API Server",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "/": "GET - API documentation",
            "/<company_name>": "GET - Search company by name",
            "/api/companies": "GET - Get all companies with pagination",
            "/api/companies/<id>": "GET - Get specific company details",
            "/api/stats": "GET - Get overall statistics",
            "/api/industries": "GET - Get industry analysis",
            "/api/search": "GET - Search companies",
            "/api/companies/search": "GET - Advanced company search",
            "/api/health": "GET - API health check"
        }
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "total_companies": len(companies_data)
    })

@app.route('/<company_name>', methods=['GET'])
def get_company_info(company_name):
    """Get detailed information for a specific company"""
    try:
        # URL decode the company name (replace %20 with spaces)
        company_name_clean = urllib.parse.unquote(company_name)
        
        # Get query parameters
        state = request.args.get('state', '')
        limit = int(request.args.get('limit', 10))
        
        print(f"Searching for: {company_name_clean}, State: {state}, Limit: {limit}")
        
        # Search in your companies data
        matching_companies = []
        
        for company in companies_data:
            # Flexible matching - check if search term appears in company name
            if (company_name_clean.upper() in company['name'].upper() or 
                company_name_clean.upper().replace(' ', '') in company['name'].upper().replace(' ', '')):
                
                # Filter by state if provided
                if state and company['state'].lower() != state.lower():
                    continue
                    
                matching_companies.append(company)
                
                # Stop if we reached the limit
                if len(matching_companies) >= limit:
                    break
        
        if matching_companies:
            return jsonify({
                'search_term': company_name_clean,
                'state_filter': state,
                'limit': limit,
                'found_count': len(matching_companies),
                'companies': matching_companies
            })
        else:
            return jsonify({
                'search_term': company_name_clean,
                'state_filter': state,
                'limit': limit,
                'found_count': 0,
                'companies': [],
                'message': 'No companies found matching your criteria'
            }), 404
            
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Error processing request'
        }), 500

@app.route('/api/companies/search', methods=['GET'])
def advanced_company_search():
    """Advanced company search with multiple filters"""
    try:
        company_name = request.args.get('name', '')
        state = request.args.get('state', '')
        industry = request.args.get('industry', '')
        min_capital = request.args.get('min_capital', 0, type=int)
        max_capital = request.args.get('max_capital', float('inf'), type=int)
        limit = request.args.get('limit', 20, type=int)
        
        matching_companies = []
        
        for company in companies_data:
            matches = True
            
            # Name filter
            if company_name and company_name.upper() not in company['name'].upper():
                matches = False
                
            # State filter
            if state and company['state'].lower() != state.lower():
                matches = False
                
            # Industry filter
            if industry and company['industry'].lower() != industry.lower():
                matches = False
                
            # Capital range filter
            if company['authorized_capital'] < min_capital or company['authorized_capital'] > max_capital:
                matches = False
                
            if matches:
                matching_companies.append(company)
                if len(matching_companies) >= limit:
                    break
        
        return jsonify({
            'filters': {
                'name': company_name,
                'state': state,
                'industry': industry,
                'min_capital': min_capital,
                'max_capital': max_capital if max_capital != float('inf') else 'unlimited',
                'limit': limit
            },
            'results_count': len(matching_companies),
            'companies': matching_companies
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/companies', methods=['GET'])
def get_companies():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    industry = request.args.get('industry')
    state = request.args.get('state')
    status = request.args.get('status')
    
    filtered_data = companies_data
    
    # Apply filters
    if industry:
        filtered_data = [c for c in filtered_data if c['industry'].lower() == industry.lower()]
    if state:
        filtered_data = [c for c in filtered_data if c['state'].lower() == state.lower()]
    if status:
        filtered_data = [c for c in filtered_data if c['status'].lower() == status.lower()]
    
    # Pagination
    total_companies = len(filtered_data)
    total_pages = (total_companies + per_page - 1) // per_page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    paginated_data = filtered_data[start_idx:end_idx]
    
    return jsonify({
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_companies': total_companies,
        'companies': paginated_data
    })

@app.route('/api/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    company = next((c for c in companies_data if c['id'] == company_id), None)
    if company:
        return jsonify(company)
    else:
        return jsonify({'error': 'Company not found'}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    df = pd.DataFrame(companies_data)
    
    stats = {
        'total_companies': len(companies_data),
        'active_companies': len([c for c in companies_data if c['status'] == 'Active']),
        'industries_count': df['industry'].nunique(),
        'states_count': df['state'].nunique(),
        'avg_capital': int(df['authorized_capital'].mean()),
        'total_capital': int(df['authorized_capital'].sum()),
        'avg_directors': float(df['director_count'].mean()),
        'latest_incorporation': df['incorporation_date'].max()
    }
    
    # Industry distribution
    industry_dist = df['industry'].value_counts().to_dict()
    stats['industry_distribution'] = industry_dist
    
    # State distribution
    state_dist = df['state'].value_counts().to_dict()
    stats['state_distribution'] = state_dist
    
    return jsonify(stats)

@app.route('/api/industries', methods=['GET'])
def get_industries():
    df = pd.DataFrame(companies_data)
    industry_stats = df.groupby('industry').agg({
        'id': 'count',
        'authorized_capital': ['sum', 'mean', 'median'],
        'paid_up_capital': 'sum',
        'director_count': 'mean'
    }).round(2)
    
    result = []
    for industry, data in industry_stats.iterrows():
        result.append({
            'industry': industry,
            'company_count': int(data[('id', 'count')]),
            'total_authorized_capital': int(data[('authorized_capital', 'sum')]),
            'avg_authorized_capital': int(data[('authorized_capital', 'mean')]),
            'median_authorized_capital': int(data[('authorized_capital', 'median')]),
            'total_paid_capital': int(data[('paid_up_capital', 'sum')]),
            'avg_directors': float(data[('director_count', 'mean')])
        })
    
    return jsonify(sorted(result, key=lambda x: x['company_count'], reverse=True))

@app.route('/api/search', methods=['GET'])
def search_companies():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        return jsonify({'error': 'Query parameter required (min 2 characters)'}), 400
    
    results = [
        c for c in companies_data 
        if query.lower() in c['name'].lower() or 
           query.lower() in c['industry'].lower() or
           query.lower() in c['state'].lower() or
           query.lower() in c['cin'].lower()
    ]
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })

@app.route('/api/trends', methods=['GET'])
def get_trends():
    df = pd.DataFrame(companies_data)
    df['incorporation_year'] = pd.to_datetime(df['incorporation_date']).dt.year
    
    yearly_trends = df.groupby('incorporation_year').agg({
        'id': 'count',
        'authorized_capital': 'mean'
    }).reset_index()
    
    trends_data = []
    for _, row in yearly_trends.iterrows():
        trends_data.append({
            'year': int(row['incorporation_year']),
            'company_count': int(row['id']),
            'avg_capital': int(row['authorized_capital'])
        })
    
    return jsonify(trends_data)

if __name__ == '__main__':
    print("🚀 Starting MCA Insights API Server...")
    print("🌐 API Documentation: http://localhost:5000")
    print("📊 Sample Data: 203 companies generated (including pharmaceutical companies)")
    print("🔍 Try these endpoints:")
    print("   - http://localhost:5000/SKYI%20FKUR%20WISH%20YOU%20INB%20PHARMACEUTICAL%20PRIVATE%20LIMITED")
    print("   - http://localhost:5000/api/stats")
    print("   - http://localhost:5000/api/companies")
    app.run(debug=True, host='0.0.0.0', port=5000)