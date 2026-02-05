#!/usr/bin/env python3
"""
Log and view crisis detection events in Weaviate

This script is used for logging high-severity wellness detections
from the ShaneBrain/Angel Cloud system.

Usage:
    # Log a crisis event
    python log_crisis.py "I feel hopeless" --severity high

    # View recent crisis logs
    python log_crisis.py --view

    # View by severity
    python log_crisis.py --view --severity critical

    # Export to file
    python log_crisis.py --export crisis_report.txt
"""

import argparse
import sys
from datetime import datetime
from weaviate_utils import get_client, log_crisis, get_class_count


def get_crisis_logs(client, severity=None, limit=50):
    """Get crisis log entries"""
    try:
        q = client.query.get(
            "CrisisLog",
            ["input_text", "severity", "timestamp"]
        )

        if severity:
            q = q.with_where({
                "path": ["severity"],
                "operator": "Equal",
                "valueString": severity
            })

        q = q.with_sort([{"path": ["timestamp"], "order": "desc"}])
        q = q.with_limit(limit)

        result = q.do()
        return result.get('data', {}).get('Get', {}).get('CrisisLog', [])
    except Exception as e:
        print(f"Error getting crisis logs: {e}")
        return []


def display_crisis_logs(logs):
    """Display crisis logs with severity coloring"""
    if not logs:
        print("No crisis logs found.")
        return

    severity_icons = {
        'low': '🟢',
        'medium': '🟡',
        'high': '🟠',
        'critical': '🔴'
    }

    print(f"\n{'='*60}")
    print(f"Crisis Log Report ({len(logs)} entries)")
    print('='*60)

    for log in logs:
        severity = log.get('severity', 'unknown')
        text = log.get('input_text', '')
        timestamp = log.get('timestamp', '')[:19]

        icon = severity_icons.get(severity, '⚪')

        print(f"\n{icon} [{severity.upper()}] {timestamp}")
        print(f"   {text[:150]}{'...' if len(text) > 150 else ''}")


def export_logs(logs, filepath):
    """Export crisis logs to a text file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("SHANEBRAIN CRISIS LOG REPORT\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n")
        f.write("="*60 + "\n\n")

        for log in logs:
            severity = log.get('severity', 'unknown')
            text = log.get('input_text', '')
            timestamp = log.get('timestamp', '')[:19]

            f.write(f"[{severity.upper()}] {timestamp}\n")
            f.write(f"{text}\n")
            f.write("-"*40 + "\n\n")

    print(f"✓ Exported {len(logs)} entries to {filepath}")


def get_severity_stats(client):
    """Get counts by severity level"""
    stats = {}
    for sev in ['low', 'medium', 'high', 'critical']:
        try:
            result = client.query.aggregate("CrisisLog").with_where({
                "path": ["severity"],
                "operator": "Equal",
                "valueString": sev
            }).with_meta_count().do()
            count = result['data']['Aggregate']['CrisisLog'][0]['meta']['count']
            stats[sev] = count
        except Exception:
            stats[sev] = 0
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Log and view crisis detection events"
    )
    parser.add_argument('text', nargs='?', help='Text that triggered the crisis detection')
    parser.add_argument('--severity', '-s', default='medium',
                        choices=['low', 'medium', 'high', 'critical'],
                        help='Severity level (default: medium)')
    parser.add_argument('--view', '-v', action='store_true',
                        help='View recent crisis logs')
    parser.add_argument('--limit', '-n', type=int, default=50,
                        help='Max results for view (default: 50)')
    parser.add_argument('--stats', action='store_true',
                        help='Show severity statistics')
    parser.add_argument('--export', '-e', metavar='FILE',
                        help='Export logs to file')

    args = parser.parse_args()

    client = get_client()
    if not client:
        print("Error: Cannot connect to Weaviate")
        sys.exit(1)

    if args.stats:
        print("\n=== Crisis Log Statistics ===")
        stats = get_severity_stats(client)
        total = sum(stats.values())
        print(f"Total: {total} entries\n")
        for sev, count in stats.items():
            pct = (count / total * 100) if total > 0 else 0
            bar = '█' * int(pct / 5)
            print(f"  {sev:8s}: {count:5d} ({pct:5.1f}%) {bar}")
        return

    if args.view or args.export:
        severity_filter = args.severity if args.severity != 'medium' else None
        logs = get_crisis_logs(client, severity=severity_filter, limit=args.limit)

        if args.export:
            export_logs(logs, args.export)
        else:
            display_crisis_logs(logs)
        return

    if args.text:
        result = log_crisis(client, args.text, args.severity)
        if result:
            print(f"✓ Logged crisis event (severity: {args.severity})")
            print(f"  UUID: {result}")
        else:
            print("✗ Failed to log crisis event")
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
