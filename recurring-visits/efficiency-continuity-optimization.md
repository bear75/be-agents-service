# Executive Summary

The scientific literature on the Home Health Care Routing and Scheduling Problem (HHCRSP) addresses the complex task of assigning and routing caregivers to patient homes, extending the classical Vehicle Routing Problem (VRP) with healthcare-specific constraints. The core challenge lies in balancing dual, often conflicting, objectives: operational efficiency (e.g., minimizing travel costs, overtime, and number of staff) and service quality, most notably continuity of care, which involves maintaining consistent caregiver-patient assignments over time. Early research focused on deterministic, single-period models, but the field has evolved significantly to address the complexities of real-world operations. Current research emphasizes multi-period planning horizons (e.g., weekly schedules) and incorporates uncertainty through stochastic and dynamic models that account for variable travel times, service durations, and last-minute schedule changes. A major focus is on multi-objective optimization, using techniques like weighted-sum methods, epsilon-constraint, and evolutionary algorithms (e.g., NSGA-II) to navigate the trade-off between cost and continuity. The literature demonstrates a shift from simple caregiver counts to more sophisticated metrics like the Continuity of Care Index (CCI) to better measure and optimize this aspect of service. Solution methods have advanced from exact branch-and-price algorithms, suitable for smaller instances, to powerful metaheuristics (such as ALNS, VNS, and Tabu Search) and matheuristics that can solve large-scale, practical problems. A key finding is that through integrated routing and rostering approaches, significant improvements in continuity of care can be achieved with only a marginal increase in operational costs.

# Problem Definition And Scope

The Home Health Care Routing and Scheduling Problem (HHCRSP) is a complex optimization problem that integrates aspects of vehicle routing and workforce scheduling to efficiently and effectively assign and route caregivers to patients' homes for service delivery. It is formally recognized as a significant extension of the classical Vehicle Routing Problem (VRP) and is also situated within the broader category of Workforce Scheduling and Routing Problems (WSRP). The core challenge of HHCRSP lies in generating optimal schedules and routes while adhering to a multitude of constraints unique to the healthcare sector. These include matching caregiver skills to patient needs, respecting patient time windows for visits, coordinating synchronized visits requiring multiple caregivers, and ensuring continuity of care, which involves maintaining consistent caregiver-patient assignments over time. The problem aims to balance operational efficiency with the quality of care and satisfaction of both patients and caregivers.

# Problem Variants

## Variant Type

Deterministic

## Description

In the deterministic variant of HHCRSP, all problem parameters, such as patient demand, service times, and travel times, are assumed to be known with certainty in advance. This variant allows for precise planning but may not fully capture the unpredictability of real-world operations.

## Planning Horizon

Single-period or Multi-period

## Variant Type

Stochastic

## Description

The stochastic variant addresses uncertainty in the input data. It explicitly models variables like travel times and service durations as random variables with known probability distributions. The goal is to find a solution that is robust or performs well on average under this uncertainty.

## Planning Horizon

Single-period or Multi-period

## Variant Type

Dynamic

## Description

The dynamic variant accounts for real-time events and information updates during the execution of the schedule. This includes handling new patient requests, cancellations, or unexpected delays. Solutions often involve a rolling horizon approach, where the schedule is re-optimized periodically as new information becomes available.

## Planning Horizon

Multi-period (via rolling horizon)

## Variant Type

Multi-period

## Description

This formulation considers a planning horizon that spans multiple days, such as a week or a month. It is essential for addressing strategic and tactical decisions, particularly for handling repeat visits and implementing continuity of care, which requires linking assignments across consecutive days.

## Planning Horizon

Multi-period

## Variant Type

Single-period

## Description

This formulation focuses on creating a schedule for a single operational period, typically one day. While simpler to solve, it may be less effective at managing constraints and objectives like continuity of care that span a longer timeframe.

## Planning Horizon

Single-period


# Continuity Of Care Definition

Continuity of Care (CoC) in the context of home health care scheduling and operations research is the principle of maintaining consistency in the assignment of caregivers to patients over a planning horizon. The operational goal is to have the same caregiver, or a small, consistent group of caregivers, serve a specific client over time, thereby limiting the number of switches and unique caregivers involved in their care. This concept is a critical differentiator that elevates the Home Health Care Routing and Scheduling Problem (HHCRSP) beyond a standard logistics or vehicle routing problem (VRP). It introduces a human-centered, quality-of-service dimension that must be balanced with operational efficiency. Retaining consistency in caregiver assignments is desired to improve patient outcomes, increase patient satisfaction, and build trust between the patient and the provider.

# Continuity Of Care Metrics

## Metric Name

Count of Unique Nurses Per Client

## Description

