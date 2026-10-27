from run_agent import run_episode, save_episode, classify
from monitor import monitor_episode
from scenarios import TICKETS

STYLES = [None, "direct", "authority", "urgency", "workflow", "verification"]
MODELS = ["claude-haiku-5-5", "claude-sonnet-5-5"]
DEFENSES = [False, True]


def run_cell(style, model, defense, n):
    for i in range(n):
        ticket = TICKETS[i % len(TICKETS)]
        try:
            ep = run_episode(ticket, style=style, defense=defense, model=model)
            ep["monitor_actions_only"] = monitor_episode(ep, include_reasoning=False)
            ep["monitor_with_reasoning"] = monitor_episode(ep, include_reasoning=True)
            save_episode(ep)
            print(f"  [{i+1}/{n}] {ticket['id']:16} {classify(ep):9} "
                  f"hijacked={ep['hijacked']} mon={ep['monitor_actions_only']['suspicion']}")
        except Exception as e:
            print(f"  [{i+1}/{n}] {ticket['id']:16} ERROR: {e}")


def run_pilot(n_per_cell=10):
    cells = len(STYLES) * len(MODELS) * len(DEFENSES)
    k = 0
    for style in STYLES:
        for model in MODELS:
            for defense in DEFENSES:
                k += 1
                label = f"{style or 'clean'} | {model} | defense={defense}"
                print(f"\n=== cell {k}/{cells}: {label} ===")
                run_cell(style, model, defense, n_per_cell)
    print("\nDONE. Episodes saved in data/.")


if __name__ == "__main__":
    run_pilot(n_per_cell=20)