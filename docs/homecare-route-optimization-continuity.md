# Executive Summary

Home care routing and scheduling is a complex, integrated problem that combines vehicle routing (VRP), staff routing, and personnel rostering. It is characterized by a multitude of operational constraints, including specific time windows for visits, matching caregiver skills and qualifications to patient needs, handling synchronized or 'double-staff' visits for specific tasks, and adhering to complex labor rules regarding breaks, shifts, and work hours. Key objectives are often in conflict, requiring a multi-objective optimization approach to balance economic efficiency (minimizing travel time, overtime, and lateness) with quality of care. This includes maximizing continuity of care (ensuring patients are seen by a consistent team of caregivers), satisfying patient preferences, and ensuring fair workload distribution among staff. The problem is typically modeled as a variant of the Vehicle Routing Problem with Time Windows (VRPTW) combined with assignment and rostering elements, often spanning multiple days and shifts. State-of-the-art solution methods include Mixed-Integer Linear Programming (MILP), Constraint Programming (CP), decomposition techniques like column generation (branch-and-price) and Logic-Based Benders Decomposition (LBBD), and various metaheuristics and matheuristics such as Adaptive Large Neighborhood Search (ALNS). Evidence from real-world applications, such as the LAPS CARE system in Sweden and a collaboration with AlayaCare, demonstrates the significant impact of advanced optimization, with case studies showing travel time reductions of 10% to 37% alongside measurable improvements in service levels and continuity of care.

# Problem Formulation

The Home Health Care Routing and Scheduling Problem (HHCRSP), also referred to as HHCSP, is academically defined as an integrated assignment, routing, and scheduling problem for a group of caregivers providing services to patients at their homes over a given planning horizon, which can be daily or weekly. It is a complex extension of the Vehicle Routing Problem (VRP) and its variants, particularly the Vehicle Routing Problem with Time Windows (VRPTW). The core structure involves assigning a set of caregivers, who start and end their shifts at a depot, to a series of patient visits. Each visit has a specific service duration and must be performed within a designated time window. The problem is complicated by a rich set of real-world constraints, including: 
- **Time Windows and Service Durations**: Each patient visit must start within a pre-defined time interval and takes a certain amount of time to complete.
- **Skills and Qualifications**: Caregivers must possess the necessary skills required for each visit, creating a skill-matching constraint.
- **Synchronized Visits**: Certain tasks, such as lifting a patient, require two caregivers to be present simultaneously, introducing temporal synchronization constraints.
- **Precedence and Dependencies**: Some tasks for a patient must be performed in a specific order.
- **Labor Regulations**: Schedules must adhere to rules regarding maximum shift lengths, minimum rest times, and mandatory lunch breaks.
- **Continuity of Care (CoC)**: A critical 'soft' constraint aiming to assign the same caregiver(s) to a patient over time to improve care quality.
- **Fairness and Workload Balance**: The total working time, travel time, and number of visits should be distributed equitably among caregivers.
- **Multi-Period and Multi-Shift Operations**: The problem often spans multiple days and shifts, requiring integrated rostering and routing.

# Optimization Objectives

Home care route optimization is fundamentally a multi-objective problem, where decision-makers must balance competing goals related to operational efficiency, service quality, and staff satisfaction. These objectives are typically combined into a weighted sum in the objective function of a mathematical model or optimized hierarchically. The most common optimization objectives include:

1.  **Minimizing Economic Costs**: This is a primary objective focused on operational efficiency. It includes:
    *   Minimizing total travel time or distance for all caregivers.
    *   Minimizing staff costs, particularly by reducing overtime pay.
    *   Minimizing penalties for lateness or missed time windows.

2.  **Maximizing Continuity of Care (CoC)**: A crucial objective for patient well-being and service quality. This is modeled in several ways:
    *   Maximizing a formal metric like the Continuity of Care Index (CCI), which measures the consistency of assignments.
    *   Minimizing the number of unique caregivers assigned to a single patient over the planning horizon.
    *   Penalizing reassignments from a previous period's schedule in a rolling horizon setting.

