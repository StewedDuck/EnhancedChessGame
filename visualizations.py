# visualizations.py

import os
import pandas as pd
import matplotlib.pyplot as plt

def main():
    # 1) Locate and load the CSV
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, 'stats.csv')
    if not os.path.exists(csv_path):
        print(f"Error: Cannot find {csv_path}")
        return
    df = pd.read_csv(csv_path)

    # 2) Compute the summary table for “Time Taken per Move”
    summary = df['avg_move_time'].agg(['min','max','mean','std'])
    summary_df = summary.to_frame().T
    summary_df.columns = ['Minimum','Maximum','Average','StdDev']

    # 3) Display the summary as a matplotlib table
    fig, ax = plt.subplots(figsize=(6, 1.5))
    ax.axis('off')  # hide axes
    tbl = ax.table(
        cellText=summary_df.values,
        colLabels=summary_df.columns,
        cellLoc='center',
        loc='center'
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(12)
    tbl.scale(1, 2)
    plt.title('Time Taken per Move — Summary Statistics')
    plt.tight_layout()
    plt.show()

    # 4) Bar chart: Number of Moves per Game
    fig, ax = plt.subplots()
    ax.bar(df.index + 1, df['move_count'])
    ax.set_title('Number of Moves per Game')
    ax.set_xlabel('Game Index')
    ax.set_ylabel('Total Moves')
    plt.tight_layout()
    plt.show()

    # 5) Bar chart: Captured Pieces Count per Game
    fig, ax = plt.subplots()
    ax.bar(df.index + 1, df['captures'])
    ax.set_title('Captured Pieces Count per Game')
    ax.set_xlabel('Game Index')
    ax.set_ylabel('Captured Pieces')
    plt.tight_layout()
    plt.show()

    # 6) Line graph: Average Move Time per Game
    fig, ax = plt.subplots()
    ax.plot(df.index + 1, df['avg_move_time'], marker='o')
    ax.set_title('Average Move Time per Game')
    ax.set_xlabel('Game Index')
    ax.set_ylabel('Avg Move Time (s)')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()
