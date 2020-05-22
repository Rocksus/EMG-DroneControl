# EMG RNN CNN Gesture Recognition

This is a project that I made to complete my undergraduate studies in computer engineering. I used muscle contraction data (EMG) as inputs for a CNN RNN hybrid neural network. I also provided several other models located in the `Models` folder.

# Model Results

Training results from each model can be seen in the `Results` folder.

## Requirements

- Python 3.5 or more
- Keras
- Myo
- Dronekit
- Dronekit-SITL
- Pymavlink
- Pymavproxy
- Mission Planner

## Setup

1. Install the required libraries in Python
   ```
    pip install dronekit
    pip install dronekit-sitl
    pip install Keras
    pip install myo-python
   ```
2. Download the Myo SDK and edit the `sdk_path` accordingly.
3. Test the connection to your drone using `DroneControl/connect_check.py`
4. If everything is fine and well you are good to go!

## Usage
Run
```
emg_control.py
```
Located in the DroneControl folder.
*Note*: Please edit the velocity of your drone accordingly inside the code.