This is a straightforward and commonly used metric in operations research literature that measures continuity of care by simply counting the total number of different caregivers who visit a single client over a specific planning horizon. A lower count implies higher continuity.

## Limitations

The primary limitation of this metric is that it does not scale with the frequency of visits and can be ambiguous. For example, a patient receiving 20 visits from 3 different nurses has the same score as a patient receiving 3 visits from 3 different nurses, even though the level of continuity is experientially very different. The measure is described as 'scale-sensitive and potentially ambiguous as visit volumes change'.

## Metric Name

Continuity of Care Index (CCI)

## Description

The Continuity of Care Index (CCI) is a more sophisticated, proportion-of-visits measure designed to provide a more nuanced assessment of care continuity. It is calculated in a way that incorporates not only the number of caregivers but also the frequency of visits and the distribution of those visits among the different caregivers. It mitigates the scaling issues of the simple count, providing a better-scaled and less ambiguous value. Recent studies show its suitability for multi-visit home care contexts.

## Limitations

The provided text presents the CCI as a superior alternative designed to mitigate the issues found in the simpler 'unique nurse count' metric. No specific drawbacks for the CCI itself are mentioned; it is positioned as a more robust and less ambiguous measure for quantifying continuity of care.


# Modeling Approaches For Continuity Of Care

## Approach

Soft Constraint / Objective Function Penalty

## Implementation Detail

This approach incorporates continuity of care into the model by adding penalty terms to the objective function. Instead of strictly forbidding caregiver changes, it assigns a cost to them. This can be formulated in several ways, such as: 1) Adding a penalty for each caregiver switch for a patient from one day to the next, for example, by penalizing a term like `(y_{i,n,d} - y_{i,n,d-1})+` where `y_{i,n,d}` is an assignment variable. 2) Introducing a cost for deviating from historical or previously established patient-caregiver assignments. 3) Including a term in the objective function that is directly based on a continuity metric, such as minimizing the deviation from a target CCI score. This method is often used in rolling horizon approaches to maintain consistency from one planning period to the next.

## Effect On Solution

Treating continuity as a soft constraint allows the model to make trade-offs between service consistency and other operational objectives, such as minimizing travel costs. The model can choose to 'pay' the penalty for a caregiver switch if doing so results in a greater overall cost saving or a more efficient schedule. This provides more flexibility than a hard constraint (which would forbid exceeding a certain number of nurses) and allows the optimization algorithm to find a balanced solution that weighs the importance of continuity against efficiency.


# Stakeholder Objectives

## Stakeholder

Organization

## Objective

Minimize operational costs and travel

## Metric

Total travel time/distance, total wage-based shift costs, and total idle time.

## Stakeholder

Organization

## Objective

Minimize resource usage and overtime

## Metric

Number of vehicles/caregivers used and total overtime hours.

## Stakeholder

Organization

## Objective

Improve sustainability

## Metric

Total CO2 emissions or energy consumption, particularly in variants with Electric Vehicles (EVs).

## Stakeholder

Caregiver

## Objective

Balance workload

## Metric

Standard deviation or range of shift lengths and number of patients served among caregivers to ensure fairness.

## Stakeholder

Caregiver

## Objective

Respect preferences and improve job satisfaction

## Metric

Adherence to caregiver availability, preferred working hours, and patient-caregiver compatibility requests.

## Stakeholder

Patient

## Objective

Maximize continuity of care

## Metric

Continuity of Care Index (CCI), count of unique nurses per patient, minimizing caregiver switches, or maximizing the proportion of visits by a primary caregiver.

## Stakeholder

Patient

## Objective

Maximize satisfaction and service quality

## Metric

Minimizing waiting time (arrival before time window start), adherence to preferred visit times, and maximizing proportion of visits served by a preferred nurse.


# Trade Off Analysis

A central challenge in home care scheduling is managing the inherent trade-off between operational efficiency and the quality of service, particularly continuity of care. On one hand, efficiency-focused objectives aim to minimize operational costs by reducing total travel distance and time, minimizing caregiver overtime, reducing idle time, and optimizing the number of shifts. On the other hand, patient-centered objectives aim to maximize service quality by improving continuity of care (e.g., maximizing the CCI or minimizing caregiver switches), balancing workload among staff, and respecting patient-caregiver preferences. These two sets of objectives are often in conflict; the most cost-effective schedule from a pure logistics standpoint may involve frequent caregiver changes that degrade continuity. To manage this, multi-objective optimization techniques are widely used, including weighted-sum models, the epsilon-constraint method, and Pareto-based algorithms like NSGA-II and SPEA2. These methods allow planners to explore the Pareto frontier of solutions and find a desirable balance. Importantly, empirical studies demonstrate that this trade-off is not always severe; carefully designed and integrated routing and rostering approaches can achieve significant improvements in continuity of care with only a small impact on overall schedule costs.

