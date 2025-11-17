# dapr_placement_viz.py
# VPython visualization for Dapr placement: consistent hashing with bounded loads + 3-phase commit
#
# Save & run with: pip install vpython
# Then run in a Jupyter-like environment that supports VPython, or run `python -m vpython dapr_placement_viz.py`
#
# Controls: Use the buttons that appear in the VPython scene.
# - Add Host: add a new host/pod to the ring
# - Remove Host: remove the last host from the ring
# - Start 3-Phase Commit: simulate Lock -> Update -> Unlock and reassign actors
# - Crash During Lock (simulate): begin 3PC and remove a host mid-lock to show crash handling

from vpython import *
import hashlib
import random
import math
import time
from collections import defaultdict, deque

# ---------------------------- Configuration ----------------------------
VIRTUAL_NODES = 50         # virtual nodes per host (makes ring smoother)
INITIAL_HOSTS = 5
ACTOR_COUNT = 80           # number of actor IDs to visualize
RING_RADIUS = 6
HOST_NODE_RADIUS = 0.4
ACTOR_SPHERE_RADIUS = 0.06
MAX_CAPACITY = 20          # soft capacity used by bounded loads
CAPACITY_MARGIN = 1.2      # multiplier: allowed load = MAX_CAPACITY * CAPACITY_MARGIN
ANIMATION_TIMESTEP = 0.02

# ---------------------------- Utility functions ----------------------------

def hash_to_pos(key: str) -> float:
    """Hash a string to a float in [0,1)."""
    h = hashlib.md5(key.encode('utf-8')).hexdigest()
    val = int(h[:16],16)
    return (val % (2**53)) / float(2**53)

def angle_from_pos(pos: float) -> float:
    return pos * 2 * math.pi

def polar_to_cartesian(angle: float, radius: float):
    return vector(radius*math.cos(angle), radius*math.sin(angle), 0)

# ---------------------------- Data structures ----------------------------

class Host:
    def __init__(self, host_id: str, color=None):
        self.id = host_id
        self.color = color if color else vector(random.random(), random.random(), random.random())
        self.virtual_nodes = []  # list of ring positions (floats)
        self.sphere = None
        self.label = None
        self.load = 0  # number of actors assigned
        self.actor_ids = set()
        self.locked = False  # for three-phase commit
        self.alive = True

    def __repr__(self):
        return f"Host({self.id}, load={self.load}, alive={self.alive})"

class Actor:
    def __init__(self, actor_id: str):
        self.id = actor_id
        self.pos = hash_to_pos(actor_id)
        self.sphere = None
        self.assigned_host = None  # host id

# ---------------------------- Ring and placement ----------------------------

class PlacementRing:
    def __init__(self):
        self.hosts = {}  # host_id -> Host
        self.virtual_map = []  # list of (pos, host_id) sorted by pos
        self.actors = []  # list of Actor
        self.sorted_positions = []

    def add_host(self, host: Host):
        self.hosts[host.id] = host
        host.virtual_nodes = []
        for i in range(VIRTUAL_NODES):
            pos = hash_to_pos(f"{host.id}#vn{i}")
            host.virtual_nodes.append(pos)
            self.virtual_map.append((pos, host.id))
        self.virtual_map.sort(key=lambda x: x[0])
        self.sorted_positions = [p for p,_ in self.virtual_map]

    def remove_host(self, host_id: str):
        if host_id not in self.hosts: return
        host = self.hosts.pop(host_id)
        self.virtual_map = [(p,hid) for (p,hid) in self.virtual_map if hid!=host_id]
        self.virtual_map.sort(key=lambda x: x[0])
        host.alive = False
        self.sorted_positions = [p for p,_ in self.virtual_map]

    def find_host_for_actor(self, actor: Actor):
        if not self.virtual_map:
            return None
        pos = actor.pos
        import bisect
        idx = bisect.bisect_left(self.sorted_positions, pos)
        if idx == len(self.sorted_positions):
            idx = 0
        candidate_host_id = self.virtual_map[idx][1]
        unique_hosts = []
        visited = set()
        i = idx
        while len(unique_hosts) < len(self.hosts):
            hid = self.virtual_map[i % len(self.virtual_map)][1]
            if hid not in visited and self.hosts[hid].alive:
                unique_hosts.append(hid)
                visited.add(hid)
            i += 1
        allowed = MAX_CAPACITY * CAPACITY_MARGIN
        for hid in unique_hosts:
            if self.hosts[hid].load < allowed:
                return hid
        return candidate_host_id

    def assign_actors(self):
        for h in self.hosts.values():
            h.load = 0
            h.actor_ids.clear()
        for actor in self.actors:
            hid = self.find_host_for_actor(actor)
            if hid is None:
                actor.assigned_host = None
            else:
                actor.assigned_host = hid
                self.hosts[hid].load += 1
                self.hosts[hid].actor_ids.add(actor.id)

    def add_actor(self, actor: Actor):
        self.actors.append(actor)

