# EMG RNN CNN Gesture Recognition

This is a project that I made to complete my undergraduate studies in computer engineering. I used muscle contraction data (EMG) as inputs for a CNN RNN hybrid neural network. I also provided several other models located in the `Models` folder.

# Overview

Model is trained using 8 EMG points, here's an example of a gesture data:
![image](https://user-images.githubusercontent.com/21309983/113470789-53f29c00-9482-11eb-935b-0edf120aeb8b.png)
Data is then processed into a several Neural Network Model with different configurations.

Working model was then tested using a real drone / simulated environment.
![image](https://user-images.githubusercontent.com/21309983/113470829-9ddb8200-9482-11eb-96e3-609265fd06a9.png)
![image](https://user-images.githubusercontent.com/21309983/113470834-a59b2680-9482-11eb-854d-4763c5e62118.png)



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
