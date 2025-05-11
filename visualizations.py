import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'stats.csv')
    if not os.path.exists(csv_path):
        print(f"Error: Cannot find {csv_path}")
        return

    # Load the data
    df = pd.read_csv(csv_path)

    # 1) Summary of Average Move Time
    summary = df['avg_move_time'].agg(['min','max','mean','std'])
    print("\nSummary of Average Move Time:")
    print(f"  Minimum : {summary['min']:.2f} s")
    print(f"  Maximum : {summary['max']:.2f} s")
    print(f"  Average : {summary['mean']:.2f} s")
    print(f"  StdDev  : {summary['std']:.2f} s")

    # 2) Bar chart: Number of Moves per Game
    plt.figure()
    plt.bar(df.index + 1, df['move_count'])
    plt.title('Number of Moves per Game')
    plt.xlabel('Game Index')
    plt.ylabel('Total Moves')
    plt.tight_layout()
    plt.show()

    # 3) Bar chart: Captured Pieces Count per Game
    plt.figure()
    plt.bar(df.index + 1, df['captures'])
    plt.title('Captured Pieces Count per Game')
    plt.xlabel('Game Index')
    plt.ylabel('Captured Pieces')
    plt.tight_layout()
    plt.show()

    # 4) Line graph: Average Move Time per Game
    plt.figure()
    plt.plot(df.index + 1, df['avg_move_time'], marker='o')
    plt.title('Average Move Time per Game')
    plt.xlabel('Game Index')
    plt.ylabel('Avg Move Time (s)')
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
