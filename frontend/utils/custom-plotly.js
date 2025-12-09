// Custom Plotly bundle with only necessary trace modules
var Plotly = require("plotly.js/lib/core");

// Load in the necessary trace modules
Plotly.register([
  require("plotly.js/lib/scatter"), // Includes line and scatter plots
  require("plotly.js/lib/bar"), // Includes bar charts
  require("plotly.js/lib/candlestick"), // Includes financial candlestick charts
]);

// Export the customized Plotly object
module.exports = Plotly;
