"""Run the agent: `python run.py` (loop) or `python run.py --once`."""
import sys
import time

from agent import config
from agent.brain import Agent

if __name__ == "__main__":
    a = Agent()
    print(f"mode={config.MODE} model={config.MODEL} universe={config.UNIVERSE} kelly={config.KELLY_FRACTION}")
    while True:
        try:
            a.cycle()
        except KeyboardInterrupt:
            raise
        except Exception as e:  # keep the loop alive; stops are re-checked next cycle
            print("[error]", e)
        if "--once" in sys.argv:
            break
        time.sleep(config.CYCLE_SECONDS)
