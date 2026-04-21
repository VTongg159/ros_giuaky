Robot Car-like (Ackermann) với Tay Máy 2-DOF
Mô phỏng robot di chuyển kiểu Car-like (Ackermann Steering) tích hợp tay máy 2-DOF trong môi trường ROS2 Jazzy / Gazebo.

Môn học: Lập trình robot với ROS — RBE3017 1
Sinh viên: Nguyễn Văn Tổng — 23020766
Giảng viên: TS. Lê Xuân Lực & Ths. Nguyễn Thiên Hạo
Trường: Đại học Công Nghệ — ĐHQGHN


 Mục lục

Giới thiệu
Tính năng
Cấu trúc hệ thống
Thông số kỹ thuật
Yêu cầu hệ thống
Cài đặt
Hướng dẫn sử dụng
Cấu trúc thư mục
Cảm biến
Kết quả mô phỏng
Hạn chế & Hướng phát triển
Tài liệu tham khảo


Giới thiệu
Dự án thiết kế, mô hình hóa và mô phỏng một mobile manipulator gồm:

Khung xe Car-like điều hướng theo cơ cấu lái Ackermann (4 bánh, 2 bánh sau dẫn động, 2 bánh trước dẫn hướng).
Tay máy 2-DOF (planar 2R) gắn phía sau thân xe, mở rộng khả năng tương tác với môi trường.
3 cảm biến: LiDAR 360°, Camera RGB, Encoder odometry.

Toàn bộ hệ thống được mô tả bằng URDF/Xacro chuẩn ROS và mô phỏng trong Gazebo + RViz.

Tính năng

 Mô hình 3D đầy đủ xuất từ SolidWorks (định dạng STL)
 File URDF/Xacro hợp lệ với đầy đủ inertial, visual, collision
 Điều khiển Ackermann qua topic /cmd_vel (plugin gz-sim-ackermann-steering-system)
 Tay máy 2-DOF điều khiển vị trí qua ros2_control
 LiDAR quét 360° — topic /scan
 Camera RGB 640×480 — topic /camera/image_raw
 Odometry — topic /odom
 TF tree đầy đủ, hiển thị chuẩn trong RViz


Cấu trúc hệ thống
base_footprint
└── base_link (thân xe)
    ├── rear_left_wheel_link   [continuous]
    ├── rear_right_wheel_link  [continuous]
    ├── left_steering_link     [revolute]
    │   └── front_left_wheel_link  [continuous]
    ├── right_steering_link    [revolute]
    │   └── front_right_wheel_link [continuous]
    ├── lidar_link             [fixed]
    ├── camera_link            [fixed]
    └── arm_link1              [revolute — θ₁]
        └── arm_link2          [revolute — θ₂]
            └── end_effector_link [fixed]
Chuỗi động học:

Khung xe → 4 bánh xe → cơ cấu lái trước
Đế tay máy → Link1 → Link2 → End-effector


Thông số kỹ thuật
Robot Car-like
Thông sốKý hiệuGiá trịChiều dài cơ sởl272.4 mmTrack width bánh trướcωf295.86 mmTrack width bánh sauωr295 mmĐường kính bánh xedw90 mm
Tay máy 2-DOF
Thông sốKý hiệuGiá trịChiều dài Link1l₁130.1 mmChiều dài Link2l₂127.05 mmGiới hạn khớp 1θ₁[-1.5, 0.87] radGiới hạn khớp 2θ₂[-1.57, 0.62] rad
Giới hạn khớp lái
KhớpGiới hạn dướiGiới hạn trênMomentVận tốc tối đaBánh xe (continuous)——10 Nm20 rad/sKhớp lái (revolute)-0.78 rad0.78 rad5 Nm4 rad/sKhớp tay máy (revolute)——15 Nm1.5 rad/s

Yêu cầu hệ thống
Thành phầnPhiên bảnOSUbuntu 24.04ROSROS2 JazzySimulatorGazebo HarmonicCông cụ thiết kếSolidWorks (xuất STL)
Các package phụ thuộc:
bashros-jazzy-ros2-control
ros-jazzy-gz-ros2-control
ros-jazzy-ackermann-msgs
ros-jazzy-joint-state-publisher
ros-jazzy-robot-state-publisher
ros-jazzy-rviz2

Cài đặt
bash# 1. Clone repository về workspace
cd ~/ros2_ws/src
git clone https://github.com/your-username/your-repo.git carlike

