import streamlit as st
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def get_stock_recommendations(risk_profile, investment_horizon, sector_preferences):
    """
    Generate stock and mutual fund recommendations based on risk profile, investment horizon,
    and sector preferences.
    
    Parameters:
    risk_profile (str): Conservative, Moderate, or Aggressive
    investment_horizon (str): Short-term, Medium-term, or Long-term
    sector_preferences (list): List of preferred sectors
    
    Returns:
    dict: Dictionary with stock and fund recommendations
    """
    # Define portfolios based on risk profiles
    portfolios = {
        "Conservative": {
            "Stock Allocation": 30,
            "Bond Allocation": 60,
            "Cash Allocation": 10,
            "Stocks": {
                "Large Cap": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ITC.NS", "HINDUNILVR.NS"],
                "Dividend": ["BPCL.NS", "COALINDIA.NS", "NTPC.NS", "IOC.NS", "POWERGRID.NS"],
                "Defensive": ["NESTLEIND.NS", "BRITANNIA.NS", "MARICO.NS", "DABUR.NS", "COLPAL.NS"]
            },
            "Funds": {
                "Debt": ["SBI Corporate Bond Fund", "HDFC Corporate Bond Fund", "ICICI Prudential Bond Fund"],
                "Hybrid": ["HDFC Hybrid Equity Fund", "ICICI Prudential Equity & Debt Fund"],
                "Index": ["SBI Nifty Index Fund", "UTI Nifty Index Fund"]
            }
        },
        "Moderate": {
            "Stock Allocation": 60,
            "Bond Allocation": 35,
            "Cash Allocation": 5,
            "Stocks": {
                "Large Cap": ["RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS"],
                "Mid Cap": ["HAVELLS.NS", "ESCORTS.NS", "MPHASIS.NS", "AUBANK.NS", "FEDERALBNK.NS"],
                "Growth": ["HCLTECH.NS", "WIPRO.NS", "DIVISLAB.NS", "JUBLFOOD.NS", "ASIANPAINT.NS"]
            },
            "Funds": {
                "Balanced": ["Kotak Equity Hybrid Fund", "Mirae Asset Hybrid Equity Fund"],
                "Multi Cap": ["Axis Multicap Fund", "HDFC Equity Fund", "Kotak Standard Multicap Fund"],
                "Flexi Cap": ["DSP Flexi Cap Fund", "Parag Parikh Flexi Cap Fund"]
            }
        },
        "Aggressive": {
            "Stock Allocation": 80,
            "Bond Allocation": 15,
            "Cash Allocation": 5,
            "Stocks": {
                "Growth": ["TATAMOTORS.NS", "BAJFINANCE.NS", "ADANIENT.NS", "ZOMATO.NS", "NYKAA.NS"],
                "Small Cap": ["CDSL.NS", "LXCHEM.NS", "NAVINFLUOR.NS", "TATAELXSI.NS", "DEEPAKNTR.NS"],
                "Momentum": ["IRCTC.NS", "POLICYBZR.NS", "ZYDUSLIFE.NS", "INDIAMART.NS", "LTTS.NS"]
            },
            "Funds": {
                "Small Cap": ["SBI Small Cap Fund", "Nippon India Small Cap Fund"],
                "Sectoral/Thematic": ["Mirae Asset Great Consumer Fund", "ICICI Prudential Technology Fund"],
                "International": ["Franklin India Feeder - Franklin U.S. Opportunities Fund", "Edelweiss Greater China Equity Off-shore Fund"]
            }
        }
    }
    
    # Adjust based on investment horizon
    horizon_adjustments = {
        "Short-term": {
            "Conservative": {"Bond": 10, "Cash": 10, "Stock": -20},
            "Moderate": {"Bond": 10, "Cash": 5, "Stock": -15},
            "Aggressive": {"Bond": 5, "Cash": 5, "Stock": -10}
        },
        "Medium-term": {
            "Conservative": {"Bond": 0, "Cash": 0, "Stock": 0},
            "Moderate": {"Bond": 0, "Cash": 0, "Stock": 0},
            "Aggressive": {"Bond": 0, "Cash": 0, "Stock": 0}
        },
        "Long-term": {
            "Conservative": {"Bond": -10, "Cash": -5, "Stock": 15},
            "Moderate": {"Bond": -10, "Cash": -5, "Stock": 15},
            "Aggressive": {"Bond": -5, "Cash": -5, "Stock": 10}
        }
    }
    
    # Sector-specific recommendations for Indian market
    sector_stocks = {
        "Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTTS.NS", "MPHASIS.NS"],
        "Banking & Finance": ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS", "HDFCLIFE.NS", "BAJFINANCE.NS"],
        "Healthcare": ["SUNPHARMA.NS", "DRREDDY.NS", "DIVISLAB.NS", "CIPLA.NS", "APOLLOHOSP.NS", "ALKEM.NS", "BIOCON.NS"],
        "Consumer Goods": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "MARICO.NS", "DABUR.NS", "COLPAL.NS"],
        "Automobile": ["TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS"],
        "Energy": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "IOC.NS", "BPCL.NS", "GAIL.NS"],
        "Metals & Mining": ["TATASTEEL.NS", "HINDALCO.NS", "JSWSTEEL.NS", "COALINDIA.NS", "VEDL.NS", "NMDC.NS", "HINDZINC.NS"],
        "Infrastructure": ["LT.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "SHREECEM.NS", "ACC.NS", "AMBUJACEM.NS", "DLF.NS"]
    }
    
    # Sector-specific mutual funds
    sector_funds = {
        "Technology": ["ICICI Prudential Technology Fund", "Tata Digital India Fund", "SBI Technology Opportunities Fund"],
        "Banking & Finance": ["ICICI Prudential Banking & Financial Services Fund", "Nippon India Banking Fund", "Aditya Birla SL Banking & Financial Services Fund"],
        "Healthcare": ["DSP Healthcare Fund", "Nippon India Pharma Fund", "SBI Healthcare Opportunities Fund"],
        "Consumer Goods": ["Nippon India Consumption Fund", "Mirae Asset Great Consumer Fund", "Tata Consumer Fund"],
        "Automobile": ["SBI Magnum Comma Fund", "Aditya Birla SL Manufacturing Equity Fund"],
        "Energy": ["ICICI Prudential Infrastructure Fund", "Kotak Infrastructure & Economic Reform Fund"],
        "Metals & Mining": ["Kotak Resources & Energy Fund", "DSP Natural Resources and New Energy Fund"],
        "Infrastructure": ["Invesco India Infrastructure Fund", "Canara Robeco Infrastructure Fund", "HDFC Infrastructure Fund"]
    }
    
    # Apply adjustments based on investment horizon
    adjusted_portfolio = dict(portfolios[risk_profile])
    horizon_adj = horizon_adjustments[investment_horizon][risk_profile]
    
    adjusted_portfolio["Stock Allocation"] += horizon_adj["Stock"]
    adjusted_portfolio["Bond Allocation"] += horizon_adj["Bond"]
    adjusted_portfolio["Cash Allocation"] += horizon_adj["Cash"]
    
    # Prepare sector-specific recommendations
    stock_recommendations = []
    fund_recommendations = []
    
    # Get stocks for preferred sectors (if specified)
    if sector_preferences:
        for sector in sector_preferences:
            if sector in sector_stocks:
                # Add 2-3 random stocks from each preferred sector
                sample_size = min(3, len(sector_stocks[sector]))
                stock_recommendations.extend(random.sample(sector_stocks[sector], sample_size))
                
                # Add 1-2 mutual funds for each preferred sector
                if sector in sector_funds:
                    fund_sample_size = min(2, len(sector_funds[sector]))
                    fund_recommendations.extend(random.sample(sector_funds[sector], fund_sample_size))
    
    # If not enough sector-specific recommendations, add from the risk profile
    if len(stock_recommendations) < 5:
        for category in adjusted_portfolio["Stocks"]:
            stocks = adjusted_portfolio["Stocks"][category]
            stock_recommendations.extend(stocks[:2])  # Add top 2 from each category
            
            if len(stock_recommendations) >= 10:
                break
    
    if len(fund_recommendations) < 3:
        for category in adjusted_portfolio["Funds"]:
            funds = adjusted_portfolio["Funds"][category]
            fund_recommendations.extend(funds[:1])  # Add top 1 from each category
            
            if len(fund_recommendations) >= 5:
                break
    
    # Ensure we don't have duplicates and limit the number
    stock_recommendations = list(set(stock_recommendations))[:10]  # Limit to 10 unique stocks
    fund_recommendations = list(set(fund_recommendations))[:5]  # Limit to 5 unique funds
    
    # Return the complete recommendation package
    return {
        "asset_allocation": {
            "Stocks": adjusted_portfolio["Stock Allocation"],
            "Bonds": adjusted_portfolio["Bond Allocation"],
            "Cash": adjusted_portfolio["Cash Allocation"]
        },
        "stock_recommendations": stock_recommendations,
        "fund_recommendations": fund_recommendations,
        "risk_profile": risk_profile,
        "investment_horizon": investment_horizon,
        "sector_preferences": sector_preferences
    }

def get_financial_advice(question_type, question_details=None):
    """
    Generate financial advice based on the question type and details
    
    Parameters:
    question_type (str): Type of financial question
    question_details (dict): Additional details for the question
    
    Returns:
    dict: Dictionary with advice and any relevant data
    """
    advice_responses = {
        "investment": [
            "For long-term wealth creation, consider investing regularly through SIPs in equity mutual funds. The power of compounding can turn small regular investments into significant wealth over time.",
            "Always prioritize paying off high-interest debt (like credit cards) before making investments. The guaranteed 'return' from avoiding high interest often exceeds what you could earn from investments.",
            "Consider index funds for core portfolio holdings - they offer low expenses and have historically outperformed many actively managed funds over long periods.",
            "Asset allocation is more important than individual stock selection. Research shows that your mix of stocks, bonds, and cash has greater impact on returns than picking specific securities.",
            "Diversify not just across asset classes but also geographically. Adding international exposure can reduce overall portfolio risk and provide opportunities in faster-growing economies.",
            "When investing in debt instruments in India, consider Systematic Transfer Plans (STPs) as a way to manage interest rate risk and enhance returns."
        ],
        "retirement": [
            "The power of starting early for retirement cannot be overstated. Even small amounts invested in your 20s and 30s can grow significantly by retirement age due to compounding.",
            "Consider the 4% rule when planning retirement: You can typically withdraw 4% of your retirement portfolio annually with minimal risk of running out of money over a 30-year retirement.",
            "Don't ignore inflation in retirement planning. At 6% inflation, your expenses will double approximately every 12 years, meaning you'll need significantly more income later in retirement.",
            "As you approach retirement, consider steadily shifting some assets from growth-oriented investments to income-generating ones, but don't become too conservative too quickly.",
            "For Indian investors, explore the National Pension System (NPS) as part of your retirement strategy. It offers tax benefits and professional management of long-term retirement funds.",
            "Create multiple income streams for retirement including fixed income, dividends, rental income, and potentially part-time work to create stability."
        ],
        "tax": [
            "Take advantage of all available tax-saving instruments under Section 80C such as ELSS funds, PPF, and NPS to reduce your taxable income effectively.",
            "Consider tax-efficient asset location. Hold tax-inefficient investments (like debt funds) in tax-advantaged accounts where possible.",
            "Review your tax-loss harvesting opportunities annually. Strategic selling of investments with losses can offset capital gains and reduce your tax liability.",
            "For equity investments, long-term capital gains exceeding ₹1 lakh are taxed at 10% without indexation benefit. Consider this when timing the sale of profitable investments.",
            "Remember that debt mutual funds held for more than 3 years qualify for long-term capital gains treatment with indexation benefits, potentially lowering your effective tax rate.",
            "When planning for retirement, factor in the tax treatment of different withdrawal sources to create a tax-efficient withdrawal strategy."
        ],
        "debt": [
            "Consider the snowball method (paying smallest debts first) or avalanche method (paying highest interest debts first) for debt reduction. The avalanche method saves more money, but the snowball method often provides psychological wins that keep you motivated.",
            "If you have multiple high-interest debts, look into debt consolidation options that could lower your overall interest rate and simplify payments.",
            "When taking a home loan, a longer tenure lowers EMI but increases total interest cost substantially. Consider taking a long-term loan but making additional principal payments when possible.",
            "For student loans in India, evaluate the tax benefits under Section 80E for interest paid, which can make education debt more manageable from a cash flow perspective.",
            "Avoid using credit cards for cash advances, as they typically carry higher interest rates and begin accruing interest immediately without a grace period.",
            "When evaluating loan offers, look beyond the interest rate to the annual percentage rate (APR), which includes fees and gives a more accurate picture of true cost."
        ],
        "budgeting": [
            "Consider the 50/30/20 rule for budgeting: allocate 50% of income to needs, 30% to wants, and 20% to savings and debt repayment.",
            "Track all expenses for at least one month to identify spending patterns and areas where you can potentially cut back. Many are surprised to find how much goes to small, recurring expenses.",
            "Set up automatic transfers to savings accounts on payday to enforce the 'pay yourself first' principle, making saving a priority rather than an afterthought.",
            "Review and cancel unused subscriptions regularly. These small recurring charges can add up to significant amounts over time.",
            "Build an emergency fund covering 3-6 months of essential expenses before focusing on other financial goals. This provides critical financial resilience.",
            "When creating a budget, include irregular expenses (like vehicle maintenance or annual insurance premiums) by dividing the annual cost into monthly allocations."
        ],
        "insurance": [
            "For life insurance, term insurance generally provides the most coverage for the lowest cost. Consider term insurance over traditional endowment policies if pure protection is the goal.",
            "The right amount of life insurance typically covers 10x your annual income, plus specific obligations like outstanding debts and future education expenses.",
            "Critical illness insurance deserves consideration alongside regular health insurance, as it provides a lump sum upon diagnosis regardless of actual medical expenses.",
            "When choosing health insurance, focus on coverage limits, network hospitals, waiting periods, and exclusions rather than just the premium amount.",
            "For two-wheeler and car insurance, third-party liability coverage is legally mandatory in India, but comprehensive coverage is often worth the additional premium.",
            "Consider a family floater health insurance policy rather than individual policies to potentially reduce premiums while maintaining adequate coverage for the entire family."
        ],
        "specific": {
            # Specific question responses will be generated based on the question
        }
    }
    
    if question_type == "specific" and question_details:
        # Generate specific advice based on the question details
        query = question_details.get("query", "").lower()
        advice = "I'd need more specific information to provide personalized advice on this topic."
        
        if "stock" in query or "invest" in query:
            advice = "When considering individual stocks, focus on companies with strong fundamentals, consistent growth, and good corporate governance. However, remember that individual stock selection carries higher risk than diversified investments like mutual funds or ETFs."
        elif "gold" in query or "silver" in query:
            advice = "Gold can be a good hedge against inflation and currency depreciation. For Indian investors, consider Sovereign Gold Bonds which offer interest in addition to potential price appreciation, eliminating storage concerns and offering tax advantages."
        elif "crypto" in query or "bitcoin" in query:
            advice = "Cryptocurrency investments are highly speculative and volatile. If you're interested in this asset class, consider allocating only a small portion of your portfolio (5% or less) that you can afford to lose completely."
        elif "education" in query or "college" in query:
            advice = "For education funding, consider starting early with a dedicated education SIP. Educational expenses in India are rising at approximately 10-12% annually, well above general inflation."
        elif "home" in query or "house" in query or "property" in query:
            advice = "When considering property investment, remember that real estate ties up significant capital and has high transaction costs. The rental yield in many Indian cities is only 2-3%, making it important to evaluate whether better returns might be available elsewhere."
        elif "retire" in query or "pension" in query:
            advice = "For retirement planning in India, consider a mix of EPF/PPF, NPS, and equity mutual funds. The rule of thumb is that you'll need approximately 80% of your pre-retirement income to maintain your lifestyle in retirement."
        elif "mutual fund" in query or "sip" in query:
            advice = "SIPs (Systematic Investment Plans) are an excellent way to invest in mutual funds as they enforce discipline, take advantage of rupee cost averaging, and reduce the impact of market volatility over time."
        
        return {"advice": advice, "query": query}
    else:
        # Randomly select advice from the appropriate category
        advice_list = advice_responses.get(question_type, advice_responses["investment"])
        return {"advice": random.choice(advice_list), "category": question_type}

