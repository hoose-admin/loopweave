AI SHOULD NEVER EDIT THIS FILE

This is a website called loopweave.io. Its primary function is to simplify stock trading metrics and plots to show users. There are two portions: micro, and macro. The Macro portion we will implment later. We will not implement it now.

# Existing data and research

Papers and existing data:

- lo, mamaysky and Wang (2000) foundations of technical analysis
- enhancing market trend prediction using CNN on Japanese candlestick patterns (2025)
- profitability of TA: evidence from the piercing line and dark cloud cover patterns in forex

Samurai trading academy results (samuraitradingacademy.com)

## Dividend Adjusted close or 
https://financialmodelingprep.com/stable/historical-price-eod/dividend-adjusted?symbol=AAPL 

## Simple Currently implemented strategies:

### 20SMA Trendlines
price should bounce off the 20sma line. Price above line should treat 20sma as support, price below line should treat 20sma as resistance. calculation should only be done once trend is confirmed. Must do logic to confirm trend. 

### Golden/Death Cross

- Identify the following signals.
- identify the next significant turning point statistically.
  - Show the turning point and stats on the downside (trade loss) and the upside (trade win). show a boxplot for each.
  - Is concavity over a certain timeframe (5 days, 10 days, 20 days?) of the chart the best way to do this? Better way to identify turning points?
- Give a boxplot to show the trade exit on winning side
- Give a boxplot to show the
- Identify the stop loss if the trade goes the other way
- Deteremine the
- Create a time based analysis (5, 10, 20, 40, 80, 160, 320, 640 days) after the target metric was identified. determine the turning point statistically based on this to maximize the trade outcome.

Buy Signal (Golden Cross):

- Core Logic: ema_20 crosses above sma_50 (or 50 crosses 200).
- Required Schema Fields: ema_20, sma_50, sma_200

Sell/Exit Signal (Death Cross):

- Core logic: ema_20 crosses below sma_50.
- Required Schema: ema_20, sma_50, sma_200

### Momentum Reversal: RSI Overbought/Oversold

Statistical Analysis Test how often the price is higher 5, 10, or 20 days after an RSI signal compared to the overall average price change.

Buy Signal: rsi falls below 30 (oversold) and then crosses back above 30.
- rsi, close

Sell Signal: rsi rises above 70 (overbought) and then crosses back below 70.
- rsi, close

### Bollinger bands

This strategy uses the Bollinger Bands (which are based on the standard deviation, capturing 95% of price movement) to identify periods of low volatility that often precede large price moves (breakouts). Statistical Analysis Test if breakouts that occur after a squeeze lead to a statistically significant higher return than breakouts that happen during high volatility.

- Contraction Signal: The distance between bb_upper and bb_lower is at its minimum over the last X days (the "Bollinger Band Squeeze").

  - bb_upper, bb_lower

- Breakout Signal: Following a squeeze, the close price breaks above bb_upper (Bullish Breakout).
  - close, bb_upper, bb_lower

### Confirmation: MACD Crossovers

MACD is primarily a momentum indicator, but its signals are often used to confirm the directional shift identified by the moving average crossovers or RSI signals. Statistical Analysis Test the false signal rate of a simple MA crossover strategy (e.g., 50/200 MA) without the MACD filter, versus the false signal rate with the MACD filter. The filter should decrease the false signals.

Strategy Component Core Logic Required Schema Fields
Bullish Confirmation: macd_histogram crosses above the zero line.

- macd_histogram
  Bearish Confirmation: macd_histogram crosses below the zero line.
- macd_histogram

### Average True Range (ATR) to identify periods of extreme calm.

The statistical edge comes from the market's tendency for low volatility to be followed by high volatility (volatility clustering).

## Best patterns: ---- IMPLEMENT LATER -----

- head and shoulders
- bullish and bearish rectangle
- triple top and bottom
- double top and bottom
- ascending and descending channel
- descending and descending triangles
- bull and bear flag
  // Dont use for now: - cup and handle?

