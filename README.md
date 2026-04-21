# 2. Cài đặt dependencies
```bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
```

# Cài thêm ackermann_msgs nếu chưa có
```bash
sudo apt-get install ros-jazzy-ackermann-msgs
```

# 3. Build
```bash
colcon build 
```

# 4. Source
```bash
source install/setup.bash
```

## Hướng dẫn sử dụng

### Khởi động mô phỏng
```bash
ros2 launch carlike gz_robot.launch.py
```
Trong RViz, chuyển Fixed Frame từ base_footprint sang odom để xem robot di chuyển.

### Điều khiển robot bằng bàn phím
```bash
python3 ~/ros2_ws/src/carlike/scripts/ackermann_teleop.py
```
Mapping phím:
| Phím | Hành động |
| --- | --- |
| W | Tiến |
| S | Lùi |
| A | Rẽ trái |
| D | Rẽ phải |
| Space | Dừng |

### Kiểm tra dữ liệu cảm biến
**LiDAR**
```bash
ros2 topic echo /scan
```

**Camera**
```bash
ros2 topic echo /camera/image_raw
```

**Encoder / Joint states**
```bash
ros2 topic echo /joint_states
```

**Odometry**
```bash
ros2 topic echo /odom
```

### Xem danh sách topic và node
```bash
ros2 topic list
ros2 node list
```