def generate_budget_recommendation(income, current_expenses):
    """
    Generate a personalized budget recommendation based on income and current expenses
    
    Parameters:
    income (float): Monthly income
    current_expenses (dict): Current expense breakdown
    
    Returns:
    dict: Recommended budget breakdown and insights
    """
    # Standard budget allocation (based on 50/30/20 rule with Indian adjustments)
    standard_allocations = {
        "Housing": 25,  # Rent/mortgage, maintenance, property tax
        "Utilities": 5,  # Electricity, water, gas, internet, phone
        "Food": 12,  # Groceries and dining out
        "Transportation": 7,  # Fuel, public transport, vehicle maintenance
        "Healthcare": 5,  # Health insurance, medications, doctor visits
        "Personal": 10,  # Clothing, personal care, entertainment
        "Education": 5,  # Courses, books, children's education
        "Savings": 20,  # Emergency fund, investments, retirement
        "Debt Repayment": 8,  # Loan EMIs, credit card payments
        "Others": 3  # Miscellaneous expenses
    }
    
    # Calculate recommended amounts based on income
    recommended_budget = {}
    for category, percentage in standard_allocations.items():
        recommended_budget[category] = round(income * percentage / 100, 2)
    
    # Analyze current vs. recommended
    budget_analysis = {}
    total_current = sum(current_expenses.values())
    
    for category in standard_allocations.keys():
        current = current_expenses.get(category, 0)
        recommended = recommended_budget[category]
        
        # Calculate difference and status
        difference = current - recommended
        percentage_difference = (difference / recommended * 100) if recommended > 0 else 0
        
        if category == "Savings":
            status = "Good" if current >= recommended else "Needs Attention"
        else:
            status = "Good" if current <= recommended else "Needs Attention"
        
        budget_analysis[category] = {
            "current": current,
            "recommended": recommended,
            "difference": difference,
            "percentage_difference": percentage_difference,
            "status": status
        }
    
    # Generate insights
    insights = []
    saving_status = budget_analysis["Savings"]["status"]
    if saving_status == "Needs Attention":
        insights.append("Your savings rate is below the recommended 20%. Consider increasing your savings to build long-term wealth and financial security.")
    
    # Find the highest overspending categories
    overspending = []
    for category, analysis in budget_analysis.items():
        if category != "Savings" and analysis["status"] == "Needs Attention":
            overspending.append((category, analysis["difference"]))
    
    overspending.sort(key=lambda x: x[1], reverse=True)
    if overspending:
        top_overspend = overspending[0][0]
        insights.append(f"You're spending significantly more than recommended on {top_overspend}. Consider ways to reduce expenses in this category.")
    
    # Check if total expenses exceed income
    if total_current > income:
        insights.append("Your total expenses exceed your income, which is creating a deficit. Focus on reducing expenses or increasing income to achieve financial stability.")
    
    # Check for balanced distribution
    essentials = sum(current_expenses.get(cat, 0) for cat in ["Housing", "Utilities", "Food", "Transportation", "Healthcare"])
    essentials_percent = (essentials / income) * 100 if income > 0 else 0
    
    if essentials_percent > 60:
        insights.append("More than 60% of your income is going toward essential expenses. This may limit financial flexibility. Consider ways to reduce essential costs if possible.")
    
    # Add a positive insight if some categories are well managed
    well_managed = [category for category, analysis in budget_analysis.items() 
                   if analysis["status"] == "Good" and category != "Savings"]
    if well_managed:
        insights.append(f"You're managing your {well_managed[0]} budget well. Keep up the good work in this area!")
    
    # Generate allocation guidance for the future
    future_allocation = dict(standard_allocations)
    
    # Adjust future allocation based on current situation
    if essentials_percent > 60:
        # If essentials are high, we can't reduce them immediately
        future_allocation["Savings"] = max(10, standard_allocations["Savings"] - 5)
        future_allocation["Personal"] = max(5, standard_allocations["Personal"] - 5)
    elif total_current > income:
        # If expenses exceed income, suggest more aggressive savings
        future_allocation["Personal"] = max(5, standard_allocations["Personal"] - 5)
        categories = ["Housing", "Food", "Transportation", "Utilities"]
        for cat in categories:
            future_allocation[cat] = max(future_allocation[cat] - 1, 0)
        future_allocation["Savings"] = standard_allocations["Savings"]
    
    future_budget = {}
    for category, percentage in future_allocation.items():
        future_budget[category] = round(income * percentage / 100, 2)
    
    return {
        "recommended_budget": recommended_budget,
        "budget_analysis": budget_analysis,
        "insights": insights,
        "future_budget": future_budget
    }

def simulate_investment_growth(initial_investment, monthly_contribution, years, expected_return, inflation_rate=6):
    """
    Simulate investment growth over time with monthly contributions
    
    Parameters:
    initial_investment (float): Starting investment amount
    monthly_contribution (float): Monthly contribution amount
    years (int): Number of years to simulate
    expected_return (float): Expected annual return (%)
    inflation_rate (float): Expected inflation rate (%)
    
    Returns:
    dict: Simulation results
    """
    # Convert rates to monthly
    monthly_return = (1 + expected_return/100) ** (1/12) - 1
    monthly_inflation = (1 + inflation_rate/100) ** (1/12) - 1
    
    # Initialize arrays
    months = years * 12
    investment_value = np.zeros(months + 1)
    investment_value[0] = initial_investment
    total_invested = np.zeros(months + 1)
    total_invested[0] = initial_investment
    real_value = np.zeros(months + 1)
    real_value[0] = initial_investment
    
    # Perform simulation
    for i in range(1, months + 1):
        # Add monthly contribution
        investment_value[i] = investment_value[i-1] * (1 + monthly_return) + monthly_contribution
        
        # Track total invested
        total_invested[i] = total_invested[i-1] + monthly_contribution
        
        # Calculate real value (adjusted for inflation)
        real_value[i] = investment_value[i] / ((1 + monthly_inflation) ** i)
    
    # Extract values at yearly points
    yearly_points = np.array([0] + [i*12 for i in range(1, years+1)])
    yearly_values = investment_value[yearly_points]
    yearly_invested = total_invested[yearly_points]
    yearly_real_values = real_value[yearly_points]
    
    # Calculate returns
    total_contributions = initial_investment + monthly_contribution * months
    final_value = investment_value[-1]
    real_final_value = real_value[-1]
    total_return = (final_value / total_contributions - 1) * 100
    
    return {
        "years": list(range(years + 1)),
        "investment_value": yearly_values.tolist(),
        "real_value": yearly_real_values.tolist(),
        "total_invested": yearly_invested.tolist(),
        "total_return": total_return,
        "final_value": final_value,
        "real_final_value": real_final_value,
        "total_contributions": total_contributions
    }