3.  **Ensuring Fair Workload Distribution**: To maintain staff morale and prevent burnout, models often include fairness objectives:
    *   Balancing the total working time or number of visits among caregivers.
    *   Minimizing the difference between the maximum and minimum workload (min-max objective).
    *   Maximizing the minimum utilization (max-min objective).
    *   Minimizing the variance in workload across the team.
    *   Penalizing both overtime and excessive idle time.

4.  **Maximizing Patient and Caregiver Preferences**: Soft constraints are often used to improve satisfaction for both parties. This involves minimizing penalties for not accommodating preferred caregiver-patient pairings.

# Key Operational Constraints

## Constraint Name

Time Windows and Service Durations

## Description

This is a core constraint in home care routing and scheduling, defining the specific time intervals within which caregivers must arrive at a patient's home and the required duration of the service. It is a fundamental component of the Vehicle Routing Problem with Time Windows (VRPTW) variants used to model this problem. The models must ensure that each visit starts within its designated time window and lasts for the prescribed service duration. The provided research also highlights the importance of extending these models to handle real-world variability, mentioning 'rolling-horizon and stochastic/robust extensions for travel/service-time uncertainty' to create more resilient schedules.

## Type

Temporal


# Continuity Of Care Models

Continuity of Care (CoC) is a critical objective in home care scheduling, aimed at ensuring a patient is consistently visited by the same caregiver(s) to improve care quality and patient satisfaction. Optimization models address this through several techniques. 

**Metrics for CoC:**
Two primary measures are used: the simple 'number of unique caregivers' assigned to a client over a planning horizon, and the more sophisticated 'Continuity of Care Index (CCI)'. The CCI is noted as a preferable metric as it is 'designed to mitigate potential issues associated with other measurement methods' and scales better with visit frequency.

**Modeling Techniques:**
1.  **Objective Function Penalties:** A common approach is to penalize inconsistency. In rolling horizon models, 'inconsistency variables' are used to track when a caregiver assigned in a prior period is not reassigned to the same patient in the current period, adding a penalty to the objective function for each such instance. Set-partitioning models incorporate continuity terms directly into the objective function weights.
2.  **Hard Constraints:** Models can include constraints that explicitly 'limit the number of unique caregivers per client' over the planning horizon.
3.  **Blueprint Routes:** A novel method involves creating 'blueprint routes' which are 'sets of (partial) efficient routes via jobs with frequent occurrences'. These pre-structured patterns for recurring visits are used to 'guide the scheduling decisions' to promote high CoC while maintaining low costs.
4.  **Integrated Models:** CoC is typically one of several competing objectives in multi-objective optimization models, balanced against travel costs, overtime, and workload fairness. Solution methods like branch-and-price and set partitioning (SPP) are adapted to include CoC considerations in their objective functions. A collaboration with AlayaCare using an SPP+LNS approach demonstrated a 16% improvement in CoC alongside a 37% travel time reduction.

# Synchronized And Paired Visits

Synchronized or paired visits, also known as double-staff visits, are a key requirement in home care for tasks that necessitate the simultaneous presence of two or more caregivers. Examples include performing lifts or bathing for patients who are 'overweight or physically disabled'. This requirement introduces significant complexity into the scheduling and routing problem.

**Modeling Approaches:**
These dependencies are modeled mathematically in several ways:
1.  **Pairing and Simultaneity Constraints:** The model can enforce that if a specific task is assigned, two distinct caregivers must be assigned to it, and their arrival and departure times at the patient's location must be synchronized.
2.  **Temporal Precedence Constraints:** A more general approach uses 'pairwise temporal precedence constraints and pairwise synchronization constraints'. This can enforce that two visits must start at the same time (a lag of zero) or within a very small time window of each other.