# 2. Cài đặt dependencies
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y

# Cài thêm ackermann_msgs nếu chưa có
sudo apt-get install ros-jazzy-ackermann-msgs

# 3. Build
colcon build --packages-select carlike

# 4. Source
source install/setup.bash

Hướng dẫn sử dụng
Khởi động mô phỏng
bashros2 launch carlike gz_robot.launch.py

Trong RViz, chuyển Fixed Frame từ base_footprint sang odom để xem robot di chuyển.

Điều khiển robot bằng bàn phím
bashpython3 ~/ros2_ws/src/carlike/scripts/ackermann_teleop.py
Mapping phím:
PhímHành độngWTiếnSLùiARẽ tráiDRẽ phảiSpaceDừng
Kiểm tra dữ liệu cảm biến
bash# LiDAR
ros2 topic echo /scan

# Camera
ros2 topic echo /camera/image_raw

# Encoder / Joint states
ros2 topic echo /joint_states

# Odometry
ros2 topic echo /odom
Xem danh sách topic và node
bashros2 topic list
ros2 node list

Cấu trúc thư mục
carlike/
├── config/
│   └── joint_controllers.yaml   # Cấu hình ros2_control
├── launch/
│   └── gz_robot.launch.py       # Launch file chính
├── meshes/                      # File STL từ SolidWorks
│   ├── base_link.STL
│   ├── rear_left_wheel_link.STL
│   ├── rear_right_wheel_link.STL
│   ├── front_left_wheel_link.STL
│   ├── front_right_wheel_link.STL
│   ├── left_steering_link.STL
│   ├── right_steering_link.STL
│   ├── arm_link1.STL
│   ├── arm_link2.STL
│   ├── end_effector_link.STL
│   ├── lidar_link.STL
│   └── camera_link.STL
├── scripts/
│   └── ackermann_teleop.py      # Script điều khiển bàn phím
├── urdf/
│   └── full_carlike.urdf        # File mô tả robot
├── worlds/                      # Môi trường Gazebo
└── package.xml

Cảm biến
LiDAR (/scan)
Thông sốGiá trịLoạigpu_lidarSố tia360 (1 tia/độ)Góc quét-180° đến +180°Phạm vi0.12 m — 10 mTần số10 HzFramelidar_link
Camera RGB (/camera/image_raw)
Thông sốGiá trịLoạicameraĐộ phân giải640 × 480Định dạngR8G8B8FOV ngang60° (1.047 rad)Tần số30 HzFramecamera_link
Encoder / Odometry (/joint_states, /odom)
Tích hợp trong plugin Ackermann Steering. Odometry tính từ encoder bánh sau:
Δs = r · Δφ
Δθ = (Δs_r - Δs_l) / W

Kết quả mô phỏng

Robot di chuyển đúng quỹ đạo Ackermann: 2 bánh sau dẫn động liên tục, 2 bánh trước lái với góc khác nhau (thỏa mãn điều kiện không trượt).
Tay máy 2-DOF hoạt động trong workspace vành khăn bán kính trong |l₁ - l₂| = 3.05 mm, bán kính ngoài l₁ + l₂ = 257.15 mm.
Cả 3 cảm biến phát dữ liệu ổn định đúng tần suất thiết kế.
TF tree đầy đủ, không có frame bị đứt.


Hạn chế & Hướng phát triển
Hạn chế hiện tại:

Chưa triển khai Inverse Kinematics cho tay máy (hiện chỉ Forward Kinematics).
Chưa điều khiển tay máy tự động.
LiDAR chưa có noise model thực tế.
Chưa tích hợp thuật toán Navigation (SLAM, move_base).

Hướng phát triển:

Tích hợp MoveIt! để lập kế hoạch quỹ đạo tay máy.
Thêm SLAM + Navigation Stack (Nav2) để robot tự điều hướng.
Bổ sung noise model cho cảm biến.
Triển khai trên phần cứng thực tế.


Tài liệu tham khảo

R. Siegwart, I. R. Nourbakhsh, D. Scaramuzza — Introduction to Autonomous Mobile Robots, 2nd ed. MIT Press, 2011.
B. Siciliano et al. — Robotics: Modelling, Planning and Control. Springer, 2009.
ROS Wiki — URDF/Tutorials
ROS Wiki — Gazebo/Tutorials
M. Quigley et al. — ROS: an open-source Robot Operating System, ICRA 2009.
ROS Answers — Ackermann steering controller