def generate_fortune_cookie():
    """
    Generate a daily financial wisdom fortune cookie with detailed Indian market relevance
    
    Returns:
    dict: Fortune cookie with wisdom, author information, explanation, application tips,
          lucky numbers, and Indian market context
    """
    fortunes = [
        {
            "wisdom": "A budget is telling your money where to go instead of wondering where it went.",
            "author": "Dave Ramsey",
            "author_info": "American financial author and radio host known for his debt-free living philosophy",
            "explanation": "Proactive financial planning gives you control over your money rather than constantly reacting to financial pressures. Creating a budget is like creating a roadmap for your financial journey.",
            "application": "Set aside specific time each month to review and update your budget, allocating funds to savings, investments, necessities, and discretionary spending before expenses arise.",
            "numbers": [8, 14, 21, 36, 42],
            "number_meaning": "These numbers correspond to saving rates (%) that might be appropriate at different life stages."
        },
        {
            "wisdom": "Do not save what is left after spending, but spend what is left after saving.",
            "author": "Warren Buffett",
            "author_info": "One of the world's most successful investors with a net worth over $100 billion, known for value investing",
            "explanation": "Prioritizing savings before spending ensures wealth accumulation. When you save first, you adapt your lifestyle to what remains rather than trying to save from what's left over.",
            "application": "Set up automatic transfers to savings/investment accounts on salary day before you have a chance to spend that money on discretionary items.",
            "numbers": [3, 17, 24, 33, 45],
            "number_meaning": "These numbers represent key ages for financial milestones in the typical investor's journey."
        },
        {
            "wisdom": "It's not how much money you make, but how much money you keep, how hard it works for you, and how many generations you keep it for.",
            "author": "Robert Kiyosaki",
            "author_info": "Author of 'Rich Dad Poor Dad' and advocate for financial education and asset acquisition",
            "explanation": "Income alone doesn't create wealth; retained earnings, investment returns, and long-term preservation across generations are what build true wealth.",
            "application": "Focus on increasing your savings rate and investment returns rather than just chasing a higher salary. Consider generational wealth strategies like family trusts.",
            "numbers": [7, 11, 18, 29, 41],
            "number_meaning": "These represent approximate percentages of income that should be saved at progressive income levels."
        },
        {
            "wisdom": "The stock market is a device for transferring money from the impatient to the patient.",
            "author": "Warren Buffett",
            "author_info": "Chairman and CEO of Berkshire Hathaway who has maintained a long-term investment perspective for over 60 years",
            "explanation": "Short-term traders often lose to those with long-term perspectives. The market rewards those who can withstand volatility and think in decades, not days.",
            "application": "Avoid checking your portfolio daily. Create an investment policy statement that commits you to holding quality investments through market cycles.",
            "numbers": [5, 12, 22, 37, 48],
            "number_meaning": "These represent ideal holding periods (in years) for different types of investment assets."
        },
        {
            "wisdom": "The four most dangerous words in investing are: 'this time it's different.'",
            "author": "Sir John Templeton",
            "author_info": "Legendary global investor and mutual fund pioneer known for buying during times of maximum pessimism",
            "explanation": "Investment bubbles are always justified by claims that historical patterns no longer apply, but market fundamentals ultimately reassert themselves.",
            "application": "When everyone claims traditional valuations don't matter anymore (like during the dot-com bubble or cryptocurrency frenzies), be especially cautious.",
            "numbers": [4, 13, 26, 31, 44],
            "number_meaning": "These numbers correspond to major market downturns (in percentage terms) that have historically represented buying opportunities."
        },
        {
            "wisdom": "Financial peace isn't the acquisition of stuff. It's learning to live on less than you make, so you can give money back and have money to invest.",
            "author": "Dave Ramsey",
            "author_info": "Creator of the 'Financial Peace University' program that has helped millions get out of debt",
            "explanation": "True financial security comes from spending less than you earn, not from possessions. This creates a surplus for both generosity and investments.",
            "application": "Calculate your personal profit margin (income minus expenses) and work to increase it through mindful spending rather than just income growth.",
            "numbers": [2, 9, 19, 27, 39],
            "number_meaning": "These represent suggested percentages to allocate to investments, charitable giving, and essential vs. discretionary spending."
        },
        {
            "wisdom": "An investment in knowledge pays the best interest.",
            "author": "Benjamin Franklin",
            "author_info": "Founding Father, polymath, and self-made businessman who valued continuous learning",
            "explanation": "Education and skill development provide the highest return on investment over time, exceeding that of financial assets alone.",
            "application": "Budget for ongoing education beyond formal schooling. Invest time and money in learning about financial markets, business, and developing valuable skills.",
            "numbers": [1, 15, 23, 32, 47],
            "number_meaning": "These figures represent optimal percentages of income to invest in different forms of personal and professional development."
        },
        {
            "wisdom": "The individual investor should act consistently as an investor and not as a speculator.",
            "author": "Benjamin Graham",
            "author_info": "Known as the father of value investing and Warren Buffett's mentor, author of 'The Intelligent Investor'",
            "explanation": "Investors focus on the underlying business value and expect returns from that value; speculators focus on price movements divorced from fundamentals.",
            "application": "Before buying a stock, write down why you're buying it and what would justify selling it based on business fundamentals, not price action alone.",
            "numbers": [6, 16, 25, 34, 43],
            "number_meaning": "These numbers represent key financial ratios to consider when evaluating investment opportunities."
        },
        {
            "wisdom": "The big money is not in the buying and selling, but in the waiting.",
            "author": "Charlie Munger",
            "author_info": "Vice Chairman of Berkshire Hathaway and Warren Buffett's long-time business partner",
            "explanation": "Significant wealth is created through compounding over time. Frequent trading creates costs and taxes that erode returns.",
            "application": "Calculate the long-term impact of compounding on your investments at various rates of return to appreciate the value of patience.",
            "numbers": [10, 20, 30, 40, 50],
            "number_meaning": "These represent the value multiplier effect of compounding at 7% over these year periods."
        },
        {
            "wisdom": "Risk comes from not knowing what you're doing.",
            "author": "Warren Buffett",
            "author_info": "Renowned for his risk-management approach and focus on investing within his 'circle of competence'",
            "explanation": "True risk isn't market volatility but lack of knowledge about your investments. Understanding what you own reduces actual risk regardless of price movements.",
            "application": "Only invest in businesses and asset classes you thoroughly understand. For everything else, use low-cost index funds rather than stock picking.",
            "numbers": [3, 9, 27, 35, 46],
            "number_meaning": "These numbers represent risk management metrics used in portfolio construction."
        },
        {
            "wisdom": "In investing, what is comfortable is rarely profitable.",
            "author": "Robert Arnott",
            "author_info": "Founder of Research Affiliates and pioneer in fundamental indexing strategies",
            "explanation": "The most profitable investments are often uncomfortable to make - either because they're out of favor, misunderstood, or represent novel approaches.",
            "application": "Develop a contrarian mindset. When an investment thesis makes you uncomfortable but the data supports it, that discomfort may signal opportunity.",
            "numbers": [7, 13, 21, 32, 38],
            "number_meaning": "These figures represent historical contrarian indicators that have signaled potential market bottoms."
        },
        {
            "wisdom": "Compound interest is the eighth wonder of the world. He who understands it, earns it; he who doesn't, pays it.",
            "author": "Albert Einstein",
            "author_info": "Nobel Prize-winning physicist who appreciated the mathematical power of exponential growth",
            "explanation": "The snowballing effect of returns-on-returns creates exponential growth that becomes increasingly powerful over time, working either for you (investments) or against you (debt).",
            "application": "Calculate the 'Rule of 72' (72 divided by interest rate = years to double money) to understand how your investments or debts will grow over time.",
            "numbers": [5, 15, 25, 35, 45],
            "number_meaning": "These represent the approximate number of years required to double your money at different interest/return rates."
        },
        {
            "wisdom": "The goal of retirement is to live off your assets, not on them.",
            "author": "Frank Eberhart",
            "author_info": "Financial advisor known for his focus on sustainable retirement income strategies",
            "explanation": "Sustainable retirement means spending investment returns while preserving principal, rather than gradually depleting your savings.",
            "application": "Calculate your required retirement corpus by dividing your annual expenses by your expected withdrawal rate (typically 3-4% for sustainability).",
            "numbers": [2, 12, 20, 30, 49],
            "number_meaning": "These figures relate to sustainable withdrawal rates (as decimals) for different retirement time horizons."
        },
        {
            "wisdom": "You must gain control over your money or the lack of it will forever control you.",
            "author": "Dave Ramsey", 
            "author_info": "Popular financial advisor who rebuilt his wealth after bankruptcy through disciplined money management",
            "explanation": "Without deliberate management, money problems dictate your choices and create stress. Taking control creates freedom and options.",
            "application": "Track every rupee for one month to understand exactly where your money goes, then create a proactive plan for future spending and saving.",
            "numbers": [4, 11, 28, 36, 44],
            "number_meaning": "These represent key debt-to-income ratios that indicate different levels of financial health and control."
        },
        {
            "wisdom": "The first rule of investment is don't lose money. The second rule is don't forget the first rule.",
            "author": "Warren Buffett",
            "author_info": "Known for his focus on capital preservation and avoiding permanent loss through careful analysis",
            "explanation": "Avoiding losses is more important than making gains because losses require larger subsequent gains to recover. A 50% loss requires a 100% gain just to break even.",
            "application": "Before considering potential returns, analyze what could go wrong with an investment and how you might lose money permanently (not just temporarily).",
            "numbers": [8, 16, 24, 31, 47],
            "number_meaning": "These numbers show how much return (%) you need to recover from different levels of investment loss."
        },
        {
            "wisdom": "It's not your salary that makes you rich, it's your spending habits.",
            "author": "Charles A. Jaffe",
            "author_info": "Financial columnist and author known for practical personal finance advice",
            "explanation": "Even high income can't create wealth if spending exceeds earnings. Conversely, modest incomes can build substantial wealth with disciplined spending.",
            "application": "Calculate your savings rate (percentage of income saved) rather than focusing solely on income or total savings amount.",
            "numbers": [6, 14, 22, 38, 42],
            "number_meaning": "These represent target savings rates (%) that can lead to financial independence at different ages."
        },
        {
            "wisdom": "Markets can remain irrational longer than you can remain solvent.",
            "author": "John Maynard Keynes",
            "author_info": "Influential economist who was also a successful investor for Cambridge University's endowment",
            "explanation": "Even if you correctly identify a market mispricing, prices can move against you for extended periods before eventually correcting, potentially causing financial ruin.",
            "application": "Always maintain adequate liquidity and avoid excessive leverage, even when your investment thesis seems certain. Position sizing is as important as being right.",
            "numbers": [9, 18, 27, 39, 48],
            "number_meaning": "These represent maximum position sizes (%) for investments with different risk profiles."
        },
        {
            "wisdom": "A successful man is one who can lay a firm foundation with the bricks others have thrown at him.",
            "author": "David Brinkley",
            "author_info": "Longtime American news anchor known for his resilience and adaptability in broadcasting",
            "explanation": "Financial and business success often comes from converting setbacks and criticism into opportunities for growth and improvement.",
            "application": "Keep a financial mistakes journal to document lessons learned from errors, ensuring you extract maximum value from negative experiences.",
            "numbers": [1, 17, 23, 33, 41],
            "number_meaning": "These figures represent key decision points (in years) for evaluating and potentially pivoting financial strategies."
        },
        {
            "wisdom": "Investment success doesn't come from 'buying good things,' but rather from 'buying things well.'",
            "author": "Howard Marks",
            "author_info": "Co-founder of Oaktree Capital Management known for his insightful market memos",
            "explanation": "The quality of an investment matters less than the price paid relative to value. Even great companies or assets make poor investments if purchased at excessive valuations.",
            "application": "Develop valuation models for your investments that help you determine not just what to buy, but at what price to buy it.",
            "numbers": [7, 19, 26, 34, 43],
            "number_meaning": "These numbers represent key valuation metrics used for different asset classes (as multiples or percentages)."
        },
        {
            "wisdom": "Know what you own, and know why you own it.",
            "author": "Peter Lynch",
            "author_info": "Legendary Fidelity Magellan Fund manager who advocated investing in what you understand",
            "explanation": "Successful investing requires understanding both what you're buying and your specific reason for owning it. This clarity helps maintain conviction during market volatility.",
            "application": "Write an investment thesis for each holding in your portfolio, and revisit it quarterly to ensure the original reasons for purchase still apply.",
            "numbers": [5, 10, 29, 37, 46],
            "number_meaning": "These represent optimal portfolio review frequencies (in days) for different investment strategies."
        },
        {
            "wisdom": "The stock market is filled with individuals who know the price of everything, but the value of nothing.",
            "author": "Philip Fisher",
            "author_info": "Influential growth investor and author of 'Common Stocks and Uncommon Profits'",
            "explanation": "Many market participants focus entirely on price movements and charts without understanding the underlying business value, creating opportunities for those who analyze fundamentals.",
            "application": "Develop a process for estimating intrinsic value based on business fundamentals rather than relying on technical analysis or price momentum.",
            "numbers": [12, 19, 25, 37, 42],
            "number_meaning": "These represent quality metrics used in growth investing frameworks (as percentages or multiples)."
        },
        {
            "wisdom": "The time of maximum pessimism is the best time to buy, and the time of maximum optimism is the best time to sell.",
            "author": "Sir John Templeton",
            "author_info": "Pioneer of global investing who made his fortune buying European stocks during WWII",
            "explanation": "The greatest investment opportunities arise when sentiment is extremely negative, while the greatest risks develop when everyone is optimistic.",
            "application": "Develop a contrarian indicator dashboard based on sentiment measures, fund flows, and valuation metrics to identify extreme market conditions.",
            "numbers": [15, 23, 31, 40, 55],
            "number_meaning": "These correspond to extreme sentiment readings that have historically marked major market turning points."
        },
        {
            "wisdom": "Far more money has been lost by investors trying to anticipate corrections, than lost in the corrections themselves.",
            "author": "Peter Lynch",
            "author_info": "Generated 29% annual returns while managing Fidelity's Magellan Fund from 1977 to 1990",
            "explanation": "Attempting to time market downturns often leads to selling prematurely and missing subsequent gains, which typically exceeds the losses during actual corrections.",
            "application": "Calculate how your portfolio would have performed if you had missed just the 10 best market days over the past decade to appreciate the risk of market timing.",
            "numbers": [3, 11, 17, 28, 36],
            "number_meaning": "These represent the average percentage of annual returns typically generated in just a handful of days each year."
        },
        {
            "wisdom": "The investor's chief problem - and even his worst enemy - is likely to be himself.",
            "author": "Benjamin Graham",
            "author_info": "Father of value investing whose protégés include Warren Buffett and numerous other successful investors",
            "explanation": "Emotional responses like fear and greed lead to poor investment decisions. Systematic approaches help overcome these psychological biases.",
            "application": "Create mechanical rebalancing rules and investment criteria that remove emotion from your decision-making process.",
            "numbers": [4, 9, 22, 38, 47],
            "number_meaning": "These represent common risk tolerance scores and their implications for portfolio construction."
        },
        {
            "wisdom": "I'm a great believer in solving hard problems by using a checklist.",
            "author": "Charlie Munger",
            "author_info": "Multidisciplinary thinker known for applying mental models from various disciplines to investing",
            "explanation": "Systematic decision frameworks help avoid common errors by ensuring all relevant factors are considered before making investment decisions.",
            "application": "Develop a pre-investment checklist covering business quality, management, financial health, valuation, and potential risks to apply to each investment.",
            "numbers": [6, 13, 21, 25, 31],
            "number_meaning": "These represent the optimal number of criteria to include in different types of investment checklists."
        }
    ]
    
    # Use a hash of the current date as a seed for consistent daily fortune
    today = datetime.now().strftime("%Y-%m-%d")
    seed = sum(ord(c) for c in today)
    random.seed(seed)
    
    # Select a fortune cookie wisdom for today
    fortune = random.choice(fortunes)
    
    # Add detailed Indian stock market context to the fortune
    indian_contexts = [
        {
            "context": "This wisdom applies especially well to India's dynamic market environment, where retail investors often chase momentum stocks without understanding fundamentals.",
            "nifty_application": "When evaluating Nifty stocks, focus on companies with consistent dividend histories and strong return on equity rather than just recent price movements.",
            "indian_example": "Retail investors who maintained discipline during the 2020 Covid crash were rewarded with nearly 140% returns on the Nifty over the following 18 months."
        },
        {
            "context": "Consider this in the context of India's growth-driven economy, where long-term equity investments have historically outperformed traditional fixed deposits.",
            "nifty_application": "Historical data shows investing in a Nifty index fund has outperformed FD returns by approximately 5-7% annually over 10+ year periods.",
            "indian_example": "Patient Indian investors who stayed invested through the 2008 financial crisis saw their portfolios recover completely by 2010 and substantially grow thereafter."
        },
        {
            "context": "Particularly relevant for investors in the Sensex and Nifty markets, where emotional decision-making often leads to buying at market peaks and selling during corrections.",
            "nifty_application": "Create a systematic investment plan (SIP) for Nifty index funds rather than trying to time market entries and exits.",
            "indian_example": "Data from AMFI shows that investors who maintained SIPs through the 2016 demonetization uncertainty were rewarded with substantial returns in subsequent years."
        },
        {
            "context": "A principle that has served successful Indian investors like Rakesh Jhunjhunwala well throughout their investing journeys in both bull and bear markets.",
            "nifty_application": "Study the investment philosophies of successful Indian investors who have navigated multiple market cycles, like Ramdeo Agrawal or Raamdeo Agrawal.",
            "indian_example": "Rakesh Jhunjhunwala's long-term holding of Titan Company illustrates the power of identifying quality businesses and holding them through market fluctuations."
        },
        {
            "context": "Apply this wisdom to navigate both bull and bear phases in Indian markets, where volatility is often higher than in developed markets.",
            "nifty_application": "The India VIX (Volatility Index) can help gauge market sentiment extremes that may signal potential turning points in the Nifty.",
            "indian_example": "Investors who added quality stocks during the March 2020 market crash when the India VIX peaked at 83.6 saw exceptional returns in the subsequent recovery."
        },
        {
            "context": "A timeless principle for investors in both developed and emerging markets like India, where fundamental analysis often takes a backseat to market sentiment.",
            "nifty_application": "Focus on companies with strong governance practices and consistent capital allocation rather than following market trends.",
            "indian_example": "Well-governed Indian companies like HDFC Bank, Asian Paints, and TCS have delivered exceptional long-term shareholder returns through multiple market cycles."
        },
        {
            "context": "Remember this as you build your portfolio of Indian equities and bonds, balancing growth opportunities with capital preservation.",
            "nifty_application": "Consider the Nifty Next 50 for exposure to emerging large caps while maintaining core positions in established Nifty 50 companies.",
            "indian_example": "A balanced portfolio of 60% equity (Nifty 50 and Nifty Next 50) and 40% high-quality debt has historically provided good risk-adjusted returns for Indian investors."
        },
        {
            "context": "This perspective has guided many of India's most successful business leaders and investors through volatile market conditions.",
            "nifty_application": "Study the management philosophy of leading Indian companies like HDFC, TCS, and Infosys to understand how they've navigated business cycles.",
            "indian_example": "When SEBI implemented significant mutual fund regulatory changes in 2018, patient investors who understood the long-term benefits avoided knee-jerk reactions."
        },
        {
            "context": "Especially important in India's retail-dominated market, where herd behavior often drives short-term price movements away from fundamental values.",
            "nifty_application": "Use the Nifty PE ratio relative to historical averages as a broad valuation guide for timing lump-sum investments or increasing SIP amounts.",
            "indian_example": "The Nifty's PE ratio exceeded 28 before major corrections in 2000, 2008, and early 2020, offering a valuation warning sign for disciplined investors."
        },
        {
            "context": "Critical perspective for navigating India's capital markets, which have delivered among the best long-term returns globally despite significant short-term volatility.",
            "nifty_application": "Compare Nifty drawdowns and recovery periods historically to build realistic expectations and maintain conviction during market corrections.",
            "indian_example": "Despite experiencing 9 major corrections of 15%+ since 2000, the Nifty has delivered approximately 12-14% annualized returns to long-term investors."
        }
    ]
    
    fortune["indian_context"] = random.choice(indian_contexts)
    
    # Reset random seed after generating the fortune
    random.seed()
    
    return fortune

