# Data Sources — Tobacco Monte Carlo Simulation

Every channel parameter in `mc_simulation.py` traces to one or more of the
sources listed here. Citations are in APA format. DOIs and URLs included where
available.

---

## Primary Sources by Channel

### C1 — VSL-Adjusted Mortality

**Deaths (8M/yr)**
- World Health Organization. (2023). *WHO Report on the Global Tobacco Epidemic
  2023*. WHO Press. https://www.who.int/publications/i/item/9789240077164
- GBD 2019 Tobacco Collaborators. (2021). Spatial, temporal, and demographic
  patterns in prevalence of smoking tobacco use and attributable disease burden
  in 204 countries and territories, 1990–2019. *The Lancet*, 397(10292), 2337–2360.
  https://doi.org/10.1016/S0140-6736(21)01169-7

**Value of Statistical Life (VSL)**
- Viscusi, W. K., & Masterman, C. J. (2017). Income elasticities and global
  values of a statistical life. *Journal of Benefit-Cost Analysis*, 8(2), 226–250.
  https://doi.org/10.1017/bca.2017.12
- U.S. Environmental Protection Agency. (2023). *Mortality Risk Valuation*.
  https://www.epa.gov/environmental-economics/mortality-risk-valuation
  (Central estimate: $11.6M, 2023 USD)
- Viscusi, W. K. (2018). *Pricing Lives: Guideposts for a Safer Society*.
  Princeton University Press.

### C2 — Direct Healthcare Costs

- Goodchild, M., Perucic, A.-M., & Nargis, N. (2018). Modelling the revenue
  implications of tobacco tax increases in low-income and middle-income countries.
  *Tobacco Control*, 27(Suppl 1), s19–s24.
  https://doi.org/10.1136/tobaccocontrol-2017-054119
  (Central estimate: $422B global healthcare costs)
- WHO Framework Convention on Tobacco Control Secretariat. (2023).
  *Global progress in implementing the WHO FCTC: 2023 Report*.
  https://www.who.int/fctc/reporting/

### C3 — Lost Productivity

- International Labour Organization. (2017). *The economic costs of tobacco
  use: Labour market consequences*. ILO Working Paper.
  https://www.ilo.org/global/topics/safety-and-health-at-work/
- Tobacco Atlas. (2023). *Tobacco Atlas, 8th Edition*. American Cancer Society &
  Vital Strategies. https://tobaccoatlas.org/
  (Updated $446B global productivity loss estimate)
- Goodchild, M., Nargis, N., & Tursan d'Espaignet, E. (2018). Global economic
  cost of smoking-attributable diseases. *Tobacco Control*, 27(1), 58–64.
  https://doi.org/10.1136/tobaccocontrol-2016-053305

### C4 — Secondhand Smoke Burden

- Öberg, M., Jaakkola, M. S., Woodward, A., Peruga, A., & Prüss-Ustün, A.
  (2011). Worldwide burden of disease from exposure to second-hand smoke:
  a retrospective analysis of data from 192 countries. *The Lancet*, 377(9760),
  139–146. https://doi.org/10.1016/S0140-6736(10)61388-8
- World Health Organization / International Agency for Research on Cancer.
  (2023). *IARC Monographs on the Evaluation of Carcinogenic Risks to Humans,
  Volume 100E: Personal Habits and Indoor Combustions*. IARC Press.

### C5 — Environmental Externalities

- World Health Organization. (2022). *Tobacco and the environment*.
  WHO Press. https://www.who.int/publications/i/item/9789240041729
- National Fire Protection Association. (2022). *Smoking-Material Fire Causes*.
  NFPA Research. https://www.nfpa.org/News-and-Research/Data-research-and-tools/
- Novotny, T. E., et al. (2009). Tobacco and cigarette butt consumption in
  humans and animals. *Tobacco Control*, 20(Suppl 1), i17–i20.
  https://doi.org/10.1136/tc.2011.043489

### C6 — Governance Capture

- Brownell, K. D., & Warner, K. E. (2009). The perils of ignoring history:
  Big tobacco played dirty and millions died. How similar is big food?
  *Milbank Quarterly*, 87(1), 259–294.
  https://doi.org/10.1111/j.1468-0009.2009.00555.x
- Drope, J., & Chapman, S. (2001). Tobacco industry efforts at discrediting
  scientific knowledge of environmental tobacco smoke: A review of internal
  industry documents. *Journal of Epidemiology & Community Health*, 55(8),
  588–594. https://doi.org/10.1136/jech.55.8.588
- Tobacco Tactics Research Group, University of Bath. (2023).
  *Tobacco industry lobbying expenditure database*.
  https://tobaccotactics.org/

---

## Industry Revenue (Π = $965B)

- Euromonitor International. (2023). *Tobacco: Global Industry Overview*.
  Passport database. (Commercial dataset; university library access)
- Statista. (2023). *Global tobacco market revenue 2022–2027*.
  https://www.statista.com/outlook/cmo/tobacco-products/worldwide
- Philip Morris International. (2023). *Annual Report 2022*. PMI.
  https://www.pmi.com/investor-relations/annual-report
- British American Tobacco. (2023). *Annual Report and Accounts 2022*. BAT.
- Altria Group. (2023). *2022 Annual Report on Form 10-K*. SEC EDGAR.
- Japan Tobacco International. (2023). *Annual Report 2022*. JTI.
- Imperial Brands. (2023). *Annual Report and Accounts 2022/23*.

Combined revenue of four major publicly traded tobacco groups plus estimated
revenue of China National Tobacco Corporation (state monopoly; ~$130B estimated
from duty/excise revenue) and smaller independent producers.

---

## SAPM Theoretical Framework

- Postnieks, E. (2026). *The Private Pareto Theorem: Why Market Games Destroy
  System Welfare*. SAPM Foundation Paper. Available: SSRN.
- Postnieks, E. (2026). *The Addiction Ratchet: Why the Tobacco Industry Cannot
  Be Reformed Without Replacing It*. SAPM Working Paper No. 37. Available: SSRN.

---

## Distribution Methodology

- Iman, R. L., & Conover, W. J. (1982). A distribution-free approach to
  inducing rank correlation among input variables. *Communications in
  Statistics — Simulation and Computation*, 11(3), 311–334.
  (Basis for rank-correlation approach; this simulation uses Cholesky instead)
- Cooke, R. M. (1991). *Experts in Uncertainty: Opinion and Subjective
  Probability in Science*. Oxford University Press.
  (Expert elicitation methodology for parameter uncertainty bounds)