# ---------------------------- Visual elements ----------------------------

scene.title = "Dapr Placement - Consistent Hashing with Bounded Loads\n"
scene.width = 1000
scene.height = 700
scene.background = vector(0.95,0.95,0.97)
scene.center = vector(0,0,0)
scene.autoscale = False

# draw base ring
ring_circle = curve(color=color.gray(0.7), radius=0.01)
for t in range(361):
    a = math.radians(t)
    ring_circle.append(pos=vector(RING_RADIUS*math.cos(a), RING_RADIUS*math.sin(a), 0))

# UI labels
info_label = wtext(text="")

placement = PlacementRing()

# initial hosts
def create_host(i):
    hid = f"host-{i}"
    h = Host(hid)
    placement.add_host(h)
    return h

for i in range(INITIAL_HOSTS):
    create_host(i+1)

# actors
for i in range(ACTOR_COUNT):
    aid = f"actor-{i+1}"
    placement.add_actor(Actor(aid))

placement.assign_actors()

# visual host builder
def build_visual_hosts():
    for child in scene.objects[:]:
        if hasattr(child, 'is_host') or hasattr(child, 'is_actor') or hasattr(child, 'is_bar'):
            child.visible = False
            del child
    for hid, host in placement.hosts.items():
        if not host.virtual_nodes:
            continue
        angles = [angle_from_pos(p) for p in host.virtual_nodes]
        sx = sum(math.cos(a) for a in angles)
        sy = sum(math.sin(a) for a in angles)
        avg_angle = math.atan2(sy, sx)
        pos = polar_to_cartesian(avg_angle, RING_RADIUS)
        s = sphere(pos=pos, radius=HOST_NODE_RADIUS, color=host.color, shininess=0.6)
        s.is_host = True
        host.sphere = s
        lbl = label(pos=pos + vector(0, -0.7, 0), text=hid, xoffset=0, yoffset=0, height=10, box=False)
        lbl.is_host = True
        host.label = lbl
        bar = box(pos=pos+vector(0,-1.2,0), size=vector(0.6,0.08,0.2), color=color.gray(0.4))
        bar.is_bar = True
        host.bar = bar
        lock_box = box(pos=pos+vector(0.55,0.15,0), size=vector(0.15,0.15,0.02), color=color.green)
        lock_box.is_host = True
        host.lock_box = lock_box

# actors
def build_actor_visuals():
    for child in scene.objects[:]:
        if hasattr(child, 'is_actor'):
            child.visible = False
            del child
    for actor in placement.actors:
        a_angle = angle_from_pos(actor.pos)
        pos = polar_to_cartesian(a_angle, RING_RADIUS - 1.1)
        s = sphere(pos=pos, radius=ACTOR_SPHERE_RADIUS, color=color.white, opacity=0.9)
        s.is_actor = True
        actor.sphere = s

def update_actor_mappings_animation(step=1.0):
    for actor in placement.actors:
        if actor.assigned_host and actor.assigned_host in placement.hosts:
            host = placement.hosts[actor.assigned_host]
            if host.sphere is not None and actor.sphere is not None:
                target = host.sphere.pos + vector(0,0.15,0)
                actor.sphere.pos = actor.sphere.pos*(1-step) + target*step
                actor.sphere.color = host.color
        else:
            if actor.sphere is not None:
                actor.sphere.pos = actor.sphere.pos*(1-step) + vector(0,0,0)*(step)
                actor.sphere.color = color.white

