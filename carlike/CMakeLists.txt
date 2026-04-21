cmake_minimum_required(VERSION 3.8)
project(carlike)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# ─── Dependencies ─────────────────────────────────────────────────────────────
# ROS2 Jazzy dùng Gazebo Harmonic → package là ros_gz_sim, ros_gz_bridge
find_package(ament_cmake REQUIRED)
find_package(robot_state_publisher REQUIRED)
find_package(ros_gz_sim REQUIRED)
find_package(ros_gz_bridge REQUIRED)
find_package(xacro REQUIRED)
find_package(urdf REQUIRED)

# ─── Install directories ───────────────────────────────────────────────────────
install(
  DIRECTORY
    config
    launch
    meshes
    rviz
    urdf
    carlike_world
    scripts
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES
    carlike_world.world
  DESTINATION share/${PROJECT_NAME}
)

# ─── Linting ──────────────────────────────────────────────────────────────────
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()