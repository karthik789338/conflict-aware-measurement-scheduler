<p align="left">
  <img src="https://komarev.com/ghpvc/?username=karthik789338&label=Profile%20views&color=0e75b6&style=flat" alt="karthik789338" />
</p>

<h1 align="center">Conflict-Aware Measurement Scheduler</h1>
<h3 align="center">A simple Python implementation of heuristic bin packing for regulated network measurement scheduling</h3>

<p align="center">
  <a href="https://karthikadari.com/" target="_blank">
    <img src="https://img.shields.io/badge/Portfolio-karthikadari.com-111?style=for-the-badge&logo=vercel&logoColor=white" />
  </a>
  <a href="https://ieeexplore.ieee.org/abstract/document/1564471" target="_blank">
    <img src="https://img.shields.io/badge/Research%20Paper-OnTimeMeasure-blue?style=for-the-badge&logo=readme&logoColor=white" />
  </a>
  <a href="https://github.com/karthik789338/conflict-aware-measurement-scheduler" target="_blank">
    <img src="https://img.shields.io/github/stars/karthik789338/conflict-aware-measurement-scheduler?style=for-the-badge" />
  </a>
  <a href="https://github.com/karthik789338/conflict-aware-measurement-scheduler" target="_blank">
    <img src="https://img.shields.io/github/forks/karthik789338/conflict-aware-measurement-scheduler?style=for-the-badge" />
  </a>
</p>

<p align="center">
  This repository contains a small and practical implementation of the scheduling idea from the
  <b>OnTimeMeasure</b> paper. The code builds conflict-aware daily timetables for measurement tasks,
  respects MLA limits, and compares heuristic bin packing against a round-robin baseline.
</p>

---

## What this project does

The scheduler places network measurement tasks into fixed time bins while following two simple rules:

- tasks that conflict cannot share the same bin
- the number of tasks inside a bin cannot exceed the MLA value

It compares:

- **Round-robin scheduling**: one task per bin
- **Heuristic bin packing**: place each task into the earliest valid bin

The main metric is **cycle time**, which is the time needed to finish one full round of all tasks.

---

## Files

- `scheduler.py` - main program
- `input.json` - base example
- `sample_input1.json` - denser conflict case
- `sample_input2.json` - lighter conflict case
- `output_*.txt` - saved console outputs
- `output_*.json` - saved structured outputs

---

## Input format

Each input file is a JSON file like this:

```json
{
  "tasks": [
    {
      "task_id": "tau1",
      "source": "S1",
      "destination": "S2",
      "tool": "Pathchar",
      "duration": 20
    }
  ],
  "conflicts": [
    ["tau1", "tau2"]
  ],
  "bin_size": 20,
  "mla": 2,
  "horizon_minutes": 1440,
  "analysis_bin_sizes": [10, 15, 20, 25, 30, 40, 60]
}
```

---

## How to run

Open CMD in the project folder and run:

```bat
python scheduler.py --input input.json --output output_input.json
```

To save the console output too:

```bat
python scheduler.py --input input.json --output output_input.json > output_input.txt
```

For the other two test files:

```bat
python scheduler.py --input sample_input1.json --output output_sample1.json
python scheduler.py --input sample_input1.json --output output_sample1.json > output_sample1.txt

python scheduler.py --input sample_input2.json --output output_sample2.json
python scheduler.py --input sample_input2.json --output output_sample2.json > output_sample2.txt
```

---

## Verified results

### `input.json`
- Heuristic cycle time: **40 minutes**
- Round-robin cycle time: **80 minutes**
- Savings: **40 minutes**
- Economy: **50.0%**

### `sample_input1.json`
- Heuristic cycle time: **80 minutes**
- Round-robin cycle time: **120 minutes**
- Savings: **40 minutes**
- Economy: **33.3%**

### `sample_input2.json`
- Heuristic cycle time: **40 minutes**
- Round-robin cycle time: **120 minutes**
- Savings: **80 minutes**
- Economy: **66.7%**

---

## Notes

This implementation focuses on the scheduling core of the problem.

It does **not** try to implement the full framework from the paper, such as:

- automatic tool-conflict graph generation
- automatic link-conflict graph generation
- custom scripting language support
- server-specific cron orchestration

Instead, it assumes that the final conflict relationships are given in the input file. That keeps the program easy to test and matches the hiring task requirement to avoid hard coding.

---

## Requirements

- Python 3.9 or newer
- no external libraries required

---

## Author

**Karthik Adari**  
Founder • Data Engineer / Applied ML • GCP/AWS • GenAI