def chatbot_response(user_query):
    """
    Generate a detailed response from the financial advice chatbot
    
    Parameters:
    user_query (str): The user's query
    
    Returns:
    str: Chatbot response
    """
    # Map user queries to advice categories
    query = user_query.lower()
    
    # Check for specific query types
    if any(word in query for word in ["invest", "stock", "market", "mutual fund", "sip", "equity", "bond"]):
        category = "investment"
        extended_info = """
### Investment Insights for Indian Investors

Indian markets have unique characteristics that investors should be aware of:

1. **High Growth Potential**: India's economy is among the fastest-growing major economies, offering significant long-term investment opportunities.

2. **Market Volatility**: Indian markets can experience higher volatility than developed markets, making disciplined investing essential.

3. **Sectoral Opportunities**: Sectors like IT, pharma, financial services, and consumer goods have historically performed well in the Indian context.

4. **SIP Advantage**: Systematic Investment Plans (SIPs) are particularly effective in the Indian market to navigate volatility through rupee-cost averaging.

5. **Tax Efficiency**: Consider the tax implications of different investment vehicles. ELSS funds offer tax benefits under Section 80C while providing equity exposure.

Remember that diversification across asset classes and investment styles is key to building resilience in your portfolio.
        """
    elif any(word in query for word in ["retire", "retirement", "pension", "old age"]):
        category = "retirement"
        extended_info = """
### Retirement Planning in the Indian Context

Planning for retirement in India requires consideration of several factors:

1. **Inflation Impact**: India's inflation rate has historically been higher than many developed economies, requiring greater growth in retirement corpus.

2. **NPS Benefits**: The National Pension System offers tax benefits and professional management, making it an important retirement planning tool.

3. **EPF Foundation**: Employee Provident Fund should be the foundation of retirement planning, but likely insufficient on its own.

4. **Health Insurance**: As healthcare costs rise with age, adequate health insurance is a critical component of retirement planning.

5. **Alternative Income Sources**: Consider building multiple income streams like rental income, dividends, and potentially part-time consultancy.

With improving life expectancy in India, plan for at least 25-30 years of post-retirement life when calculating your retirement corpus.
        """
    elif any(word in query for word in ["tax", "income tax", "capital gain", "tds", "return", "itr"]):
        category = "tax"
        extended_info = """
### Tax Planning Strategies for Indian Investors

Effective tax planning can significantly enhance your investment returns:

1. **Section 80C Investments**: Maximize your ₹1.5 lakh deduction through ELSS funds, PPF, NPS, and other eligible investments.

2. **LTCG on Equity**: Long-term capital gains on equity exceeding ₹1 lakh are taxed at 10% without indexation benefits.

3. **Debt Fund Taxation**: Debt fund gains held for over 3 years qualify for LTCG with indexation benefits at 20%, potentially more favorable than FD interest taxation.

4. **NPS Tax Benefits**: Additional ₹50,000 deduction under Section 80CCD(1B) beyond the 80C limit.

5. **HRA and Home Loan Benefits**: Consider the tax advantages of claiming HRA exemption or home loan interest deduction under Section 24.

Remember that tax planning should be a year-round activity rather than a last-minute rush in March.
        """
    elif any(word in query for word in ["loan", "debt", "credit", "emi", "mortgage", "interest"]):
        category = "debt"
        extended_info = """
### Debt Management Strategies for Indian Households

Managing debt effectively is crucial for financial health:

1. **Home Loan Optimization**: Consider a balance between tenure and EMI. A longer tenure reduces EMI but increases total interest cost.

2. **Pre-payment Strategy**: Use annual bonuses or windfalls to make partial prepayments on high-interest debts like personal loans.

3. **Credit Card Management**: Always pay credit card bills in full as the interest rates can exceed 40% annually, one of the highest debt costs.

4. **Education Loan Benefits**: Take advantage of the tax deduction on education loan interest under Section 80E, which has no upper limit.

5. **Debt Consolidation**: Consider consolidating multiple high-interest loans into a single lower-interest loan, potentially saving on interest costs.

The 40/20/40 rule suggests allocating 40% of extra funds to debt repayment, 20% to savings, and 40% to lifestyle, helping balance debt reduction with other financial priorities.
        """
    elif any(word in query for word in ["budget", "spend", "expense", "save", "saving"]):
        category = "budgeting"
        extended_info = """
### Budgeting Principles for Indian Households

Effective budgeting adapts universal principles to the Indian context:

1. **Zero-Based Budgeting**: Assign every rupee a purpose before the month begins, ensuring all income is allocated intentionally.

2. **Festival Planning**: Set aside funds monthly for major festival expenses rather than relying on credit during Diwali, Eid, or other celebrations.

3. **Digital Tracking**: Use UPI payment history and banking apps to categorize and analyze spending patterns.

4. **Multiple Savings Buckets**: Create separate funds for emergency, short-term goals, and long-term aspirations.

5. **Joint Financial Planning**: For families, involve all decision-makers in the budgeting process to ensure buy-in and compliance.

Consider using the Kakeibo method of budgeting that focuses on four categories: needs, wants, culture/education, and unexpected expenses, with reflection on each purchase.
        """
    elif any(word in query for word in ["insurance", "policy", "premium", "cover", "claim"]):
        category = "insurance"
        extended_info = """
### Insurance Planning for Indian Families

Insurance needs in India have unique considerations:

1. **Term Insurance Coverage**: A good rule of thumb is 10-15 times your annual income, with higher multipliers for younger individuals with more dependents.

2. **Health Insurance Adequacy**: Family floater plans should consider rising healthcare costs in tier-1 cities, with a minimum coverage of ₹10 lakhs for a family of four.

3. **Critical Illness Coverage**: Consider a separate critical illness policy as many serious conditions require treatment costs well beyond regular health insurance limits.

4. **Super Top-up Advantage**: Super top-up policies can provide high coverage at relatively low premiums by covering aggregate claims above a threshold.

5. **Avoid Investment-Linked Insurance**: Pure protection through term insurance and separate investments typically provides better coverage and returns than endowment or ULIP policies.

Remember that adequate insurance is the foundation of financial planning, protecting your other financial goals from disruption due to unexpected events.
        """
    else:
        # For specific or unclassified queries
        category = "specific"
        advice_response = get_financial_advice(category, {"query": query})
        detailed_advice = advice_response["advice"]
        
        # Add more context and depth for specific queries
        if "stock" in query:
            detailed_advice += """

When evaluating Indian stocks, consider these additional factors:

- **Promoter Holding**: Companies with significant promoter (founder/family) ownership often align management interests with shareholders.
- **Institutional Investment**: Significant FII and DII holdings can indicate quality but might also lead to volatility with large position changes.
- **Dividend History**: A consistent dividend history often indicates stable cash flows and shareholder-friendly management.
- **Corporate Governance**: Look beyond reported numbers to management quality, related party transactions, and accounting quality.
- **Competitive Moat**: Assess the company's ability to maintain advantages in an increasingly competitive Indian market.

Remember that stock selection should be part of a broader asset allocation strategy rather than the entire investment approach.
"""
        elif "mutual" in query:
            detailed_advice += """

For mutual fund selection in India, consider these additional insights:

- **Expense Ratio Impact**: Direct plans offer significantly lower expense ratios than regular plans, potentially saving 0.5-1.5% annually.
- **Fund Manager Tenure**: Consistent fund management is particularly important in the actively managed Indian mutual fund landscape.
- **AUM Considerations**: Very large funds may struggle to outperform in mid and small-cap spaces due to reduced flexibility.
- **Rolling Returns**: Evaluate performance across multiple time periods rather than just point-to-point returns to understand consistency.
- **Risk-Adjusted Metrics**: Consider Sharpe ratio, Sortino ratio, and downside capture in addition to absolute returns.

A core-satellite approach using index funds as the core and selected active funds as satellites can balance cost efficiency with outperformance potential.
"""
        elif "gold" in query:
            detailed_advice += """

Gold holds a unique place in Indian investment portfolios:

- **Different Forms**: Consider Sovereign Gold Bonds for long-term holding, Gold ETFs for medium-term, and digital gold for short-term objectives.
- **Optimal Allocation**: Most financial advisors suggest limiting gold to 5-15% of your overall portfolio.
- **SGB Advantages**: SGBs offer 2.5% annual interest in addition to potential appreciation, with tax-free gains if held to maturity (8 years).
- **Festival Timing**: Gold purchases during festivals like Akshaya Tritiya or Dhanteras may carry higher premiums than non-festive periods.
- **Hallmarking Importance**: For physical gold, ensure BIS hallmarking to guarantee purity.

Gold can serve as both a portfolio diversifier and a hedge against currency depreciation, but unlikely to match equity returns over very long periods.
"""
        
        return detailed_advice
    
    # Get advice for the relevant category
    basic_advice = get_financial_advice(category)["advice"]
    
    # Combine the basic advice with extended information
    detailed_response = f"{basic_advice}\n\n{extended_info}"
    
    return detailed_response