**Solution Methodologies:**
Solving problems with these constraints requires specialized algorithms. In exact methods like branch-and-price or column generation, synchronization is handled by adding 'additional synchronization resources' to the subproblem (the resource-constrained shortest path problem). This ensures that the routes (columns) generated are valid with respect to the pairing requirements. For larger or more complex instances, metaheuristics such as 'adaptive VNS/ALNS and hybrid metaheuristics' have been shown to be effective at finding high-quality solutions. These constraints are often integrated into comprehensive MILP or set-partitioning formulations that also consider other factors like time windows, skills, and continuity of care.

# Workload Balancing Techniques

Workload balancing is a crucial objective in home care scheduling to ensure a fair and equitable distribution of work among caregivers, which can improve staff satisfaction and retention. This is typically handled as an objective within the larger optimization model, often in competition with minimizing travel costs and maximizing continuity of care.

**Mathematical Formulations and Strategies:**
Several techniques are used to model and achieve workload balance:
1.  **Min-Max or Max-Min Objectives:** A common approach is to formulate the objective function to either 'minimize the maximum workload' (min-max) among all caregivers or 'maximize the minimum utilization' (max-min). This directly tackles the issue of some caregivers being overworked while others are underutilized. Cappanera and Scutellà (2015) are cited for using this pattern-based approach.
2.  **Variance-Based Objectives:** An alternative is to minimize the variance of the workload (e.g., working hours, travel time, or number of visits) across the team of caregivers. This promotes a more even distribution of work.
3.  **Penalties for Imbalance:** The objective function can include penalty terms for undesirable outcomes. This includes penalties for 'overtime' (exceeding contracted hours) and excessive 'idle time', both of which contribute to workload imbalance.

These fairness objectives are integrated into comprehensive models, such as pattern-based MILP formulations (e.g., PHCP) and other integrated scheduling models that simultaneously consider skills, continuity of care, and routing efficiency. The final schedule represents a trade-off between these competing goals, calibrated based on the priorities of the home care provider.

# Mathematical Programming Models

## Model Name

Mixed-Integer Linear Programming (MILP)

## Description

Formulates the integrated staffing, assignment, routing, and scheduling problem using a combination of integer and continuous variables with linear constraints and objectives. This approach can directly model a wide array of problem features, including caregiver-patient skill matching, visit time windows, synchronized visits, labor regulations, and continuity of care. Valid inequalities are often added to strengthen the formulation and improve solver performance.

## Typical Application

Used for solving integrated multi-day and multi-shift problems, often with hierarchical objectives. It is also applied in pattern-based approaches to ensure fair workload balancing (e.g., using max-min objectives). While powerful, MILP models are often used for smaller instances or as a component within more advanced decomposition algorithms due to computational complexity.

## Model Name

Set Partitioning (SPP) / Route-based Models

## Description

This approach formulates the HHCRSP by defining a master problem that selects an optimal set of feasible single-caregiver routes (represented as columns) to ensure each patient visit is covered exactly once. The objective function minimizes a weighted sum of costs, which can include travel time, overtime, idle time, and penalties for violating soft constraints like patient preferences or lack of care continuity. The routes themselves must satisfy all hard constraints like time windows and skills.

## Typical Application

A very common and effective formulation for HHCRSP, frequently serving as the master problem within column generation and branch-and-price frameworks. It is particularly well-suited for complex, multi-objective problems, as demonstrated in a collaboration with Alayacare where it led to significant improvements in both travel time and continuity of care.

## Model Name

Stochastic and Robust Programming

## Description

These are advanced modeling techniques that extend deterministic models like MILP to explicitly account for uncertainty in problem parameters, primarily travel and service times. Stochastic programming uses probability distributions to optimize expected performance, while robust optimization aims to find solutions that remain feasible and perform well under any realization of uncertainty within a defined set. Methods include stochastic programming with recourse, sample average approximation, and distributionally robust models.

## Typical Application

