import plotly.graph_objects as go
import numpy as np
t = np.linspace(0, 2 * np.pi, 100)
fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=np.sin(t), name='sin(t)'))
fig.add_trace(go.Scatter(x=t, y=np.cos(t), name='cost(t)'))
fig.update_layout(hovermode='x unified')
fig.show()