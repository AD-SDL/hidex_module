import rclpy
from rclpy.executors import MultiThreadedExecutor, SingleThreadedExecutor

from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
# from rclpy.clock import clock

from threading import Thread

from std_msgs.msg import String
from std_srvs.srv import Empty
from sensor_msgs.msg import JointState
from std_msgs.msg import Header

# from hidex_driver.hidex_driver import hidex_reader # UNCOMMENT WHEN IT IS READY

class HidexDescriptionClient(Node):

    def __init__(self, NODE_NAME = 'HidexDescriptionNode'):
        super().__init__(NODE_NAME)

        # self.hidex = hidex_reader() #TODO: USE THIS WHEN IT IS READY

        timer_period = 0.1  # seconds

        self.state = "UNKNOWN"
        joint_cb_group = ReentrantCallbackGroup()
        state_cb_group = ReentrantCallbackGroup()

        self.statePub = self.create_publisher(String, NODE_NAME + '/state',10)
        self.stateTimer = self.create_timer(timer_period, callback = self.stateCallback, callback_group = state_cb_group)

        self.joint_publisher = self.create_publisher(JointState,'joint_states', 10, callback_group = joint_cb_group)
        self.joint_state_handler = self.create_timer(timer_period, callback = self.joint_state_publisher_callback, callback_group = joint_cb_group)
    
    
    def stateCallback(self):
        '''
        Publishes the hidex_description state to the 'state' topic. 
        '''
        msg = String()
        msg.data = 'State: %s' % self.state
        self.statePub.publish(msg)
        self.get_logger().info('Publishing State: "%s"' % msg.data)
        self.state = "READY"


    def joint_state_publisher_callback(self):
        
        # joint_states = self.hidex.refresh_joint_state() #TODO:USE THIS WHEN IT IS READY
        joint_states = [0]
        hidex_joint_msg = JointState()
        hidex_joint_msg.header = Header()
        hidex_joint_msg.header.stamp = self.get_clock().now().to_msg()
        hidex_joint_msg.name = ['Hidex_Plate_Joint']
        hidex_joint_msg.position = joint_states
        # print(joint_states)

        # hidex_joint_msg.position = [0.01, -1.34, 1.86, -3.03, 0.05, 0.05, 0.91]
        hidex_joint_msg.velocity = []
        hidex_joint_msg.effort = []

        self.joint_publisher.publish(hidex_joint_msg)
        self.get_logger().info('Publishing joint states: "%s"' % str(joint_states))


def main(args=None):
    rclpy.init(args=args)
    try:
        hidex_joint_state_publisher = HidexDescriptionClient()
        executor = MultiThreadedExecutor()
        executor.add_node(hidex_joint_state_publisher)

        try:
            hidex_joint_state_publisher.get_logger().info('Beginning client, shut down with CTRL-C')
            executor.spin()
        except KeyboardInterrupt:
            hidex_joint_state_publisher.get_logger().info('Keyboard interrupt, shutting down.\n')
        finally:
            executor.shutdown()
            hidex_joint_state_publisher.destroy_node()
    finally:
        rclpy.shutdown()


if __name__ == '__main__':
    main()