Applied to HHCRSP to create more reliable and resilient schedules that are less susceptible to real-world disruptions like traffic delays or longer-than-expected care visits. For example, robust versions have been developed for integrated staffing and routing problems, and stochastic models have been solved using specialized branch-and-price algorithms.


# Exact Algorithms

## Algorithm Name

Column Generation (CG)

## Description

An iterative algorithm designed to solve large-scale linear programs that have an enormous number of variables (columns), such as set partitioning models. Instead of enumerating all possible columns (routes), it starts with a restricted subset and iteratively generates new columns that have the potential to improve the objective function. These new columns are found by solving a 'pricing subproblem'.

## Role In Hhcrsp

In the context of HHCRSP, column generation is used to solve the linear programming relaxation of the set partitioning master problem. The pricing subproblem's role is to generate new, cost-effective caregiver routes. This subproblem is typically modeled as a Resource-Constrained Shortest Path Problem (RCSPP), which must find the best route while respecting constraints like time windows, caregiver skills, and synchronization requirements.

## Algorithm Name

Branch-and-Price (B&P)

## Description

An exact algorithm for large-scale integer programming that combines the branch-and-bound search framework with column generation. At each node of the branch-and-bound tree, column generation is used to solve the linear relaxation of the problem. Branching occurs on the original problem variables to enforce integrality.

## Role In Hhcrsp

This is a standard and powerful exact method for solving the HHCRSP to optimality, especially when formulated as a set partitioning problem. It can effectively handle a wide range of complex constraints (e.g., temporal dependencies, skills) by incorporating them into the pricing subproblem. The literature also describes extensions like branch-and-price-and-cut and stochastic branch-and-price to handle uncertain travel/service times.

## Algorithm Name

Logic-Based Benders Decomposition (LBBD)

## Description

A decomposition technique that partitions a problem into a master problem and one or more subproblems, which are solved iteratively. The master problem typically handles a subset of decisions (e.g., assignments), and its solution is passed to the subproblems, which check for feasibility and generate 'Benders cuts' (logical constraints) to add back to the master problem, thereby eliminating infeasible or suboptimal solutions.

## Role In Hhcrsp

LBBD is used to provide exact solutions for integrated HHCRSP models by separating the higher-level assignment and rostering decisions (master problem) from the detailed routing and scheduling of individual caregivers (subproblems). This decomposition makes the problem more tractable and has been successfully applied to solve integrated, multi-period HHC problems that include uncertainty and overtime controls. Nested LBBD has also been reported for complex multi-shift problems.


# Heuristic And Metaheuristic Algorithms

## Algorithm Name

Adaptive Large Neighborhood Search (ALNS) / Large Neighborhood Search (LNS)

## Description

A metaheuristic approach widely used for large-scale home care scheduling instances. It functions as an improvement method, often in a hybrid or two-phase model. A common application involves using a constructive heuristic or Constraint Programming (CP) to generate an initial feasible solution, which is then iteratively improved by the ALNS algorithm. The method works by repeatedly 'destroying' a portion of the current solution and 'repairing' it in an attempt to find a better overall schedule. It is noted for its effectiveness in solving real-world instances, such as those in a collaboration with AlayaCare where an LNS algorithm outperformed the incumbent solution.

## Approach Type

Local Search / Hybrid (Matheuristic)

## Algorithm Name

Column Generation (CG) and Branch-and-Price (B&P)

## Description

An exact decomposition method used to solve large-scale vehicle routing and scheduling problems. The problem is decomposed into a master problem and one or more subproblems. The master problem is typically a set partitioning problem that selects an optimal combination of caregiver-day routes from a large set. The subproblem, known as the pricing problem, generates new, valid routes (columns) that have the potential to improve the overall solution. This approach is effective for handling complex constraints like time windows, skills, and synchronization by incorporating them into the resource-constrained shortest path problem solved in the subproblem. It is also adapted for stochastic variants.

## Approach Type

Decomposition / Exact Method

## Algorithm Name

Logic-Based Benders Decomposition (LBBD)

