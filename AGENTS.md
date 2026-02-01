# **AGENTS.md**

## 1. Purpose and Scope

This project simulates Germany’s wealth distribution, population structure, earnings, taxation, and government budget evolution over time using Monte-Carlo methods. Multiple agents interact:

* **Population Agent** – synthetic individuals with demographic and economic states.
* **Government Agent** – public budget, tax collection, spending decisions, fiscal rules.
* **Model Agents** – specialised computational agents (Income Model, Wealth Model, Tax Model).
* **Simulation Controller** – orchestrates the interactions across time.
* **Backtesting Agent** – validates simulated aggregates against empirical data.

Each agent has clearly defined responsibilities and communicates via typed interfaces.

---

## 2. Agent Overview

### 2.1 Population Agent

Represents synthetic individuals (or households).
Responsibilities:

* Store demographic attributes (age, sex, education, region).
* Store and update economic state (income, wealth, taxes, assets).
* Provide methods to compute total income, apply tax results, evolve wealth.
* Provide sampling weights to scale results to national totals.

Key interactions:

* Receives income samples from the IncomeModel.
* Receives wealth updates from the WealthModel.
* Receives tax deductions from the TaxCalculator.
* Receives transfer payments from the Government Agent.

---

### 2.2 Government Agent (State)

Represents the German public sector.

Responsibilities:

* Collect revenue (taxes, social contributions).
* Allocate spending across functional categories (education, social protection, protection/defence, etc.).
* Apply fiscal rules (e.g. German debt brake).
* Pay transfers to the population.
* Track debt, deficits, revenue, expenditure, GDP, and spending shares.

Key interactions:

* Receives tax revenue from persons.
* Distributes transfers back to the population.
* Provides expenditure categories to the simulation controller.
* Exposes constraints (deficit limit) to ensure scenario feasibility.

---

### 2.3 Income Model Agent

Responsibility:

* Generate labor and capital income based on demographic and distribution parameters.

Interactions:

* Given a Person object and RNG, returns income values.
* Uses DistributionFactory to sample conditional distributions.

---

### 2.4 Wealth Model Agent

Responsibility:

* Initialise and evolve wealth (liquid/illiquid assets, debt).
* Apply saving rules and investment returns.

Interactions:

* Updates Person wealth each year.
* Uses macroeconomic assumptions and person-specific data.

---

### 2.5 Tax Model Agent

Responsibility:

* Compute German income tax, solidarity surcharge, church tax.
* Compute capital gains tax.
* Compute social contributions.

Interactions:

* Provides tax amounts to both Person and Government.
* Uses bracket definitions from configuration.

---

### 2.6 Distribution Factory Agent

Responsibility:

* Provide parameterised or empirical distributions for sampling demographic and economic data.
* Support conditional sampling based on person attributes.

Interactions:

* Supplies IncomeModel, WealthModel, and Person initialisation with samples.

---

### 2.7 Simulation Controller Agent

Responsibilities:

* Coordinate simulation steps across multiple years.
* Manage interactions between Person, Government, and model agents.
* Aggregate results and pass them to analytics/backtesting.

---

### 2.8 Backtesting Agent

Responsibilities:

* Compare simulated aggregates to reference empirical values.
* Compute error metrics and signal deviations.
* Validate simulation quality and calibrate parameters.

Key interactions:

* Consumes SimulationResult.
* Loads reference datasets.
* Uses metrics agents (MAPE/RMSE/KL).

---

## 3. Inter-Agent Interaction Cycle

For each simulated year:

1. IncomeModel → computes incomes for each Person.
2. PersonAgent → aggregates total income.
3. TaxModel → computes taxes.
4. PersonAgent → applies tax results.
5. GovernmentAgent → collects taxes.
6. TransferRuleAgent → computes transfers.
7. GovernmentAgent → pays transfers & updates expenditure.
8. WealthModel → evolves wealth.
9. GovernmentAgent → enforces fiscal rules.
10. SimulationControllerAgent → aggregates statistics and stores yearly state.