Worst: - bullish and bearish pennant

# UI

## Setup

Next.js app
Typescript
Styled components - NO TAILWIND

All of the data that comes into and goes out of the application should have types set. This includes incoming stock and pattern data, user data, etc. Always enforce types.

API router in frontend that reaches out to the backend server on cloud run. This api server in next js just simplifies all the routes and consolidates them into a single place.

All plots will use plotly. The /micro feed page will have all static plots, clicking on a static plot in the /micro page will take you to a page for each asset.

## Design Principles

Hyper Minimalist and clean scandanavian design.

Use Material UI icons.

### Color Scheme:

These are the only hex codes that should be used:
FFF, AAA, 666, 333, 64a7fa (Primary color), ff7878 (secondary color)
The colors should be used in a tiered hierarchical system to create depth according to best practices for minimalist UIs with depth.

### Fonts:

loopweave logo and text should use the font: "Asimovian"
General text should be "Poiret One" font
description and detail text should be "Roboto"

## Pages

### Front Page

Front Page (https://www.loopweave.io)

### Login Page

Login page (https://www.loopweave.io/login): Connected to firebase auth

- Username and password are supported

### Account Page

In the upper right of all pages there is a account icon. Clicking on that when not logged in brings you to the login page.

Click on the account icon when logged in brings you to the /account page where users can edit information about themselves.

### Micro Page

Micro page (https://www.loopweave.io/micro/USER_UUID)

- If a user navigates to /micro without being logged in, then there is a default profile that is displayed.
- User data and favorites are stored in firebase.
- displays user specific metrics or trends. There is a button at the top which deploys a slider. This we will call the "metric slider". It should be its own styled component. It is described below. Selecting the metric from the metric slider will query bigquery database which stocks meet this criteria.
- Default results will be cached and served for all people on the default profile
- Here the top 10 cards are shown which align to the metrics that the user has set

  - Each card is for a different stock that meets the criteria of the metric
  - each card has a picture of the stock price in a hyper minimalist format, with lines for the stock price and the indicator that necessary to see according to the prior list (macd, 200SMA, etc).
  - Plots need to be static to optimize performance in plotly.

    - When rendering: Plotly.newPlot('myDiv', data, layout, config);
    - const config = {
      displayModeBar: false, // Hides the toolbar
      staticPlot: true, // Disables all interactivity
      responsive: true // Optional: makes it responsive
      };
    - Create a Custom Plotly Bundle to reduce the plotly package size and memory overhead in the application. We only need line, scatter, bar, and candlestick plots.
      - Step 1: Create a dedicated Plotly module file
      - Create a new JavaScript file in your project (e.g., src/utils/custom-plotly.js). This file will define your minimized Plotly object.
    - var Plotly = require('plotly.js/lib/core');
      // 2. Load in the necessary trace modules
      Plotly.register([
      require('plotly.js/lib/scatter'), // Includes line and scatter plots
      require('plotly.js/lib/bar'), // Includes bar charts
      require('plotly.js/lib/candlestick') // Includes financial candlestick charts
      ]);

    // 3. Export the customized Plotly object
    module.exports = Plotly;

    Something like this:
    // src/components/MyMinimalPlot.js
    import React from 'react';

    // Import the factory and your custom Plotly bundle
    import createPlotlyComponent from 'react-plotly.js/factory';
    import Plotly from '../utils/custom-plotly'; // Path to your custom file

    // Create the specific Plot component
    const Plot = createPlotlyComponent(Plotly);

    class MyMinimalPlot extends React.Component {
    render() {
    return (
    <Plot
    data={this.props.data}
    layout={this.props.layout}
    config={{
                  displayModeBar: false, // Optional: Hide toolbar for minimalism
                  staticPlot: true,      // Optional: Disable interactivity
              }}
    />
    );
    }
    }

    export default MyMinimalPlot;

#### Metric slide-in

Metrics include:

- MACD cross over
- Golden Cross
- Death Cross
- RSI Extremes
- Volume spikes
- Breakouts below resistance
- Breakouts above resistance
- Candlestick patterns:
  - BULLISH: inverted hammer, bullish engulfing, morning star, three white soldiers
  - Bearish: three black crows, bearish engulfing, shooting star, evening star

I want you to generate a super minimalist image of what each of these metrics looks like, and create a card for each one.

Group the metrics into three divs, each with a different visual color. 1. General (death cross, macd crossover, resistance, rsi, volume), 2. BULLISH candlestick PAtterns, 3. Bearish candlestick patterns

### Micro detail page:

- When a user clicks on one of the static cars in the /micro page, it should take them to a detailed page of the stock with a fully featured and interactive plotly plot of the stock price line chart, RSI line chart, volume bar chart that are all synced up and incorporated into a single plot separated by sections
- This shows the data for the stock including the PE ratio, Forward PE ratio, EBIDTA, market cap, etc. Please make a full list of all the typical fields that you would find in something like yahoo finance.

### Subscription page

(https://www.loopweave.io/subscribe)

- Payment links through stripe. Monthly fee of $1
- /micro will have a subscription option that will allow users to create custom metrics under the routing /micro/custom

### Macro Page

- Macro page: (https://www.loopweave.io/macro/USER_UUID)

# Backend

## General

- local scripts that will deploy the infrastructure. This includes all the gcloud commands
- ALWAYS use Python types for all data coming into and going out of the backend.
- The Complete Architecture is
  - front end hosted on cloud run,
  - Cloud run instance 1 (API): a backend API that has routes hit by the frontend and the cloud scheduler
  - cloud scheduler: that runs a job on the Analytics cloud run instance every 24 hours.
  - cloud run instance 2 (Analytics): that runs the Pandas-TA jobs to calculate the metrics and the Patterns and upload them to Bigquery. jobs on this instance are started up by the cloud scheduler, and run for the length of time needed before spinning down.
  - FireBase will handle the Auth
  - firestore will handle the user profiles and settings.
  - Stripe will handle payments for subscriptions

## API

- Cloud Run backend defines the backend API.
  - This should be a fastAPI python backend that serves a limited number of endpoints
  - Include full CI/CD that will send this to artifact registry and deploy from there
  - Create the dockerfile for this backend

### API Routes

- The following routes should be implemented:

#### frontend routes

- needed for user sign in
- fetching user profiles
- stripe payments
- etc. I need you to carefully go through all the frontend requests needed and add routes here as necessary.

#### /timeseries

Bigquery query that retrieves all the necessary stock data and pre calculated metrics in the 'timeseries' table

#### /patterns/{}

Queries the bigquery table to retrieve the necessary pattern data

#### /stocks

gets the general stock data from the 'stocks' table

## Cloud Run instance 2 (analytics)

This cloud run instance is used for longer running jobs. It it called once every 24 hours by the cloud scheduler.

#### /sync

    - Pull the data from the previous 24 hours from the following finance api: (https://site.financialmodelingprep.com/developer/docs)
    - I want to start with 20 companies to sync their data to bigquery. I want to use daily (EOD) intervals, for the data going back 5 years.
      - I need you to propose a solution on how to most efficiently query data from FMP api to get all of the stocks.

#### /ta-metrics

    - Query the BigQuery data which will include the stock proces, and calculate all the major metrics and insert them into new columns in the bigquery table (EMa, SMA, MACD, etc)
    - Calculate the patterns like (Three Black Crows, Doji Star, Engulfing Pattern, Inverted Hammer). Do this using the daily stock data. Place the start time, end time, stock ID, pattern type into the "ta" bigquery table.
    - use the following python library to calculate the metrics and the patterns https://www.pandas-ta.dev/

## Cloud Scheduler

Once every 24 hours at 3AM EST a cron job is run. It hits the endpoints in the cloud run instance 2 (Analytics).

- At 3AM EST: A cloud scheduler job hits /sync to sync the financial data to the timeseries bigquery table
- At 4AM EST: A cloud scheduler job hits the /ta-metrics endpoint to sync all the TA metrics to bigquery

## bigquery

where all the financial data is stored. It contains three tables: timeseries, stocks, patterns

### Three tables:

#### timeseries:

timeseries data with all the open, close, all the other metrics from the API (Stock Batch Quote API)

      - Is this most appropriate? https://financialmodelingprep.com/stable/batch-quote?symbols=AAPL&apikey=
      - Is this most appropriate for this application? https://financialmodelingprep.com/stable/historical-price-eod/full?symbol=AAPL&apikey=

      - This will be updated by the cron job to contain all the PANDAS-TA metrics like EMA, SMA, etc

      - how do we implement indexing to return results in the most efficient manner?

#### stocks

Company data information: https://financialmodelingprep.com/stable/profile?symbol=AAPL&apikey=

#### patterns

This contains all the patterns calculated via the cron job and uploaded here - Company ID, timeframe, pattern, etc. - how do we implement indexing to return results in the most efficient manner?
How do we index this table for more efficient querying?

Schema should be the following:

- uuid of the pattern identification
- Pattern name
- pattern start DT
- pattern end DT
- context DT start(+/- 20 days or 20% the pattern length? Idk)
- context DT end
- volume integral or derivative? Regression of some kind?
- RSI
- MACD
- stock name
- candle wick info on entry and exit? - need guidance here
- stock type (finance, tech, manufacturing, etc)
- market (NASDAQ, sp500, etc)

#### trades

This contains the following data. here is the schema:

- trade uuid
- pattern uuid
- pattern name
- prediction
- result (correct incorrect)
- percent (+10% or -20?)
- stock
- long/short
- DT open
- DT close
- stock value Open
- stock value close

## Analytics

- must determine statistically the ultimate downside and upside reversal to get a final price target for the trade (monetize this)
- must determine which strategy will product best results including Leverage amount, Stops, etc.

## Firestore

Firestore contains all the user data. Please use a general user Schema here. The user should be able to manage their profile in the upper right by clicking on an account material UI icon and save information here.

# ------ DO NOT IMPLEMENT ANY OF THE FOLLOWING FEATURES YET ------

## Marketing

Make a YT channel
Rip the style off bravos research

## General

### Documents:

data.sec.gov: Form 10-k and 10-Q
sec.api.io: Form 8-k, prospectus (s1, s3, 424b), Form 13F

Banks/Finanical institutions (fdic call reports)
insurance companies (extensive reporting)
NEED MORE DATA SOURCES FOR THE MACRO VIEW

### Public Sentiment

- Connect to social media sources to get sentiment
- There is a website that has sentiment calculations, see if they have an API
  -Market Sentiment | Trend-Following | Seasonality | Macroeconomic Conditions | Price Patterns | Market Breadth
- https://www.stockgeist.ai/stock-market-api/

## Machine learning models

- determine how forward PE ratios will form
- cluster analysis to see how other companies historically with comparable metrics to current companies have performed.
  - debt risk
  - PE ratios
  -
- Anaylze the impact of fed interest rates on company valulations
- understand debt burden
- Try with DNN using Bigquery Query language to make simple model
- Compare simple DNN model with a CNN-LSTM model
  - for high dimensional multivariate time series
  - CNN Layer first processes the multivariate data (price, volume, market cap, etc) from the fixed window
    - Extract relevant features and patterns from the fixed window
  - feature vectors from CNN send to LSTM layer which learns the time based dependencies and long term sequence evolution fo extracted features.
- Implement training and serving pipeline
  - Follow google best practices here for training models, serving, storing them (buckets?), monitoring, etc.