## Description

An exact decomposition technique that separates a problem into a master problem and subproblems. In the context of home health care, it is used to separate the assignment/rostering decisions (master problem) from the routing/scheduling decisions (subproblems). This separation allows for the solution of integrated multi-period problems with complex features like uncertainty and overtime control. The context mentions its application for integrated staffing, assignment, routing, and scheduling, including a robust version to handle uncertainty in travel and service times.

## Approach Type

Decomposition / Exact Method

## Algorithm Name

Constraint Programming (CP) and Hybrid Methods

## Description

Constraint Programming is used to handle complex feasibility and sequencing problems involving constraints like time windows, skills, and breaks. It is often used as part of a hybrid 'matheuristic'. A prominent example is a two-stage approach where a CP heuristic first generates a feasible solution, which is then passed to an Adaptive Large Neighborhood Search (ALNS) algorithm for improvement. This hybrid approach leverages CP's strength in constraint satisfaction and ALNS's power in optimization.

## Approach Type

Hybrid (Matheuristic)

## Algorithm Name

Other Metaheuristics (VNS, Tabu Search, Genetic Algorithms)

## Description

The context groups several other metaheuristics as being widely used for large instances and dynamic settings. These include Variable Neighborhood Search (VNS), Tabu Search, Genetic Algorithms (GA/NSGA-II), GRASP, and memetic algorithms. VNS and Tabu Search are advanced local search methods, while Genetic Algorithms are population-based methods inspired by natural selection. They are often used in two-phase or three-phase decompositions (e.g., schedule-first, route-second).

## Approach Type

Local Search / Population-based


# Constraint Programming Approaches

Constraint Programming (CP) is a powerful declarative programming paradigm used to solve complex combinatorial problems like the HHCRSP. Its primary strength lies in its ability to handle a wide variety of heterogeneous and complex constraints, making it highly suitable for the assignment and sequencing aspects of home care scheduling. CP models excel at managing intricate requirements such as strict visit time windows, caregiver skill qualifications, mandatory breaks, and temporal dependencies between tasks, including pairwise synchronization for double-staff visits and precedence constraints. In practice, CP is often employed in hybrid or multi-stage solution methods. A common and effective strategy is a two-stage approach where a CP heuristic is first used to quickly generate an initial feasible schedule that satisfies all hard constraints. This feasible solution is then passed to a metaheuristic algorithm, such as Adaptive Large Neighborhood Search (ALNS), for subsequent improvement and optimization. This hybrid approach leverages CP's strength in finding feasible solutions in a complex search space and the metaheuristic's power in optimizing objectives like cost and quality. The provided research indicates that solvers like Google OR-Tools' CP-SAT and OptaPlanner are used in both research and practical applications to tackle these challenging scheduling problems.

# Stochastic And Dynamic Optimization

Advanced optimization models in home health care address real-world uncertainty through stochastic, robust, and dynamic approaches. These models go beyond deterministic assumptions to create more resilient and adaptable schedules.

**Stochastic and Robust Optimization for Time Uncertainty:**
To account for variability in travel and service times, several advanced methods are employed. These include stochastic programming with recourse, sample average approximation, robust optimization, and distributionally robust models. These techniques aim to find solutions that are effective over a range of possible scenarios rather than a single deterministic forecast. For example, research by Liu et al. (2019) introduced a route-based model that explicitly accounted for stochastic service and travel times, which was solved using a branch-and-price algorithm combined with a discrete approximation method. Similarly, Naderi et al. (2023) developed a robust version of their logic-based Benders decomposition (LBBD) algorithm to manage uncertainty in travel and service times, creating schedules that are less susceptible to disruptions from delays. Stochastic branch-and-price with discrete approximations is another key technique mentioned for handling uncertain times.

