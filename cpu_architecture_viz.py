"""
CPU Architecture Visualization with VPython
Displays a detailed interactive simulation of CPU pipeline stages, cache hierarchy,
and instruction execution flow.
"""

from vpython import *
import time

# Configuration
WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900

class CPUArchitecture:
    def __init__(self):
        # Scene setup
        scene.width = WINDOW_WIDTH
        scene.height = WINDOW_HEIGHT
        scene.title = "Interactive CPU Architecture Visualization"
        scene.caption = """
        <b>CPU Pipeline Simulator</b>
        Controls:
        - Click 'Next Cycle' to advance one clock cycle
        - Click 'Run' to auto-advance
        - Click 'Reset' to restart
        """

        # Colors
        self.PIPELINE_COLOR = vector(0.2, 0.5, 0.8)
        self.CACHE_COLOR = vector(0.8, 0.6, 0.2)
        self.REGISTER_COLOR = vector(0.3, 0.7, 0.3)
        self.MEMORY_COLOR = vector(0.7, 0.3, 0.3)
        self.DATA_COLOR = vector(1, 1, 0)
        self.ACTIVE_COLOR = vector(0, 1, 0)

        # State
        self.cycle = 0
        self.running = False
        self.instructions = [
            "LOAD R1, [0x100]",
            "ADD R2, R1, #5",
            "STORE R2, [0x104]",
            "LOAD R3, [0x108]",
            "MUL R4, R2, R3"
        ]
        self.instruction_index = 0

        # Pipeline state tracking
        self.pipeline_state = {
            'fetch': None,
            'decode': None,
            'execute': None,
            'memory': None,
            'writeback': None
        }

        # Create UI buttons
        self.setup_ui()

        # Build the architecture
        self.build_architecture()

    def setup_ui(self):
        """Setup interactive UI buttons"""
        scene.append_to_caption('\n\n')

        button(text="Next Cycle", bind=self.next_cycle)
        scene.append_to_caption('  ')
        button(text="Run/Pause", bind=self.toggle_run)
        scene.append_to_caption('  ')
        button(text="Reset", bind=self.reset)

        scene.append_to_caption('\n\n<div id="status">Cycle: 0 | Ready</div>')

    def build_architecture(self):
        """Build all CPU architecture components"""
        # Pipeline Stages (top section)
        self.build_pipeline_stages()

        # Registers (left middle)
        self.build_registers()

        # ALU (center middle)
        self.build_alu()

        # Cache Hierarchy (right section)
        self.build_cache_hierarchy()

        # Main Memory (bottom right)
        self.build_main_memory()

        # Control Unit (left top)
        self.build_control_unit()

        # Data paths
        self.build_data_paths()

        # Instruction display
        self.build_instruction_display()

    def build_pipeline_stages(self):
        """Create the 5-stage pipeline visualization"""
        self.pipeline_boxes = {}
        self.pipeline_labels = {}
        self.pipeline_data = {}

        stages = ['Fetch', 'Decode', 'Execute', 'Memory', 'Writeback']
        start_x = -15
        spacing = 6.5
        y_pos = 10

        for i, stage in enumerate(stages):
            x_pos = start_x + i * spacing

            # Pipeline stage box
            box_obj = box(
                pos=vector(x_pos, y_pos, 0),
                size=vector(6, 3, 1),
                color=self.PIPELINE_COLOR,
                opacity=0.7
            )

            # Stage label
            label_obj = label(
                pos=vector(x_pos, y_pos + 2, 0),
                text=stage,
                height=10,
                border=4,
                font='monospace'
            )

            # Data label (shows current instruction in stage)
            data_obj = label(
                pos=vector(x_pos, y_pos, 0),
                text='',
                height=8,
                color=self.DATA_COLOR,
                border=2,
                font='monospace',
                opacity=0
            )

            stage_key = stage.lower()
            self.pipeline_boxes[stage_key] = box_obj
            self.pipeline_labels[stage_key] = label_obj
            self.pipeline_data[stage_key] = data_obj

        # Add arrows between stages
        self.pipeline_arrows = []
        for i in range(len(stages) - 1):
            arrow_obj = arrow(
                pos=vector(start_x + i * spacing + 3, y_pos, 0),
                axis=vector(spacing - 6, 0, 0),
                shaftwidth=0.3,
                color=color.white,
                opacity=0.5
            )
            self.pipeline_arrows.append(arrow_obj)

    def build_registers(self):
        """Create register file visualization"""
        self.register_boxes = []
        self.register_labels = []

        x_pos = -15
        start_y = 3
        num_registers = 8

        # Register file container
        box(
            pos=vector(x_pos, start_y - 1.5, -1),
            size=vector(6, 10, 0.5),
            color=self.REGISTER_COLOR,
            opacity=0.3
        )

        label(
            pos=vector(x_pos, start_y + 4, 0),
            text='Registers',
            height=10,
            border=4,
            font='monospace'
        )

        for i in range(num_registers):
            y_pos = start_y - i * 1

            reg_box = box(
                pos=vector(x_pos, y_pos, 0),
                size=vector(5, 0.8, 0.5),
                color=self.REGISTER_COLOR,
                opacity=0.7
            )

            reg_label = label(
                pos=vector(x_pos, y_pos, 0),
                text=f'R{i}: 0x0000',
                height=8,
                border=2,
                font='monospace'
            )

            self.register_boxes.append(reg_box)
            self.register_labels.append(reg_label)

    def build_alu(self):
        """Create ALU visualization"""
        x_pos = -5
        y_pos = 0

        # ALU body (trapezoid-ish shape using pyramid)
        self.alu = pyramid(
            pos=vector(x_pos, y_pos, 0),
            size=vector(4, 6, 2),
            axis=vector(0, 1, 0),
            color=vector(0.5, 0.5, 0.8),
            opacity=0.8
        )

        self.alu_label = label(
            pos=vector(x_pos, y_pos, 0),
            text='ALU',
            height=12,
            border=4,
            font='monospace',
            box=False
        )

        self.alu_op_label = label(
            pos=vector(x_pos, y_pos - 2, 0),
            text='',
            height=8,
            color=self.DATA_COLOR,
            border=2,
            font='monospace',
            opacity=0
        )

    def build_cache_hierarchy(self):
        """Create cache hierarchy (L1, L2)"""
        self.cache_boxes = {}
        self.cache_labels = {}

        # L1 Cache
        l1_x, l1_y = 10, 5
        l1_box = box(
            pos=vector(l1_x, l1_y, 0),
            size=vector(6, 4, 1),
            color=self.CACHE_COLOR,
            opacity=0.7
        )
        l1_label = label(
            pos=vector(l1_x, l1_y + 2.5, 0),
            text='L1 Cache',
            height=10,
            border=4,
            font='monospace'
        )
        l1_info = label(
            pos=vector(l1_x, l1_y, 0),
            text='32 KB\nHits: 0\nMisses: 0',
            height=8,
            border=2,
            font='monospace'
        )

        self.cache_boxes['l1'] = l1_box
        self.cache_labels['l1'] = l1_info

        # L2 Cache
        l2_x, l2_y = 10, -1
        l2_box = box(
            pos=vector(l2_x, l2_y, 0),
            size=vector(7, 4, 1),
            color=self.CACHE_COLOR,
            opacity=0.6
        )
        l2_label = label(
            pos=vector(l2_x, l2_y + 2.5, 0),
            text='L2 Cache',
            height=10,
            border=4,
            font='monospace'
        )
        l2_info = label(
            pos=vector(l2_x, l2_y, 0),
            text='256 KB\nHits: 0\nMisses: 0',
            height=8,
            border=2,
            font='monospace'
        )

        self.cache_boxes['l2'] = l2_box
        self.cache_labels['l2'] = l2_info

        # Arrow from L1 to L2
        arrow(
            pos=vector(l1_x, l1_y - 2.5, 0),
            axis=vector(0, l2_y - l1_y + 4.5, 0),
            shaftwidth=0.3,
            color=color.white,
            opacity=0.5
        )

    def build_main_memory(self):
        """Create main memory visualization"""
        x_pos = 10
        y_pos = -7

        self.memory_box = box(
            pos=vector(x_pos, y_pos, 0),
            size=vector(8, 4, 1),
            color=self.MEMORY_COLOR,
            opacity=0.7
        )

        label(
            pos=vector(x_pos, y_pos + 2.5, 0),
            text='Main Memory',
            height=10,
            border=4,
            font='monospace'
        )

        self.memory_info = label(
            pos=vector(x_pos, y_pos, 0),
            text='DDR4 RAM\nAccesses: 0',
            height=8,
            border=2,
            font='monospace'
        )

        # Arrow from L2 to Memory
        arrow(
            pos=vector(10, -3.5, 0),
            axis=vector(0, -2.5, 0),
            shaftwidth=0.3,
            color=color.white,
            opacity=0.5
        )

    def build_control_unit(self):
        """Create control unit visualization"""
        x_pos = -15
        y_pos = 15

        self.control_box = box(
            pos=vector(x_pos, y_pos, 0),
            size=vector(6, 3, 1),
            color=vector(0.6, 0.3, 0.6),
            opacity=0.7
        )

        label(
            pos=vector(x_pos, y_pos + 2, 0),
            text='Control Unit',
            height=10,
            border=4,
            font='monospace'
        )

        self.control_label = label(
            pos=vector(x_pos, y_pos, 0),
            text='PC: 0x1000',
            height=8,
            border=2,
            font='monospace'
        )

    def build_data_paths(self):
        """Create data path connections"""
        # These are visual connections between components
        self.data_path_arrows = []

        # Register to ALU
        arrow(
            pos=vector(-12, 2, 0),
            axis=vector(5, -1, 0),
            shaftwidth=0.2,
            color=color.cyan,
            opacity=0.3
        )

        # ALU to Memory stage
        arrow(
            pos=vector(-3, 0, 0),
            axis=vector(5, 8, 0),
            shaftwidth=0.2,
            color=color.cyan,
            opacity=0.3
        )

        # Cache to Pipeline
        arrow(
            pos=vector(7, 5, 0),
            axis=vector(-5, 5, 0),
            shaftwidth=0.2,
            color=color.cyan,
            opacity=0.3
        )

    def build_instruction_display(self):
        """Create instruction queue display"""
        x_pos = 5
        y_pos = 15

        box(
            pos=vector(x_pos, y_pos, -1),
            size=vector(10, 3, 0.5),
            color=vector(0.4, 0.4, 0.4),
            opacity=0.3
        )

        label(
            pos=vector(x_pos, y_pos + 2, 0),
            text='Instruction Queue',
            height=10,
            border=4,
            font='monospace'
        )

        self.instruction_display = label(
            pos=vector(x_pos, y_pos, 0),
            text=self.get_instruction_queue_text(),
            height=8,
            border=2,
            font='monospace'
        )

    def get_instruction_queue_text(self):
        """Get text for instruction queue"""
        lines = []
        for i in range(min(3, len(self.instructions))):
            idx = (self.instruction_index + i) % len(self.instructions)
            prefix = '>' if i == 0 else ' '
            lines.append(f'{prefix} {self.instructions[idx]}')
        return '\n'.join(lines)

    def next_cycle(self):
        """Advance one clock cycle"""
        self.cycle += 1

        # Update pipeline state (move instructions through stages)
        self.advance_pipeline()

        # Update visualizations
        self.update_pipeline_display()
        self.update_control_unit()
        self.update_instruction_display()

        # Update status
        scene.caption = scene.caption.split('<div id="status">')[0] + \
                       f'<div id="status">Cycle: {self.cycle} | ' + \
                       f'Processing: {self.instructions[self.instruction_index % len(self.instructions)]}</div>'

    def advance_pipeline(self):
        """Move instructions through pipeline stages"""
        # Move instructions through pipeline (right to left to avoid overwriting)
        self.pipeline_state['writeback'] = self.pipeline_state['memory']
        self.pipeline_state['memory'] = self.pipeline_state['execute']
        self.pipeline_state['execute'] = self.pipeline_state['decode']
        self.pipeline_state['decode'] = self.pipeline_state['fetch']

        # Fetch new instruction
        if self.instruction_index < len(self.instructions) or self.cycle % 5 == 1:
            self.pipeline_state['fetch'] = self.instructions[self.instruction_index % len(self.instructions)]
            self.instruction_index += 1
        else:
            self.pipeline_state['fetch'] = None

    def update_pipeline_display(self):
        """Update pipeline stage visualizations"""
        for stage_key, instruction in self.pipeline_state.items():
            box_obj = self.pipeline_boxes[stage_key]
            data_obj = self.pipeline_data[stage_key]

            if instruction:
                # Highlight active stage
                box_obj.color = self.ACTIVE_COLOR
                box_obj.opacity = 0.9

                # Show instruction
                data_obj.text = instruction[:15] + '...' if len(instruction) > 15 else instruction
                data_obj.opacity = 1

                # Animate ALU for execute stage
                if stage_key == 'execute':
                    self.alu_op_label.text = 'EXECUTING'
                    self.alu_op_label.opacity = 1
                    self.alu.color = self.ACTIVE_COLOR
            else:
                # Dim inactive stage
                box_obj.color = self.PIPELINE_COLOR
                box_obj.opacity = 0.5
                data_obj.opacity = 0

                if stage_key == 'execute':
                    self.alu_op_label.opacity = 0
                    self.alu.color = vector(0.5, 0.5, 0.8)

    def update_control_unit(self):
        """Update control unit display"""
        pc = 0x1000 + (self.cycle * 4)
        self.control_label.text = f'PC: 0x{pc:04X}'

    def update_instruction_display(self):
        """Update instruction queue display"""
        self.instruction_display.text = self.get_instruction_queue_text()

    def toggle_run(self):
        """Toggle auto-run mode"""
        self.running = not self.running

        if self.running:
            self.auto_run()

    def auto_run(self):
        """Auto-advance cycles"""
        if self.running:
            self.next_cycle()
            rate(2)  # 2 cycles per second
            self.auto_run()

    def reset(self):
        """Reset the simulation"""
        self.running = False
        self.cycle = 0
        self.instruction_index = 0

        # Clear pipeline state
        for key in self.pipeline_state:
            self.pipeline_state[key] = None

        # Reset displays
        self.update_pipeline_display()
        self.update_control_unit()
        self.update_instruction_display()

        scene.caption = scene.caption.split('<div id="status">')[0] + \
                       '<div id="status">Cycle: 0 | Ready (Reset)</div>'

# Create and run the visualization
if __name__ == "__main__":
    cpu = CPUArchitecture()

    # Keep the visualization running
    while True:
        rate(30)  # 30 FPS for smooth visualization
