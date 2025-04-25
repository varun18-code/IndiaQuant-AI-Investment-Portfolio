import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import math

def simulate_satellite_imagery_data(ticker, days=30):
    """
    Simulate satellite imagery data for retail foot traffic or manufacturing activity
    for Indian companies
    
    Parameters:
    ticker (str): Stock ticker
    days (int): Number of days of data to generate
    
    Returns:
    dict: Simulated satellite imagery data
    """
    # Map Indian tickers to business types for simulation purposes
    business_type_map = {
        'RELIANCE.NS': 'manufacturing',
        'TCS.NS': 'tech',
        'INFY.NS': 'tech',
        'WIPRO.NS': 'tech',
        'HDFCBANK.NS': 'financial',
        'ICICIBANK.NS': 'financial',
        'SBIN.NS': 'financial',
        'TATAMOTORS.NS': 'manufacturing',
        'TATASTEEL.NS': 'manufacturing',
        'BHARTIARTL.NS': 'telecom',
        'HINDUNILVR.NS': 'retail',
        'ITC.NS': 'retail',
        'BAJFINANCE.NS': 'financial',
        'ASIANPAINT.NS': 'manufacturing',
        'MARUTI.NS': 'manufacturing',
        'HCLTECH.NS': 'tech',
        'SUNPHARMA.NS': 'pharma',
        'DRREDDY.NS': 'pharma',
        'BAJAJFINSV.NS': 'financial',
        'KOTAKBANK.NS': 'financial'
    }
    
    business_type = business_type_map.get(ticker, 'other')
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    dates = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Generate activity metrics based on business type
    if business_type == 'retail':
        # Simulate foot traffic for retail
        base_value = 100
        # Add day of week pattern (higher on weekends)
        activity = [base_value + 20 * int(d.weekday() >= 5) for d in date_range]
        # Add random noise
        activity = [a + np.random.normal(0, 10) for a in activity]
        # Add slight upward trend
        activity = [a * (1 + i * 0.002) for i, a in enumerate(activity)]
        metric_name = "Foot Traffic"
        
    elif business_type == 'manufacturing':
        # Simulate manufacturing activity
        base_value = 80
        # Manufacturing typically doesn't vary by day of week
        activity = [base_value for _ in date_range]
        # Add random noise
        activity = [a + np.random.normal(0, 5) for a in activity]
        # Add slight upward trend
        activity = [a * (1 + i * 0.001) for i, a in enumerate(activity)]
        metric_name = "Production Activity"
        
    else:
        # Generic activity for other businesses
        base_value = 90
        activity = [base_value + np.random.normal(0, 8) for _ in date_range]
        metric_name = "Activity Index"
    
    # Ensure all values are positive
    activity = [max(0, a) for a in activity]
    
    # Calculate change metrics
    current_activity = activity[-1]
    previous_activity = activity[-7] if days >= 7 else activity[0]
    weekly_change = ((current_activity / previous_activity) - 1) * 100
    
    average_activity = sum(activity) / len(activity)
    
    # Generate insights
    if weekly_change > 5:
        insight = f"Significant increase in {metric_name.lower()} detected"
        sentiment = "positive"
    elif weekly_change < -5:
        insight = f"Significant decrease in {metric_name.lower()} detected"
        sentiment = "negative"
    else:
        insight = f"Stable {metric_name.lower()} observed"
        sentiment = "neutral"
    
    return {
        'dates': dates,
        'activity': activity,
        'metric_name': metric_name,
        'current_value': current_activity,
        'weekly_change_pct': weekly_change,
        'average_value': average_activity,
        'insight': insight,
        'sentiment': sentiment,
        'business_type': business_type
    }