**Dynamic and Online Optimization for Real-Time Events:**
To handle dynamic events such as new patient visit requests, caregiver absences, or cancellations, models use online and real-time rescheduling techniques. The most common approach is the 'rolling horizon' methodology. In this framework, schedules are re-optimized periodically (e.g., daily or several times a day) to incorporate the latest information. This allows the system to react to unforeseen events while attempting to preserve key objectives like continuity of care by penalizing reassignments from the previous period's schedule. Other strategies include decomposing the problem into assignment versus routing subproblems and applying online improvement heuristics to quickly adjust schedules in response to new information. Research has also focused on developing specific mixed-integer programming models for scenarios involving dynamic patient arrivals.

# Industry Case Studies And Best Practices

## Case Study Name

LAPS CARE

## Organization

City of Stockholm, Sweden

## Methods Used

The system utilizes operations research modeling to automate and optimize the manual planning of home care unit assignments. While the specific algorithm isn't detailed in the case study summary, the broader context suggests methods like MILP, decomposition, and metaheuristics are standard for such problems.

## Reported Outcomes

The implementation resulted in a 10-15% increase in operational efficiency across more than 200 units. This translated to annual savings of 20-30 million euros. The system was later scaled to include 800 units and 15,000 home care workers, with projected savings remaining in the 20-30 million euro range.

## Case Study Name

AlayaCare Collaboration (Grenouilleau et al. 2019)

## Organization

AlayaCare

## Methods Used

The problem was formulated as a Set Partitioning Problem (SPP) with objectives for continuity of care. The solution approach was a hybrid matheuristic combining SPP with a Large Neighborhood Search (LNS) algorithm to find high-quality solutions for real-world instances.

## Reported Outcomes

In a direct comparison on real instances, this hybrid method outperformed AlayaCare's incumbent solution significantly, achieving a 37% reduction in total travel time and a 16% improvement in continuity of care.

## Case Study Name

Industry Best Practice: Tactical and Operational Decomposition

## Organization

General Practice

## Methods Used

This practice involves a two-level planning process. Tactically, weekly patterns or 'blueprint routes' are designed for recurring care tasks to establish a baseline that supports high continuity of care (CoC). Operationally, daily routing problems are solved to handle specific daily appointments, time windows, and shift costs, followed by assigning nurses to these optimized shifts while tracking CoC metrics.

## Reported Outcomes

This approach helps balance the competing goals of efficiency and continuity of care. By pre-structuring recurring jobs with blueprint routes, it maintains high CoC while allowing daily optimization to handle variability and reduce costs.

## Case Study Name

Industry Best Practice: Hybrid Solution Methods

## Organization

General Practice

## Methods Used

A common and effective approach is to hybridize different optimization techniques. For example, using Constraint Programming (CP) or constructive heuristics to quickly find an initial feasible solution that respects complex constraints (like synchronization and skills), and then using a metaheuristic like Adaptive Large Neighborhood Search (ALNS) or Large Neighborhood Search (LNS) to iteratively improve the solution's quality (e.g., reduce travel time, improve workload balance). For problems requiring guarantees on key performance indicators like overtime, exact methods like Logic-Based Benders Decomposition (LBBD) or Branch-and-Price are applied, often on a reduced version of the problem.

## Reported Outcomes

This hybridization leverages the strengths of different methods: the feasibility-finding power of CP, the large-scale improvement capability of LNS/ALNS, and the optimality guarantees of exact methods. This leads to robust and high-quality solutions for complex, large-scale HHCRSP instances.

## Case Study Name

Industry Best Practice: Rolling Horizon Planning

## Organization

General Practice

## Methods Used

Instead of creating a static schedule for a long period, a rolling horizon methodology is used. The schedule is optimized for the immediate future (e.g., the next day), and this process is repeated periodically (e.g., daily) as new information (like patient demand or caregiver availability) becomes available. To maintain continuity, penalties are introduced for reassigning a caregiver from a patient they were assigned to in the previous period.

## Reported Outcomes

This approach allows the system to be dynamic and responsive to real-world changes without completely disrupting the schedule and eroding continuity of care. It provides a stable yet flexible planning framework.


