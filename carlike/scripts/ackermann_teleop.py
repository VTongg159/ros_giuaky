#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from ackermann_msgs.msg import AckermannDriveStamped
from geometry_msgs.msg import Twist
import sys
import termios
import tty
import select

msg = """
Điều khiển xe Ackermann & Chuyển đổi sang /cmd_vel
---------------------------
Cơ chế: Publish AckermannDriveStamped -> /cmd_ackermann
        Convert sang Twist -> /cmd_vel (để Gazebo hiểu)

Phím tắt:
        W       
      A S D     

W/S : Tăng/giảm tốc độ (linear.x)
A/D : Đánh lái trái/phải (angular.z)
Space : Dừng khẩn cấp

CTRL-C để thoát
"""

class AckermannTeleop(Node):
    def __init__(self):
        super().__init__('ackermann_teleop_key')
        
        # Publish cả 2 topic để bạn test
        self.pub_ackermann = self.create_publisher(AckermannDriveStamped, '/cmd_ackermann', 10)
        
        # Bonus: Convert sang cmd_vel để Gazebo Ackermann Plugin nhận được luôn
        self.pub_twist = self.create_publisher(Twist, '/cmd_vel', 10)

        self.speed = 0.0
        self.steering_angle = 0.0

        self.MAX_SPEED = 2.0
        self.MAX_STEER = 0.5
        self.SPEED_STEP = 0.1
        self.STEER_STEP = 0.05

    def get_key(self, settings):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

    def run(self):
        print(msg)
        settings = termios.tcgetattr(sys.stdin)
        try:
            while rclpy.ok():
                key = self.get_key(settings)
                if key == 'w':
                    self.speed = min(self.speed + self.SPEED_STEP, self.MAX_SPEED)
                elif key == 's':
                    self.speed = max(self.speed - self.SPEED_STEP, -self.MAX_SPEED)
                elif key == 'a':
                    self.steering_angle = min(self.steering_angle + self.STEER_STEP, self.MAX_STEER)
                elif key == 'd':
                    self.steering_angle = max(self.steering_angle - self.STEER_STEP, -self.MAX_STEER)
                elif key == ' ':
                    self.speed = 0.0
                    self.steering_angle = 0.0
                elif key == '\x03':  # CTRL-C
                    break
                
                # Cập nhật liên tục ngay cả khi không bấm phím
                self.publish_messages()
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.speed = 0.0
            self.steering_angle = 0.0
            self.publish_messages()
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

    def publish_messages(self):
        # 1. Publish ra /cmd_ackermann (Yêu cầu chính)
        ack_msg = AckermannDriveStamped()
        ack_msg.header.stamp = self.get_clock().now().to_msg()
        ack_msg.header.frame_id = 'base_link'
        ack_msg.drive.speed = self.speed
        ack_msg.drive.steering_angle = self.steering_angle
        self.pub_ackermann.publish(ack_msg)

        # 2. Convert và Publish sang /cmd_vel (Bonus cho Gazebo)
        twist_msg = Twist()
        twist_msg.linear.x = self.speed
        twist_msg.angular.z = self.steering_angle
        self.pub_twist.publish(twist_msg)

def main(args=None):
    rclpy.init(args=args)
    node = AckermannTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
