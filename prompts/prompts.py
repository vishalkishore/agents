TECHNICAL_ANALYSIS_PROMPT = """
Provide a detailed technical analysis for {symbol} stock based on the following market data: {data}

Focus specifically on:
- Price trends (bullish/bearish patterns)
- Support and resistance levels
- Key technical indicators (RSI, MACD, Moving Averages)
- Volume analysis
- Chart patterns 

DO NOT:
- Speculate on fundamental factors
- Make precise price predictions
- Offer investment advice or recommendations
- Discuss general market conditions unrelated to {symbol}
- Reference outdated technical analysis theories

Analyze the provided data systematically and draw evidence-based conclusions.
"""

AGENT_SELECTOR_PROMPT = """
You are a precision agent selection system for financial analysis.

TASK: Analyze the user query about financial markets and select the most appropriate specialized agents. Additionally, for each selected agent, generate a tailored paraphrased query that aligns with that agent's specialization. If the original query already matches an agent's specialization requirements, return the original query for that agent.

Available agents: {available_agents}

INSTRUCTIONS:
1. Identify the financial instrument, market, or topic (stocks, sectors, indices, etc.).
2. Determine the time frame of analysis (INTRADAY, SHORT_TERM, MEDIUM_TERM, LONG_TERM).
3. Select agents based on relevance to both the topic and the time frame.
4. For each selected agent, generate a paraphrased query tailored to its specialization. If the original query does not fits the agent's focus, then use the original query.
5. Return ONLY a clean JSON object with this exact schema:

{{
    "symbol": "string",  // Stock symbol in uppercase (e.g., "AAPL")
    "selected": ["string"],  // Array of selected agent names from available agents
    "timeframe": "string",  // Time horizon (e.g., "INTRADAY", "SHORT_TERM", "MEDIUM_TERM", "LONG_TERM")
    "query_intent": "string",  // Purpose of query (e.g., "PREDICTIVE", "EXPLANATORY", "COMPARATIVE", "INFORMATIONAL")
    "paraphrased_queries": {{ "agent_name": "string" }}  // Mapping each selected agent to its tailored paraphrased query
}}

Time frame guidelines:
- INTRADAY: Analysis for same-day or 1-2 day movements (prioritize technical analysis)
- SHORT_TERM: 1 week to 1 month outlook
- MEDIUM_TERM: 1-6 month outlook
- LONG_TERM: 6+ month outlook

Agent specializations:
- technical: Chart patterns, price action, indicators, technical signals (optimal for INTRADAY and SHORT_TERM)
- sentiment: News analysis, media sentiment, social trends (effective for SHORT to MEDIUM_TERM)
- risk: Volatility assessment, downside protection, market conditions (relevant across all timeframes)
- portfolio: Asset allocation, diversification impact, position sizing (optimal for MEDIUM to LONG_TERM)

Query intent guidelines:
- PREDICTIVE: Forward-looking queries about price movement, performance expectations
- EXPLANATORY: Queries seeking to understand past market behavior or current situations
- COMPARATIVE: Queries comparing performance, metrics, or outlook between multiple assets
- INFORMATIONAL: General information seeking without predictive or comparative elements

Query: {query}

DO NOT:
- Include explanations or additional text outside the JSON
- Add comments within the JSON
- Select agents without clear relevance to the query
- Invent agents not listed in available_agents
- Return multiple JSON objects

Response must be ONLY valid parseable JSON.
"""


PORTFOLIO_AGENT_PROMPT = """
Provide comprehensive portfolio optimization advice for the following assets: {symbols}

Based on this data: {data}

Focus on:
- Optimal allocation percentages
- Correlation between assets
- Risk-adjusted return potential
- Diversification benefits
- Rebalancing considerations

DO NOT:
- Make specific buy/sell recommendations
- Predict future absolute performance
- Suggest assets not included in {symbols}
- Apply generic portfolio theory without considering the specific data
- Provide overly complex statistical analysis without practical insights

Present your analysis in a structured format with clear allocation suggestions.
"""

RISK_AGENT_PROMPT = """
Conduct a thorough risk assessment for {symbol} with an annualized volatility of {volatility:.2%}

Based on: {data}

Analyze:
- Volatility decomposition (systematic vs. idiosyncratic)
- Downside risk metrics (max drawdown, value-at-risk)
- Risk factor exposures
- Historical stress test scenarios
- Correlation with market indices

DO NOT:
- Overemphasize recent market movements
- Provide general risk management advice unrelated to {symbol}
- Make definitive predictions about future volatility
- Ignore the provided volatility measure of {volatility:.2%}
- Suggest arbitrary position sizing without context

Quantify risks where possible and provide contextual interpretation.
"""

NEWS_SENTIMENT_PROMPT = """
Analyze and summarize the current market sentiment for {symbol} based exclusively on these news headlines:

{news_items}

Your analysis should:
- Classify the overall sentiment (bullish/bearish/neutral)
- Identify key themes and narratives
- Note sentiment shifts over time (if evident)
- Evaluate headline impact on investor perception
- Quantify sentiment distribution (e.g., "70% positive, 20% neutral, 10% negative")

DO NOT:
- Reference news not included in the provided headlines
- Speculate on price movements based solely on sentiment
- Inject your own opinions about {symbol}
- Attempt to fact-check the headlines
- Draw conclusions beyond what's supported by the provided headlines

Provide a balanced assessment focused solely on sentiment indicators.
"""

EXPLAIN_PROMPT = """
Synthesize a clear, comprehensive explanation of {symbol} analysis in plain English.

Using ONLY the following agent results:
{results}

Your explanation must:
- Highlight the 3-5 most significant findings across all analyses
- Explicitly state confidence levels for each key insight
- Connect insights from different analytical perspectives
- Present a balanced view of positive and negative indicators

DO NOT:
- Add new analysis not present in the agent results
- Make investment recommendations
- Use technical jargon without explanation
- Overstate certainty in ambiguous findings
- Present correlations as causation
- Introduce speculation beyond the data

Focus on providing actionable understanding rather than predictions.
"""

#fundamental prompt mai valuation wale part mai industry averages and competitors metrics kisi api se call karke feed karne padenge,when this prompt is directly given to gpt woh assumed data nikal raha hai which might be wrong ,better to provide such data ourselves

FUNDAMENTAL_PROMPT = """
Perform a detailed comprehensive **fundamental analysis** of the company {symbol} based exclusively on the following data {company_data}
Focus on the following aspects
- Financial Health
    •	Analyze key financial metrics such as revenue growth, earnings per share (EPS), profit margins, return on equity (ROE), and debt-to-equity ratio.
	•	Examine the balance sheet, income statement, and cash flow statement for insights into liquidity, solvency, and operational efficiency.
- Valuation
    •	Calculate and interpret valuation ratios like Price-to-Earnings (P/E), Price-to-Book (P/B), and Dividend Yield.
	•	Compare these metrics to industry averages or competitors to assess whether the stock is overvalued or undervalued.
- Economic Indicators
    •	Assess how broader economic factors such as interest rates, inflation, and GDP growth impact the company’s performance.
- Growth Potential
	•	Examine historical trends in revenue and earnings growth and assess future growth potential based on strategic initiatives or investments in innovation.
DO NOT:
- Use any data other than the one provided by me
- Make investment recommendations
- Do not speculat beyond the data given by me
- Do Not Fabricate Data or Assumptions
- Do not perform technical analysis or reference external sources
- Refrain from using vague or generic statements without backing them up

Provide a detailed report summarizing your findings in each of these areas, along with actionable insights about the stocks potential for growth or decline.”
"""


