# NFL Quarterback & Running Back Value Analysis

This project investigates how NFL teams allocate salary cap resources to quarterbacks and running backs and how effectively those dollars translate into on-field production and team success. It spans the 2015–2025 seasons (except 2021, for which data is unavailable) and was built using Python, pandas, NumPy and Matplotlib. The interactive site is styled with HTML/CSS using official NFL colors.

## Data Sources

* **Pro Football Reference passing statistics (2015–2025).** Provides quarterback counting stats and advanced metrics, including ESPN’s Total Quarterback Rating (QBR). Only players with position `QB` were retained.
* **Pro Football Reference rushing statistics (2015–2025).** Provides running back counting stats such as attempts, yards, touchdowns and success rate. Only players with position `RB` were retained.
* **NFL team salary by position group (2015–2025).** Contains team-level spending on each position group along with wins, win percentage and playoff appearance indicators.

## Metrics

* **Quarterback Rating (QBR).** ESPN’s QBR is a proprietary efficiency metric (0–100 scale) incorporating passing, rushing, sacks and turnovers with situational adjustments. We use team‐weighted QBR where each quarterback’s QBR is weighted by his passing attempts.
* **Running Back Rating (RBR).** A composite metric created for this project. For each season, a running back’s success rate, yards per attempt, total yards and total touchdowns are normalized and then averaged. Team‐weighted RBR is calculated by weighting each player’s RBR by his rushing attempts.
* **Wins/Win Percentage.** Team wins were taken from the salary dataset; quarterback win percentages were estimated from PFR’s `QBrec` field.

## Analysis

* **Top players (Home Page).** For each season, the top five quarterbacks by QBR and the top five running backs by RBR are displayed in tables and bar charts.
* **Salary vs Performance (Analysis Page).** Team spending on quarterbacks and running backs is plotted against team‐weighted QBR and RBR. Linear regression lines and Pearson correlation coefficients are reported. We find only a modest positive relationship between quarterback spending and QBR (r ≈ {corr['qb_salary_corr']:.2f}) and an even weaker relationship for running backs (r ≈ {corr['rb_salary_corr']:.2f}).
* **Winning Correlation.** To determine positional importance for winning, we correlate team‐weighted QBR and RBR with team wins. Quarterback efficiency correlates more strongly with wins (r ≈ {corr['qb_wins_corr']:.2f}) than running back efficiency does (r ≈ {corr['rb_wins_corr']:.2f}).

## Usage

Open `index.html` in a web browser to view the top players by year. Click the **Analysis** link in the navigation bar to view regression analyses and winning correlations. The site is designed to be hosted on GitHub Pages; simply publish the `project_site` directory to deploy.

## Technology

* **Python** for data wrangling and visualization
* **pandas** and **NumPy** for data processing
* **Matplotlib** for static charts
* **HTML/CSS** for presentation, styled with official NFL palette

## Limitations and Future Work

* The salary data is aggregated at the team level and does not provide player‐specific contract values. Future versions could incorporate individual contract data for finer granularity.
* Team win data is taken from the salary dataset. An independent source for win totals and playoff results could improve accuracy.
* RBR weights each component equally. Alternative weightings or machine learning techniques could refine the running back efficiency metric.
