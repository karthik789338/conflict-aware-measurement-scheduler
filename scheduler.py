import argparse
import json
from math import floor

MINUTES_PER_DAY = 24 * 60


def load_input(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_output(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def pick_task_id(task):
    # Some test files may use task_id, some may use id.
    # This keeps the script easy to test without editing the code each time.
    if 'task_id' in task:
        return str(task['task_id'])
    if 'id' in task:
        return str(task['id'])
    raise ValueError(f"Task is missing both 'task_id' and 'id': {task}")


def normalize_tasks(task_rows):
    tasks = []
    seen = set()

    for row in task_rows:
        task_id = pick_task_id(row)
        if task_id in seen:
            raise ValueError(f"Duplicate task id found: {task_id}")
        seen.add(task_id)

        tasks.append({
            'task_id': task_id,
            'source': row['source'],
            'destination': row['destination'],
            'tool': row['tool'],
            'duration': int(row['duration'])
        })

    return tasks


def build_conflict_map(tasks, conflict_edges):
    task_ids = [task['task_id'] for task in tasks]
    conflict_map = {task_id: set() for task_id in task_ids}

    for edge in conflict_edges:
        if len(edge) != 2:
            raise ValueError(f"Each conflict edge must have exactly two task ids. Got: {edge}")

        left, right = str(edge[0]), str(edge[1])
        if left not in conflict_map or right not in conflict_map:
            raise ValueError(f"Unknown task id in conflict edge: {edge}")

        conflict_map[left].add(right)
        conflict_map[right].add(left)

    return conflict_map


def validate_inputs(tasks, bin_size, mla):
    if bin_size <= 0:
        raise ValueError('bin_size must be greater than 0.')
    if mla < 1:
        raise ValueError('mla must be at least 1.')

    for task in tasks:
        if task['duration'] <= 0:
            raise ValueError(f"Task {task['task_id']} has non-positive duration.")
        if task['duration'] > bin_size:
            raise ValueError(
                f"Task {task['task_id']} has duration {task['duration']}, which is bigger than bin_size {bin_size}."
            )


def can_share_bin(task, current_bin, conflict_map, mla):
    if len(current_bin['tasks']) >= mla:
        return False

    for existing in current_bin['tasks']:
        if task['task_id'] in conflict_map[existing['task_id']]:
            return False

    return True


def sort_tasks(tasks):
    # Long jobs first. If two jobs take the same time, use task id to keep output stable.
    return sorted(tasks, key=lambda t: (-t['duration'], t['task_id']))


def build_heuristic_bins(tasks, conflict_map, bin_size, mla):
    bins = []

    for task in sort_tasks(tasks):
        placed = False

        for current_bin in bins:
            if can_share_bin(task, current_bin, conflict_map, mla):
                current_bin['tasks'].append(task)
                placed = True
                break

        if not placed:
            bins.append({
                'bin': len(bins) + 1,
                'start_minute': len(bins) * bin_size,
                'size': bin_size,
                'tasks': [task]
            })

    return bins


def build_round_robin_bins(tasks, bin_size):
    bins = []

    for index, task in enumerate(sort_tasks(tasks), start=1):
        bins.append({
            'bin': index,
            'start_minute': (index - 1) * bin_size,
            'size': bin_size,
            'tasks': [task]
        })

    return bins


def minute_to_clock(value):
    value = value % MINUTES_PER_DAY
    hour = value // 60
    minute = value % 60
    return f'{hour:02d}:{minute:02d}'


def build_cycle_schedule(bins):
    rows = []

    for current_bin in bins:
        start_minute = current_bin['start_minute']
        for task in current_bin['tasks']:
            rows.append({
                'task_id': task['task_id'],
                'source': task['source'],
                'destination': task['destination'],
                'tool': task['tool'],
                'duration': task['duration'],
                'bin': current_bin['bin'],
                'start_minute': start_minute,
                'finish_minute': start_minute + task['duration'],
                'start_time': minute_to_clock(start_minute),
                'finish_time': minute_to_clock(start_minute + task['duration'])
            })

    return sorted(rows, key=lambda row: (row['start_minute'], row['task_id']))


def expand_to_day(cycle_rows, cycle_time, horizon_minutes):
    if cycle_time <= 0:
        return []

    timetable = []
    repetitions = floor(horizon_minutes / cycle_time)

    for cycle_number in range(repetitions):
        offset = cycle_number * cycle_time
        for row in cycle_rows:
            start_minute = row['start_minute'] + offset
            finish_minute = row['finish_minute'] + offset
            if finish_minute > horizon_minutes:
                continue

            timetable.append({
                'cycle': cycle_number + 1,
                'task_id': row['task_id'],
                'bin': row['bin'],
                'tool': row['tool'],
                'source': row['source'],
                'destination': row['destination'],
                'duration': row['duration'],
                'start_minute': start_minute,
                'finish_minute': finish_minute,
                'start_time': minute_to_clock(start_minute),
                'finish_time': minute_to_clock(finish_minute)
            })

    return timetable


def summarize(name, bins, horizon_minutes):
    cycle_schedule = build_cycle_schedule(bins)
    cycle_time = len(bins) * bins[0]['size'] if bins else 0
    daily_timetable = expand_to_day(cycle_schedule, cycle_time, horizon_minutes) if bins else []

    return {
        'scheme': name,
        'bin_count': len(bins),
        'cycle_time': cycle_time,
        'jobs_per_cycle': len(cycle_schedule),
        'cycles_in_day': floor(horizon_minutes / cycle_time) if cycle_time else 0,
        'jobs_scheduled_in_day': len(daily_timetable),
        'cycle_schedule': cycle_schedule,
        'daily_timetable': daily_timetable
    }


def analyze_bin_sizes(tasks, conflict_map, mla, bin_sizes, horizon_minutes):
    rows = []

    for bin_size in bin_sizes:
        entry = {'bin_size': bin_size}
        try:
            validate_inputs(tasks, bin_size, mla)
            h_bins = build_heuristic_bins(tasks, conflict_map, bin_size, mla)
            rr_bins = build_round_robin_bins(tasks, bin_size)
            h_summary = summarize('heuristic', h_bins, horizon_minutes)
            rr_summary = summarize('round_robin', rr_bins, horizon_minutes)

            entry.update({
                'status': 'ok',
                'heuristic_cycle_time': h_summary['cycle_time'],
                'round_robin_cycle_time': rr_summary['cycle_time'],
                'cycle_time_saved': rr_summary['cycle_time'] - h_summary['cycle_time'],
                'heuristic_bins': h_summary['bin_count'],
                'round_robin_bins': rr_summary['bin_count']
            })
        except ValueError as exc:
            entry.update({'status': 'invalid', 'message': str(exc)})

        rows.append(entry)

    return rows


def print_conflict_map(conflict_map):
    task_ids = sorted(conflict_map.keys())
    print('\nCONFLICT MAP (X = cannot share a bin)')
    print('-' * 72)
    print(' ' * 10 + '  '.join(f'{task_id:>8}' for task_id in task_ids))

    for task_id in task_ids:
        row = f'  {task_id:<8} '
        for other in task_ids:
            if other == task_id:
                cell = '-'
            elif other in conflict_map[task_id]:
                cell = 'X'
            else:
                cell = '.'
            row += f'  {cell:>8}'
        print(row)


def print_summary(summary):
    print(f"\n{summary['scheme'].upper()} SCHEDULE")
    print('-' * 72)
    print(f"Bins used        : {summary['bin_count']}")
    print(f"Cycle time       : {summary['cycle_time']} minutes")
    print(f"Jobs per cycle   : {summary['jobs_per_cycle']}")
    print(f"Cycles in 24 hrs : {summary['cycles_in_day']}")
    print(f"Jobs in 24 hrs   : {summary['jobs_scheduled_in_day']}")
    print('\nCycle schedule')

    for row in summary['cycle_schedule']:
        print(
            f"  Bin {row['bin']:>2} | {row['task_id']:>6} | {row['tool']:<12} | "
            f"{row['source']} -> {row['destination']} | {row['start_time']} - {row['finish_time']}"
        )


def print_bin_analysis(rows):
    print('\nBIN SIZE ANALYSIS')
    print('-' * 72)
    print(f"  {'bin':>4}  {'heuristic':>12}  {'round-robin':>12}  {'saved':>8}  {'economy':>8}")

    for row in rows:
        if row['status'] == 'ok':
            rr = row['round_robin_cycle_time']
            saved = row['cycle_time_saved']
            pct = f'{saved / rr * 100:.1f}%' if rr > 0 else 'n/a'
            print(
                f"  {row['bin_size']:>4}  {row['heuristic_cycle_time']:>9} min  "
                f"{rr:>9} min  {saved:>5} min  {pct:>8}"
            )
        else:
            print(f"  {row['bin_size']:>4}  invalid -- {row['message']}")


def main():
    parser = argparse.ArgumentParser(description='Conflict-aware measurement scheduler')
    parser.add_argument('--input', required=True, help='Path to input JSON file')
    parser.add_argument('--output', help='Optional path to save output JSON')
    args = parser.parse_args()

    payload = load_input(args.input)
    tasks = normalize_tasks(payload['tasks'])
    conflict_map = build_conflict_map(tasks, payload.get('conflicts', []))
    bin_size = int(payload['bin_size'])
    mla = int(payload.get('mla', 1))
    horizon_minutes = int(payload.get('horizon_minutes', MINUTES_PER_DAY))
    analysis_bin_sizes = payload.get('analysis_bin_sizes', [])

    validate_inputs(tasks, bin_size, mla)

    heuristic_bins = build_heuristic_bins(tasks, conflict_map, bin_size, mla)
    round_robin_bins = build_round_robin_bins(tasks, bin_size)

    heuristic_summary = summarize('heuristic', heuristic_bins, horizon_minutes)
    round_robin_summary = summarize('round_robin', round_robin_bins, horizon_minutes)
    bin_analysis = analyze_bin_sizes(tasks, conflict_map, mla, analysis_bin_sizes, horizon_minutes)

    result = {
        'input': payload,
        'heuristic': heuristic_summary,
        'round_robin': round_robin_summary,
        'bin_analysis': bin_analysis
    }

    print_conflict_map(conflict_map)
    print_summary(heuristic_summary)
    print_summary(round_robin_summary)
    if bin_analysis:
        print_bin_analysis(bin_analysis)

    if args.output:
        save_output(args.output, result)


if __name__ == '__main__':
    main()
