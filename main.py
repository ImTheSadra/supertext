#!/usr/bin/env python3
import math
import curses
import sys
import random
import time

def supershape(theta, m, n1, n2, n3, a=1.0, b=1.0):
    cos_part = math.pow(abs((1.0 / a) * math.cos(theta * m / 4.0)), n1)
    sin_part = math.pow(abs((1.0 / b) * math.sin(theta * m / 4.0)), n2)
    r = math.pow(cos_part + sin_part, -1.0 / n3)
    return r if r else 0.0

def generate_supershape_surface(theta_vals, phi_vals, params, time, mode, rot_y):
    m0 = params['m']
    n1_0 = params['n1']
    n2_0 = params['n2']
    n3_0 = params['n3']
    a0 = params['a']
    b0 = params['b']
    scale = params['scale']
    height_scale = params['height']

    wave1 = math.sin(time * 0.3) * 0.8
    wave2 = math.cos(time * 0.2) * 0.6
    wave3 = math.sin(time * 0.25 + 1.0) * 0.5

    m = max(0.5, m0 + wave1 * 0.6)
    n1 = max(0.1, n1_0 + wave2 * 0.4)
    n2 = max(0.1, n2_0 + wave3 * 0.4)
    n3 = max(0.1, n3_0 + math.sin(time * 0.15) * 0.3)
    a = max(0.1, a0 + math.sin(time * 0.1) * 0.1)
    b = max(0.1, b0 + math.cos(time * 0.12) * 0.1)

    points = []
    for theta in theta_vals:
        r = supershape(theta, m, n1, n2, n3, a, b)
        y_base = (theta / (2.0 * math.pi) - 0.5) * 2.0 * height_scale * 1.2
        for phi in phi_vals:
            x = r * math.cos(phi) * scale
            y = y_base
            z = r * math.sin(phi) * scale

            if mode == 'liquid':
                amp = 0.15 + 0.1 * math.sin(time * 0.5)
                wave = math.sin(theta * 5 + time * 1.5) * math.cos(phi * 3 + time * 1.2) * amp
                factor = 1.0 + wave
                x *= factor
                z *= factor
                y *= (1.0 + 0.1 * math.sin(theta * 4 + time * 1.8))

            elif mode == 'explosion':
                pulse = 0.5 + 0.5 * math.sin(time * 0.8)
                exp_amp = 0.8 + 0.6 * math.sin(time * 1.2)
                radius = math.sqrt(x*x + y*y + z*z) or 0.001
                noise = math.sin(theta * 7 + time * 3) * math.cos(phi * 5 + time * 2.5)
                factor = 1.0 + 0.4 * noise * pulse
                s = 1.0 + exp_amp * 0.5 * (0.5 + 0.5 * math.sin(theta * 3 + time * 2))
                x *= factor * s
                y *= factor * s
                z *= factor * s

            elif mode == 'pulse':
                pulse_scale = 0.7 + 0.3 * math.sin(time * 1.2)
                x *= pulse_scale
                y *= pulse_scale
                z *= pulse_scale

            if rot_y != 0:
                c = math.cos(rot_y)
                s = math.sin(rot_y)
                x, z = x * c - z * s, x * s + z * c

            points.append((x, y, z))

    return points

def project_points(points, screen_width, screen_height, cx, cy, scale_2d):
    projected = []
    for (x, y, z) in points:
        px = int(cx + x * scale_2d)
        py = int(cy - y * scale_2d)
        if 0 <= px < screen_width and 0 <= py < screen_height:
            projected.append((px, py, z))
        else:
            projected.append(None)
    return projected

def draw_shape(window, projected_points):
    window.clear()
    for proj in projected_points:
        if proj is None:
            continue
        px, py, z = proj
        if z > 0:
            try:
                window.addch(py, px, '#')
            except curses.error:
                pass

def main(stdscr):
    try:
        idx = sys.argv.index("-m") + 1
        m_val = float(sys.argv[idx]) if idx < len(sys.argv) else random.uniform(0.5, 10)
    except:
        m_val = random.uniform(0.5, 10)

    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(50)

    height, width = stdscr.getmaxyx()
    shape_height = height - 2
    shape_width = width

    params = {
        'm': m_val,
        'n1': 1.0,
        'n2': 1.0,
        'n3': 1.0,
        'a': 1.0,
        'b': 1.0,
        'scale': 0.8 * min(shape_width, shape_height) / 40,
        'height': 1.0,
    }

    mode = 'morph'
    paused = False
    rot_y = 0.0
    speed = 1.0
    time_accum = 0.0

    num_theta = 60
    num_phi = 40
    theta_vals = [i / num_theta * 2 * math.pi for i in range(num_theta)]
    phi_vals = [j / num_phi * 2 * math.pi for j in range(num_phi)]

    clock = time.time()
    while True:
        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('r') or key == ord('R'):
            params['m'] = random.uniform(0.5, 20)
            params['n1'] = random.uniform(0.1, 10)
            params['n2'] = random.uniform(0.1, 10)
            params['n3'] = random.uniform(0.1, 10)
            params['a'] = random.uniform(0.1, 5)
            params['b'] = random.uniform(0.1, 5)
            params['scale'] = 0.8 * min(shape_width, shape_height) / 40 * random.uniform(0.7, 1.3)
        elif key == ord('m'):
            modes = ['morph', 'liquid', 'explosion', 'pulse']
            idx = (modes.index(mode) + 1) % len(modes)
            mode = modes[idx]
        elif key == ord('+') or key == ord('='):
            speed = min(2.0, speed + 0.1)
        elif key == ord('-'):
            speed = max(0.1, speed - 0.1)

        if not paused:
            now = time.time()
            dt = (now - clock) * speed
            clock = now
            time_accum += dt
            rot_y += dt * 0.5

        points3d = generate_supershape_surface(
            theta_vals, phi_vals, params, time_accum, mode, rot_y
        )

        cx = shape_width // 2
        cy = shape_height // 2
        screen_scale = min(shape_width, shape_height) * 0.35
        projected = project_points(points3d, shape_width, shape_height, cx, cy, screen_scale)

        draw_shape(stdscr, projected)

        info = f"Mode: {mode}  |  m:{params['m']:.1f} n1:{params['n1']:.1f} n2:{params['n2']:.1f} n3:{params['n3']:.1f}  |  Speed:{speed:.1f}  |  [space] pause  [r] random  [m] mode  [+/-] speed  [q] quit"
        try:
            stdscr.addstr(shape_height, 0, info[:width-1])
        except curses.error:
            pass

        stdscr.refresh()
        time.sleep(0.02)

if __name__ == "__main__":
    curses.wrapper(main)