def simulate_shipping_data(days=30):
    """
    Simulate global shipping congestion data
    
    Parameters:
    days (int): Number of days of data to generate
    
    Returns:
    dict: Simulated shipping congestion data
    """
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    dates = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Shipping routes relevant to Indian trade
    routes = [
        "India to North America",
        "Europe to India",
        "China to India",
        "India to Middle East",
        "Southeast Asia to India",
        "India to Africa"
    ]
    
    # Generate congestion data for each route
    route_data = {}
    overall_congestion = []
    
    for route in routes:
        # Base congestion level varies by route - India-specific
        if "China to India" in route:
            base_value = 70  # Highest congestion on China routes
        elif "India to North America" in route:
            base_value = 65  # High congestion on US routes
        elif "Europe to India" in route:
            base_value = 60  # Moderate congestion on European routes
        elif "Southeast Asia to India" in route:
            base_value = 55  # Moderate congestion on SE Asian routes
        elif "India to Middle East" in route:
            base_value = 45  # Lower congestion on Middle East routes
        else:
            base_value = 50  # Default for other routes
        
        # Generate congestion values with some randomness and trend
        congestion = []
        current_value = base_value
        
        for i in range(days):
            # Add random daily fluctuation
            change = np.random.normal(0, 3)
            # Add slight trend (can be customized)
            trend = -0.05  # Slight downward trend
            current_value = current_value + change + trend
            # Ensure values stay reasonable
            current_value = max(20, min(95, current_value))
            congestion.append(current_value)
        
        route_data[route] = congestion
    
    # Calculate overall congestion (average across all routes)
    for i in range(days):
        day_average = sum(route_data[route][i] for route in routes) / len(routes)
        overall_congestion.append(day_average)
    
    # Calculate metrics
    current_congestion = overall_congestion[-1]
    previous_congestion = overall_congestion[-7] if days >= 7 else overall_congestion[0]
    weekly_change = ((current_congestion / previous_congestion) - 1) * 100
    
    # Generate insights for Indian shipping routes
    if weekly_change > 5:
        insight = "Shipping congestion on Indian trade routes is increasing"
        sentiment = "negative"  # Higher congestion is typically negative for supply chains
    elif weekly_change < -5:
        insight = "Shipping congestion on Indian trade routes is decreasing"
        sentiment = "positive"  # Lower congestion is typically positive for supply chains
    else:
        insight = "Shipping congestion on Indian trade routes remains stable"
        sentiment = "neutral"
    
    return {
        'dates': dates,
        'routes': routes,
        'route_data': route_data,
        'overall_congestion': overall_congestion,
        'current_congestion': current_congestion,
        'weekly_change_pct': weekly_change,
        'insight': insight,
        'sentiment': sentiment
    }

def generate_credit_card_spending_data(ticker, days=90):
    """
    Generate simulated credit card spending data for consumer behavior analysis
    
    Parameters:
    ticker (str): Stock ticker
    days (int): Number of days of data to generate
    
    Returns:
    dict: Simulated credit card spending data
    """
    # Map Indian tickers to retail categories for simulation
    category_map = {
        'RELIANCE.NS': 'Retail & Telecom',
        'TCS.NS': 'IT Services',
        'INFY.NS': 'IT Services',
        'WIPRO.NS': 'IT Services',
        'HDFCBANK.NS': 'Banking Services',
        'ICICIBANK.NS': 'Banking Services',
        'SBIN.NS': 'Banking Services',
        'TATAMOTORS.NS': 'Automobile',
        'MARUTI.NS': 'Automobile',
        'MAHINDRA.NS': 'Automobile',
        'BHARTIARTL.NS': 'Telecom Services',
        'HINDUNILVR.NS': 'FMCG',
        'ITC.NS': 'FMCG',
        'DABUR.NS': 'FMCG',
        'ASIANPAINT.NS': 'Home Improvement',
        'SUNPHARMA.NS': 'Pharmaceuticals',
        'DRREDDY.NS': 'Pharmaceuticals',
        'BAJFINANCE.NS': 'Financial Services',
        'HDFCLIFE.NS': 'Insurance',
        'ZOMATO.NS': 'Food Delivery',
        'NYKAA.NS': 'E-commerce'
    }
    
    category = category_map.get(ticker, 'General Consumer Goods')
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    dates = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Generate spending data
    # Base spending varies by category for Indian market segments
    if category in ['IT Services', 'Retail & Telecom']:
        base_spending = 110
    elif category in ['E-commerce', 'FMCG', 'Telecom Services']:
        base_spending = 100
    elif category in ['Home Improvement', 'Pharmaceuticals']:
        base_spending = 95
    elif category in ['Food Delivery', 'Automobile']:
        base_spending = 90
    elif category in ['Banking Services', 'Financial Services', 'Insurance']:
        base_spending = 105
    else:
        base_spending = 85
    
    # Generate spending values with weekly patterns and trends
    spending = []
    for i, d in enumerate(date_range):
        # Weekly pattern (higher on weekends)
        day_factor = 1.0 + (0.2 if d.weekday() >= 5 else 0)
        
        # Seasonal trend for Indian festivals and seasons
        month = d.month
        if month == 10 or month == 11:  # Diwali and Durga Puja season
            seasonal_factor = 1.3
        elif month == 8:  # Raksha Bandhan, Independence Day, and Janmashtami
            seasonal_factor = 1.15
        elif month == 3 or month == 4:  # Holi and new financial year
            seasonal_factor = 1.2
        elif month == 1:  # Post-New Year sales
            seasonal_factor = 1.1
        elif month >= 6 and month <= 7:  # Monsoon sales
            seasonal_factor = 0.9  # Slightly lower during monsoon
        else:
            seasonal_factor = 1.0
        
        # General trend (slight growth)
        trend_factor = 1.0 + (i * 0.0005)
        
        # Random fluctuation
        random_factor = np.random.normal(1, 0.05)
        
        # Calculate daily spending
        daily_spending = base_spending * day_factor * seasonal_factor * trend_factor * random_factor
        spending.append(daily_spending)
    
    # Calculate metrics
    current_spending = spending[-7:]
    previous_spending = spending[-14:-7] if days >= 14 else spending[:7]
    
    current_avg = sum(current_spending) / len(current_spending)
    previous_avg = sum(previous_spending) / len(previous_spending)
    
    weekly_change = ((current_avg / previous_avg) - 1) * 100
    
    # Generate year-over-year comparison if we have enough data
    yoy_change = None
    yoy_insight = None
    if days >= 365:
        current_period = spending[-30:]
        year_ago_period = spending[-365:-335]
        
        current_period_avg = sum(current_period) / len(current_period)
        year_ago_avg = sum(year_ago_period) / len(year_ago_period)
        
        yoy_change = ((current_period_avg / year_ago_avg) - 1) * 100
        
        if yoy_change > 10:
            yoy_insight = f"Strong year-over-year growth in {category} spending"
        elif yoy_change > 0:
            yoy_insight = f"Moderate year-over-year growth in {category} spending"
        elif yoy_change > -10:
            yoy_insight = f"Slight year-over-year decline in {category} spending"
        else:
            yoy_insight = f"Significant year-over-year decline in {category} spending"
    
    # Generate insights
    if weekly_change > 5:
        insight = f"Increasing consumer spending in {category}"
        sentiment = "positive"
    elif weekly_change < -5:
        insight = f"Decreasing consumer spending in {category}"
        sentiment = "negative"
    else:
        insight = f"Stable consumer spending in {category}"
        sentiment = "neutral"
    
    return {
        'dates': dates,
        'spending': spending,
        'category': category,
        'current_spending_avg': current_avg,
        'weekly_change_pct': weekly_change,
        'yoy_change_pct': yoy_change,
        'insight': insight,
        'yoy_insight': yoy_insight,
        'sentiment': sentiment
    }

