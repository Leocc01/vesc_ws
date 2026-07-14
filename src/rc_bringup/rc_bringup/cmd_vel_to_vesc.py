import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float64

class CmdVelToVesc(Node):
    def __init__(self):
        super().__init__('cmd_vel_to_vesc')
        self.speed_pub = self.create_publisher(
            Float64, '/commands/motor/speed', 10)
        self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_cb, 10)
        # linear.x 1.0 = 몇 ERPM인지 설정
        self.erpm_gain = 8000.0

    def cmd_vel_cb(self, msg):
        erpm = Float64()
        erpm.data = msg.linear.x * self.erpm_gain
        self.speed_pub.publish(erpm)

def main():
    rclpy.init()
    rclpy.spin(CmdVelToVesc())

if __name__ == '__main__':
    main()