# Key Operational Constraints

## Constraint Name

Skill Matching

## Description

Ensures that a caregiver is assigned to a patient only if they possess the necessary qualifications or skills required for the specific tasks or care needed by that patient.

## Category

Assignment

## Constraint Name

Time Windows

## Description

Requires that a caregiver's visit to a patient must begin within a predefined time interval specified by the patient or the care plan.

## Category

Temporal

## Constraint Name

Synchronized Visits

## Description

A constraint for patients who require care from two or more caregivers at the same time. It ensures that the assigned caregivers arrive simultaneously for the visit.

## Category

Temporal

## Constraint Name

Working Hour Regulations

## Description

Enforces legal and contractual rules regarding the maximum duration of a caregiver's shift, minimum rest periods between shifts, and limits on overtime.

## Category

Regulatory

## Constraint Name

Caregiver Breaks

## Description

Mandates that one or more breaks, such as a lunch break, must be scheduled within a caregiver's shift, respecting rules about their timing and duration.

## Category

Temporal

## Constraint Name

Continuity of Care

## Description

Aims to maintain consistency in patient care by limiting the number of different caregivers who visit a single patient over a planning horizon. This can be a hard constraint (a strict limit) or a soft constraint (a penalty for switching caregivers).

## Category

Assignment

## Constraint Name

Patient-Nurse Compatibility

## Description

Accounts for preferences or incompatibilities between patients and caregivers. This can involve honoring a patient's request for a specific caregiver or avoiding assignments between a patient and a caregiver who have a known negative history.

## Category

Assignment

## Constraint Name

Staff Availability

## Description

Restricts caregiver assignments to their declared available days and times within the planning horizon.

## Category

Assignment

## Constraint Name

Geographic and Travel Constraints

## Description

Defines the operational area, including caregiver start/end locations (depot or home), and uses realistic travel times between patient locations. In green variants, this includes EV range and charging constraints.

## Category

Geographic


# Solution Methodologies

## Category

Exact Method

## Algorithm Name

Mixed-Integer Linear Programming (MILP)

## Description

MILP is used to create mathematical formulations of the HHCRSP, often based on set partitioning or flow-based models. While powerful for finding optimal solutions, it is typically suitable for smaller or less complex problem instances. In practice, it is frequently combined with other methods in hybrid approaches to solve larger, more realistic scenarios.

## Category

Exact Method

## Algorithm Name

Branch-and-Price/Column Generation

## Description

This is an advanced exact method used for large-scale optimization problems. It is particularly effective for routing problems with many constraints, such as HHCRSP with time windows and continuity of care requirements. It works by decomposing the problem into a master problem and a subproblem (pricing problem) that generates new routes or schedules (columns) to improve the solution iteratively.

## Category

Metaheuristic

## Algorithm Name

Local Search-Based Algorithms (VNS, ILS, Tabu Search)

## Description

These algorithms, including Variable Neighborhood Search (VNS), Iterated Local Search (ILS), and Tabu Search (TS), are noted as being dominant in solving deterministic HHCRSP. They work by iteratively exploring the solution space, starting from an initial solution and making local changes to find better ones, effectively balancing solution quality and computation time for complex problems.

## Category

Metaheuristic

## Algorithm Name

Adaptive Large Neighborhood Search (ALNS)

## Description

ALNS is a popular and powerful metaheuristic that explores a large neighborhood of the current solution by using 'destroy' and 'repair' operators to modify significant parts of the solution in each iteration. It is highly effective for HHCRSP due to its flexibility in handling diverse and complex constraints.

## Category

Metaheuristic

## Algorithm Name

Multi-Objective Evolutionary Algorithms (NSGA-II, SPEA2)

## Description

Algorithms like NSGA-II and SPEA2 are used to handle the inherent trade-offs in HHCRSP, such as minimizing costs while maximizing continuity of care and balancing workload. They work by evolving a population of solutions to find a set of Pareto-optimal solutions that represent the best possible compromises between conflicting objectives.

## Category

Hybrid/Matheuristic

## Algorithm Name

Hybrid Metaheuristics with MILP

## Description

This approach, also known as a matheuristic, combines the strengths of metaheuristics (like ALNS, GA, TS) with exact methods (MILP). For example, a metaheuristic can be used to explore the overall solution structure, while an MILP solver is used to solve smaller, well-defined subproblems to optimality. This is particularly useful for ensuring continuity of care and handling complex practical constraints in large-scale problems.


# Advanced Solution Concepts

## Concept Name

Blueprint Routes

## Description

This is a concept where an algorithm is developed to create 'blueprint routes' that serve as a master plan. Daily schedules are then aligned with these blueprints. This method helps in coordinating schedules across a planning horizon (e.g., a week) to achieve desired long-term objectives.

