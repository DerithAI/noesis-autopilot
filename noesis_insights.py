#!/usr/bin/env python3
"""
NOESIS INSIGHTS — Generate insights and timeline from autopilot memory.
Analyzes episodes and produces human-readable intelligence.
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class InsightEngine:
    def __init__(self, db_path: str = "autopilot_memory.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def get_episodes(self) -> List[dict]:
        cur = self.conn.execute(
            "SELECT * FROM episodes ORDER BY cycle ASC"
        )
        return [dict(row) for row in cur.fetchall()]

    def generate_timeline(self) -> List[Dict[str, Any]]:
        episodes = self.get_episodes()
        timeline = []
        
        for ep in episodes:
            content = json.loads(ep["content"])
            timeline.append({
                "cycle": ep["cycle"],
                "timestamp": ep["timestamp"],
                "event_type": ep["event_type"],
                "coherence": ep["coherence"],
                "energy": ep["energy"],
                "action": content.get("action", "unknown"),
                "files": content.get("files", 0),
            })
        return timeline

    def generate_insights(self) -> Dict[str, Any]:
        episodes = self.get_episodes()
        if not episodes:
            return {"status": "no_data", "message": "No episodes found. Run autopilot first."}

        total = len(episodes)
        
        # Coherence trajectory
        coherences = [ep["coherence"] for ep in episodes]
        coherence_trend = "↗️ rising" if coherences[-1] > coherences[0] else "↘️ falling" if coherences[-1] < coherences[0] else "➡️ stable"
        
        # Energy trajectory
        energies = [ep["energy"] for ep in episodes]
        energy_efficiency = (energies[0] - energies[-1]) / total if total > 0 else 0
        
        # Actions taken
        actions = [json.loads(ep["content"]).get("action", "unknown") for ep in episodes]
        action_counts = {}
        for a in actions:
            action_counts[a] = action_counts.get(a, 0) + 1
        dominant_action = max(action_counts, key=action_counts.get)
        
        # Critical moments
        critical = []
        for i, ep in enumerate(episodes):
            if ep["coherence"] < 0.3:
                critical.append({
                    "cycle": ep["cycle"],
                    "type": "low_coherence",
                    "coherence": ep["coherence"],
                    "note": "System detected instability"
                })
            if ep["energy"] < 50:
                critical.append({
                    "cycle": ep["cycle"],
                    "type": "low_energy",
                    "energy": ep["energy"],
                    "note": "Energy reserves depleted"
                })
        
        # Growth metrics
        first = episodes[0]
        last = episodes[-1]
        first_content = json.loads(first["content"])
        last_content = json.loads(last["content"])
        
        return {
            "status": "success",
            "summary": {
                "total_cycles": total,
                "session_duration_sec": total * 3,  # approx if 3s interval
                "coherence_start": coherences[0],
                "coherence_end": coherences[-1],
                "coherence_trend": coherence_trend,
                "coherence_delta": round(coherences[-1] - coherences[0], 3),
                "energy_start": energies[0],
                "energy_end": energies[-1],
                "energy_consumed": round(energies[0] - energies[-1], 2),
                "energy_efficiency_per_cycle": round(energy_efficiency, 4),
                "dominant_action": dominant_action,
                "action_distribution": action_counts,
                "critical_moments_count": len(critical),
            },
            "critical_moments": critical,
            "timeline": self.generate_timeline(),
            "narrative": self._generate_narrative(episodes, coherences, energies, action_counts),
        }

    def _generate_narrative(self, episodes: List[dict], coherences: List[float], 
                            energies: List[float], actions: Dict[str, int]) -> str:
        total = len(episodes)
        trend = "improved" if coherences[-1] > coherences[0] else "declined" if coherences[-1] < coherences[0] else "maintained"
        
        narrative = f"""# NOESIS Cognitive Session Report

## Executive Summary

The system completed {total} autonomous cycles of self-observation and deliberation.
Coherence {trend} from {coherences[0]:.2f} to {coherences[-1]:.2f} (Δ {round(coherences[-1] - coherences[0], 3)}).
Energy consumption: {round(energies[0] - energies[-1], 2)} units across all cycles.

## Decision Patterns

"""
        for action, count in sorted(actions.items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100
            narrative += f"- **{action.upper()}**: {count} times ({pct:.1f}%)\n"
        
        narrative += f"""
## System Evolution

"""
        if coherences[-1] >= 0.5:
            narrative += "The system achieved operational stability (coherence ≥ 0.5) and transitioned into continuous monitoring mode.\n"
        else:
            narrative += "The system remained in renewal/recovery mode throughout the session. Consider increasing engagement or reducing load.\n"
        
        narrative += f"""
## Cognitive Load

- Avg energy per cycle: {round(sum(energies)/total, 2)} if total > 0 else 0
- Peak coherence: {max(coherences):.2f} (cycle {coherences.index(max(coherences)) + 1})
- Lowest coherence: {min(coherences):.2f} (cycle {coherences.index(min(coherences)) + 1})

---
*Generated by NOESIS Insight Engine v1.0*
*Timestamp: {datetime.now().isoformat()}*
"""
        return narrative

    def print_report(self):
        insights = self.generate_insights()
        
        if insights["status"] == "no_data":
            print(insights["message"])
            return

        s = insights["summary"]
        
        print("=" * 60)
        print("  📊 NOESIS INSIGHTS REPORT")
        print("=" * 60)
        print(f"  Cycles:           {s['total_cycles']}")
        print(f"  Duration:         ~{s['session_duration_sec']}s")
        print(f"  Coherence:        {s['coherence_start']:.2f} → {s['coherence_end']:.2f} {s['coherence_trend']}")
        print(f"  Energy:           {s['energy_start']:.1f} → {s['energy_end']:.1f} (used: {s['energy_consumed']})")
        print(f"  Efficiency:       {s['energy_efficiency_per_cycle']} per cycle")
        print(f"  Dominant action:  {s['dominant_action'].upper()}")
        print(f"  Critical moments: {s['critical_moments_count']}")
        print("-" * 60)
        print("  Actions:")
        for action, count in sorted(s['action_distribution'].items(), key=lambda x: x[1], reverse=True):
            bar = "█" * count + "░" * (s['total_cycles'] - count)
            print(f"    {action:<12} {bar} {count}")
        print("=" * 60)
        
        if insights["critical_moments"]:
            print("\n  ⚠️  CRITICAL MOMENTS:")
            for cm in insights["critical_moments"]:
                print(f"    Cycle {cm['cycle']:04d}: {cm['type']} — {cm['note']}")
        
        print("\n" + insights["narrative"])
        
        # Save to file
        report_path = Path("noesis_insights.md")
        report_path.write_text(insights["narrative"], encoding="utf-8")
        print(f"\n  💾 Report saved to: {report_path.resolve()}")
        
        # Save timeline JSON
        timeline_path = Path("noesis_timeline.json")
        timeline_path.write_text(json.dumps(insights["timeline"], indent=2, default=str), encoding="utf-8")
        print(f"  💾 Timeline saved to: {timeline_path.resolve()}")
        
        # Save insights JSON
        insights_path = Path("noesis_insights.json")
        # Remove narrative for clean JSON
        clean_insights = {k: v for k, v in insights.items() if k != "narrative"}
        insights_path.write_text(json.dumps(clean_insights, indent=2, default=str), encoding="utf-8")
        print(f"  💾 Insights saved to: {insights_path.resolve()}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="autopilot_memory.db", help="Path to memory DB")
    args = parser.parse_args()
    
    engine = InsightEngine(args.db)
    engine.print_report()
