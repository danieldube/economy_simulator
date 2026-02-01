## 1. Architecture Overview

### 1.1 Package Structure

```text
wealth_sim_germany/
    config/
    data/
    models/
    simulation/
    backtesting/
    analysis/
    cli/
    utils/
tests/
```

### 1.2 Core Modules

* **config** – scenario definitions and YAML loader.
* **data** – distribution registry and population sampling.
* **models** – Person, Government, TaxCalculator, IncomeModel, WealthModel.
* **simulation** – SimulationController and year-step engine.
* **backtesting** – reference comparison and metrics.
* **analysis** – distribution analytics and reporting.
* **cli** – command-line entrypoint.
* **utils** – logging, types, RNG, helpers.

---

## 2. Domain Model Specification

### 2.1 Types and Enums (`utils/types.py`)

* `PersonId`
* `Sex`
* `EducationLevel`
* `Region`
* `GovFunction`
* `IncomeSource`

---

### 2.2 Person Model (`models/person.py`)

Fields:

* Demographics: `age`, `sex`, `education`, `region`
* Income: labor, capital, transfers, total, taxes, net
* Wealth: liquid/illiquid assets, debt, stocks, net wealth
* Weight: sampling weight

Methods:

* `compute_total_gross_income()`
* `apply_tax_result(income_tax, social_contrib, capital_tax)`
* `update_wealth(savings_rate, labor_return_rate, capital_return_rate)`

---

### 2.3 Government / State Model (`models/government.py`)

Fields:

* Revenue: tax categories, social contributions, total
* Expenditure categories by `GovFunction`
* Debt, deficit, GDP
* Policy parameters: spending shares, deficit limit

Methods:

* `collect_taxes_from_population(persons)`
* `allocate_expenditure(policy_overrides=None)`
* `apply_fiscal_rules()`
* `pay_transfers(persons, transfer_rule)`

---

### 2.4 Income Model (`models/income.py`)

Methods:

* `sample_labor_income(person, rng)`
* `sample_capital_income(person, rng)`

Uses conditional distributions from the DistributionFactory.

---

### 2.5 Wealth Model (`models/wealth.py`)

Methods:

* `initialise_wealth(person, rng)`
* `evolve_wealth(person, rng, macro_params)`

---

### 2.6 Tax Calculator (`models/tax.py`)

Methods:

* `compute_income_tax(taxable_income)`
* `compute_capital_tax(capital_income)`
* `compute_social_contributions(gross_income)`
* `compute_all_taxes(person)`

Tax rules parameterised in `TaxConfig`.

---

### 2.7 TransferRule (Protocol)

* `compute_transfer(person, government) -> float`

Used by GovernmentAgent to distribute social-protection spending.

---

## 3. Data & Distribution Layer

### 3.1 DistributionFactory (`data/distributions.py`)

* Register empirical distributions.
* Register parametric (scipy) distributions.
* `sample(name, rng, conditions=None)` supporting conditional filtering.

---

### 3.2 Data Sources (`data/sources.py`)

* Abstract loader for CSV, future remote APIs.
* Supplies DataFrames to the distribution factory.

---

### 3.3 Weight Scaling (`data/weights.py`)

Functions:

* `compute_global_weight(pop_size, synthetic_n)`
* `assign_weights(persons, tot_pop)`

---

## 4. Configuration System

### 4.1 Pydantic Schemas (`config/schemas.py`)

* `TaxConfig`
* `GovernmentSpendingConfig`
* `PopulationConfig`
* `MacroParams`
* `ScenarioConfig`
* `BacktestConfig`

### 4.2 Loader (`config/loader.py`)

* `load_scenario_config(path) -> ScenarioConfig`

---

## 5. Simulation Engine

### 5.1 SimulationContext (`simulation/time_step.py`)

Contains all models and RNG.

### 5.2 Year-Step Function

`run_single_year(ctx, persons, government, year, scenario) -> (persons, government)`

Steps:

1. Income sampling.
2. Tax calculation.
3. Government revenue update.
4. Policy overrides applied.
5. Expenditure allocation.
6. Transfer payments.
7. Wealth update.
8. Debt/deficit calculation.
9. Fiscal rule enforcement.

---

### 5.3 SimulationController (`simulation/engine.py`)

Methods:

* `initialise()` – build distribution factory, create persons, create government.
* `run()` – loop for N years and store yearly aggregates.

Returns: `SimulationResult`

---

## 6. Analytics & Reporting

### 6.1 Aggregations

Functions:

* `gini(values, weights)`
* `weighted_mean(values, weights)`
* `aggregate_by_group(persons, group_field, value_field)`

### 6.2 Reporting

* `build_aggregates(persons, government, year)` → dict of indicators.
* Optional plots.

---

## 7. Backtesting

### 7.1 Metrics (`backtesting/metrics.py`)

* MAPE
* RMSE
* KL divergence

### 7.2 Backtesting Engine (`backtesting/engine.py`)

Methods:

* `load_reference_data()`
* `compare(result)`
* `check_tolerances(comparison_df)`

---

## 8. CLI

Command: `wealth-sim run --config scenario.yaml --backtest-config backtest.yaml`

---

## 9. Implementation Plan

### Phase 1 – project skeleton

Create directory structure, config loader, utilities, tests.

### Phase 2 – Person, Government, DistributionFactory

Implement core domain models, stubs for distributions, tests.

### Phase 3 – Income and Wealth Models

Implement sampling logic and wealth evolution, tests.

### Phase 4 – Tax Calculator

Implement German tax rules parameterised by config.

### Phase 5 – Government behaviour

Expenditure allocation, debt brake, transfers.

### Phase 6 – Simulation engine

Implement multi-year orchestration and aggregation.

### Phase 7 – Backtesting

Implement metrics, backtesting engine and CLI integration.

### Phase 8 – Documentation & cleanup

Write docs, ensure type safety, add examples.
