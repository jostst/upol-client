# uPOL Client
This is a client software for controlling a hyperspectral polarization microscope. It works by passing commands to a server (physically connected to the hardware) through a websockets connection. The connection is NOT SECURE IN THIS IMPLEMENTATION as only password is used.

The main goal behind this project is to eliminate the necessity of screens and peripheral devices connected to experimental setups.

**_NOTE:_**  The software is under active development and might change rapidly. There are probably bugs and/or bad code present, but the software currently serves its purpose.

**_ANOTHER NOTE:_**  Although the code as is might not be directly applicable to many users, the concepts can be used in development of similar projects.

## Project outline
All the code is contained in multiple files, that are connected together to form a wholesome client. Overview follows.

In general, `client.py` establishes websocket connection and authentication, whereas `model.py` takes care of handling updates from the GUI to the server, whereas `main.py` presents the main GUI and handles reported updates from the server.

### `/main.py`
This file contains the GUI elements and GUI callbacks. Important component is the server message handler, which appropriately updates the GUI components based on the messages recieved from the server.

### `/components/client.py`
`client.py` establishes connection to the server and authenticates through the use of passwords. It handles sending and recieving messages but does not format checking. The reciever methods pass the recieved messages to the handler for processing.

### `/components/model.py`
`model.py` presents an interconnection layer between the remote server and the GUI. The changes in the parameters are stored in a model class object instance and reported to the server using `client.py` component.

## Requirements
The module was written in Python 3.12.1. A somewhat stale list of requirements is listed in this repository in file requirements.txt

## Messaging protocol
### 1. General Messages (`MSG`)
- **Description**: Used for general communication or logging purposes.
- **Purpose**:
  - Transmit text-based messages.
  - Provide basic communication functionality.
  ```json
  {
    "type": "MSG",
    "data": "Hello, this is a general message."
  }
  ```
---

### 2. Heartbeat Messages (`HRB`)
- **Description**: Signals the system's heartbeat to indicate connectivity or status.
- **Purpose**:
  - Monitor system health.
  - Ensure active connection between components.
```json
{
  "type": "HRB",
  "data": null
}
```
---

### 3. Value Updates (`VAL`)
- **Description**: Updates the values of various hardware or system components.
- **Modules and Submodules**:
  - **Focus**:
    - `positionMM`: Current position of the focus system.
    - `set_jog`: Configure jog step size.
    - `home`: Reset focus to the home position.
    - `step_major`: Perform a major step adjustment.
    - `step_minor`: Perform a minor step adjustment.
  - **Camera**:
    - `Exposure`: Update camera exposure time.
    - `Gain`: Update camera gain value.
    - `Live`: Start or stop the live feed.
    - `Snapshot`: Request a camera snapshot.
  - **Polarization**:
    - **Submodules**:
      - `rot1`:
        - `position`: Update rotational position of `rot1`.
        - `home`: Reset `rot1` to the home position.
      - `rot2`:
        - `position`: Update rotational position of `rot2`.
        - `home`: Reset `rot2` to the home position.
      - `flt1`:
        - `position`: Update filter position.
        - `home`: Reset `flt1` to the home position.
  - **Hyperspectral**:
    - `wavelength`: Update or retrieve the current wavelength.
    - `black`: Enable or disable black calibration.
    - `temperature`: Retrieve the current temperature.
    - `status`: Update or retrieve the status of the system.
    - `range`: Update the minimum and maximum wavelength range.
```json
{
  "type": "VAL",
  "data": {
    "module": "focus",
    "field": "positionMM",
    "value": 50.123
  }
}
```
---

### 4. Image Messages (`IMG`)
- **Description**: Handles the transmission of Base64-encoded images for display or processing.
- **Purpose**:
  - Transmit visual data to be rendered or processed.
  - Enable real-time or snapshot-based image updates.
```json
{
  "type": "IMG",
  "data": "iVBORw0KGgoAAAANSUhEUgAAAAUA..."
}
```
---

