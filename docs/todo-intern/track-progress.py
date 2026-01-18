#!/usr/bin/env python3
"""
TODO Progress Tracker

Parses markdown TODO lists and generates progress reports.

Usage:
    python track-progress.py                 # Show all progress
    python track-progress.py --file docs.md  # Show specific file
    python track-progress.py --summary       # Show summary only
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class TaskStats:
    """Statistics for a TODO file."""
    total: int = 0
    completed: int = 0
    in_progress: int = 0
    blocked: int = 0
    
    @property
    def not_started(self) -> int:
        return self.total - self.completed - self.in_progress - self.blocked
    
    @property
    def percentage(self) -> float:
        return (self.completed / self.total * 100) if self.total > 0 else 0.0


class TodoTracker:
    """Parse and track TODO items in markdown files."""
    
    # Regex patterns for different checkbox states
    COMPLETED = re.compile(r'^- \[x\]', re.IGNORECASE)
    IN_PROGRESS = re.compile(r'^- \[~\]', re.IGNORECASE)
    BLOCKED = re.compile(r'^- \[!\]', re.IGNORECASE)
    NOT_STARTED = re.compile(r'^- \[ \]')
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path(__file__).parent
    
    def parse_file(self, filepath: Path) -> TaskStats:
        """Parse a markdown file and count TODO items."""
        stats = TaskStats()
        
        if not filepath.exists():
            return stats
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                if self.COMPLETED.match(line):
                    stats.completed += 1
                    stats.total += 1
                elif self.IN_PROGRESS.match(line):
                    stats.in_progress += 1
                    stats.total += 1
                elif self.BLOCKED.match(line):
                    stats.blocked += 1
                    stats.total += 1
                elif self.NOT_STARTED.match(line):
                    stats.total += 1
        
        return stats
    
    def get_all_stats(self) -> Dict[str, TaskStats]:
        """Get statistics for all TODO files."""
        files = {
            'Documentation': 'documentation.md',
            'Features': 'features.md',
            'Infrastructure': 'infrastructure.md',
            'Community': 'community.md',
        }
        
        stats = {}
        for name, filename in files.items():
            filepath = self.base_dir / filename
            stats[name] = self.parse_file(filepath)
        
        return stats
    
    def generate_progress_bar(self, percentage: float, width: int = 30) -> str:
        """Generate a text progress bar."""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
    
    def print_summary(self, stats: Dict[str, TaskStats]):
        """Print a summary of all TODOs."""
        print("\n" + "="*70)
        print("📊 LOOM PROJECT TODO SUMMARY")
        print("="*70)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Calculate totals
        total_tasks = sum(s.total for s in stats.values())
        total_completed = sum(s.completed for s in stats.values())
        total_in_progress = sum(s.in_progress for s in stats.values())
        total_blocked = sum(s.blocked for s in stats.values())
        total_not_started = sum(s.not_started for s in stats.values())
        
        overall_percentage = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        # Overall progress
        print("OVERALL PROGRESS")
        print("-" * 70)
        print(f"  {self.generate_progress_bar(overall_percentage)}")
        print(f"  Completed: {total_completed}/{total_tasks} tasks\n")
        
        # By category
        print("BY CATEGORY")
        print("-" * 70)
        
        for name, stat in sorted(stats.items(), key=lambda x: x[1].percentage, reverse=True):
            if stat.total == 0:
                continue
            
            print(f"\n{name}")
            print(f"  {self.generate_progress_bar(stat.percentage)}")
            print(f"  ✅ Completed:    {stat.completed:3d}")
            print(f"  🚧 In Progress:  {stat.in_progress:3d}")
            print(f"  🚫 Blocked:      {stat.blocked:3d}")
            print(f"  ⏸️  Not Started:  {stat.not_started:3d}")
            print(f"  📊 Total:        {stat.total:3d}")
        
        print("\n" + "="*70)
        
        # Status breakdown
        print("\nSTATUS BREAKDOWN")
        print("-" * 70)
        print(f"  ✅ Completed:    {total_completed:4d} ({total_completed/total_tasks*100:.1f}%)")
        print(f"  🚧 In Progress:  {total_in_progress:4d} ({total_in_progress/total_tasks*100:.1f}%)")
        print(f"  🚫 Blocked:      {total_blocked:4d} ({total_blocked/total_tasks*100:.1f}%)")
        print(f"  ⏸️  Not Started:  {total_not_started:4d} ({total_not_started/total_tasks*100:.1f}%)")
        print(f"  📊 Total:        {total_tasks:4d}")
        print("="*70 + "\n")
    
    def print_detailed(self, name: str, stats: TaskStats):
        """Print detailed statistics for a single file."""
        print(f"\n{'='*70}")
        print(f"📋 {name.upper()} TODO LIST")
        print(f"{'='*70}\n")
        
        if stats.total == 0:
            print("  No tasks found.\n")
            return
        
        print(f"  {self.generate_progress_bar(stats.percentage)}\n")
        print(f"  ✅ Completed:    {stats.completed:3d} ({stats.percentage:.1f}%)")
        print(f"  🚧 In Progress:  {stats.in_progress:3d}")
        print(f"  🚫 Blocked:      {stats.blocked:3d}")
        print(f"  ⏸️  Not Started:  {stats.not_started:3d}")
        print(f"  📊 Total:        {stats.total:3d}")
        print(f"\n{'='*70}\n")
    
    def update_master_list(self, stats: Dict[str, TaskStats]):
        """Update the progress tracker in project-init.md."""
        master_file = self.base_dir / 'project-init.md'
        
        if not master_file.exists():
            print("Warning: project-init.md not found")
            return
        
        # Read current content
        with open(master_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Generate new table
        table_lines = [
            "| Category | Complete | Total | Progress |",
            "|----------|----------|-------|----------|"
        ]
        
        for name, stat in stats.items():
            emoji = "✅" if stat.percentage >= 75 else "🚧" if stat.percentage >= 25 else "⏸️"
            table_lines.append(
                f"| {name} | {stat.completed} | {stat.total} | {emoji} {stat.percentage:.0f}% |"
            )
        
        # Calculate overall
        total = sum(s.total for s in stats.values())
        completed = sum(s.completed for s in stats.values())
        overall = (completed / total * 100) if total > 0 else 0
        
        table_lines.append("")
        table_lines.append(f"**Overall:** {completed}/{total} ({overall:.0f}%)")
        
        new_table = "\n".join(table_lines)
        
        # Replace table in content
        pattern = r'\| Category \| Complete \| Total \| Progress \|.*?\n\*\*Overall:\*\*.*'
        replacement = new_table
        
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Write back
        with open(master_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Updated {master_file.name}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Track TODO progress')
    parser.add_argument('--file', help='Specific file to track')
    parser.add_argument('--summary', action='store_true', help='Show summary only')
    parser.add_argument('--update', action='store_true', help='Update master list')
    
    args = parser.parse_args()
    
    tracker = TodoTracker()
    
    if args.file:
        # Show specific file
        filepath = tracker.base_dir / args.file
        stats = tracker.parse_file(filepath)
        tracker.print_detailed(args.file, stats)
    else:
        # Show all
        all_stats = tracker.get_all_stats()
        tracker.print_summary(all_stats)
        
        if args.update:
            tracker.update_master_list(all_stats)


if __name__ == '__main__':
    main()