def generate_weather_impact_data(ticker, days=90):
    """
    Generate weather and climate impact data for agricultural and other weather-sensitive sectors
    
    Parameters:
    ticker (str): Stock ticker
    days (int): Number of days of data to generate
    
    Returns:
    dict: Simulated weather impact data
    """
    # Map Indian tickers to weather sensitivity (higher = more sensitive)
    weather_sensitivity_map = {
        'COROMANDEL.NS': 0.9,  # Fertilizers & agro
        'BAJAJHIND.NS': 0.8,   # Sugar
        'RENUKA.NS': 0.8,      # Sugar
        'TATACONSUMER.NS': 0.7, # Tea
        'ITC.NS': 0.6,         # FMCG with agricultural exposure
        'GODREJAGRO.NS': 0.9,  # Agrochemicals
        'UPL.NS': 0.8,         # Agrochemicals
        'MARICO.NS': 0.5,      # FMCG with agricultural inputs
        'KRBL.NS': 0.9,        # Rice
        'MAHINDRA.NS': 0.4,    # Farm equipment
        'NESTLEIND.NS': 0.3,   # FMCG with some agricultural exposure
        'DABUR.NS': 0.4,       # Ayurvedic products with herb inputs
        'BRITANNIA.NS': 0.3,   # Food products
        'HEROMOTOCO.NS': 0.2,  # Two-wheelers (rural demand affected by monsoons)
        'ADANIPORTS.NS': 0.3,  # Ports (affected by severe weather)
        'ONGC.NS': 0.4,        # Oil & Gas (offshore operations affected by weather)
    }
    
    # Default sensitivity for tickers not in the map
    weather_sensitivity = weather_sensitivity_map.get(ticker, 0.1)
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    dates = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Determine the primary agricultural category based on ticker
    agri_categories = {
        'COROMANDEL.NS': 'Fertilizers & Agro',
        'BAJAJHIND.NS': 'Sugar',
        'RENUKA.NS': 'Sugar',
        'TATACONSUMER.NS': 'Tea & Coffee',
        'ITC.NS': 'Diverse Agricultural',
        'GODREJAGRO.NS': 'Agrochemicals',
        'UPL.NS': 'Agrochemicals',
        'MARICO.NS': 'Edible Oils',
        'KRBL.NS': 'Rice',
    }
    
    category = agri_categories.get(ticker, 'General Agricultural')
    
    # Generate seasonal pattern based on Indian monsoon
    # Monsoon generally from June to September (months 6-9)
    rainfall_pattern = []
    temperature_pattern = []
    crop_health_index = []
    extreme_weather_events = []
    
    for d in date_range:
        month = d.month
        
        # Rainfall pattern (higher during monsoon)
        if 6 <= month <= 9:
            base_rainfall = 80 + random.randint(-10, 10)  # Monsoon season
        elif 10 <= month <= 11:
            base_rainfall = 30 + random.randint(-10, 10)  # Post-monsoon
        elif 12 <= month <= 2:
            base_rainfall = 10 + random.randint(-5, 5)    # Winter
        else:
            base_rainfall = 20 + random.randint(-10, 10)  # Pre-monsoon
            
        rainfall_pattern.append(base_rainfall)
        
        # Temperature pattern
        if 4 <= month <= 6:
            base_temp = 35 + random.randint(-3, 3)       # Summer
        elif 7 <= month <= 10:
            base_temp = 30 + random.randint(-3, 3)       # Monsoon/Post-monsoon
        elif 11 <= month <= 2:
            base_temp = 20 + random.randint(-5, 5)       # Winter
        else:
            base_temp = 28 + random.randint(-3, 3)       # Spring
            
        temperature_pattern.append(base_temp)
        
        # Crop health calculation based on optimal conditions for most Indian crops
        # Too much rain or too high temperatures can be harmful
        rainfall_effect = 1.0 - abs(base_rainfall - 60) / 100
        temperature_effect = 1.0 - abs(base_temp - 28) / 30
        
        # Seasonal timing effect (growing seasons)
        season_effect = 0.8
        if (category == 'Rice' and 6 <= month <= 10) or \
           (category == 'Sugar' and 4 <= month <= 8) or \
           (category == 'Tea & Coffee' and not (12 <= month <= 2)) or \
           (category == 'Edible Oils' and 6 <= month <= 11):
            season_effect = 1.2
        
        crop_health = (0.5 * rainfall_effect + 0.5 * temperature_effect) * season_effect
        # Add some randomness to crop health
        crop_health = max(0, min(1, crop_health + random.uniform(-0.1, 0.1)))
        crop_health_index.append(crop_health * 100)  # Convert to 0-100 scale
        
        # Extreme weather events (rare)
        if random.random() < 0.02:  # 2% chance of extreme weather event on any day
            extreme_type = random.choice(['Flood', 'Drought', 'Cyclone', 'Heatwave'])
            extreme_weather_events.append({
                'date': dates[len(rainfall_pattern)-1],
                'type': extreme_type,
                'severity': random.uniform(0.6, 0.9)  # 0-1 scale
            })
    
    # Calculate metrics
    current_crop_health = crop_health_index[-7:]
    previous_crop_health = crop_health_index[-14:-7] if days >= 14 else crop_health_index[:7]
    
    current_avg = sum(current_crop_health) / len(current_crop_health)
    previous_avg = sum(previous_crop_health) / len(previous_crop_health)
    
    weekly_change = ((current_avg / previous_avg) - 1) * 100 if previous_avg > 0 else 0
    
    # Generate insight based on current conditions
    if current_avg > 80:
        insight = f"Excellent growing conditions for {category} crops"
        sentiment = "positive"
    elif current_avg > 60:
        insight = f"Good growing conditions for {category} crops"
        sentiment = "positive"
    elif current_avg > 40:
        insight = f"Average growing conditions for {category} crops"
        sentiment = "neutral"
    else:
        insight = f"Poor growing conditions for {category} crops"
        sentiment = "negative"
    
    # Add impact information if there were extreme weather events
    if extreme_weather_events:
        latest_event = extreme_weather_events[-1]
        insight += f". Recent {latest_event['type']} may impact yields."
        if latest_event['severity'] > 0.7:
            sentiment = "negative"
    
    # Calculate company impact factor - how much this weather affects the company
    weather_impact_factor = round(weather_sensitivity * (100 - current_avg) / 100, 2)
    
    return {
        'dates': dates,
        'rainfall': rainfall_pattern,
        'temperature': temperature_pattern,
        'crop_health': crop_health_index,
        'extreme_events': extreme_weather_events,
        'category': category,
        'current_health_avg': current_avg,
        'weekly_change_pct': weekly_change,
        'weather_impact_factor': weather_impact_factor,
        'insight': insight,
        'sentiment': sentiment
    }

