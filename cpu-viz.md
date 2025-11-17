# CPU Architecture Visualization

An interactive 3D visualization of CPU architecture using VPython, featuring detailed pipeline stages, cache hierarchy, and instruction execution flow.

## Features

### Architecture Components

1. **5-Stage Pipeline**
   - Fetch: Instruction fetching from memory
   - Decode: Instruction decoding and register read
   - Execute: ALU operations and address calculation
   - Memory: Data memory access
   - Writeback: Write results back to registers

2. **Cache Hierarchy**
   - L1 Cache (32 KB)
   - L2 Cache (256 KB)
   - Main Memory (DDR4 RAM)
   - Visual data paths showing cache-memory connections

3. **CPU Components**
   - Register File (8 general-purpose registers)
   - Arithmetic Logic Unit (ALU)
   - Control Unit with Program Counter (PC)
   - Data paths connecting components

4. **Interactive Controls**
   - **Next Cycle**: Step through one clock cycle at a time
   - **Run/Pause**: Auto-advance through cycles (2 cycles/second)
   - **Reset**: Reset simulation to initial state

### Visual Features

- Color-coded components for easy identification
- Active pipeline stages highlighted in green
- Instruction flow through pipeline stages
- Real-time cycle counter and instruction display
- Instruction queue showing upcoming instructions

## Installation

1. Install Python 3.7 or higher
2. Install VPython:
   ```bash
   pip install -r requirements_cpu_viz.txt
   ```
   or
   ```bash
   pip install vpython
   ```

## Usage

Run the visualization:
```bash
python cpu_architecture_viz.py
```

The visualization will open in your default web browser.

### Controls

- **Next Cycle Button**: Click to advance one clock cycle and see instructions move through the pipeline
- **Run/Pause Button**: Toggle automatic execution mode
- **Reset Button**: Reset the simulation to cycle 0

### Understanding the Visualization

- **Pipeline Stages** (top): Shows the 5-stage pipeline with current instructions in each stage
  - Blue boxes indicate inactive stages
  - Green boxes indicate active stages processing instructions

- **Control Unit** (top left): Displays the Program Counter (PC) value

- **Instruction Queue** (top right): Shows upcoming instructions to be executed

- **Register File** (left): 8 general-purpose registers (R0-R7) with their current values

- **ALU** (center): Arithmetic Logic Unit that performs computations
  - Shows "EXECUTING" when processing an instruction

- **Cache Hierarchy** (right):
  - L1 Cache: Fastest, smallest cache
  - L2 Cache: Larger but slower than L1
  - Main Memory: Largest but slowest

### Example Instructions

The visualization comes with a sample instruction set:
```assembly
LOAD R1, [0x100]      # Load value from memory address 0x100 into R1
ADD R2, R1, #5        # Add 5 to R1 and store in R2
STORE R2, [0x104]     # Store R2 value to memory address 0x104
LOAD R3, [0x108]      # Load value from memory address 0x108 into R3
MUL R4, R2, R3        # Multiply R2 and R3, store in R4
```

## Customization

You can modify the visualization by editing `cpu_architecture_viz.py`:

### Change Instructions
Edit the `self.instructions` list in the `__init__` method:
```python
self.instructions = [
    "YOUR INSTRUCTION 1",
    "YOUR INSTRUCTION 2",
    # Add more instructions
]
```

### Adjust Execution Speed
Change the rate in the `auto_run` method:
```python
rate(2)  # Change 2 to desired cycles per second
```

### Modify Colors
Edit color definitions in the `__init__` method:
```python
self.PIPELINE_COLOR = vector(0.2, 0.5, 0.8)  # R, G, B (0-1 range)
self.CACHE_COLOR = vector(0.8, 0.6, 0.2)
# etc.
```

## Architecture Details

### Pipeline Operation

1. **Cycle 1**: Instruction 1 enters Fetch stage
2. **Cycle 2**: Instruction 1 moves to Decode, Instruction 2 enters Fetch
3. **Cycle 3**: Instructions flow through pipeline
4. **Cycle 5+**: Pipeline is fully occupied (5 instructions in different stages)

### Pipelining Benefits

- **Throughput**: One instruction completes per cycle (after pipeline is full)
- **Latency**: Each instruction takes 5 cycles to complete
- **Efficiency**: Multiple instructions processed simultaneously

## Technical Notes

- Built with VPython (Visual Python) for 3D graphics
- Runs in web browser using GlowScript technology
- Real-time 3D rendering at 30 FPS
- Interactive controls using VPython's button widgets

## Troubleshooting

**Visualization doesn't open:**
- Ensure VPython is installed correctly
- Check that your default browser supports WebGL
- Try using Chrome or Firefox

**Slow performance:**
- Close other browser tabs
- Reduce the auto-run speed
- Check system resources

**Installation issues:**
- Make sure Python 3.7+ is installed
- Try upgrading pip: `pip install --upgrade pip`
- Install VPython directly: `pip install vpython`

## Future Enhancements

Potential additions:
- Branch prediction visualization
- Hazard detection and forwarding
- Out-of-order execution
- Multi-core architecture
- Custom instruction editor
- Performance metrics (CPI, IPC)
- Cache hit/miss statistics

## License

This visualization is provided as-is for educational purposes.
