import time
import math
import threading
from dronekit import connect, VehicleMode, LocationGlobalRelative

# ============================================================
# CONNECTION
# ============================================================

print("Connecting to Mission Planner SITL...")
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True)
print(f"Connected! Mode: {vehicle.mode.name}")

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def switch_mode(mode_name, timeout=10):
    vehicle.mode = VehicleMode(mode_name)
    start = time.time()
    while vehicle.mode.name != mode_name:
        if time.time() - start > timeout:
            print(f"[WARN] Timeout switching to {mode_name}")
            return False
        time.sleep(0.5)
    print(f"[MODE] {mode_name} active")
    return True


def arm_and_takeoff(target_altitude):
    print("[INFO] Waiting for vehicle to be armable...")
    while not vehicle.is_armable:
        time.sleep(1)

    switch_mode("GUIDED")

    print("[INFO] Arming...")
    vehicle.armed = True
    while not vehicle.armed:
        time.sleep(1)

    print(f"[INFO] Taking off to {target_altitude} meters")
    vehicle.simple_takeoff(target_altitude)

    while True:
        alt = vehicle.location.global_relative_frame.alt
        print(f"  Altitude: {alt:.2f} m")
        if alt >= target_altitude * 0.95:
            print("[INFO] Target altitude reached")
            break
        time.sleep(1)


def get_offset_location(original, d_north, d_east, alt):
    earth_radius = 6378137.0
    d_lat = d_north / earth_radius
    d_lon = d_east / (earth_radius * math.cos(math.radians(original.lat)))

    new_lat = original.lat + math.degrees(d_lat)
    new_lon = original.lon + math.degrees(d_lon)

    return LocationGlobalRelative(new_lat, new_lon, alt)


def get_distance(loc1, loc2):
    d_lat = loc2.lat - loc1.lat
    d_lon = loc2.lon - loc1.lon
    return math.sqrt(d_lat**2 + d_lon**2) * 1.113195e5


def goto_offset(d_north, d_east, altitude, label, hover_time=0, threshold=1.5):
    current = vehicle.location.global_relative_frame
    target = get_offset_location(current, d_north, d_east, altitude)

    print(f"\n[NAV] Going to {label}")
    vehicle.simple_goto(target)

    while True:
        dist = get_distance(vehicle.location.global_relative_frame, target)
        alt = vehicle.location.global_relative_frame.alt
        print(f"  {label} | Distance: {dist:.1f} m | Alt: {alt:.2f} m")
        if dist <= threshold:
            print(f"[ARRIVED] {label}")
            break
        time.sleep(1)

    if hover_time > 0:
        print(f"[LOITER] Hovering {hover_time}s at {label}")
        time.sleep(hover_time)

# ============================================================
# TELEMETRY THREAD
# ============================================================

stop_event = threading.Event()

def telemetry_worker():
    while not stop_event.is_set():
        alt = vehicle.location.global_relative_frame.alt
        batt = vehicle.battery
        if batt:
            print(f"[TELEMETRY] Alt={alt:.2f}m | Battery={batt.voltage:.2f}V")
        stop_event.wait(2)

def attitude_callback(self, attr_name, value):
    print(f"[ATTITUDE] Roll={value.roll:.2f} Pitch={value.pitch:.2f} Yaw={value.yaw:.2f}")

vehicle.add_attribute_listener('attitude', attitude_callback)

t = threading.Thread(target=telemetry_worker, daemon=True)
t.start()

# ============================================================
# MAIN MISSION
# ============================================================

print("\n=== START CREATIVE MISSION ===")

# 1️⃣ ARM + TAKEOFF
arm_and_takeoff(10)

# 2️⃣ MAJU 15m
goto_offset(15, 0, 10, "Forward Point", hover_time=3)

# ============================================================
# 3️⃣ POLA SEGI LIMA DENGAN VARIASI ALTITUDE
# ============================================================

print("\n=== PENTAGON PATTERN ===")

RADIUS = 20
angles = [72 * i for i in range(5)]
altitudes = [12, 15, 18, 14, 10]  # variasi altitude tiap titik

for i, angle in enumerate(angles):
    rad = math.radians(angle)
    d_north = RADIUS * math.cos(rad)
    d_east = RADIUS * math.sin(rad)
    altitude = altitudes[i]

    goto_offset(
        d_north,
        d_east,
        altitude,
        label=f"Pentagon WP{i+1}",
        hover_time=2
    )

# ============================================================
# 4️⃣ MUNDUR 15m
# ============================================================

goto_offset(-15, 0, 10, "Backward Point", hover_time=2)

# ============================================================
# 5️⃣ LANDING
# ============================================================

print("\n=== LANDING ===")
switch_mode("LAND")

while vehicle.location.global_relative_frame.alt > 0.2:
    print(f"  Descending... {vehicle.location.global_relative_frame.alt:.2f} m")
    time.sleep(1)

print("[MISSION COMPLETE]")

stop_event.set()
t.join(timeout=5)

vehicle.remove_attribute_listener('attitude', attitude_callback)
vehicle.close()

print("Vehicle closed safely.")