## Script file
Acquisition of the system can be scripted in a file. This file is sent to the server as plain text to be processed. An example of an acquisition script is in file `example_script.input`. The file is divided into structured sections, each serving a specific purpose in defining the acquisition metadata, parameters, and steps.

---

### General Structure
A script file consists of three main sections:
1. **VERSION**: Specifies the script format version.
2. **ACQUISITION**: Defines metadata and general settings for the acquisition.
3. **STEPS**: Specifies detailed parameters for each acquisition step.

---

### Section: VERSION
The `VERSION` section specifies the version of the script file format for compatibility purposes.

#### Format
VERSION <version_number>

```
VERSION 1.0
```
---

### Section: ACQUISITION
The `ACQUISITION` section contains metadata and configuration settings for the acquisition process.

#### Format
Key-value pairs describe the general setup. Additional metadata fields can be included as nested key-value pairs under `metadata`.

#### Required Fields
| **Field**       | **Description**                                                                 |
|------------------|---------------------------------------------------------------------------------|
| `project`        | Name of the project.                                                           |
| `experiment`     | Identifier for the experiment.                                                 |
| `path`           | File path for saving the acquisition output.                                   |
| `date`           | Date of the acquisition in `YYYY-MM-DD` format.                                |
| `operator`       | Name of the operator responsible for the acquisition (can include a title).    |
| `metadata`       | Additional metadata as nested key-value pairs (optional but recommended).      |
| `num_steps`      | Total number of acquisition steps defined in the `STEPS` section.              |

```
ACQUISITION  
project: Sample Acquisition  
experiment: EXP_001  
path: testing/test1.zip  
date: 2024-12-10  
operator: Name Surname, Ph.D.  
metadata:  
  description: Test acquisition with variable parameters  
  custom_field1: Value1  
  custom_field2: Value2  
num_steps: 4  
```
---

### Section: STEPS
The `STEPS` section defines the specific parameters for each acquisition step. Each step is described in a tabular format.

#### Format
- The first row contains comments that describe the column names and expected values.
- Each subsequent row represents an acquisition step, with fields separated by tabs.

#### Required Fields
| **Field**       | **Description**                                                                |
|------------------|--------------------------------------------------------------------------------|
| `step`          | Step number (starting from 0).                                                 |
| `t_int`         | Integration time (in milliseconds).                                            |
| `gain`          | Gain value for the acquisition.                                                |
| `z_pos`         | Z-position (e.g., focus depth) in micrometers.                                 |
| `lam`           | Wavelength (in nanometers).                                                    |
| `phi_g`         | Global angle in degrees.                                                       |
| `phi_a`         | Absolute angle in degrees.                                                     |
| `flt_a`         | Filter selection (1, 2, 3, or 4).                                              |

```
STEPS  
# Columns: step, t_int (integration time), gain, z_pos (z position), lam (wavelength),  
#          phi_g (global angle), phi_a (absolute angle), flt_a (filter: 1, 2, 3, or 4)  
0	100	1.5	0.0	550	45	90	1  
1	110	1.8	0.0	600	50	95	2  
2	120	2.0	0.0	650	55	100	3  
3	130	2.2	0.0	700	60	105	4  
```
---

### Notes
- **Comments**: Lines starting with `#` are treated as comments and ignored during processing.
- **Tabs**: Use tabs to separate values in the `STEPS` section for clarity.
- **Consistency**: Ensure that the `num_steps` in the `ACQUISITION` section matches the number of rows in the `STEPS` section.


## Acknowledgements
This work was done as part of the project "Order models for optical microscopy of biological tissues" (Z1-4384) financially supported by the SLovenian Research Agency. Project homepage: [here](https://www.ijs.si/ijsw/ARRSProjekti/2022/Modeli%20urejenosti%20za%20optično%20mikroskopijo%20bioloških%20tkiv)

## Disclaimer
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.