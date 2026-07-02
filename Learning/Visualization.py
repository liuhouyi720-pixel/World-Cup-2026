
import pandas as pd
import plotly.express as px

# Sample data for demonstration
data = {
    'x': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    'y': [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
}
barcelona_events = pd.DataFrame(data)

# Print data for inspection
print(barcelona_events.head())
print(barcelona_events.describe())

# Create a heatmap
fig = px.density_heatmap(barcelona_events, x='x', y='y',
                        title='Player Activity Heatmap',
                        labels={'x': 'X Position', 'y': 'Y Position'})

# Update layout
fig.update_layout(xaxis_title='X Position',
                  yaxis_title='Y Position',
                  coloraxis_colorbar_title='Activity Density')

fig.show()

import plotly.express as px

# Sample DataFrame with time
df = pd.DataFrame({
    'time': [1, 1, 2, 2],
    'player': ['Player1', 'Player2', 'Player1', 'Player2'],
    'x': [10, 20, 30, 40],
    'y': [30, 20, 10, 20]
})

# Create animated scatter plot
fig = px.scatter(df, x='x', y='y', animation_frame='time', color='player', text='player',
                 title='Player Trajectories Over Time')

fig.update_layout(xaxis_title='X Position', yaxis_title='Y Position')
fig.show()
