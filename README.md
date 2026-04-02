# Network Measurement Scheduler

> Implementation of a conflict‑aware measurement scheduler inspired by Prof. Calyam et al., “OnTimeMeasure: A Scalable Framework for Scheduling Active Measurements” (IEEE E2EMON 2005).  
> https://ieeexplore.ieee.org/abstract/document/1564471

## 🌟 Highlights

- Schedules active measurement tasks into fixed‑size time bins without violating tool conflicts or MLA constraints.  
- Implements both heuristic bin‑packing and round‑robin schemes and reports cycle times for each.  
- Generates a daily timetable over 24 hours for any valid input JSON describing tasks, conflicts, and measurement parameters.  
- Includes a bin‑size analysis to show how cycle time changes with different bin sizes.  

## ℹ️ Overview

This project implements a simple scheduler for active network measurements based on the ideas in the OnTimeMeasure framework. The goal is to assign measurement tasks to time bins in a way that avoids conflicting tests running together, respects a measurement level agreement (MLA) on how many jobs can run in parallel, and keeps the overall cycle time as small as possible.

The input is a JSON file that lists measurement tasks (source, destination, tool, duration), a task conflict graph, a bin size, an MLA value, and optional settings for how long to schedule and which bin sizes to analyze. The script reads this input, builds both a heuristic bin‑packing schedule and a round‑robin schedule, prints a human‑readable summary to the console, and can write a detailed JSON output with per‑job schedules.

### ✍️ Authors

This code and report were written as part of a research assistant hiring exercise based on the work of Prasad Calyam and collaborators on OnTimeMeasure and conflict‑free active measurement scheduling. The implementation is kept straightforward on purpose so that task definitions, conflict relationships, and scheduling parameters can be changed easily for testing.

## 🚀 Usage

### Command‑line

From the project directory:

```bash
python scheduler.py --input input.json --output output_input.json
```

Example runs (using the sample files in this folder):

```bash
# 4‑task example from the hiring sheet
python scheduler.py --input input.json --output output_input.json

# 6‑task example 1
python scheduler.py --input sample_input1.json --output output_sample1.json

# 6‑task example 2
python scheduler.py --input sample_input2.json --output output_sample2.json
```

Each run prints:

- A **conflict map** table (X means two tasks cannot share a bin).  
- A **heuristic schedule** summary: bins used, cycle time, jobs per cycle, cycles and jobs in 24 hours, and the one‑cycle timetable.  
- A **round‑robin schedule** summary with the same fields for comparison.  
- A **bin size analysis** table showing, for several bin sizes, the cycle time under each scheme and the time saved by the heuristic.  

The JSON output (if `--output` is given) contains the original input plus structured details for both schemes and the bin‑size analysis.

## ⬇️ Installation

The scheduler is a single Python 3 script with only standard library dependencies (`argparse`, `json`, `math`). To run it:

1. Make sure Python 3 is installed and on your PATH.  
2. Place `scheduler.py` and your input JSON files in the same directory.  
3. Run the commands shown in the usage section from a terminal.  

No external packages or cloud services are required for this version. In a real deployment, the same logic could be run as a cron job or service on a GCP Compute Engine instance, writing schedules and measurement results to Cloud Storage or a database.

## 💭 Feedback and Contributing

This script is meant to be easy to read and modify. The main extension points are:

- Changing or extending the JSON schema for tasks and conflicts.  
- Adding more metrics to the summary (for example, collision counts or bandwidth usage).  
- Experimenting with different heuristic strategies (first‑fit vs. best‑fit, different bin ordering, and so on).  

For review, the most useful feedback would be on the clarity of the scheduling logic, the choice of data structures, and how well the code reflects the OnTimeMeasure design.