def generate_agricultural_satellite_data(ticker, days=90):
    """
    Generate agricultural satellite imagery analysis data
    
    Parameters:
    ticker (str): Stock ticker
    days (int): Number of days of data to generate
    
    Returns:
    dict: Simulated agricultural satellite data
    """
    # Map tickers to crop types
    crop_map = {
        'COROMANDEL.NS': 'Multiple Crops',
        'BAJAJHIND.NS': 'Sugarcane',
        'RENUKA.NS': 'Sugarcane',
        'TATACONSUMER.NS': 'Tea',
        'ITC.NS': 'Multiple Crops',
        'GODREJAGRO.NS': 'Multiple Crops',
        'UPL.NS': 'Multiple Crops',
        'MARICO.NS': 'Coconut/Sunflower',
        'KRBL.NS': 'Rice',
    }
    
    crop_type = crop_map.get(ticker, 'General Crops')
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    dates = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Generate NDVI (Normalized Difference Vegetation Index) - a common satellite vegetation index
    # NDVI ranges from -1 to 1, but for healthy vegetation it's typically 0.2 to 0.8
    ndvi_base = 0.6  # Healthy vegetation
    
    # Different crop types have different patterns
    if crop_type == 'Sugarcane':
        # Sugarcane is year-round but with seasonal variations
        ndvi_values = [ndvi_base + 0.1 * math.sin(i/30 * math.pi) for i in range(days)]
    elif crop_type == 'Rice':
        # Rice has more distinct growing seasons
        ndvi_values = []
        for d in date_range:
            month = d.month
            if 6 <= month <= 9:  # Kharif season
                ndvi_values.append(ndvi_base + random.uniform(0.05, 0.15))
            elif 11 <= month <= 2:  # Rabi season
                ndvi_values.append(ndvi_base + random.uniform(0, 0.1))
            else:
                ndvi_values.append(ndvi_base - random.uniform(0.1, 0.2))
    elif crop_type == 'Tea':
        # Tea is evergreen but with seasonal variations
        ndvi_values = [ndvi_base - 0.05 * math.cos(i/60 * math.pi) for i in range(days)]
    else:
        # General pattern with seasonal randomness
        ndvi_values = [ndvi_base + random.uniform(-0.15, 0.15) for _ in range(days)]
    
    # Add noise to NDVI values
    ndvi_values = [max(-1, min(1, v + random.uniform(-0.05, 0.05))) for v in ndvi_values]
    
    # Calculate LAI (Leaf Area Index) - another common vegetation index
    # LAI is typically between 0 and 8 for crops
    lai_values = [max(0, min(8, 6 * v + random.uniform(-0.5, 0.5))) for v in ndvi_values]
    
    # Calculate soil moisture index (0-100%)
    moisture_values = []
    for i, d in enumerate(date_range):
        month = d.month
        # Base moisture depends on typical Indian rainfall patterns
        if 6 <= month <= 9:  # Monsoon season
            base_moisture = 70 + random.uniform(-10, 20)
        elif 10 <= month <= 11:  # Post-monsoon
            base_moisture = 60 + random.uniform(-15, 15)
        elif 12 <= month <= 2:  # Winter
            base_moisture = 40 + random.uniform(-10, 10)
        else:  # Pre-monsoon
            base_moisture = 30 + random.uniform(-10, 15)
        
        moisture_values.append(max(0, min(100, base_moisture)))
    
    # Generate crop area estimates (in thousands of hectares)
    if crop_type == 'Sugarcane':
        crop_area = random.uniform(4000, 5000)  # India is a major sugarcane producer
    elif crop_type == 'Rice':
        crop_area = random.uniform(43000, 45000)  # India is one of the largest rice producers
    elif crop_type == 'Tea':
        crop_area = random.uniform(550, 600)  # India is a major tea producer
    elif crop_type == 'Coconut/Sunflower':
        crop_area = random.uniform(1800, 2000)
    else:
        crop_area = random.uniform(1000, 3000)
    
    # Calculate metrics
    current_ndvi = ndvi_values[-7:]
    previous_ndvi = ndvi_values[-14:-7] if days >= 14 else ndvi_values[:7]
    
    current_avg_ndvi = sum(current_ndvi) / len(current_ndvi)
    previous_avg_ndvi = sum(previous_ndvi) / len(previous_ndvi)
    
    ndvi_change = ((current_avg_ndvi / previous_avg_ndvi) - 1) * 100 if previous_avg_ndvi > 0 else 0
    
    # Generate yield prediction (metric tons per hectare)
    if crop_type == 'Sugarcane':
        base_yield = 70  # tonnes/hectare
    elif crop_type == 'Rice':
        base_yield = 4   # tonnes/hectare
    elif crop_type == 'Tea':
        base_yield = 2   # tonnes/hectare
    else:
        base_yield = 3   # tonnes/hectare
    
    # Adjust yield based on NDVI
    yield_adjustment = (current_avg_ndvi - 0.4) / 0.4  # Normalize to a factor around 1
    predicted_yield = base_yield * (1 + yield_adjustment)
    predicted_yield = max(base_yield * 0.7, min(base_yield * 1.3, predicted_yield))
    
    # Total production estimate
    total_production = crop_area * predicted_yield
    
    # Generate insight
    if current_avg_ndvi > 0.6:
        insight = f"{crop_type} crops showing excellent vigor in satellite imagery"
        sentiment = "positive"
    elif current_avg_ndvi > 0.4:
        insight = f"{crop_type} crops showing average vigor in satellite imagery"
        sentiment = "neutral"
    else:
        insight = f"{crop_type} crops showing poor vigor in satellite imagery"
        sentiment = "negative"
    
    if ndvi_change > 5:
        insight += ". Significant improvement in crop health detected."
    elif ndvi_change < -5:
        insight += ". Significant deterioration in crop health detected."
        sentiment = "negative"
    
    return {
        'dates': dates,
        'ndvi_values': ndvi_values,
        'lai_values': lai_values,
        'soil_moisture': moisture_values,
        'crop_type': crop_type,
        'crop_area': crop_area,
        'current_avg_ndvi': current_avg_ndvi,
        'ndvi_change_pct': ndvi_change,
        'predicted_yield': predicted_yield,
        'total_production': total_production,
        'insight': insight,
        'sentiment': sentiment
    }