# Optimization Software And Solvers

## Tool Name

OptaPlanner

## Developer

Red Hat / Open Source Community

## Type

Open-source constraint solver library

## Relevance To Hhcrsp

Used in both research and practice for solving HHCRSP. It is effective for finding feasible solutions under complex constraints like time windows, skills, and breaks. The context mentions it is often used as part of a hybrid approach, such as a CP-heuristic, and is demonstrated to be effective for medium-sized instances.

## Tool Name

Constraint Programming (CP) Solvers (e.g., IBM CP Optimizer, Google OR-Tools CP-SAT)

## Developer

Various (e.g., IBM, Google)

## Type

CP Solver / Commercial or Open-source software

## Relevance To Hhcrsp

CP is explicitly cited as a key technique for handling the feasibility, assignment, and sequencing aspects of HHCRSP. Solvers like CP Optimizer and CP-SAT are used to enforce complex rules regarding time windows, skills, and breaks. They are often used in a two-stage approach, where CP finds an initial feasible schedule which is then improved by another algorithm like ALNS.

## Tool Name

Branch & Price (B&P) / Column Generation (CG)

## Developer

Academic/Research Community

## Type

Decomposition Algorithm / Exact Method

## Relevance To Hhcrsp

This is a powerful exact method for solving large-scale vehicle routing problems. In HHCRSP, it decomposes the problem where 'columns' represent valid single-caregiver routes for a day or shift. The master problem then selects the best combination of routes to cover all visits. It is highly effective for incorporating complex constraints like time windows, skills, and synchronization into the column-generating 'pricing' subproblem. Stochastic versions can also handle uncertain travel/service times.

## Tool Name

Logic-Based Benders Decomposition (LBBD)

## Developer

Academic/Research Community

## Type

Decomposition Algorithm / Exact Method

## Relevance To Hhcrsp

LBBD is an exact technique that effectively decomposes integrated problems. For HHCRSP, it separates the higher-level assignment/rostering decisions from the lower-level routing/scheduling subproblems. This makes it particularly suitable for complex, multi-period models that integrate staffing and routing. It has been successfully applied to robust versions of the problem to account for uncertainty in travel and service times and to control for overtime.

## Tool Name

Adaptive Large Neighborhood Search (ALNS) / Large Neighborhood Search (LNS)

## Developer

Academic/Research Community

## Type

Metaheuristic / Matheuristic Algorithm

## Relevance To Hhcrsp

ALNS and LNS are among the most widely used and effective metaheuristics for HHCRSP. They work by iteratively destroying a part of the current solution and repairing it to find improvements. They are highly scalable to large instances and effective in dynamic settings. They are often hybridized with other methods, such as using a Set Partitioning formulation within the search (as in the AlayaCare case) or being used to improve a solution first found by a CP heuristic.


# Benchmark Datasets And Instances

## Dataset Name

Bredström and Rönnqvist instances

## Originator

Bredström and Rönnqvist (2008)

## Description

A widely used set of benchmark instances specifically created for the Home Health Care (HHC) scheduling and routing problem. These instances are significant because they extend general Vehicle Routing Problem with Time Windows (VRPTW) models to include constraints that are characteristic of home care scenarios. Notably, they incorporate pairwise temporal precedence and synchronization constraints, which are essential for modeling tasks that require multiple caregivers to be present simultaneously (i.e., double-staff or synchronized visits). The dataset was introduced alongside a Mixed-Integer Linear Programming (MILP) formulation and is frequently used by researchers to test and validate new algorithms, particularly exact methods, decomposition techniques, and metaheuristics designed to solve complex HHC problems.


# Key Literature Reviews And Surveys

## Title

A Review of Home Health Care Routing and Scheduling Problems (HHCRSP)

## Authors

Not specified in context

## Year

2024.0

## Summary Of Scope

