
# phsase 3 - Code   
import numpy as np
import matplotlib.pyplot as plt

# Simulated LIDAR data (360-degree scan, 1-degree resolution)
def simulate_lidar(position, obstacles, max_range=10):
    angles = np.deg2rad(np.arange(360))
    readings = np.full(360, max_range)

    for i, angle in enumerate(angles):
        for dist in np.linspace(0.5, max_range, 100):  # Start closer than 8
            x = position[0] + dist * np.cos(angle)
            y = position[1] + dist * np.sin(angle)
            if any(np.linalg.norm([x - ox, y - oy]) < 0.5 for ox, oy in obstacles):
                readings[i] = dist
                break
    return readings

# Simple obstacle avoidance logic
def obstacle_avoidance(lidar_data):
    left = np.mean(lidar_data[60:120])
    front = np.mean(np.concatenate([lidar_data[0:30], lidar_data[330:360]]))
    right = np.mean(lidar_data[240:300])

    if front < 1.0:
        if left > right:
            return "turn_left"
        else:
            return "turn_right"
    return "move_forward"

# Motion execution
def update_position(pos, direction, step_size=0.5):
    x, y, heading = pos
    if direction == "move_forward":
        x += step_size * np.cos(np.deg2rad(heading))
        y += step_size * np.sin(np.deg2rad(heading))
    elif direction == "turn_left":
        heading += 30
    elif direction == "turn_right":
        heading -= 30
    return (x, y, heading % 360)

# Simulated world
obstacles = [(5, 5), (7, 6), (6, 8)]
position = (0, 0, 0)  # x, y, heading

# Simulation loop
trajectory = [position[:2]]
for _ in range(30):
    lidar = simulate_lidar(position, obstacles)
    action = obstacle_avoidance(lidar)
    position = update_position(position, action)
    trajectory.append(position[:2])

# Plot result
trajectory = np.array(trajectory)
plt.plot(trajectory[:, 0], trajectory[:, 1], label="Path")
ox, oy = zip(*obstacles)
plt.scatter(ox, oy, color='red', label="Obstacles")
plt.legend()
plt.xlabel("X")
plt.ylabel("Y")
plt.title("Autonomous Robot Path Planning")
plt.grid()
plt.show()

# phase 4
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import heapq

# --- Sensor Fusion Simulation (Simple average) ---
def sensor_fusion_sim(gps, imu):
    return [(g + i) / 2 for g, i in zip(gps, imu)]

# --- A* Path Planning ---
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal):
    open_set = [(heuristic(start, goal), 0, start, [])]
    visited = set()
    while open_set:
        cost, g, node, path = heapq.heappop(open_set)
        if node in visited:
            continue
        visited.add(node)
        path = path + [node]
        if node == goal:
            return path
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = node[0] + dx, node[1] + dy
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]) and grid[nx][ny] == 0:
                heapq.heappush(open_set, (g + 1 + heuristic((nx, ny), goal), g + 1, (nx, ny), path))
    return None

# --- Anomaly Detection ---
def detect_anomalies(data, threshold=2):
    mean = np.mean(data)
    std = np.std(data)
    return [x for x in data if abs(x - mean) > threshold * std]

# --- Telemetry Log (Pandas) ---
def make_vehicle_log():
    data = {
        "Time": pd.date_range(start="2025-01-01", periods=5, freq='s'),
        "Speed_kmph": [30, 32, 29, 120, 31],
        "Battery": [98, 97, 96, 95, 94]
    }
    return pd.DataFrame(data)

# --- Plotting Functions ---
def plot_path(grid, path):
    grid_np = np.array(grid)
    plt.imshow(grid_np, cmap='Greys', origin="upper")
    if path:
        px, py = zip(*path)
        plt.plot(py, px, marker='o', color='red', label='Path')
    plt.title("A* Path Planning")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_speed(df):
    plt.plot(df["Time"], df["Speed_kmph"], marker='o', color='blue', label="Speed")
    threshold_line = np.mean(df["Speed_kmph"]) + 2 * np.std(df["Speed_kmph"])
    plt.axhline(threshold_line, color='red', linestyle='--', label='Anomaly Threshold')
    plt.title("Vehicle Speed Over Time")
    plt.xlabel("Time")
    plt.ylabel("Speed (kmph)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# --- Main ---
print("-- AI-EBPL Simplified with Visualization --")

# Sensor Fusion
gps = [40, 30]
imu = [42, 28]
fused = sensor_fusion_sim(gps, imu)
print("Fused Position:", fused)

# A* Path Planning
grid = [
    [0, 0, 0, 1],
    [1, 0, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 0]
]
path = astar(grid, (0, 0), (3, 3))
print("Planned Path:", path)
plot_path(grid, path)

# Telemetry Anomaly Detection
df = make_vehicle_log()
print("\nVehicle Telemetry Log:\n", df)
anomalies = detect_anomalies(df["Speed_kmph"])
print("Anomalous Speeds:", anomalies)
plot_speed(df)

# phase 5

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
np.random.seed(42)
time_steps = 100
#Simulated sensor data (in meters)
lidar_data= np.random.normal(loc=10.0, scale=2.0, size=time_steps)
camera_data= np.random.normal(loc=10.2, scale=1.5, size=time_steps)
fused_data = (lidar_data + camera_data) / 2
x_pos = np.cumsum(np.cos(fused_data / 10))
y_pos=np.cumsum(np.sin(fused_data/ 10))
obstacles= np.array([[10, 10], [15, 13], [20, 18]])
def check_proximity (x, y, obstacles, threshold=2.5):
  for ox, oy in obstacles:
      dist= np.sqrt((x-ox)*2+ (y - oy)*2)
      if dist<threshold:
          return True
  return False
proximity_flags= [check_proximity (x, y, obstacles) for x, y in zip(x_pos, y_pos)]
data = pd.DataFrame({
  'Time': np.arange(time_steps),
  'Lidar_Distance': lidar_data,
  'Camera_Distance': camera_data,
  'Fused Distance': fused_data,
  'X': x_pos,
  'Y': y_pos,
  'Obstacle_Close': proximity_flags
})
plt.figure(figsize=(10, 6))
plt.plot(data['X'], data['Y'], label='Planned Path', color='blue')
plt.scatter(obstacles[:, 0], obstacles[:, 1], color='red', label='Obstacles', marker='X', s=100)
danger_points=data[data['Obstacle_Close']]
plt.scatter(danger_points['X'], danger_points['Y'], color='orange', label='Proximity Alert', s=60)
plt.title("AI-EBPL: Autonomous Path Planning with Sensor Fusion")
plt.xlabel("X Position")
plt.ylabel("Y Position")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.tight_layout()
plt.show()
