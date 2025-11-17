# Dapr Placement - Consistent Hashing with Bounded Loads

**File:** `index.py`

An interactive visualization of Dapr's actor placement service, demonstrating:

- **Consistent hashing** with virtual nodes for even distribution
- **Bounded loads** to prevent capacity overload
- **3-phase commit protocol** (Lock → Update → Unlock) for safe cluster updates
- **Crash handling** during distributed updates

## Controls

- **Add Host** - Add a new host/pod to the ring
- **Remove Host** - Remove the last host from the ring
- **Start 3-Phase Commit** - Simulate Lock → Update → Unlock sequence
- **Crash During Lock** - Simulate host failure during lock phase

## What You'll See

- A circular ring representing the hash space
- Colored spheres (hosts) positioned on the ring based on their hash
- Small spheres (actors) that animate to their assigned hosts
- Load bars showing relative host utilization
- Lock indicators showing host state during commits

## Configuration

Adjustable constants at the top of `index.py`:

- `VIRTUAL_NODES` - Number of virtual nodes per host (default: 50)
- `INITIAL_HOSTS` - Starting number of hosts (default: 5)
- `ACTOR_COUNT` - Number of actors to visualize (default: 80)
- `MAX_CAPACITY` - Soft capacity limit per host (default: 20)
- `CAPACITY_MARGIN` - Multiplier for allowed overload (default: 1.2)

## How It Works

### Consistent Hashing

Each host creates multiple virtual nodes on a hash ring. Actors are assigned to the nearest host clockwise on the ring. This ensures even distribution and minimal reassignment when hosts are added or removed.

### Bounded Loads

To prevent hotspots, the algorithm enforces a capacity limit. If the nearest host is at capacity, the actor is assigned to the next available host with space.

### 3-Phase Commit

When the cluster topology changes:

1. **Lock** - All sidecars lock and finish in-flight requests
2. **Update** - New hash table is distributed and actors reassigned
3. **Unlock** - Sidecars unlock and process new requests

This ensures zero downtime and consistent state across the cluster.

## Resources

- [Dapr Placement Service](https://docs.dapr.io/concepts/dapr-services/placement/)
- [Consistent Hashing Paper](https://en.wikipedia.org/wiki/Consistent_hashing)
- [Bounded Loads Algorithm](https://arxiv.org/abs/1608.01350)
