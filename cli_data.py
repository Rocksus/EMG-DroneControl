from __future__ import print_function
from myo.utils import TimeInterval
import myo
import sys


class Listener(myo.DeviceListener):

  def __init__(self):
    self.interval = TimeInterval(None, 0.05)
    self.orientation = None
    self.pose = myo.Pose.rest
    self.emg_enabled = False
    self.locked = False
    self.rssi = None
    self.emg = None

  def output(self):
    if not self.interval.check_and_reset():
      return

    parts = []
    if self.orientation:
      for comp in self.orientation:
        parts.append('{}{:.4f}'.format(' ' if comp >= 0 else '', comp))
    parts.append(str(self.pose).ljust(15))
    parts.append('E' if self.emg_enabled else ' ')
    parts.append('L' if self.locked else ' ')
    parts.append(self.rssi or 'NORSSI')
    if self.emg:
      for comp in self.emg:
        parts.append(str(comp).ljust(5))
    print('\r' + ''.join('[{}]'.format(p) for p in parts), end='')
    sys.stdout.flush()

  def on_connected(self, event):
    event.device.request_rssi()
    event.device.stream_emg(True)
    self.emg_enabled = True
    
  def on_rssi(self, event):
    self.rssi = event.rssi
    self.output()

  def on_pose(self, event):
    self.pose = event.pose
    self.output()

  def on_orientation(self, event):
    self.orientation = event.orientation
    self.output()

  def on_emg(self, event):
    self.emg = event.emg
    self.output()


if __name__ == '__main__':
  myo.init(sdk_path='myo-sdk-win-0.9.0')
  hub = myo.Hub()
  listener = Listener()
  while hub.run(listener.on_event, 500):
    pass