def get_book_insights():
    """
    Get financial literacy insights from popular financial books
    
    Returns:
    dict: Dictionary of book insights
    """
    books = {
        "Rich Dad Poor Dad": {
            "author": "Robert Kiyosaki",
            "publication_year": "1997",
            "key_lessons": [
                "Assets put money in your pocket; liabilities take money out of your pocket",
                "The rich don't work for money; they make money work for them",
                "Financial education is more important than academic education for wealth building",
                "Understanding the difference between good debt (used to acquire assets) and bad debt (used for liabilities)",
                "Most people work for three entities: the company, the government (taxes), and the bank (mortgages, loans)"
            ],
            "detailed_lessons": {
                "Assets vs Liabilities": "Kiyosaki redefines these terms - assets generate income, while liabilities generate expenses. A house you live in is actually a liability (not an asset as traditionally defined) because it costs money every month. Building wealth means focusing on acquiring income-generating assets.",
                "Financial Education": "Schools teach people to be employees, not business owners or investors. Learning accounting, investing, market understanding, and tax strategies is essential but rarely taught in traditional education.",
                "Cash Flow Focus": "Wealthy people focus on cash flow (passive income) rather than capital gains. They aim to build assets that generate regular income without requiring active work."
            },
            "indian_context": "In the Indian context, Kiyosaki's emphasis on financial education is particularly relevant as our school system traditionally focuses on academics rather than money management. His asset-acquisition principles can be applied through Indian instruments like commercial real estate, dividend stocks from established Nifty companies, or creating small businesses with low overhead. With India's growing middle class focusing heavily on property ownership, many Indians may benefit from reconsidering whether their primary residence is truly an 'asset' in Kiyosaki's definition when it consumes a large portion of monthly income in EMIs and maintenance. The book's message about creating passive income streams is especially relevant in India's gig economy.",
            "book_summary": "Robert Kiyosaki contrasts the financial philosophies of his educated but financially struggling 'Poor Dad' (his biological father) with his mentor 'Rich Dad' (his friend's father). The book challenges conventional beliefs about money, revealing how the wealthy use financial literacy, business creation, and investment strategies that aren't typically taught in schools. Through personal stories and simple explanations, Kiyosaki introduces concepts like the cash flow quadrant, good vs. bad debt, and how taxes favor entrepreneurs rather than employees. While controversial for some of its advice, the book has become a classic for its accessible explanation of how wealth is built through acquiring income-generating assets.",
            "practical_examples": [
                "Starting a small rental property business in growing Indian tier-2 cities",
                "Creating a portfolio of high-dividend BSE/NSE stocks",
                "Building a side business while maintaining employment",
                "Investing in peer-to-peer lending platforms for monthly income"
            ],
            "critics_say": "Critics point out that Kiyosaki's advice oversimplifies complex financial decisions and that some of his business practices have been questioned. Additionally, his emphasis on real estate may not work in all market conditions or locations."
        },
        "The Psychology of Money": {
            "author": "Morgan Housel",
            "publication_year": "2020",
            "key_lessons": [
                "Your financial decisions are influenced more by personal history and psychology than math",
                "Long-term investing success is more about behavior than intelligence",
                "Wealth is what you don't see - it's the money not spent",
                "Reasonable financial planning is more valuable than complex optimization",
                "Luck and risk play a significant role in financial outcomes; be humble"
            ],
            "detailed_lessons": {
                "Personal Experience": "Each person's view of money is shaped by their unique experiences, often from formative early years. Someone who grew up during high inflation will invest differently than someone who grew up during a bull market.",
                "Reasonable > Rational": "Perfect optimization is impossible in finance. Sticking with reasonable strategies that you can maintain is better than theoretically optimal ones you'll abandon.",
                "Room for Error": "The most important part of financial planning is preparing for things not going according to plan. Having a margin of safety is essential."
            },
            "indian_context": "For Indian investors, Housel's teachings about managing behavior during market volatility is crucial given the emotional cycles often seen in domestic markets. His emphasis on long-term thinking aligns well with successful Indian wealth creators who built fortunes through patient compounding rather than speculation. The concept of 'wealth is what you don't see' is especially relevant in India's status-conscious society, where conspicuous consumption often takes precedence over wealth building. Indian investors can particularly benefit from the book's wisdom on avoiding 'FOMO' investing when markets are volatile, as witnessed during recent IPO frenzies or cryptocurrency speculation.",
            "book_summary": "Morgan Housel explores how our unique experiences with money shape our behavior more than financial education. Through 19 short stories, he demonstrates that doing well with money isn't necessarily about what you know, but about how you behave. The book argues that financial success comes from managing emotions and expectations rather than complex technical analysis. Housel emphasizes that individual biases, personal history, and temperament play a more significant role in financial outcomes than mathematical optimization. With engaging storytelling and clear examples, he shows how reasonable financial decisions maintained consistently can outperform 'brilliant' but unsustainable strategies.",
            "practical_examples": [
                "Creating automatic SIPs in index funds to remove emotional decision-making",
                "Building an emergency fund that helps you stay invested during market downturns",
                "Developing a personal definition of 'enough' to avoid lifestyle inflation",
                "Understanding your own money history and how it shapes your financial behaviors"
            ],
            "critics_say": "Some critics note that the book offers more philosophy than actionable tactics, and that its collection of essays sometimes lacks a cohesive framework for implementation."
        },
        "The Intelligent Investor": {
            "author": "Benjamin Graham",
            "publication_year": "1949 (with updates)",
            "key_lessons": [
                "Distinguish investing from speculation through thorough analysis",
                "Use the 'margin of safety' principle to reduce investment risk",
                "Market fluctuations offer opportunities; don't fear volatility but use it",
                "Focus on value rather than price; assess companies based on fundamentals",
                "Investment success requires emotional discipline more than high IQ"
            ],
            "detailed_lessons": {
                "Mr. Market": "Graham's famous metaphor personifies the market as an emotional business partner who offers to buy or sell shares at vastly different prices based on his mood. The intelligent investor takes advantage of Mr. Market's mood swings rather than being influenced by them.",
                "Margin of Safety": "Only purchase securities when there is a significant discount to their intrinsic value, providing a buffer against errors in analysis or unforeseen problems.",
                "Defensive vs. Enterprising": "Graham distinguishes between defensive investors (who want protection from serious mistakes) and enterprising investors (who will devote time and care to selection of securities)."
            },
            "indian_context": "Graham's principles have influenced top Indian investors like Ramdeo Agrawal and Rakesh Jhunjhunwala. His value investing approach can be particularly useful in India's often sentiment-driven markets, helping investors identify fundamentally strong companies during market corrections. The concept of 'margin of safety' is especially relevant in emerging markets like India where corporate governance and transparency can vary widely between companies. Indian value investors applying Graham's principles should look for businesses with strong balance sheets, conservative accounting, and proven track records rather than chasing growth stories with questionable fundamentals. The distinction between investing and speculation is critical in India's sometimes 'hot tip' driven market environment.",
            "book_summary": "Known as the Bible of value investing, Benjamin Graham's masterpiece introduces fundamental concepts like intrinsic value, margin of safety, and Mr. Market. The book distinguishes between defensive and enterprising investors, offering strategies for both types. Warren Buffett credits this book as the foundation of his investment philosophy. Graham teaches investors to develop a rational methodology based on security analysis rather than following market trends or emotions. While some of his specific criteria have been updated over the years, the underlying principles about investor psychology, valuation, and risk management remain timeless foundations for thoughtful investing.",
            "practical_examples": [
                "Calculating intrinsic value using multiple valuation methodologies",
                "Creating an investment policy statement to guide decisions during market volatility",
                "Building a diversified portfolio of value stocks with strong fundamentals",
                "Maintaining cash reserves to take advantage of market corrections"
            ],
            "critics_say": "Critics argue that Graham's approach doesn't work as well in modern markets dominated by technology companies with intangible assets, or that it's too conservative and may miss significant growth opportunities."
        },
        "Think and Grow Rich": {
            "author": "Napoleon Hill",
            "publication_year": "1937",
            "key_lessons": [
                "Desire: Start with a burning desire for financial success and specific goals",
                "Faith: Cultivate absolute belief in your ability to achieve your goals",
                "Specialized knowledge: Develop expertise in your chosen field",
                "Organized planning: Create a concrete plan and take persistent action",
                "The power of the mastermind: Surround yourself with supportive, knowledgeable people"
            ],
            "detailed_lessons": {
                "Autosuggestion": "Hill emphasizes the power of repeating positive affirmations to influence your subconscious mind toward success. Programming your mind with specific desires and beliefs helps overcome limiting thoughts.",
                "Persistence": "Persistence is the key factor that transforms failures into success. Most people give up right before breakthroughs would occur.",
                "Transmutation": "Sexual energy can be channeled into creative and professional pursuits, providing drive and charisma that contribute to success."
            },
            "indian_context": "Hill's emphasis on persistence resonates with India's entrepreneurial journey. Many successful Indian businesspeople, from Dhirubhai Ambani to modern startup founders, embody the principles of focused desire and organized planning that Hill advocates. The 'mastermind' concept translates well to India's strong family business networks and growing entrepreneurial ecosystems in cities like Bengaluru and Hyderabad. In the Indian context, Hill's teachings about specialized knowledge find relevance as the economy shifts from traditional employment to knowledge and innovation-driven sectors. Many of India's most successful entrepreneurs demonstrate the book's principle of starting with a clear desire and working relentlessly toward it, often despite significant obstacles and setbacks.",
            "book_summary": "Based on interviews with 500+ successful people including Henry Ford and Thomas Edison, Napoleon Hill identified 13 principles that lead to financial success. The book emphasizes that wealth begins with a state of mind and specific thought patterns that can be learned and applied by anyone willing to follow the system. While written during the Great Depression, its principles about desire, faith, specialized knowledge, and organized planning remain influential today. The book stands out for blending practical business advice with psychological techniques and spiritual concepts about the power of thought. Though some concepts may seem dated, the core message about setting clear goals and developing persistence continues to inspire entrepreneurs worldwide.",
            "practical_examples": [
                "Writing down specific financial goals with amounts and deadlines",
                "Creating a 'mastermind group' of peers for accountability and idea sharing",
                "Developing daily affirmations reinforcing your ability to achieve wealth",
                "Turning setbacks into opportunities through maintained persistence"
            ],
            "critics_say": "Critics note that Hill's methods lack scientific validation, and some question the authenticity of his claimed relationships with famous businesspeople. The book's spiritual and metaphysical elements may not resonate with all readers."
        },
        "The Millionaire Next Door": {
            "author": "Thomas J. Stanley and William D. Danko",
            "publication_year": "1996",
            "key_lessons": [
                "Most millionaires live well below their means, avoiding conspicuous consumption",
                "Time, energy and money should be allocated efficiently in ways conducive to building wealth",
                "Financial independence is more important than displaying high social status",
                "Economic outpatient care (financial help to adult children) often hinders wealth building",
                "Choosing the right occupation is crucial for wealth accumulation"
            ],
            "detailed_lessons": {
                "PAWs vs UAWs": "The book distinguishes between Prodigious Accumulators of Wealth (PAWs) who save and invest aggressively, and Under Accumulators of Wealth (UAWs) who earn high incomes but save little.",
                "Income vs Wealth": "High income does not equal wealth. Many high-income professionals live paycheck to paycheck due to lifestyle inflation, while modest-income business owners build significant wealth through frugality.",
                "Wealth Formula": "The authors provide a formula for expected net worth: Multiply your age by your annual household income, divide by 10. This equals what your net worth should be for your age and income."
            },
            "indian_context": "In India's increasingly consumerist society, this book's message about frugality and understated wealth counters the growing tendency toward status display. The traditional Indian values of saving and modest living align perfectly with the millionaire behaviors documented in this research. In urban India, where luxury brands and expensive lifestyles are increasingly normalized, the book's findings provide a valuable counterpoint about prioritizing financial security over appearances. The research also resonates with the success stories of many first-generation Indian entrepreneurs who built substantial businesses while maintaining modest personal lifestyles. The book's findings about self-employed individuals building more wealth than corporate employees may inspire India's growing entrepreneurial sector.",
            "book_summary": "Based on extensive research of actual millionaires, this book revealed that most American millionaires don't live in mansions or drive luxury cars. Instead, they practice frugality, disciplined saving, and careful investment. The authors identify seven common traits that appear among those who successfully build wealth, regardless of their income level. The book challenges common assumptions about wealth, showing that most millionaires are self-made, often in 'ordinary' businesses, and accumulate wealth through consistent financial discipline rather than flashy investments or high-status careers. By contrasting the habits of Prodigious Accumulators of Wealth (PAWs) with Under Accumulators of Wealth (UAWs), the authors provide a framework for understanding how personal choices determine financial outcomes more than income levels.",
            "practical_examples": [
                "Calculating your expected net worth based on the book's formula",
                "Auditing your lifestyle for 'status' expenses that don't build wealth",
                "Creating a household budget with savings as the first priority",
                "Evaluating career choices based on wealth-building potential"
            ],
            "critics_say": "Critics note that the research is now dated and focused primarily on American self-employed business owners, potentially limiting its applicability to other contexts or economies."
        },
        "A Random Walk Down Wall Street": {
            "author": "Burton G. Malkiel",
            "publication_year": "1973 (with regular updates)",
            "key_lessons": [
                "Markets are generally efficient; consistently beating the market is difficult",
                "Index fund investing outperforms most actively managed funds over time",
                "Asset allocation based on risk tolerance and time horizon is more important than stock picking",
                "Investment costs significantly impact long-term returns",
                "Diversification across asset classes is essential for risk management"
            ],
            "detailed_lessons": {
                "Efficient Market Hypothesis": "Malkiel explains that markets efficiently incorporate all available information, making it extremely difficult to consistently outperform through either technical analysis (chart patterns) or fundamental analysis.",
                "Life-Cycle Investing": "The book offers detailed asset allocation suggestions based on age and life stage, with more aggressive allocations for younger investors and more conservative ones for those near retirement.",
                "Investment Bubbles": "Through historical examples like the Dutch tulip mania and the dot-com bubble, Malkiel shows how markets occasionally become irrational, creating both dangers and opportunities."
            },
            "indian_context": "With the growing popularity of index funds in India, Malkiel's advice is increasingly relevant. Indian investors often chase 'hot tips' and active funds despite evidence that systematic, low-cost investing through index funds often delivers better long-term results for retail investors. The high expense ratios of many Indian mutual funds (sometimes 2-2.5% annually) make Malkiel's cost-conscious approach particularly important. As India's capital markets continue to mature, the efficiency of the market, especially for large-cap stocks, has increased, making index investing an increasingly compelling strategy. Indian investors who have traditionally preferred active management or direct stock picking may benefit from considering Malkiel's evidence about the long-term performance of these approaches compared to systematic indexing.",
            "book_summary": "Malkiel examines and largely debunks technical and fundamental analysis strategies while advocating for the Efficient Market Hypothesis. The book makes a compelling case for index fund investing and offers practical advice on portfolio construction for investors at different life stages. It's considered one of the first books to popularize index investing for the average person. Beginning with a history of investment bubbles and follies, Malkiel demonstrates why trying to outguess the market typically fails. He then walks readers through various investment options - from stocks and bonds to REITs and emerging markets - providing clear explanations of how these investments work and their role in a diversified portfolio. While acknowledging some market inefficiencies, Malkiel argues that for most individual investors, trying to exploit these inefficiencies costs more than it's worth.",
            "practical_examples": [
                "Creating a diversified portfolio of low-cost index funds",
                "Adjusting asset allocation based on your investment timeline",
                "Minimizing costs by avoiding high-fee active management",
                "Implementing systematic rebalancing to maintain risk parameters"
            ],
            "critics_say": "Active managers and some value investors criticize Malkiel's efficient market view, arguing that skilled investors can indeed outperform consistently through careful analysis and patience."
        },
        "Your Money or Your Life": {
            "author": "Vicki Robin and Joe Dominguez",
            "publication_year": "1992 (updated 2018)",
            "key_lessons": [
                "Money represents your life energy; be conscious of this exchange",
                "Track every penny to increase awareness of spending patterns",
                "Evaluate each expense by asking if it aligns with your values and life purpose",
                "Seek financial independence through reduced spending rather than just increased earning",
                "True fulfillment comes from 'enough' rather than 'more'"
            ],
            "detailed_lessons": {
                "Real Hourly Wage": "Calculate what you truly earn per hour after accounting for all work-related expenses (commuting, professional clothes, etc.) and time commitments. This often reveals a much lower rate than your nominal wage.",
                "Fulfillment Curve": "The relationship between spending and happiness follows a curve - more spending initially increases happiness, but eventually reaches a peak of 'enough,' after which more consumption actually decreases well-being.",
                "Crossover Point": "Financial independence occurs at the 'crossover point' when your investment income exceeds your expenses, making paid work optional rather than necessary."
            },
            "indian_context": "In India's rapidly developing economy with growing consumerism, this book's message about conscious spending and defining 'enough' provides a thoughtful counterbalance. The concept of aligning money with purpose connects well with traditional Indian philosophical views on material wealth. For the Indian middle class experiencing rapid income growth and expanding consumption options, the book offers valuable perspective on whether additional consumption truly leads to increased well-being. The concept of trading life energy for money resonates in India's demanding work culture, where lengthy commutes and long working hours are common. The book's approach to financial independence through mindful spending rather than aggressive earning aligns with India's traditional values of moderation and satisfaction with sufficient resources rather than excess.",
            "book_summary": "This transformative book presents a nine-step program for transforming your relationship with money. The authors challenge readers to calculate their real hourly wage, track spending meticulously, and evaluate the true fulfillment derived from each purchase. The ultimate goal is 'financial independence' defined as having enough investment income to cover expenses without needing to work. Unlike most personal finance books focused primarily on investing or earning more, this book fundamentally questions the relationship between money, time, and fulfillment. It encourages readers to examine whether they're trading their life energy for things that truly matter. The systematic approach begins with calculating your true hourly wage, tracking all money flows, and creating a wall chart to visualize progress toward the crossover point where investment income meets expenses.",
            "practical_examples": [
                "Calculating your real hourly wage after all work-related expenses",
                "Creating a complete tracking system for all income and expenses",
                "Evaluating each purchase by asking 'Does this bring me fulfillment proportionate to the life energy spent?'",
                "Building a wall chart to visualize progress toward financial independence"
            ],
            "critics_say": "Critics suggest the approach may be too extreme for some, and that the original investment strategy (primarily government bonds) requires updating in the current low-interest environment."
        },
        "The Little Book of Common Sense Investing": {
            "author": "John C. Bogle",
            "publication_year": "2007 (updated 2017)",
            "key_lessons": [
                "Costs matter tremendously in investing; minimize fees and expenses",
                "Simplicity beats complexity in investment strategies",
                "Broad market index funds outperform most active strategies over time",
                "Invest for the long term; avoid market timing and excessive trading",
                "Focus on what you can control: costs, diversification, and discipline"
            ],
            "detailed_lessons": {
                "Cost Impact": "Bogle demonstrates mathematically how seemingly small fees (1-2%) compound over decades to consume a massive portion of investment returns. A 2% annual fee can reduce a portfolio's final value by nearly two-thirds over 50 years.",
                "Investor Returns Gap": "Actual investor returns typically lag fund returns because investors tend to buy high and sell low, chasing performance rather than staying disciplined.",
                "Reversion to Mean": "Top-performing funds rarely maintain their outperformance; statistical reversion to the mean is a powerful force in financial markets."
            },
            "indian_context": "As India's mutual fund industry matures, Bogle's insights on cost minimization become increasingly relevant. Indian investors often focus on past returns while ignoring the significant impact of expense ratios on long-term wealth accumulation. With expense ratios for many active funds in India ranging from 1.5% to 2.5%, the mathematical impact Bogle describes is especially relevant. The recent growth of low-cost index funds in India provides new opportunities for implementing Bogle's approach. His warning about performance chasing is particularly applicable in the Indian context, where fund companies heavily advertise recent outperformance to attract new investors despite the poor predictive value of such results. Indian investors can apply Bogle's teachings by focusing on Nifty and Sensex index funds with the lowest expense ratios rather than trying to identify the next star fund manager.",
            "book_summary": "Written by the founder of Vanguard and creator of the first index fund, this book makes a compelling case for low-cost index investing. Bogle presents substantial evidence that trying to beat the market is a losing proposition for most investors, and that capturing market returns through index funds while minimizing costs is the most reliable path to investment success. Using clear language and compelling data, Bogle demonstrates how the mathematics of investing make it virtually impossible for the average actively managed fund to outperform indexes after accounting for all costs. He systematically dismantles common arguments against indexing while providing a simple, actionable investment strategy accessible to investors of all experience levels. The book's power comes from its mathematical clarity about how costs compound over time to reduce returns.",
            "practical_examples": [
                "Calculating the long-term impact of fees on your investment portfolio",
                "Creating a simple portfolio of broad-market index funds",
                "Setting up a systematic investment plan with regular contributions",
                "Maintaining investment discipline through market cycles"
            ],
            "critics_say": "Some critics argue that Bogle's approach is too conservative, potentially missing opportunities in inefficient markets or asset classes where active management may add value."
        }
    }
    return books