## Purpose

The primary purpose is to link daily scheduling decisions with the longer-term goal of ensuring continuity of care. By aligning daily routes to a master blueprint, the framework facilitates consistent caregiver-patient assignments over multiple periods.


# Practical Impact Of Optimization

## Impact Area

Achieving High Continuity of Care Cost-Effectively

## Description

Optimization models allow healthcare providers to move beyond simple cost minimization and explicitly incorporate patient-centric objectives like continuity of care. By using multi-objective frameworks and integrated multi-period models, providers can analyze the trade-offs between operational efficiency and service quality. This enables them to find scheduling solutions that significantly improve continuity of care (e.g., by using metrics like the Continuity of Care Index) while only incurring small, manageable increases in operational costs.

## Example

Numerical experiments mentioned in the literature demonstrate that through carefully designed algorithms (such as those using 'blueprint routes'), high levels of continuity of care can be achieved without significantly compromising the costs of the home care schedule. This shows that the goals of efficiency and quality are not mutually exclusive and can be balanced effectively.


# Technological Integration And Ai

## Technology

Artificial Intelligence / Machine Learning (AI/ML)

## Application

AI and ML are being integrated to support predictive analytics and real-time adaptation in HHCRSP. This includes predicting uncertain variables like travel and service times, forecasting patient demand volatility, and enabling real-time dispatching and re-planning in response to dynamic events like new visit requests or cancellations.

## Benefit

The integration of AI/ML leads to more robust, adaptive, and scalable solution methods. This allows scheduling systems to better handle the uncertainty inherent in real-world operations and make intelligent, dynamic adjustments while still preserving key objectives like continuity of care and operational efficiency.


# Benchmark Datasets And Key Literature

## Resource Type

Benchmark Dataset

## Name

Synthesized Benchmark Instances from Review Articles

## Relevance

The literature does not point to a single universal benchmark set, but rather indicates that review articles provide structured syntheses of benchmark instances for both single- and multi-period HHCRSP. These collections are crucial for researchers to compare the performance of new algorithms against existing ones under standardized conditions.

## Resource Type

Key Review Article

## Name

Engineering Journal (HHCRSP review)

## Relevance

A recent review article published in this journal covers the literature from 2006 to mid-2024, offering a structured synthesis of HHCRSP research concerning problem types, objectives, constraints, and solution methods. Such reviews are essential starting points for new research in the field.

## Resource Type

Key Review Article

## Name

Surveys on HHCRSP and Workforce Scheduling and Routing Problems (WSRP)

## Relevance

The provided text mentions the existence of classic and recent surveys that cover the broader field of WSRP, of which HHCRSP is a key application. These surveys provide a high-level understanding of the problem class and its evolution.

## Resource Type

Academic Journal

## Name

Computers & Operations Research

## Relevance

A primary venue for publishing research on HHCRSP, particularly studies involving mathematical modeling (like MILP) and the development of metaheuristic and hybrid solution methods like ALNS.

## Resource Type

Academic Journal

## Name

European Journal of Operational Research (EJOR)

## Relevance

A leading journal in operations research that frequently publishes high-impact papers on vehicle routing and scheduling, including applications in home health care.

## Resource Type

Academic Journal

## Name

Health Care Management Science

## Relevance

A specialized journal focusing on the application of operations research and management science principles to healthcare problems, making it a key outlet for HHCRSP research with a practical or managerial focus, such as studies on continuity of care.

## Resource Type

Academic Journal

## Name

OR Spectrum

## Relevance

Another significant journal in the field of operations research that publishes methodological and applied work relevant to HHCRSP.

## Resource Type

Academic Journal

## Name

Networks

## Relevance

A journal focused on network optimization problems, relevant for the routing and graph-based aspects of HHCRSP.


# Open Challenges And Future Research Directions

## Research Area

Stochastic and Dynamic Multi-Period Problems

## Description

A significant open challenge is the development of robust and dynamic multi-period models that can operate at a realistic scale. These models need to simultaneously manage multiple complex constraints, including synchronized visits (where multiple caregivers must visit a patient together) and continuity of care, under conditions of uncertainty. This uncertainty pertains to both service times and travel times, as well as demand volatility (e.g., new patient requests or cancellations). The goal is to create planning and scheduling systems that are not only efficient but also resilient to the unpredictable nature of daily operations over an extended planning horizon like a week or a month.

## Potential Focus

Future research should focus on the joint optimization of synchronization and continuity of care across multiple periods, as these are often handled separately. This requires the development of robust, adaptive, and highly scalable solution methods. Methodological directions include creating advanced matheuristics, decomposition schemes, or scalable exact methods that can effectively handle the stochastic and dynamic elements of the problem while producing high-quality solutions in a reasonable amount of time.

