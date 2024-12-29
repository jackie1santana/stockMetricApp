<template>
  <div class="stock-analysis-container">
    <h1>📊 Stock Analysis Dashboard</h1>
    <div class="input-container">
      <input v-model="symbol" placeholder="Enter Stock Symbol" />
      <button @click="getStockData">Analyze Stock</button>
    </div>

    <div v-if="stockData" class="stock-details">
      <div class="grid-container">
        <div class="grid-item">
          <h2>Overview</h2>
          <p><strong>Symbol:</strong> {{ symbol.toUpperCase() }}</p>
          <p><strong>Current Price:</strong> ${{ stockData.current_price.toFixed(2) }}</p>
          <p><strong>EPS:</strong> ${{ stockData.eps }}</p>
          <p v-if="stockData.eps > 0" class="profit-text">
            "Company is profitable! Each share earns ${{ stockData.eps }}."
          </p>
          <p v-else class="loss-text">
            "Negative earnings at ${{ stockData.eps }}. Not profitable right now."
          </p>
        </div>

        <div class="grid-item">
          <h3>Valuation</h3>
          <p><strong>P/E Ratio:</strong> {{ stockData.pe_ratio }}</p>
          <p v-if="stockData.pe_ratio < 15">
            "Looks undervalued—potentially a solid buy if fundamentals hold."
          </p>
          <p v-else-if="stockData.pe_ratio > 20">
            "Overvalued—investors expect high growth. Be cautious."
          </p>
          <p v-else>
            "Reasonably valued—watch trends and earnings reports."
          </p>
        </div>

        <div class="grid-item">
          <h3>Profit Analysis</h3>
          <p><strong>Debt:</strong> {{ stockData.debt }}</p>
          <p><strong>Net Income:</strong> {{ stockData.earnings }}</p>
          <p><strong>Profit Margin:</strong> {{ stockData.profit_margin }}</p>
          <p v-if="parseFloat(stockData.earnings.replace('$', '').replace(/,/g, '')) > 0">
            "Currently profitable with solid margins!"
          </p>
          <p v-else>
            "Still in losses—keep an eye on improvements."
          </p>

          <h4>Quarterly History</h4>
          <div v-for="(quarter, index) in stockData.quarterly_history" :key="index" class="quarter-details">
            <p><strong>{{ quarter.quarter }}:</strong> Revenue: {{ quarter.revenue }}, Net Income: {{ quarter.net_income }}, Profit Margin: {{ quarter.profit_margin }}</p>
            <p>{{ quarter.profit_margin.includes('-') ? 'Loss-making quarter.' : 'Profitable quarter!' }}</p>
          </div>
        </div>

        <div class="grid-item">
          <h3>Dividends</h3>
          <p><strong>Dividend:</strong> ${{ parseFloat(stockData.dividend.replace('$', ''))?.toFixed(2) }}</p>
          <p><strong>Dividend Yield:</strong> {{ stockData.dividend_yield }}</p>
          <h4>Dividend Projections</h4>
          <p v-for="shares in [10, 20, 50, 75, 100, 200, 500, 1000, 3000, 10000]" :key="shares">
            {{ shares }} shares: ${{ (shares * parseFloat(stockData.dividend.replace('$', ''))).toFixed(2) }} per quarter
          </p>
        </div>

        <div class="grid-item">
          <h3>Future Projections</h3>
          <p v-if="futureEarnings > 0">
            "Projected earnings could grow to approximately ${{ futureEarnings.toFixed(2) }}."
          </p>
          <p v-else>
            "Needs improvement to turn profitable."
          </p>
          <p><strong>1 Year Price Estimate:</strong> ${{ projectedPrice(1) }}</p>
          <p><strong>2 Year Price Estimate:</strong> ${{ projectedPrice(2) }}</p>
          <p><strong>5 Year Price Estimate:</strong> ${{ projectedPrice(5) }}</p>
          <p><strong>10 Year Price Estimate:</strong> ${{ projectedPrice(10) }}</p>
          <p><strong>20 Year Price Estimate:</strong> ${{ projectedPrice(20) }}</p>
          <p><strong>30 Year Price Estimate:</strong> ${{ projectedPrice(30) }}</p>
          <p><strong>Growth Insights:</strong> Based on patterns, the company may need to reduce debt and improve margins for sustained growth.</p>
          <p><strong>Warren Buffet Metric:</strong> {{ warrenBuffetVerdict }}</p>
        </div>
      </div>

      <h3>Final Verdict</h3>
      <p><strong>Verdict:</strong> {{ verdict }}</p>
      <p><strong>Reason:</strong> {{ reason }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'Stock',
  data() {
    return {
      symbol: '',
      stockData: null,
      futureEarnings: 0,
      verdict: '',
      reason: '',
      warrenBuffetVerdict: ''
    };
  },
  methods: {
    async getStockData() {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/stock/${this.symbol}/`);
        this.stockData = response.data;
        this.analyzeStock();
      } catch (error) {
        console.error('Error fetching stock data:', error);
      }
    },

    analyzeStock() {
      if (!this.stockData) return;
      const { eps, current_price, pe_ratio, debt } = this.stockData;

      this.futureEarnings = eps > 0 ? eps * 1.15 ** 3 : 0;

      if (pe_ratio < 15 && parseFloat(debt.replace('$', '').replace(/,/g, '')) < 5000000000) {
        this.warrenBuffetVerdict = 'Yes - Strong fundamentals, low debt, and undervalued.';
      } else {
        this.warrenBuffetVerdict = "No - High debt or overvaluation, may not fit Buffet's model.";
      }
    },

    projectedPrice(years) {
      const growthRate = 0.05;
      return (this.stockData.current_price * (1 + growthRate) ** years).toFixed(2);
    }
  }
};
</script>


<style scoped>
.stock-analysis-container {
  font-family: Arial, sans-serif;
  margin: 20px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
.grid-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}
.grid-item {
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 4px;
  background: #f9f9f9;
}
.profit-text {
  color: green;
}
.loss-text {
  color: red;
}
</style>

