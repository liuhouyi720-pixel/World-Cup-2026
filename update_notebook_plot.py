import json
from pathlib import Path
notebook_path = Path(r'd:\UIUC\Projects\World Cup 2026\football-match-data-analysis-tactical-insights.ipynb')
with notebook_path.open('r', encoding='utf-8') as f:
    data = json.load(f)
cell = data['cells'][27]
new_source = [
    "# Plot average player positions on a standard football pitch",
    "def draw_pitch(ax, pitch_color='#a8d08d', line_color='white'):",
    "    ax.set_facecolor(pitch_color)",
    "    ax.plot([0, 0], [0, 80], color=line_color)",
    "    ax.plot([120, 120], [0, 80], color=line_color)",
    "    ax.plot([0, 120], [0, 0], color=line_color)",
    "    ax.plot([0, 120], [80, 80], color=line_color)",
    "    ax.plot([60, 60], [0, 80], color=line_color)",
    "    ax.add_patch(plt.Rectangle((0, 21), 18, 38, fill=False, edgecolor=line_color, linewidth=1.5))",
    "    ax.add_patch(plt.Rectangle((102, 21), 18, 38, fill=False, edgecolor=line_color, linewidth=1.5))",
    "    ax.add_patch(plt.Rectangle((0, 30), 6, 20, fill=False, edgecolor=line_color, linewidth=1.5))",
    "    ax.add_patch(plt.Rectangle((114, 30), 6, 20, fill=False, edgecolor=line_color, linewidth=1.5))",
    "    ax.add_patch(plt.Circle((60, 40), 9.15, fill=False, edgecolor=line_color, linewidth=1.5))",
    "    ax.add_patch(plt.Circle((60, 40), 0.5, color=line_color))",
    "    ax.add_patch(plt.Circle((12, 40), 0.5, color=line_color))",
    "    ax.add_patch(plt.Circle((108, 40), 0.5, color=line_color))",
    "    ax.set_xlim(-5, 125)",
    "    ax.set_ylim(-5, 85)",
    "    ax.set_aspect('equal')",
    "    ax.axis('off')",
    "",
    "fig, ax = plt.subplots(figsize=(12, 8))",
    "draw_pitch(ax)",
    "ax.scatter(formation['x'], formation['y'], s=120, color='blue', edgecolors='black', linewidth=0.8, zorder=5)",
    "for i, row in formation.iterrows():",
    "    ax.text(row['x'], row['y'] + 2.5, row['player'], fontsize=9, ha='center', va='bottom', color='black', zorder=6)",
    "",
    "ax.set_title('Average Player Positions on a Football Pitch')",
    "plt.show()",
    ""
]
cell['source'] = new_source
with notebook_path.open('w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
print('updated')