def show():
    """Display the financial advisor page"""
    st.title("Financial Advisor")
    
    # Create tabs for different financial advisor tools
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["AI Financial Assistant", "Investment Planner", "Budget Optimizer", "Daily Wisdom", "Financial Literacy"])
    
    with tab1:
        st.header("Ask the Financial Assistant")
        
        st.markdown("""
        Welcome to your AI Financial Assistant. This tool provides personalized financial advice and answers
        to your money-related questions. Try asking about investments, retirement planning, tax strategies, 
        debt management, budgeting, or insurance.
        """)
        
        # Initialize or retrieve chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").markdown(message["content"])
            else:
                st.chat_message("assistant").markdown(message["content"])
        
        # Input for new message
        user_query = st.chat_input("Ask a financial question...")
        
        if user_query:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_query})
            st.chat_message("user").markdown(user_query)
            
            # Generate response
            response = chatbot_response(user_query)
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.chat_message("assistant").markdown(response)
    
    with tab2:
        st.header("Personalized Investment Planner")
        
        st.markdown("""
        This tool helps you create a personalized investment plan based on your risk tolerance,
        investment horizon, and sector preferences. Input your information below to receive
        tailored recommendations.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk profile selection
            risk_profile = st.radio(
                "Select your risk tolerance:",
                ["Conservative", "Moderate", "Aggressive"],
                index=1
            )
            
            # Investment horizon
            investment_horizon = st.selectbox(
                "What is your investment time horizon?",
                ["Short-term (0-3 years)", "Medium-term (3-7 years)", "Long-term (7+ years)"],
                index=1
            )
            
            # Convert horizon to simplified format
            horizon_map = {
                "Short-term (0-3 years)": "Short-term",
                "Medium-term (3-7 years)": "Medium-term",
                "Long-term (7+ years)": "Long-term"
            }
            
            # Sector preferences
            sectors = [
                "Technology", "Banking & Finance", "Healthcare", 
                "Consumer Goods", "Automobile", "Energy",
                "Metals & Mining", "Infrastructure"
            ]
            
            selected_sectors = st.multiselect(
                "Select your preferred sectors (optional):",
                sectors
            )
        
        with col2:
            # Investment amount inputs
            initial_investment = st.number_input(
                "Initial investment amount (₹):",
                min_value=0,
                value=100000,
                step=10000
            )
            
            monthly_contribution = st.number_input(
                "Monthly contribution (₹):",
                min_value=0,
                value=10000,
                step=1000
            )
            
            # Expected returns based on risk profile
            expected_returns = {
                "Conservative": 8,
                "Moderate": 12,
                "Aggressive": 15
            }
            
            expected_return = st.slider(
                "Expected annual return (%):",
                min_value=5.0,
                max_value=20.0,
                value=float(expected_returns[risk_profile]),
                step=0.5
            )
            
            # Inflation assumption
            inflation_rate = st.slider(
                "Expected inflation rate (%):",
                min_value=3.0,
                max_value=10.0,
                value=6.0,
                step=0.5
            )
        
        # Generate recommendations on button click
        if st.button("Generate Investment Plan"):
            # Get recommendations
            recommendations = get_stock_recommendations(
                risk_profile,
                horizon_map[investment_horizon],
                selected_sectors
            )
            
            # Display asset allocation
            st.subheader("Recommended Asset Allocation")
            
            allocation = recommendations["asset_allocation"]
            
            # Create pie chart
            fig = px.pie(
                values=[allocation["Stocks"], allocation["Bonds"], allocation["Cash"]],
                names=["Equity", "Debt", "Cash"],
                title="Recommended Portfolio Allocation",
                color_discrete_sequence=["#4CAF50", "#2196F3", "#FFC107"]
            )
            
            fig.update_layout(
                height=400,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display stock recommendations
            st.subheader("Recommended Stocks")
            
            stock_recs = recommendations["stock_recommendations"]
            if stock_recs:
                st.markdown(", ".join(stock_recs))
            else:
                st.info("No stock recommendations available for your criteria.")
            
            # Display fund recommendations
            st.subheader("Recommended Mutual Funds")
            
            fund_recs = recommendations["fund_recommendations"]
            if fund_recs:
                st.markdown(", ".join(fund_recs))
            else:
                st.info("No fund recommendations available for your criteria.")
            
            # Display growth projection
            st.subheader("Investment Growth Projection")
            
            # Calculate years from investment horizon
            years_map = {
                "Short-term": 3,
                "Medium-term": 7,
                "Long-term": 15
            }
            
            years = years_map[horizon_map[investment_horizon]]
            
            # Simulate investment growth
            simulation = simulate_investment_growth(
                initial_investment,
                monthly_contribution,
                years,
                expected_return,
                inflation_rate
            )
            
            # Create growth chart
            fig = go.Figure()
            
            # Add investment value line
            fig.add_trace(go.Scatter(
                x=simulation["years"],
                y=simulation["investment_value"],
                mode='lines+markers',
                name='Investment Value',
                line=dict(color='#4CAF50', width=3)
            ))
            
            # Add amount invested line
            fig.add_trace(go.Scatter(
                x=simulation["years"],
                y=simulation["total_invested"],
                mode='lines+markers',
                name='Amount Invested',
                line=dict(color='#2196F3', width=3)
            ))
            
            # Add inflation-adjusted value
            fig.add_trace(go.Scatter(
                x=simulation["years"],
                y=simulation["real_value"],
                mode='lines+markers',
                name='Inflation-Adjusted Value',
                line=dict(color='#FFC107', width=3, dash='dash')
            ))
            
            # Update layout
            fig.update_layout(
                title='Projected Investment Growth',
                xaxis_title='Years',
                yaxis_title='Value (₹)',
                height=500,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            # Format y-axis as currency
            fig.update_layout(yaxis=dict(tickformat=",.0f"))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display key statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Final Investment Value",
                    f"₹{simulation['final_value']:,.0f}",
                    f"₹{simulation['final_value'] - simulation['total_contributions']:,.0f} growth"
                )
            
            with col2:
                st.metric(
                    "Total Amount Invested",
                    f"₹{simulation['total_contributions']:,.0f}"
                )
            
            with col3:
                st.metric(
                    "Inflation-Adjusted Value",
                    f"₹{simulation['real_final_value']:,.0f}",
                    f"{simulation['total_return']:.1f}% total return"
                )
            
            # Additional insights
            st.subheader("Key Insights")
            
            st.markdown(f"""
            * Your {risk_profile.lower()} portfolio focuses on {
                'capital preservation with some growth' if risk_profile == 'Conservative' 
                else 'balancing growth and stability' if risk_profile == 'Moderate'
                else 'maximizing long-term growth'
            }.
            
            * With a {horizon_map[investment_horizon].lower()} horizon, you can {
                'expect moderate but more stable returns' if horizon_map[investment_horizon] == 'Short-term'
                else 'benefit from medium-term market growth cycles' if horizon_map[investment_horizon] == 'Medium-term'
                else 'take advantage of long-term compounding and ride out market volatility'
            }.
            
            * The power of compounding will generate approximately **₹{simulation['final_value'] - simulation['total_contributions']:,.0f}** in investment returns over your investment period.
            
            * Accounting for inflation of {inflation_rate}%, your investment's real purchasing power will be **₹{simulation['real_final_value']:,.0f}**.
            """)
            
            # Disclaimer
            st.info("Disclaimer: These projections are based on historical market data and assumptions about future performance. Actual returns may vary. This is not financial advice - please consult with a financial advisor before making investment decisions.")
    
    with tab3:
        st.header("Budget Optimizer")
        
        st.markdown("""
        Visualize and optimize your monthly budget with this interactive tool.
        Enter your income and current expenses to receive personalized recommendations.
        """)
        
        # Income input
        income = st.number_input(
            "Monthly Income (₹):",
            min_value=0,
            value=50000,
            step=5000
        )
        
        # Current expenses
        st.subheader("Current Monthly Expenses")
        
        col1, col2 = st.columns(2)
        
        current_expenses = {}
        
        with col1:
            current_expenses["Housing"] = st.number_input("Housing (rent/mortgage):", min_value=0, value=15000, step=1000)
            current_expenses["Utilities"] = st.number_input("Utilities:", min_value=0, value=3000, step=500)
            current_expenses["Food"] = st.number_input("Food:", min_value=0, value=8000, step=500)
            current_expenses["Transportation"] = st.number_input("Transportation:", min_value=0, value=4000, step=500)
            current_expenses["Healthcare"] = st.number_input("Healthcare:", min_value=0, value=2000, step=500)
        
        with col2:
            current_expenses["Personal"] = st.number_input("Personal (clothing, entertainment):", min_value=0, value=5000, step=500)
            current_expenses["Education"] = st.number_input("Education:", min_value=0, value=2000, step=500)
            current_expenses["Savings"] = st.number_input("Savings:", min_value=0, value=5000, step=1000)
            current_expenses["Debt Repayment"] = st.number_input("Debt Repayment:", min_value=0, value=3000, step=500)
            current_expenses["Others"] = st.number_input("Others:", min_value=0, value=2000, step=500)
        
        # Create playful budget allocation
        if st.button("Optimize My Budget"):
            # Calculate total current expenses
            total_expenses = sum(current_expenses.values())
            
            # Get budget recommendations
            budget_recommendation = generate_budget_recommendation(income, current_expenses)
            
            # Display budget overview
            st.subheader("Budget Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Display spending vs. income
                status = "positive" if total_expenses <= income else "negative"
                difference = income - total_expenses
                
                if status == "positive":
                    st.success(f"**Current Status:** You're spending ₹{abs(difference):,.0f} less than your income. Great job!")
                else:
                    st.error(f"**Current Status:** You're spending ₹{abs(difference):,.0f} more than your income. This needs attention.")
                
                # Display insights
                st.subheader("Key Insights")
                
                for insight in budget_recommendation["insights"]:
                    st.markdown(f"* {insight}")
            
            with col2:
                # Create current vs. income pie chart
                if total_expenses > income:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Pie(
                        labels=["Income", "Excess Spending"],
                        values=[income, total_expenses - income],
                        hole=0.4,
                        marker_colors=["#4CAF50", "#F44336"]
                    ))
                    
                    fig.update_layout(
                        title="Income vs. Spending",
                        height=300,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                else:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Pie(
                        labels=["Expenses", "Unspent Income"],
                        values=[total_expenses, income - total_expenses],
                        hole=0.4,
                        marker_colors=["#2196F3", "#4CAF50"]
                    ))
                    
                    fig.update_layout(
                        title="Income vs. Spending",
                        height=300,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Display current vs. recommended budget
            st.subheader("Current vs. Recommended Budget")
            
            # Prepare data for comparison chart
            categories = list(current_expenses.keys())
            current_values = [current_expenses[cat] for cat in categories]
            recommended_values = [budget_recommendation["recommended_budget"][cat] for cat in categories]
            
            # Create comparison bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=categories,
                y=current_values,
                name="Current",
                marker_color="#2196F3"
            ))
            
            fig.add_trace(go.Bar(
                x=categories,
                y=recommended_values,
                name="Recommended",
                marker_color="#4CAF50"
            ))
            
            fig.update_layout(
                title="Expense Comparison",
                xaxis_title="Category",
                yaxis_title="Amount (₹)",
                height=500,
                margin=dict(l=0, r=0, t=40, b=0),
                barmode="group"
            )
            
            # Format y-axis as currency
            fig.update_layout(yaxis=dict(tickformat=",.0f"))
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display recommended future allocation
            st.subheader("Recommended Budget Allocation")
            
            # Prepare data for pie chart
            future_budget = budget_recommendation["future_budget"]
            
            # Create pie chart
            fig = go.Figure()
            
            fig.add_trace(go.Pie(
                labels=list(future_budget.keys()),
                values=list(future_budget.values()),
                hole=0.4,
                marker_colors=px.colors.qualitative.Bold
            ))
            
            fig.update_layout(
                title="Ideal Budget Allocation",
                height=500,
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display detailed recommendations
            st.subheader("Category-by-Category Analysis")
            
            # Create a dataframe for display
            analysis_data = []
            
            for category, data in budget_recommendation["budget_analysis"].items():
                analysis_data.append({
                    "Category": category,
                    "Current": f"₹{data['current']:,.0f}",
                    "Recommended": f"₹{data['recommended']:,.0f}",
                    "Difference": f"₹{abs(data['difference']):,.0f} {'over' if data['difference'] > 0 else 'under'}",
                    "Status": data["status"]
                })
            
            analysis_df = pd.DataFrame(analysis_data)
            
            # Apply color to status column
            def highlight_status(val):
                color = "green" if val == "Good" else "red"
                return f"color: {color}; font-weight: bold"
            
            # Display the styled dataframe
            st.dataframe(
                analysis_df.style.applymap(
                    highlight_status,
                    subset=["Status"]
                ),
                hide_index=True,
                use_container_width=True
            )
            
            # Budget adjustment tips
            st.subheader("Budget Optimization Tips")
            
            # Display tips for categories that need attention
            needs_attention = [
                category for category, data in budget_recommendation["budget_analysis"].items()
                if data["status"] == "Needs Attention"
            ]
            
            if "Housing" in needs_attention:
                st.markdown("""
                * **Housing:** Consider if you can negotiate rent, find a roommate, or move to a slightly less expensive area. Remember, housing should ideally be around 25% of your income.
                """)
            
            if "Food" in needs_attention:
                st.markdown("""
                * **Food:** Try meal planning, buying groceries in bulk, cooking at home more often, and limiting food delivery services to reduce food expenses.
                """)
            
            if "Personal" in needs_attention:
                st.markdown("""
                * **Personal Expenses:** Review subscriptions and memberships you might not be fully utilizing. Consider if there are free alternatives for entertainment.
                """)
            
            if "Transportation" in needs_attention:
                st.markdown("""
                * **Transportation:** Explore carpooling, public transportation, or combining trips to save on fuel costs. For vehicle owners, stay on top of regular maintenance to avoid costly repairs.
                """)
            
            if "Savings" in needs_attention:
                st.markdown("""
                * **Savings:** Set up automatic transfers to savings accounts on payday to prioritize saving. Start with small amounts if necessary, but aim to gradually increase to 20% of income.
                """)
            
            # Disclaimer
            st.info("Disclaimer: This budget optimization tool provides general recommendations based on standard personal finance principles. Your individual situation may require different allocations. Consider consulting with a financial advisor for personalized advice.")
    
    with tab4:
        st.header("Financial Wisdom Fortune Cookie")
        st.markdown("""
        Receive your daily financial wisdom to inspire your investment journey.
        Each day brings a new insight from financial experts around the world, customized for the Indian market context.
        These wisdom nuggets are accompanied by practical applications, detailed explanations, and even lucky numbers with financial significance!
        """)
        
        # Get today's fortune cookie
        fortune = generate_fortune_cookie()
        
        # Create enhanced container with cookie image style
        st.markdown("""
        <style>
        .cookie-container {
            background: linear-gradient(135deg, #f8e9c9 0%, #e6cc95 100%);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            position: relative;
            font-family: 'Times New Roman', serif;
        }
        .cookie-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><circle cx="25" cy="25" r="3" fill="rgba(139,69,19,0.2)"/><circle cx="75" cy="75" r="3" fill="rgba(139,69,19,0.2)"/><circle cx="75" cy="25" r="3" fill="rgba(139,69,19,0.2)"/><circle cx="25" cy="75" r="3" fill="rgba(139,69,19,0.2)"/><circle cx="50" cy="50" r="3" fill="rgba(139,69,19,0.2)"/></svg>');
            opacity: 0.5;
            z-index: 0;
            border-radius: 15px;
        }
        .wisdom-text {
            font-size: 1.2rem;
            color: #5d4037;
            font-style: italic;
            position: relative;
            z-index: 1;
            text-align: center;
        }
        .wisdom-author {
            font-size: 1rem;
            color: #8d6e63;
            text-align: right;
            margin-top: 15px;
            position: relative;
            z-index: 1;
        }
        .author-info {
            font-size: 0.8rem;
            color: #a1887f;
            text-align: right;
            margin-top: 5px;
            font-style: italic;
            position: relative;
            z-index: 1;
        }
        .context-heading {
            font-size: 0.95rem;
            color: #5d4037;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 6px;
            position: relative;
            z-index: 1;
        }
        .context-text {
            font-size: 0.9rem;
            color: #6d4c41;
            margin-top: 20px;
            border-top: 1px dashed #bcaaa4;
            padding-top: 10px;
            position: relative;
            z-index: 1;
        }
        .explanation-box {
            background-color: rgba(255,255,255,0.4);
            padding: 15px;
            border-radius: 8px;
            position: relative;
            z-index: 1;
            margin-top: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .application-box {
            background-color: rgba(255,248,225,0.5);
            padding: 15px;
            border-radius: 8px;
            position: relative;
            z-index: 1;
            margin-top: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 4px solid #ffd54f;
        }
        .lucky-numbers {
            margin-top: 15px;
            background-color: rgba(255,255,255,0.4);
            padding: 10px;
            border-radius: 8px;
            display: inline-block;
            position: relative;
            z-index: 1;
        }
        .number-badge {
            display: inline-block;
            width: 35px;
            height: 35px;
            background: linear-gradient(135deg, #ff9800 0%, #f44336 100%);
            color: white;
            border-radius: 50%;
            text-align: center;
            line-height: 35px;
            margin-right: 8px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .number-meaning {
            font-size: 0.85rem;
            font-style: italic;
            color: #795548;
            margin-top: 8px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Main cookie content
        st.markdown(f"""
        <div class="cookie-container">
            <div class="wisdom-text">"{fortune['wisdom']}"</div>
            <div class="wisdom-author">— {fortune['author']}</div>
            <div class="author-info">{fortune['author_info']}</div>
            
            <div class="context-heading">Understanding This Wisdom:</div>
            <div class="explanation-box">
                {fortune['explanation']}
            </div>
            
            <div class="context-heading">How To Apply It:</div>
            <div class="application-box">
                {fortune['application']}
            </div>
            
            <div class="context-heading">Indian Market Context:</div>
            <div class="context-text">{fortune['indian_context']['context']}</div>
            
            <div class="lucky-numbers">
                <strong>Lucky Market Numbers: </strong>
                <span class="number-badge">{fortune['numbers'][0]}</span>
                <span class="number-badge">{fortune['numbers'][1]}</span>
                <span class="number-badge">{fortune['numbers'][2]}</span>
                <span class="number-badge">{fortune['numbers'][3]}</span>
                <span class="number-badge">{fortune['numbers'][4]}</span>
                <div class="number-meaning">{fortune['number_meaning']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhance the Indian market context with detailed examples
        st.subheader("Applying This Wisdom to Indian Markets")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div style="background-color: rgba(232, 245, 233, 0.8); 
                        padding: 15px; 
                        border-radius: 8px; 
                        margin-bottom: 15px;
                        border-left: 4px solid #4CAF50;
                        height: 100%;">
                <h4 style="color: #2E7D32; margin-top: 0;">Nifty Application</h4>
                <p style="margin-bottom: 0;">{}</p>
            </div>
            """.format(fortune['indian_context']['nifty_application']), unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background-color: rgba(225, 245, 254, 0.8); 
                        padding: 15px; 
                        border-radius: 8px; 
                        margin-bottom: 15px;
                        border-left: 4px solid #03A9F4;
                        height: 100%;">
                <h4 style="color: #0277BD; margin-top: 0;">Historical Example</h4>
                <p style="margin-bottom: 0;">{}</p>
            </div>
            """.format(fortune['indian_context']['indian_example']), unsafe_allow_html=True)
        
        st.markdown("**Note:** The lucky numbers represent " + fortune['number_meaning'].lower() + " They aren't financial advice, but rather educational insights in numerical form.")
        
        # Provide options to apply these numbers to your financial journey
        st.subheader("Apply Your Lucky Numbers")
        
        st.markdown("""
        Your lucky numbers could be applied to various aspects of your financial journey:
        
        - **SIP Amount**: Consider adjusting your SIP amounts using combinations of your lucky numbers
        - **Investment Dates**: Try investing on dates formed by your lucky numbers
        - **Allocation Percentages**: Use these numbers to guide sectoral allocation decisions
        - **Entry/Exit Points**: Consider these as potential price points for entry or exit from investments
        - **Risk Parameters**: Use these as reference points when setting stop-loss or target levels
        - **Portfolio Review Cycles**: Schedule your portfolio reviews based on these intervals (days/weeks/months)
        """)
        
        # Enhanced share options
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Share Today's Wisdom", use_container_width=True):
                # Compose enhanced share text with Indian context
                ctx = fortune['indian_context']
                share_text = f"""Today's Financial Wisdom: 
\"{fortune['wisdom']}\" - {fortune['author']}

Understanding: {fortune['explanation'][:100]}...

Indian Market Application: {ctx['nifty_application'][:100]}...

#IndiaQuant #FinancialWisdom"""
                st.success("Wisdom copied to clipboard! You can now paste it anywhere to share.")
                st.code(share_text, language=None)
            
    with tab5:
        st.header("Financial Literacy Resources")
        
        st.markdown("""
        Explore essential financial concepts from top books on wealth and investing.
        These timeless principles will help you develop a strong foundation for your
        financial journey, no matter where you're starting.
        """)
        
        # Get book insights
        books = get_book_insights()
        
        # Create a book selector
        book_titles = list(books.keys())
        
        # Add a default selection instruction
        book_titles.insert(0, "Select a book to explore")
        
        selected_book = st.selectbox(
            "Choose a financial book to explore its key lessons:",
            book_titles
        )
        
        # Display book insights if a valid book is selected
        if selected_book != "Select a book to explore":
            book = books[selected_book]
            
            # Book header with title and author
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); 
                        padding: 20px; 
                        border-radius: 10px; 
                        margin-bottom: 20px;
                        color: white;">
                <h3 style="margin: 0;">{selected_book}</h3>
                <p style="margin: 5px 0 0 0; opacity: 0.8;">by {book['author']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Book summary
            st.subheader("Book Summary")
            st.markdown(f"<p style='font-style: italic;'>{book['book_summary']}</p>", unsafe_allow_html=True)
            
            # Key lessons
            st.subheader("Key Lessons")
            
            for i, lesson in enumerate(book['key_lessons']):
                st.markdown(f"""
                <div style="background-color: rgba(240, 242, 246, 0.8); 
                            padding: 15px; 
                            border-radius: 8px; 
                            margin-bottom: 10px;
                            border-left: 4px solid #2575fc;">
                    <p style="margin: 0;"><strong>Lesson {i+1}:</strong> {lesson}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Indian context
            st.subheader("Indian Market Context")
            st.markdown(f"""
            <div style="background-color: rgba(255, 235, 205, 0.8); 
                        padding: 15px; 
                        border-radius: 8px; 
                        margin: 20px 0;
                        border-left: 4px solid #FF9800;">
                <p style="margin: 0;">{book['indian_context']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Actionable steps based on book principles
            st.subheader("Actionable Steps")
            
            if selected_book == "Rich Dad Poor Dad":
                actionable_steps = [
                    "Create a personal balance sheet listing your assets and liabilities",
                    "Identify and plan your first small asset purchase (dividend stock, small real estate)",
                    "Set aside time each week to improve your financial education",
                    "Analyze your expenses to identify what's actually an asset vs. a liability",
                    "Practice thinking like a business owner, not an employee"
                ]
            elif selected_book == "The Psychology of Money":
                actionable_steps = [
                    "Write down your personal money history and how it might be affecting your decisions",
                    "Set up automatic investments to remove emotional decision-making",
                    "Calculate your 'enough' number - when you have sufficient wealth",
                    "Build a financial plan with room for error and unexpected events",
                    "Focus on reasonable long-term consistency over optimal short-term gains"
                ]
            elif selected_book == "The Intelligent Investor":
                actionable_steps = [
                    "Calculate the intrinsic value of a company before investing",
                    "Implement a 'margin of safety' by only buying significantly below intrinsic value",
                    "Create a written investment policy to guide decisions during market volatility",
                    "Analyze companies based on long-term earning power rather than short-term results",
                    "Treat market fluctuations as opportunities rather than threats"
                ]
            elif selected_book == "Think and Grow Rich":
                actionable_steps = [
                    "Write down specific financial goals with deadlines",
                    "Create daily affirmations reinforcing your ability to achieve wealth",
                    "Form a 'mastermind' group of like-minded people pursuing financial success",
                    "Develop specialized knowledge in an area with earning potential",
                    "Create a detailed plan with specific actions toward your financial goals"
                ]
            elif selected_book == "The Millionaire Next Door":
                actionable_steps = [
                    "Calculate your expected net worth based on age and income",
                    "Audit your spending for status symbols that don't build wealth",
                    "Create a household budget that prioritizes saving and investing",
                    "Choose occupations and businesses in areas with wealth-building potential",
                    "Teach your children self-sufficiency and financial responsibility"
                ]
            elif selected_book == "A Random Walk Down Wall Street":
                actionable_steps = [
                    "Shift investments from high-cost active funds to low-cost index funds",
                    "Create an appropriate asset allocation based on your age and risk tolerance",
                    "Implement a systematic rebalancing strategy for your portfolio",
                    "Focus on tax efficiency in your investment accounts",
                    "Ignore short-term market forecasts and financial news"
                ]
            elif selected_book == "Your Money or Your Life":
                actionable_steps = [
                    "Calculate your real hourly wage including all work-related expenses and time",
                    "Track every rupee that enters or leaves your life",
                    "Create a wall chart tracking monthly income, expenses, and investment income",
                    "Evaluate all expenses by asking if you received fulfillment proportional to life energy",
                    "Reduce expenses while maintaining or increasing life quality"
                ]
            elif selected_book == "The Little Book of Common Sense Investing":
                actionable_steps = [
                    "Calculate the total expense ratio of your current investments",
                    "Start or increase regular contributions to low-cost index funds",
                    "Create a simple asset allocation with broad market coverage",
                    "Reduce or eliminate speculative investments and individual stock picking",
                    "Set up a regular review schedule but limit portfolio changes"
                ]
            
            for i, step in enumerate(actionable_steps):
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="background-color: #2575fc; 
                                color: white; 
                                width: 25px; 
                                height: 25px; 
                                border-radius: 50%; 
                                text-align: center; 
                                line-height: 25px;
                                margin-right: 10px;
                                flex-shrink: 0;">
                        {i+1}
                    </div>
                    <div style="background-color: rgba(240, 242, 246, 0.8); 
                                padding: 10px 15px; 
                                border-radius: 8px;
                                flex-grow: 1;">
                        {step}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Related books recommendation
            st.subheader("Related Books")
            
            related_books = {
                "Rich Dad Poor Dad": ["The Cashflow Quadrant", "Unfair Advantage", "The Psychology of Money"],
                "The Psychology of Money": ["The Millionaire Next Door", "Your Money or Your Life", "Rich Dad Poor Dad"],
                "The Intelligent Investor": ["Security Analysis", "The Little Book of Common Sense Investing", "One Up On Wall Street"],
                "Think and Grow Rich": ["How to Win Friends and Influence People", "The Richest Man in Babylon", "Atomic Habits"],
                "The Millionaire Next Door": ["The Automatic Millionaire", "Rich Dad Poor Dad", "Your Money or Your Life"],
                "A Random Walk Down Wall Street": ["The Little Book of Common Sense Investing", "The Four Pillars of Investing", "The Intelligent Investor"],
                "Your Money or Your Life": ["Early Retirement Extreme", "The Simple Path to Wealth", "The Millionaire Next Door"],
                "The Little Book of Common Sense Investing": ["A Random Walk Down Wall Street", "The Bogleheads' Guide to Investing", "The Intelligent Investor"]
            }
            
            col1, col2, col3 = st.columns(3)
            
            for i, related_book in enumerate(related_books[selected_book]):
                with [col1, col2, col3][i % 3]:
                    st.markdown(f"""
                    <div style="text-align: center; 
                                padding: 15px; 
                                background-color: #f0f2f6; 
                                border-radius: 10px;
                                height: 100px;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                align-items: center;
                                margin-bottom: 10px;">
                        <p style="font-weight: bold; margin: 0;">{related_book}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            # Show a gallery of all books when no specific book is selected
            st.subheader("Popular Financial Books")
            st.markdown("Select a book above to explore detailed insights and lessons")
            
            # Create a grid layout for book covers
            col1, col2, col3, col4 = st.columns(4)
            
            # List all books with brief descriptions
            book_brief = {
                "Rich Dad Poor Dad": "Learn to think about money the way the rich do",
                "The Psychology of Money": "Understanding the human behavior behind financial decisions",
                "The Intelligent Investor": "The definitive book on value investing",
                "Think and Grow Rich": "The mindset and habits that create wealth",
                "The Millionaire Next Door": "The surprising secrets of America's wealthy",
                "A Random Walk Down Wall Street": "The case for efficient markets and index investing",
                "Your Money or Your Life": "Transforming your relationship with money",
                "The Little Book of Common Sense Investing": "The only way to guarantee your fair share of market returns"
            }
            
            columns = [col1, col2, col3, col4]
            
            for i, (title, brief) in enumerate(book_brief.items()):
                with columns[i % 4]:
                    st.markdown(f"""
                    <div style="text-align: center; 
                                padding: 15px; 
                                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                                border-radius: 10px;
                                height: 180px;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                align-items: center;
                                margin-bottom: 20px;">
                        <p style="font-weight: bold; margin: 0 0 10px 0;">{title}</p>
                        <p style="font-size: 0.8rem; margin: 0;">{brief}</p>
                    </div>
                    """, unsafe_allow_html=True)

# Run the show function when this module is executed
if __name__ == "__main__":
    show()