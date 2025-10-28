import sys
import re
import argparse
from html import unescape

def read_html(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def text_from_html(html):
    text = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.S|re.I)
    text = re.sub(r'<style.*?>.*?</style>', '', text, flags=re.S|re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_cpu_percent(text):
    m = re.search(r'(?i)(?:average\s+cpu\s+utilization|processor utilization).*?(\d{1,3})\s*%?', text)
    if m:
        try:
            val = int(m.group(1))
            return max(0, min(100, val))
        except:
            pass
    m2 = re.search(r'(?i)cpu[^\d]{0,8}(\d{1,3})\s*%|\b(\d{1,3})\s*%\s+cpu\b', text)
    if m2:
        for g in m2.groups():
            if g:
                return max(0, min(100, int(g)))
    return None

def count_preventing_devices(text):
    hits = re.findall(r'(?i)(?:not entering suspend|prevent.*sleep|usb suspend|preventing sleep|request.*prevent)', text)
    return len(hits)

def display_on_hint(text):
    return bool(re.search(r'(?i)(display timeout|monitor timeout|display is on|screen timeout)', text))

def timer_resolution_requests(text):
    return bool(re.search(r'(?i)timer resolution|high resolution timer|high resolution', text))

def estimate_power(cpu_pct, device_count, display_on, timer_req,
                   peak_watts, idle_watts, device_watts_each, display_watts_extra, timer_watts_extra):
    # CPU contribution (linear model)
    cpu_component = 0.0
    if cpu_pct is not None:
        cpu_component = (cpu_pct / 100.0) * (peak_watts - idle_watts)
    # devices
    devices_component = device_count * device_watts_each
    display_component = display_watts_extra if display_on else 0.0
    timer_component = timer_watts_extra if timer_req else 0.0
    p_avg = idle_watts + cpu_component + devices_component + display_component + timer_component
    # sanity: not exceed peak hard maximum
    p_avg = min(p_avg, max(peak_watts, p_avg))
    return p_avg

def main():
    parser = argparse.ArgumentParser(description="Estimate energy from powercfg /energy HTML report")
    parser.add_argument('html', help='path to energy-report.html')
    parser.add_argument('--seconds', type=float, default=60.0, help='duration to estimate in seconds (default 60)')
    parser.add_argument('--peak', type=float, default=400.0, help='assumed host/physical peak power (Watts). Default 400 W')
    parser.add_argument('--idle', type=float, default=120.0, help='assumed idle power (Watts). Default 120 W')
    parser.add_argument('--device-w', type=float, default=2.0, help='watts consumed per device preventing suspend (default 2W)')
    parser.add_argument('--display-w', type=float, default=6.0, help='extra watts if display is on (default 6W)')
    parser.add_argument('--timer-w', type=float, default=4.0, help='extra watts if high-res timers active (default 4W)')
    args = parser.parse_args()

    html = read_html(args.html)
    text = text_from_html(html)

    cpu_pct = extract_cpu_percent(text)
    devices = count_preventing_devices(text)
    display_on = display_on_hint(text)
    timer_req = timer_resolution_requests(text)

    p_avg = estimate_power(cpu_pct, devices, display_on, timer_req,
                           args.peak, args.idle, args.device_w, args.display_w, args.timer_w)

    hours = args.seconds / 3600.0
    energy_kwh = p_avg * hours / 1000.0

    # Print results + what was found
    print("=== Powercfg energy-report estimate ===")
    print(f"Source file: {args.html}")
    print(f"Parsed CPU% (if any): {cpu_pct if cpu_pct is not None else 'not found'}")
    print(f"Devices preventing suspend (detected): {devices}")
    print(f"Display-on hint detected: {display_on}")
    print(f"High-resolution timer hint detected: {timer_req}")
    print()
    print("Assumptions / coefficients:")
    print(f"  peak_watts = {args.peak} W")
    print(f"  idle_watts = {args.idle} W")
    print(f"  per-device = {args.device_w} W")
    print(f"  display extra = {args.display_w} W")
    print(f"  timer extra = {args.timer_w} W")
    print(f"Duration = {args.seconds} seconds")
    print()
    print(f"Estimated average power: {p_avg:.1f} W")
    print(f"Estimated energy: {energy_kwh:.3f} kWh ({energy_kwh*1000:.1f} Wh, {energy_kwh*3.6e6:.0f} J)")
    print("=======================================")

if __name__ == '__main__':
    main()