def update_host_bars():
    max_load = max([h.load for h in placement.hosts.values()] + [1])
    for h in placement.hosts.values():
        frac = min(h.load / float(MAX_CAPACITY), 2.0)
        size_y = 0.08 + frac*0.25
        h.bar.size = vector(0.6, size_y, 0.2)
        h.bar.pos = h.sphere.pos + vector(0, -1.2 + size_y/2 - 0.04, 0)
        if h.load > MAX_CAPACITY * CAPACITY_MARGIN:
            h.bar.color = color.red
        else:
            h.bar.color = color.green

def update_lock_boxes():
    for h in placement.hosts.values():
        if h.locked:
            h.lock_box.color = color.orange
        else:
            h.lock_box.color = color.green if h.alive else color.gray(0.5)

# ---------------------------- Simulation actions ----------------------------

host_counter = INITIAL_HOSTS

def add_host_action():
    global host_counter
    host_counter += 1
    hid = f"host-{host_counter}"
    h = Host(hid)
    placement.add_host(h)
    placement.assign_actors()
    build_visual_hosts()
    update_host_bars()
    info_label.text = f"Added {hid}."

def remove_host_action():
    if not placement.hosts:
        info_label.text = "No hosts to remove."
        return
    hid = sorted(placement.hosts.keys())[-1]
    placement.remove_host(hid)
    placement.assign_actors()
    build_visual_hosts()
    update_host_bars()
    info_label.text = f"Removed {hid}."

def crash_during_lock_action():
    if not placement.hosts:
        info_label.text = "No hosts."
        return
    hid = random.choice(list(placement.hosts.keys()))
    info_label.text = f"Starting 3PC and simulating crash of {hid} during lock phase."
    scene.waitfor('click')  # user click to proceed
    three_phase_commit(crash_host=hid)

def three_phase_commit(crash_host=None):
    # Phase 1: Lock
    for h in placement.hosts.values():
        h.locked = True
    build_visual_hosts()
    update_lock_boxes()
    info_label.text = "Phase 1 (Lock): Sidecars locked. Ongoing requests finish; new requests held."
    t0 = time.time()
    while time.time()-t0 < 1.0:
        rate(60)
        update_actor_mappings_animation(0.2)
    # simulate crash during lock
    if crash_host and crash_host in placement.hosts:
        placement.hosts[crash_host].alive = False
        placement.remove_host(crash_host)
        info_label.text = f"Host {crash_host} crashed and was removed from ring during lock."
        build_visual_hosts()
        update_host_bars()
        update_lock_boxes()
    # Phase 2: Update
    info_label.text = "Phase 2 (Update): Sending new hash table snapshot."
    placement.assign_actors()
    t0 = time.time()
    while time.time()-t0 < 1.2:
        rate(60)
        update_actor_mappings_animation(0.4)
        update_host_bars()
    # Phase 3: Unlock
    for h in placement.hosts.values():
        h.locked = False
    update_lock_boxes()
    info_label.text = "Phase 3 (Unlock): Sidecars unlocked; new requests proceed."
    t0 = time.time()
    while time.time()-t0 < 0.8:
        rate(60)
        update_actor_mappings_animation(0.3)
        update_host_bars()
    info_label.text = "Three-phase commit completed."

def start_commit_action():
    info_label.text = "Starting three-phase commit (Lock -> Update -> Unlock)."
    three_phase_commit(crash_host=None)

# ---------------------------- UI Controls ----------------------------

button_bindings = []

def make_button(text_label, action):
    btn = button(text=text_label, bind=lambda b: action())
    button_bindings.append(btn)
    return btn

make_button("Add Host", add_host_action)
make_button("Remove Host", remove_host_action)
make_button("Start 3-Phase Commit", start_commit_action)
make_button("Crash During Lock (simulate)", crash_during_lock_action)

info_label = wtext(text="Ready. Use the buttons above to interact.\n\n")
legend = wtext(text="\nLegend: Host nodes are colored. Small spheres inside ring are actor IDs.\nHost bars show relative load. Lock box: green=unlocked, orange=locked, gray=dead.\n\n")

# initial visuals build
build_visual_hosts()
build_actor_visuals()
update_actor_mappings_animation(step=1.0)
update_host_bars()
update_lock_boxes()

def main_loop():
    while True:
        rate(30)
        update_actor_mappings_animation(step=0.06)
        update_host_bars()
        update_lock_boxes()

main_loop()
