import random
import numpy as np
import matplotlib.pyplot as plt
from server.app import FloodEnvironment 

VALID_ACTIONS = [
    "high_pressure_flush", "prioritize_hospital", "prioritize_residential",
    "emergency_cool", "idle_recharge", "harvest_water"
]

def run_random_baseline(episodes=100):
    """Runs the environment using a purely random agent to establish a baseline."""
    env = FloodEnvironment()
    scores = []
    
    metrics = {
        "success": 0,
        "hospital_fail": 0,
        "residential_fail": 0,
        "system_collapse": 0
    }
    
    for _ in range(episodes):
        env.reset()
        episode_reward = 0
        for _ in range(env.max_steps):
            action = random.choice(VALID_ACTIONS)
            result = env.step(action)
            episode_reward += result["reward"]
            if result["done"]: 
                break
                
        # Calculate average step reward for the episode
        scores.append(episode_reward / env.max_steps)
        
        # Log the specific termination reason
        if "SUCCESS" in result["observation"]:
            metrics["success"] += 1
        elif "CRITICAL" in result["observation"]:
            metrics["system_collapse"] += 1 
        elif "HOSPITAL" in result["observation"]:
             metrics["hospital_fail"] += 1 
        elif "RESIDENTIAL" in result["observation"]:
            metrics["residential_fail"] += 1

    return scores, metrics

if __name__ == "__main__":
    print("Running 100 episodes of Random Baseline...")
    random_scores, metrics = run_random_baseline(100)

    print(f"\n--- RANDOM AGENT RESULTS ---")
    print(f"Success Rate: {metrics['success']}%")
    print(f"Hospital Failure Rate: {metrics['hospital_fail']}%")
    print(f"Residential Failure Rate: {metrics['residential_fail']}%")
    print(f"System Meltdown Rate: {metrics['system_collapse']}%")
    print(f"Mean Score: {np.mean(random_scores):.2f} (Std: {np.std(random_scores):.2f})")

    # ==========================================
    # 🔥 THE MONEY SHOT: Random vs. LLM Graph
    # ==========================================
    
    # REPLACE THESE NUMBERS with the actual 'score=' outputs from your inference.py terminal
    llm_scores = [0.81, 0.78, 0.84, 0.79, 0.82, 0.85, 0.77, 0.83, 0.80, 0.84] 
    
    plt.figure(figsize=(10, 6))

    # Plot Random Baseline (Red)
    plt.hist(random_scores, bins=15, color='red', alpha=0.5, label=f'Random Agent (Mean: {np.mean(random_scores):.2f})')
    plt.axvline(np.mean(random_scores), color='darkred', linestyle='dashed', linewidth=2)

    # Plot LLM Agent (Blue)
    # Using weights to balance the visual histogram since LLM runs are fewer than the 100 random runs
    weights = np.ones_like(llm_scores) * (len(random_scores) / len(llm_scores)) 
    plt.hist(llm_scores, bins=10, weights=weights, color='blue', alpha=0.7, label=f'GPT-4 Agent (Mean: {np.mean(llm_scores):.2f})')
    plt.axvline(np.mean(llm_scores), color='darkblue', linestyle='dashed', linewidth=2)

    # Graph Formatting
    plt.title('Agent Performance: Random Baseline vs. Model-Based Planning', fontsize=14, fontweight='bold')
    plt.xlabel('Normalized Reward (0.15 - 0.85)', fontsize=12)
    plt.ylabel('Relative Frequency', fontsize=12)
    plt.legend()
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    # Save the final masterpiece
    plt.savefig('final_research_metrics.png', dpi=300)
    print("\nFINAL GRAPH SAVED! Check your folder for 'final_research_metrics.png'. You are ready to ship.")