This comprehensive review, published in an engineering journal, analyzes the HHCRSP literature from 2006 to mid-2024. It provides a structured synthesis of research based on problem types (deterministic, dynamic, stochastic), objectives (including fairness and continuity of care), constraints, and solution methods. The paper discusses the application of two-phase heuristics (e.g., Constraint Programming followed by ALNS) for problems with complex requirements and also covers mathematical models for dynamic patient arrival scenarios. A significant part of the review offers practical guidance for researchers on the selection and comparison of benchmark instances across different studies.

## Title

Routing and scheduling in Home Health Care

## Authors

Not specified in context

## Year

2021.0

## Summary Of Scope

This survey paper provides an overview of the HHCRSP literature, highlighting a significant evolution in solution methodologies. It observes that methods proposed before 2014 were often based on simpler greedy heuristics and local search, whereas since 2015-2016, more advanced and powerful techniques such as Benders decomposition, column generation, and various hybrid methods have become increasingly prevalent. The paper also discusses the importance and use of standard benchmark instances, distinguishing between general VRP benchmarks (e.g., Solomon) and those specifically designed for HHC (e.g., Bredström and Rönnqvist).

## Title

Review of Solution Methods for Home Health Care Routing and Scheduling

## Authors

Not specified in context

## Year

2022.0

## Summary Of Scope

This review, sourced from a PubMed Central article, summarizes a range of influential solution approaches for HHCRSP. It covers: a two-stage approach using a constraint programming heuristic for an initial feasible solution, which is then improved by an adaptive large neighborhood search (ALNS); a set partitioning formulation by Grenouilleau et al. (2019) that handles multiple objectives and is solved with an LNS algorithm; a branch-and-price-and-cut algorithm within a rolling horizon methodology for large instances by Bard et al. (2014); and a route-based model by Liu et al. (2019) that addresses stochastic service and travel times using a branch-and-price algorithm with a discrete approximation method.


# Summary Of Research Trends

Research in home care optimization is continuously evolving to create more realistic and powerful models and solution methods. A significant trend observed since the mid-2010s is a shift away from simple greedy heuristics towards more advanced and powerful optimization techniques. Current and future research directions are focused on several key areas:

*   **Advanced Decomposition and Hybrid Methods**: There is increasing use of exact and matheuristic methods capable of solving large, complex, integrated problems. These include column generation (branch-and-price), which decomposes the problem by caregiver routes, and Logic-Based Benders Decomposition (LBBD), which effectively separates the assignment/rostering master problem from the routing subproblems. Hybrid methods that combine the strengths of different approaches, such as using Constraint Programming (CP) to find an initial feasible solution and then improving it with a metaheuristic like Adaptive Large Neighborhood Search (ALNS), are also gaining prominence.

*   **Stochastic and Robust Optimization**: Recognizing that travel and service times are rarely deterministic, a major research thrust is the development of models that account for uncertainty. This is addressed through stochastic programming with recourse, sample average approximation, and robust optimization, which aim to find solutions that are resilient to variations in travel and service durations. Recent work has embedded these concepts within branch-and-price and LBBD frameworks.

*   **Dynamic and Online Scheduling**: Researchers are developing models to handle dynamic events, such as last-minute patient requests or caregiver unavailability. Rolling horizon approaches, where the schedule is periodically re-optimized as new information becomes available, are a common practical strategy. Research explores more formal online algorithms and decomposition methods to manage these dynamic updates efficiently while preserving schedule stability and continuity of care.

*   **Integrated Planning**: There is a move towards more holistic models that integrate multiple planning stages simultaneously. This includes combining medium-term staff rostering and shift scheduling with daily visit assignment and routing to make better trade-offs between cost, continuity, and fairness over longer horizons.

*   **Sophisticated Preference and Quality Modeling**: Future research will likely involve more sophisticated models for patient and caregiver preferences, as well as more nuanced metrics for quality of care beyond simple continuity indices. The use of 'blueprint routes' for recurring tasks to structurally embed high continuity is an example of this trend.