def generate_social_media_trends(ticker, days=30):
    """
    Generate social media trends and alternative web data for a ticker
    
    Parameters:
    ticker (str): Stock ticker
    days (int): Number of days of data to generate
    
    Returns:
    dict: Simulated social media trend data
    """
    # Map Indian tickers to sectors and consumer brand recognition
    brand_presence = {
        'RELIANCE.NS': 0.9,    # Jio, Retail, etc.
        'TCS.NS': 0.7,         # IT services
        'HDFCBANK.NS': 0.8,    # Banking
        'ICICIBANK.NS': 0.7,   # Banking
        'BHARTIARTL.NS': 0.8,  # Telecom
        'HINDUNILVR.NS': 0.9,  # FMCG
        'ITC.NS': 0.7,         # FMCG/Hotels
        'WIPRO.NS': 0.6,       # IT Services
        'INFY.NS': 0.7,        # IT Services
        'MARUTI.NS': 0.8,      # Automobile
        'TATAMOTORS.NS': 0.8,  # Automobile
        'BAJAJ-AUTO.NS': 0.7,  # Automobile
        'ZOMATO.NS': 0.9,      # Food delivery
        'PAYTM.NS': 0.8,       # Fintech
        'NYKAA.NS': 0.8,       # E-commerce
    }
    
    # Default brand strength for tickers not in the map
    brand_strength = brand_presence.get(ticker, 0.4)
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    dates = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Generate different social media metrics
    # Mention volume (base scale depends on brand strength)
    base_mentions = int(5000 * brand_strength)
    mention_volume = [max(0, int(base_mentions + base_mentions * np.random.normal(0, 0.2))) for _ in range(days)]
    
    # Generate sentiment scores (-1 to 1)
    base_sentiment = 0.2  # Slightly positive default
    sentiment_scores = [max(-1, min(1, base_sentiment + np.random.normal(0, 0.2))) for _ in range(days)]
    
    # Generate engagement rates (0-100%)
    base_engagement = 20 * brand_strength  # As percentage
    engagement_rates = [max(0, min(100, base_engagement + np.random.normal(0, 5))) for _ in range(days)]
    
    # Web search trends (indexed to 100)
    base_search = 60 + 30 * brand_strength
    search_trends = [max(0, min(100, base_search + np.random.normal(0, 10))) for _ in range(days)]
    
    # Identify anomalies and potential catalysts
    anomalies = []
    for i in range(1, days):
        # Check for significant changes in mention volume
        if mention_volume[i] > mention_volume[i-1] * 1.5:
            anomalies.append({
                'date': dates[i],
                'type': 'Volume Spike',
                'magnitude': mention_volume[i] / mention_volume[i-1],
                'description': 'Unusual increase in social media mentions'
            })
        
        # Check for significant sentiment changes
        if abs(sentiment_scores[i] - sentiment_scores[i-1]) > 0.3:
            direction = "positive" if sentiment_scores[i] > sentiment_scores[i-1] else "negative"
            anomalies.append({
                'date': dates[i],
                'type': 'Sentiment Shift',
                'magnitude': abs(sentiment_scores[i] - sentiment_scores[i-1]),
                'description': f'Significant shift to {direction} sentiment'
            })
    
    # Calculate metrics
    current_sentiment = sentiment_scores[-7:]
    current_mentions = mention_volume[-7:]
    previous_sentiment = sentiment_scores[-14:-7] if days >= 14 else sentiment_scores[:7]
    previous_mentions = mention_volume[-14:-7] if days >= 14 else mention_volume[:7]
    
    avg_current_sentiment = sum(current_sentiment) / len(current_sentiment)
    avg_current_mentions = sum(current_mentions) / len(current_mentions)
    avg_previous_sentiment = sum(previous_sentiment) / len(previous_sentiment)
    avg_previous_mentions = sum(previous_mentions) / len(previous_mentions)
    
    sentiment_change = avg_current_sentiment - avg_previous_sentiment
    mention_change_pct = ((avg_current_mentions / avg_previous_mentions) - 1) * 100 if avg_previous_mentions > 0 else 0
    
    # Generate topics and hashtags
    topics = []
    
    # Create sector-specific topics
    if "ZOMATO" in ticker or "SWIGGY" in ticker:
        topics = ["Food Delivery", "Restaurant Reviews", "Delivery Experience", "App Features", "Pricing"]
    elif "BANK" in ticker:
        topics = ["Banking Services", "Financial Products", "Customer Service", "Digital Banking", "Interest Rates"]
    elif "AUTO" in ticker or "MOTORS" in ticker:
        topics = ["Vehicle Safety", "Fuel Efficiency", "New Models", "EV Transition", "Customer Service"]
    elif "TECH" in ticker or "TCS" in ticker or "INFY" in ticker or "WIPRO" in ticker:
        topics = ["IT Services", "Digital Transformation", "Technology Innovation", "Employee Culture", "Global Projects"]
    elif "TELECOM" in ticker or "AIRTEL" in ticker or "JIO" in ticker:
        topics = ["Network Coverage", "Data Plans", "5G Rollout", "Service Quality", "Pricing"]
    else:
        topics = ["Product Quality", "Customer Service", "Brand Value", "Market Position", "Innovation"]
    
    # Generate topic distribution
    topic_distribution = {}
    remaining = 100
    for i, topic in enumerate(topics):
        # Last topic gets the remainder
        if i == len(topics) - 1:
            topic_distribution[topic] = remaining
        else:
            share = random.randint(10, 30)
            if share > remaining:
                share = remaining
            topic_distribution[topic] = share
            remaining -= share
    
    # Generate insight
    if avg_current_sentiment > 0.3 and mention_change_pct > 10:
        insight = f"Strong positive social media momentum for {ticker}"
        sentiment = "positive"
    elif avg_current_sentiment < -0.2 and mention_change_pct > 10:
        insight = f"Increasing negative social media sentiment for {ticker}"
        sentiment = "negative"
    elif avg_current_sentiment > 0.1:
        insight = f"Stable positive social media sentiment for {ticker}"
        sentiment = "positive"
    elif avg_current_sentiment < -0.1:
        insight = f"Concerning negative social sentiment for {ticker}"
        sentiment = "negative"
    else:
        insight = f"Neutral social media sentiment for {ticker}"
        sentiment = "neutral"
    
    # Add anomaly information if present
    if anomalies:
        recent_anomaly = max(anomalies, key=lambda x: x['date'])
        insight += f". Recent {recent_anomaly['type']} detected on {recent_anomaly['date']}."
    
    return {
        'dates': dates,
        'mention_volume': mention_volume,
        'sentiment_scores': sentiment_scores,
        'engagement_rates': engagement_rates,
        'search_trends': search_trends,
        'anomalies': anomalies,
        'avg_sentiment': avg_current_sentiment,
        'avg_mentions': avg_current_mentions,
        'sentiment_change': sentiment_change,
        'mention_change_pct': mention_change_pct,
        'topic_distribution': topic_distribution,
        'insight': insight,
        'sentiment': sentiment
    }

