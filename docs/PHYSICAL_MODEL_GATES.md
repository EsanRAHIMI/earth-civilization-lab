# Physical-accounting prototype: scientific gates
This version adds an explicitly unit-tagged carbon stock-flow accounting core.
The invariant is atmosphere carbon + ocean carbon + land carbon + remaining fossil carbon.
Combustion moves carbon from fossil reserves to atmosphere; atmosphere-ocean and atmosphere-land exchange move carbon between stocks. Annual residual must be under 1e-7 GtC.
This invariant is a software/physics accounting requirement; it does not establish validity of the flux coefficients or forecasts.
The current carbon exchange coefficients and initial stocks are illustrative and **not calibrated**. The current 1000-year population and energy growth assumptions are unrealistic extrapolations, intentionally retained to expose the need for endogenous feedbacks. No global temperature claim can be made.
Acceptance gates for future release:
1. Document initial stock source and vintage, emissions factor and uncertainty.
2. Fit observed carbon flux and emissions with an external historical holdout.
3. Add an independently benchmarked carbon cycle and temperature response with units.
4. Couple population cohorts, energy supply, land/water/food and institutions with transparent data.
5. Test structural alternatives and policy robustness under model uncertainty.
6. Seek independent scientific review before policy claims.