def generate_mobile_location_data(ticker, days=30):
    """
    Generate mobile location data analysis for retail and consumer businesses
    
    Parameters:
    ticker (str): Stock ticker
    days (int): Number of days of data to generate
    
    Returns:
    dict: Simulated mobile location data
    """
    # Tickers with significant consumer retail footprint (stores, etc.)
    retail_presence = {
        'RELIANCE.NS': 0.9,      # Reliance Retail
        'DMART.NS': 0.8,         # DMart
        'TITAN.NS': 0.7,         # Tanishq, etc.
        'JUBLFOOD.NS': 0.7,      # Domino's Pizza
        'TRENT.NS': 0.7,         # Westside, Zara
        'VMART.NS': 0.6,         # V-Mart Retail
        'SHOPERSTOP.NS': 0.6,    # Shoppers Stop
        'ABFRL.NS': 0.7,         # Aditya Birla Fashion
        'INDIGOPNTS.NS': 0.5,    # Indigo Paints stores
        'BATA.NS': 0.6,          # Bata Stores
        'PAGEIND.NS': 0.6,       # Jockey stores
        'ASIANPAINT.NS': 0.5,    # Paint stores
        'BHARTIARTL.NS': 0.5,    # Airtel stores
    }
    
    # Default retail presence for tickers not in the map
    retail_strength = retail_presence.get(ticker, 0.1)
    
    # If the company has very little retail presence, this data might not be relevant
    if retail_strength < 0.3:
        return None
    
    # Create date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    dates = [d.strftime('%Y-%m-%d') for d in date_range]
    
    # Generate foot traffic data (base value depends on retail presence)
    base_traffic = int(10000 * retail_strength)
    # Add day-of-week pattern (higher on weekends)
    foot_traffic = [base_traffic + base_traffic * 0.3 * int(d.weekday() >= 5) for d in date_range]
    # Add random noise
    foot_traffic = [max(0, int(ft + ft * np.random.normal(0, 0.15))) for ft in foot_traffic]
    
    # Generate visit duration in minutes
    if "JUBLFOOD" in ticker:  # Restaurants have shorter visits
        base_duration = 30
    elif "DMART" in ticker:  # Grocery has medium visits
        base_duration = 45
    elif "SHOPERSTOP" in ticker or "TRENT" in ticker:  # Department stores have longer visits
        base_duration = 60
    else:  # Default duration
        base_duration = 40
        
    visit_duration = [max(5, int(base_duration + np.random.normal(0, 5))) for _ in range(days)]
    
    # Generate conversion rates (percentage of visitors who make a purchase)
    if "JUBLFOOD" in ticker:  # Restaurants have high conversion
        base_conversion = 75
    elif "DMART" in ticker:  # Grocery has high conversion
        base_conversion = 70
    elif "TITAN" in ticker:  # Jewelry has lower conversion
        base_conversion = 30
    else:  # Default conversion
        base_conversion = 45
        
    conversion_rates = [max(10, min(95, base_conversion + np.random.normal(0, 5))) for _ in range(days)]
    
    # Generate cross-shopping data (where else do customers shop?)
    # This would be a dictionary of other retailers and percentages
    cross_shopping = {}
    
    if "RELIANCE" in ticker:
        cross_shopping = {
            'DMart': 35,
            'BigBazaar': 40,
            'Lifestyle': 25,
            'Shoppers Stop': 20,
            'Westside': 15
        }
    elif "DMART" in ticker:
        cross_shopping = {
            'Reliance Fresh': 30,
            'BigBazaar': 45,
            'More': 25,
            'Spencers': 20,
            'JioMart': 25
        }
    elif "JUBLFOOD" in ticker:
        cross_shopping = {
            'Pizza Hut': 50,
            'McDonald\'s': 40,
            'KFC': 35,
            'Burger King': 30,
            'Subway': 25
        }
    else:
        cross_shopping = {
            'Competitor 1': 40,
            'Competitor 2': 35,
            'Competitor 3': 25,
            'Competitor 4': 20,
            'Competitor 5': 15
        }
    
    # Generate location heatmap data (which regions have highest traffic)
    # Simulated as top 5 Indian cities with relative percentages
    location_heatmap = {}
    
    if "RELIANCE" in ticker or "DMART" in ticker:  # National chains
        location_heatmap = {
            'Mumbai': 25,
            'Delhi NCR': 22,
            'Bangalore': 15,
            'Hyderabad': 12,
            'Chennai': 10,
            'Other': 16
        }
    elif "JUBLFOOD" in ticker:  # Food chains concentrated in metros
        location_heatmap = {
            'Mumbai': 28,
            'Delhi NCR': 25,
            'Bangalore': 18,
            'Hyderabad': 12,
            'Pune': 8,
            'Other': 9
        }
    else:  # Default distribution
        location_heatmap = {
            'Mumbai': 22,
            'Delhi NCR': 20,
            'Bangalore': 15,
            'Hyderabad': 10,
            'Chennai': 8,
            'Other': 25
        }
    
    # Calculate metrics
    current_traffic = foot_traffic[-7:]
    previous_traffic = foot_traffic[-14:-7] if days >= 14 else foot_traffic[:7]
    
    avg_current_traffic = sum(current_traffic) / len(current_traffic)
    avg_previous_traffic = sum(previous_traffic) / len(previous_traffic)
    
    traffic_change_pct = ((avg_current_traffic / avg_previous_traffic) - 1) * 100 if avg_previous_traffic > 0 else 0
    
    # Generate insight
    if traffic_change_pct > 10:
        insight = f"Significant increase in store foot traffic detected"
        sentiment = "positive"
    elif traffic_change_pct < -10:
        insight = f"Concerning decline in store foot traffic"
        sentiment = "negative"
    else:
        insight = f"Stable store foot traffic patterns"
        sentiment = "neutral"
    
    # Add additional insight based on metrics
    avg_conversion = sum(conversion_rates[-7:]) / 7
    if avg_conversion > 60:
        insight += f". High conversion rate of {avg_conversion:.1f}% indicates strong product appeal."
    elif avg_conversion < 30:
        insight += f". Low conversion rate of {avg_conversion:.1f}% suggests potential issues with product appeal or pricing."
    
    return {
        'dates': dates,
        'foot_traffic': foot_traffic,
        'visit_duration': visit_duration,
        'conversion_rates': conversion_rates,
        'cross_shopping': cross_shopping,
        'location_heatmap': location_heatmap,
        'avg_traffic': avg_current_traffic,
        'traffic_change_pct': traffic_change_pct,
        'insight': insight,
        'sentiment': sentiment
    }

def get_alternative_data(ticker):
    """
    Get all alternative data for a ticker
    
    Parameters:
    ticker (str): Stock ticker
    
    Returns:
    dict: Dictionary with all alternative data sources
    """
    # Basic alternative data
    satellite_data = simulate_satellite_imagery_data(ticker)
    shipping_data = simulate_shipping_data()
    spending_data = generate_credit_card_spending_data(ticker)
    
    # Enhanced alternative data
    weather_data = generate_weather_impact_data(ticker)
    agricultural_satellite_data = generate_agricultural_satellite_data(ticker)
    social_media_data = generate_social_media_trends(ticker)
    mobile_location_data = generate_mobile_location_data(ticker)
    
    return {
        'satellite_data': satellite_data,
        'shipping_data': shipping_data,
        'spending_data': spending_data,
        'weather_data': weather_data,
        'agricultural_satellite_data': agricultural_satellite_data,
        'social_media_data': social_media_data,
        'mobile_location_data': mobile_location_data
    }
