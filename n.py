import subprocess
import sys
import site
import hashlib

# Add user site-packages to path (for Cloud Shell)
user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.insert(0, user_site)
    print(f"[+] Added {user_site} to PATH")

# Auto-install dependencies
def install_dependencies():
    """Auto-install required packages with better error handling"""
    required_packages = ['seleniumbase', 'pyautogui', 'requests', 'numpy']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"[+] {package} already installed")
        except ImportError:
            print(f"[!] Installing {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user", "--quiet"])
                print(f"[+] {package} installed successfully")
                import importlib
                importlib.invalidate_caches()
            except subprocess.CalledProcessError as e:
                print(f"[-] Failed to install {package}: {e}")
                print(f"[!] Try manual install: pip install {package}")
                if package in ['seleniumbase', 'requests']:  # Critical packages
                    sys.exit(1)
    
    # Optional: Try install curl-cffi for TOP-TIER TLS fingerprinting
    try:
        __import__('curl_cffi')
        print(f"[+] curl_cffi available (TOP-TIER TLS fingerprinting enabled)")
    except ImportError:
        print(f"[!] curl_cffi not available - trying tls_client...")
        try:
            __import__('tls_client')
            print(f"[+] tls_client available (ELITE TLS fingerprinting enabled)")
        except ImportError:
            print(f"[!] Advanced TLS libraries not available (optional)")
            print(f"[!] Install with: pip install curl-cffi OR pip install tls-client")
            # Don't fail if not available

install_dependencies()

from seleniumbase import SB
import time
import random
import secrets
from datetime import datetime
import json
import os
import requests

# Import enhanced utilities
try:
    from bot_utils import (
        BotLogger, retry_with_backoff, InputValidator, 
        RateLimiter, ConfigManager, HealthChecker, CleanupManager
    )
    from firebase_manager import SecureFirebaseManager
    from cloudflared_manager import CloudflaredManager
    ENHANCED_UTILS_AVAILABLE = True
    print("[+] Enhanced utilities loaded")
except ImportError as e:
    print(f"[!] Enhanced utilities not available: {e}")
    print("[!] Running in legacy mode")
    ENHANCED_UTILS_AVAILABLE = False

# Import numpy for advanced behavioral ML
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("[!] numpy not available - using fallback for behavioral ML")

# TARGET_URL akan diambil dari Firebase berdasarkan bot_number
TARGET_URL = None  # Diisi saat runtime dari /bot{N}/links

# Global logger (will be initialized in main())
logger = None

# === TOP-TIER TLS FINGERPRINTING (2026) ===
class TopTierTLSSession:
    """
    TOP-TIER TECHNIQUE: Perfect TLS + HTTP/2 Fingerprint Spoofing
    Priority: curl-cffi > tls-client > requests
    Success rate: 50% → 90%+ untuk Akamai/DataDome/Kasada
    """
    def __init__(self):
        self.session_type = "standard"
        self.session = None
        
        # Try curl-cffi first (BEST - perfect Chrome impersonation)
        try:
            from curl_cffi import requests as curl_requests
            self.session = curl_requests.Session(impersonate="chrome131")
            self.session_type = "curl-cffi"
            log("[TLS] TOP-TIER: curl-cffi enabled (Perfect Chrome 131 TLS+HTTP/2)", "SUCCESS")
            return
        except ImportError:
            pass
        
        # Fallback to tls-client (GOOD - TLS only)
        try:
            import tls_client
            self.session = tls_client.Session(
                client_identifier="chrome_131",
                random_tls_extension_order=True
            )
            self.session_type = "tls-client"
            log("[TLS] ELITE: tls-client enabled (Chrome 131 TLS)", "SUCCESS")
            return
        except ImportError:
            pass
        
        # Final fallback to standard requests (BASIC)
        self.session = requests.Session()
        self.session_type = "standard"
        log("[TLS] BASIC: Using standard requests (Install curl-cffi for +15% success rate)", "INFO")
    
    def get(self, url, **kwargs):
        """HTTP GET with perfect TLS+HTTP/2 fingerprint"""
        try:
            return self.session.get(url, **kwargs)
        except Exception as e:
            log(f"[TLS] Request error: {str(e)[:50]}", "ERROR")
            # Fallback to standard requests
            return requests.get(url, **kwargs)
    
    def post(self, url, **kwargs):
        """HTTP POST with perfect TLS+HTTP/2 fingerprint"""
        try:
            return self.session.post(url, **kwargs)
        except Exception as e:
            log(f"[TLS] Request error: {str(e)[:50]}", "ERROR")
            return requests.post(url, **kwargs)
    
    def get_session_info(self):
        """Get current session type info"""
        return {
            "type": self.session_type,
            "tls_perfect": self.session_type in ["curl-cffi", "tls-client"],
            "http2_perfect": self.session_type == "curl-cffi"
        }

class AdvancedFingerprintRandomizer:
    """Dynamic realistic fingerprint generator - ribuan kombinasi unik yang realistis"""
    
    def __init__(self):
        # Generate session-unique seed untuk konsistensi dalam 1 session
        self.session_id = secrets.token_hex(16)
        self.session_seed = int(hashlib.sha256(self.session_id.encode()).hexdigest()[:8], 16)
        
        # === BUILDING BLOCKS untuk kombinasi dinamis ===
        
        # Chrome versions (realistic range) - UPDATED TO LATEST
        self.chrome_versions = ["128.0.0.0", "129.0.0.0", "130.0.0.0", "131.0.0.0", "132.0.0.0"]
        self.firefox_versions = ["128.0", "129.0", "130.0", "131.0", "132.0"]
        self.edge_versions = ["128.0.0.0", "129.0.0.0", "130.0.0.0", "131.0.0.0"]
        
        # Windows GPU pools (realistic combinations)
        self.windows_nvidia_gpus = [
            "NVIDIA GeForce RTX 4090", "NVIDIA GeForce RTX 4080", "NVIDIA GeForce RTX 4070",
            "NVIDIA GeForce RTX 3090", "NVIDIA GeForce RTX 3080", "NVIDIA GeForce RTX 3070", "NVIDIA GeForce RTX 3060",
            "NVIDIA GeForce RTX 2080 Ti", "NVIDIA GeForce RTX 2070", "NVIDIA GeForce RTX 2060",
            "NVIDIA GeForce GTX 1660 Ti", "NVIDIA GeForce GTX 1650", "NVIDIA GeForce GTX 1080", "NVIDIA GeForce GTX 1070"
        ]
        
        self.windows_amd_gpus = [
            "AMD Radeon RX 7900 XTX", "AMD Radeon RX 7900 XT", "AMD Radeon RX 7800 XT",
            "AMD Radeon RX 6900 XT", "AMD Radeon RX 6800 XT", "AMD Radeon RX 6700 XT", "AMD Radeon RX 6600 XT",
            "AMD Radeon RX 5700 XT", "AMD Radeon RX 5600 XT", "AMD Radeon RX 580", "AMD Radeon RX 570"
        ]
        
        self.windows_intel_gpus = [
            "Intel(R) UHD Graphics 770", "Intel(R) UHD Graphics 730", "Intel(R) UHD Graphics 630", "Intel(R) UHD Graphics 620",
            "Intel(R) Iris(R) Xe Graphics", "Intel(R) Iris(R) Plus Graphics", "Intel(R) HD Graphics 530"
        ]
        
        # Mac GPU pools
        self.mac_apple_gpus = ["Apple M3 Max", "Apple M3 Pro", "Apple M3", "Apple M2 Max", "Apple M2 Pro", "Apple M2", "Apple M1 Max", "Apple M1 Pro", "Apple M1"]
        self.mac_intel_gpus = ["Intel(R) UHD Graphics 630", "Intel(R) Iris(R) Plus Graphics 645", "Intel(R) HD Graphics 530"]
        
        # Screen resolutions (realistic per device type)
        self.desktop_screens = [
            (1920, 1080, 1040), (2560, 1440, 1400), (3840, 2160, 2120), (2560, 1080, 1040), (3440, 1440, 1400)
        ]
        self.laptop_screens = [
            (1920, 1080, 1040), (1366, 768, 728), (1536, 864, 824), (1440, 900, 860), (1680, 1050, 1010), (1600, 900, 860)
        ]
        self.mac_screens = [
            (2880, 1800, 1760), (3024, 1964, 1924), (2560, 1664, 1624), (3456, 2234, 2194), (3072, 1920, 1880)
        ]
        
        # Hardware configs: {gpu_tier: (cores_range, ram_options)}
        self.hardware_tiers = {
            "high_end": ([12, 16, 20, 24], [16, 32, 64]),      # RTX 4090, RX 7900
            "mid_high": ([8, 10, 12], [16, 32]),                # RTX 3070, RX 6700
            "mid": ([6, 8], [8, 16]),                           # GTX 1660, RX 580
            "low_mid": ([4, 6], [8, 16]),                       # Intel UHD, entry GPUs
            "low": ([2, 4], [4, 8]),                            # Old Intel HD
            "mac_high": ([10, 12], [16, 32, 64]),               # M3 Max, M2 Pro
            "mac_mid": ([8, 10], [8, 16, 24]),                  # M2, M1 Pro
        }
        
        # Windows fonts (base + random additions)
        self.windows_fonts_base = ["Arial", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Segoe UI", "Tahoma", "Times New Roman", "Verdana"]
        self.windows_fonts_extra = ["Trebuchet MS", "Comic Sans MS", "Impact", "Lucida Console", "Palatino Linotype", "Arial Black", "Century Gothic"]
        
        # Mac fonts (base + random additions)
        self.mac_fonts_base = ["Arial", "Helvetica", "Helvetica Neue", "Times", "Times New Roman", "Courier", "Courier New", "Verdana", "Georgia"]
        self.mac_fonts_extra = ["Monaco", "Menlo", "San Francisco", "Avenir", "Futura", "Optima", "Palatino"]
        
        # Timezone-Locale mapping
        self.timezone_locale_map = {
            "America/New_York": (-300, ["en-US", "en"], "en-US,en;q=0.9"),
            "America/Chicago": (-360, ["en-US", "en"], "en-US,en;q=0.9"),
            "America/Los_Angeles": (-480, ["en-US", "en"], "en-US,en;q=0.9"),
            "America/Denver": (-420, ["en-US", "en"], "en-US,en;q=0.9"),
            "America/Toronto": (-300, ["en-CA", "en"], "en-CA,en;q=0.9"),
            "America/Sao_Paulo": (-180, ["pt-BR", "pt"], "pt-BR,pt;q=0.9,en;q=0.8"),
            "Europe/London": (0, ["en-GB", "en"], "en-GB,en;q=0.9"),
            "Europe/Paris": (60, ["fr-FR", "fr"], "fr-FR,fr;q=0.9,en;q=0.8"),
            "Europe/Berlin": (60, ["de-DE", "de"], "de-DE,de;q=0.9,en;q=0.8"),
            "Europe/Madrid": (60, ["es-ES", "es"], "es-ES,es;q=0.9,en;q=0.8"),
            "Europe/Amsterdam": (60, ["nl-NL", "nl"], "nl-NL,nl;q=0.9,en;q=0.8"),
            "Europe/Rome": (60, ["it-IT", "it"], "it-IT,it;q=0.9,en;q=0.8"),
            "Europe/Moscow": (180, ["ru-RU", "ru"], "ru-RU,ru;q=0.9,en;q=0.8"),
            "Asia/Tokyo": (540, ["ja-JP", "ja"], "ja-JP,ja;q=0.9,en;q=0.8"),
            "Asia/Shanghai": (480, ["zh-CN", "zh"], "zh-CN,zh;q=0.9,en;q=0.8"),
            "Asia/Seoul": (540, ["ko-KR", "ko"], "ko-KR,ko;q=0.9,en;q=0.8"),
            "Asia/Singapore": (480, ["en-SG", "en"], "en-SG,en;q=0.9"),
            "Asia/Dubai": (240, ["ar-AE", "en"], "ar-AE,en;q=0.9"),
            "Asia/Jakarta": (420, ["id-ID", "id"], "id-ID,id;q=0.9,en;q=0.8"),
            "Asia/Bangkok": (420, ["th-TH", "th"], "th-TH,th;q=0.9,en;q=0.8"),
            "Asia/Kolkata": (330, ["hi-IN", "en"], "hi-IN,en;q=0.9"),
            "Australia/Sydney": (660, ["en-AU", "en"], "en-AU,en;q=0.9"),
            "Pacific/Auckland": (780, ["en-NZ", "en"], "en-NZ,en;q=0.9"),
        }
        
        self.audio_noise = random.uniform(0.00001, 0.0001)
        self.generate_fingerprint()
    
    def generate_fingerprint(self):
        """Generate DYNAMIC REALISTIC fingerprint - ribuan kombinasi unik"""
        random.seed(self.session_seed + int(time.time() * 1000) % 10000)
        
        # Step 1: Pilih OS & Browser type
        os_choice = random.choice(["windows_chrome", "windows_firefox", "windows_edge", "mac_chrome", "mac_safari"])
        
        # Step 2: Generate berdasarkan OS choice
        if os_choice == "windows_chrome":
            self.platform = "Win32"
            chrome_ver = random.choice(self.chrome_versions)
            self.user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36"
            
            # Pilih GPU type (NVIDIA, AMD, atau Intel)
            gpu_type = random.choices(["nvidia", "amd", "intel"], weights=[40, 30, 30])[0]
            
            if gpu_type == "nvidia":
                gpu_name = random.choice(self.windows_nvidia_gpus)
                self.webgl_vendor = "Google Inc. (NVIDIA)"
                self.webgl_renderer = f"ANGLE (NVIDIA, {gpu_name} Direct3D11 vs_5_0 ps_5_0, D3D11)"
                # ELITE: Hardware consistency - GPU tier MUST match RAM & Screen
                if "4090" in gpu_name or "4080" in gpu_name:
                    tier = "high_end"
                    screens = self.desktop_screens  # Hanya desktop besar
                    cores = random.choice([16, 20, 24])  # High-end CPU
                    ram = random.choice([32, 64])  # High-end RAM (min 32GB)
                elif "4070" in gpu_name or "3090" in gpu_name:
                    tier = "high_end"
                    screens = self.desktop_screens
                    cores = random.choice([12, 16])
                    ram = random.choice([16, 32])
                elif "3080" in gpu_name or "3070" in gpu_name or "3060" in gpu_name or "2080" in gpu_name or "2070" in gpu_name:
                    tier = "mid_high"
                    screens = self.desktop_screens
                    cores = random.choice([8, 10, 12])
                    ram = random.choice([16, 32])
                else:  # GTX 1660, 1650, 1080, 1070
                    tier = "mid"
                    screens = self.desktop_screens[:3] + self.laptop_screens[:3]
                    cores = random.choice([6, 8])
                    ram = random.choice([8, 16])
            
            elif gpu_type == "amd":
                gpu_name = random.choice(self.windows_amd_gpus)
                self.webgl_vendor = "Google Inc. (AMD)"
                self.webgl_renderer = f"ANGLE (AMD, {gpu_name} Direct3D11 vs_5_0 ps_5_0, D3D11)"
                # ELITE: Hardware consistency
                if "7900" in gpu_name or "6900" in gpu_name:
                    tier = "high_end"
                    screens = self.desktop_screens
                    cores = random.choice([16, 20, 24])
                    ram = random.choice([32, 64])
                elif "6800" in gpu_name or "7800" in gpu_name or "6700" in gpu_name:
                    tier = "mid_high"
                    screens = self.desktop_screens
                    cores = random.choice([8, 10, 12])
                    ram = random.choice([16, 32])
                else:  # RX 580, 570, 5600, 6600
                    tier = "mid"
                    screens = self.desktop_screens[:3] + self.laptop_screens[:3]
                    cores = random.choice([6, 8])
                    ram = random.choice([8, 16])
            
            else:  # Intel - HANYA LAPTOP
                gpu_name = random.choice(self.windows_intel_gpus)
                self.webgl_vendor = "Google Inc. (Intel)"
                self.webgl_renderer = f"ANGLE (Intel, {gpu_name} Direct3D11 vs_5_0 ps_5_0, D3D11)"
                # ELITE: Intel GPU = laptop, hardware consistency
                if "Iris" in gpu_name or "770" in gpu_name or "730" in gpu_name:
                    tier = "low_mid"
                    screens = self.laptop_screens
                    cores = random.choice([4, 6])
                    ram = random.choice([8, 16])
                else:  # UHD 630, 620, HD 530
                    tier = "low"
                    screens = self.laptop_screens[:4]
                    cores = random.choice([2, 4])
                    ram = random.choice([4, 8])
            
            # Generate hardware berdasarkan tier yang sudah di-set di atas
            self.hardware_concurrency = cores
            self.device_memory = ram
            self.max_touch_points = 0
            
            # Generate screen
            screen = random.choice(screens)
            self.screen_width, self.screen_height, self.avail_height = screen
            self.color_depth = 24
            # Pixel ratio logic yang lebih realistis
            if screen[0] >= 3840:  # 4K
                self.pixel_ratio = random.choice([1, 1.5, 2])
            elif screen[0] >= 2560:  # 2K
                self.pixel_ratio = random.choice([1, 1.25])
            else:  # 1080p ke bawah
                self.pixel_ratio = 1
            
            # Generate fonts (base + random extras) - ELITE: Consistent per OS
            self.fonts = self.windows_fonts_base.copy()
            # ELITE: Fixed font list untuk avoid fingerprint inconsistency
            # Windows 10 selalu punya font yang sama, tidak random
            self.fonts.extend(["Trebuchet MS", "Arial Black", "Impact"])  # Fixed extras
            
            self.profile_name = f"Win Chrome {gpu_type.upper()} {cores}C/{ram}GB"
        
        elif os_choice == "windows_firefox":
            self.platform = "Win32"
            ff_ver = random.choice(self.firefox_versions)
            self.user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{ff_ver}) Gecko/20100101 Firefox/{ff_ver.split('.')[0]}.0"
            
            gpu_type = random.choices(["nvidia", "intel"], weights=[60, 40])[0]
            
            if gpu_type == "nvidia":
                gpu_name = random.choice(self.windows_nvidia_gpus)
                self.webgl_vendor = "NVIDIA Corporation"
                self.webgl_renderer = f"{gpu_name}/PCIe/SSE2"
                # Tier berdasarkan GPU
                if "RTX 40" in gpu_name or "RTX 30" in gpu_name or "RTX 20" in gpu_name:
                    tier = "mid_high"
                    screens = self.desktop_screens[:4]  # Desktop sedang-besar
                else:  # GTX series
                    tier = "mid"
                    screens = self.desktop_screens[:3] + self.laptop_screens[:3]
            else:  # Intel
                gpu_name = random.choice(self.windows_intel_gpus)
                self.webgl_vendor = "Intel"
                self.webgl_renderer = gpu_name
                tier = "low_mid"
                screens = self.laptop_screens  # Hanya laptop
            
            cores = random.choice(self.hardware_tiers[tier][0])
            ram = random.choice(self.hardware_tiers[tier][1])
            self.hardware_concurrency = cores
            self.device_memory = ram
            self.max_touch_points = 0
            
            screen = random.choice(screens)
            self.screen_width, self.screen_height, self.avail_height = screen
            self.color_depth = 24
            self.pixel_ratio = 1  # Firefox biasanya 1x
            
            self.fonts = self.windows_fonts_base.copy()
            num_extra = random.randint(1, len(self.windows_fonts_extra))
            self.fonts.extend(random.sample(self.windows_fonts_extra, num_extra))
            
            self.profile_name = f"Win Firefox {gpu_type.upper()} {cores}C/{ram}GB"
        
        elif os_choice == "windows_edge":
            self.platform = "Win32"
            edge_ver = random.choice(self.edge_versions)
            self.user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{edge_ver} Safari/537.36 Edg/{edge_ver}"
            
            # Edge biasanya di laptop bisnis dengan Intel
            gpu_name = random.choice(self.windows_intel_gpus)
            self.webgl_vendor = "Google Inc. (Intel)"
            self.webgl_renderer = f"ANGLE (Intel, {gpu_name} Direct3D11 vs_5_0 ps_5_0, D3D11)"
            tier = "low_mid"
            
            cores = random.choice(self.hardware_tiers[tier][0])
            ram = random.choice(self.hardware_tiers[tier][1])
            self.hardware_concurrency = cores
            self.device_memory = ram
            self.max_touch_points = 0
            
            screen = random.choice(self.laptop_screens[:4])  # Laptop screen saja
            self.screen_width, self.screen_height, self.avail_height = screen
            self.color_depth = 24
            self.pixel_ratio = 1
            
            self.fonts = self.windows_fonts_base.copy()
            num_extra = random.randint(2, 5)
            self.fonts.extend(random.sample(self.windows_fonts_extra, num_extra))
            
            self.profile_name = f"Win Edge Intel {cores}C/{ram}GB"
        
        elif os_choice in ["mac_chrome", "mac_safari"]:
            self.platform = "MacIntel"
            chrome_ver = random.choice(self.chrome_versions)
            
            if os_choice == "mac_chrome":
                self.user_agent = f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_ver} Safari/537.36"
            else:
                safari_ver = "17.2.1"
                self.user_agent = f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{safari_ver} Safari/605.1.15"
            
            # Mac: Apple Silicon atau Intel
            mac_type = random.choices(["apple_silicon", "intel"], weights=[70, 30])[0]
            
            if mac_type == "apple_silicon":
                gpu_name = random.choice(self.mac_apple_gpus)
                self.webgl_vendor = "Apple Inc."
                self.webgl_renderer = gpu_name
                if "Max" in gpu_name or "M3 Pro" in gpu_name:
                    tier = "mac_high"
                else:
                    tier = "mac_mid"
            else:
                gpu_name = random.choice(self.mac_intel_gpus)
                self.webgl_vendor = "Google Inc. (Intel)"
                self.webgl_renderer = f"ANGLE (Intel, {gpu_name}, OpenGL 4.1)"
                tier = "mac_mid"
            
            cores = random.choice(self.hardware_tiers[tier][0])
            ram = random.choice(self.hardware_tiers[tier][1])
            self.hardware_concurrency = cores
            self.device_memory = ram
            self.max_touch_points = 0
            
            screen = random.choice(self.mac_screens)
            self.screen_width, self.screen_height, self.avail_height = screen
            self.color_depth = 24
            self.pixel_ratio = 2
            
            self.fonts = self.mac_fonts_base.copy()
            num_extra = random.randint(2, len(self.mac_fonts_extra))
            self.fonts.extend(random.sample(self.mac_fonts_extra, num_extra))
            
            browser = "Chrome" if os_choice == "mac_chrome" else "Safari"
            self.profile_name = f"Mac {browser} {gpu_name} {cores}C/{ram}GB"
        
        # Timezone & Language - MATCH WITH IP GEOLOCATION
        # ELITE: Timezone harus match dengan IP location untuk avoid detection
        # Default ke Asia/Jakarta untuk IP Indonesia, bisa di-override
        self.timezone = "Asia/Jakarta"  # Default untuk IP Indonesia
        self.timezone_offset = 420  # UTC+7
        self.language = ["id-ID", "id"]
        self.accept_language = "id-ID,id;q=0.9,en;q=0.8"
        
        # Jika butuh timezone lain, bisa di-set manual sesuai IP geolocation
        # Contoh: IP US → America/New_York, IP UK → Europe/London
        
        # WebGL shader precision
        if "NVIDIA" in self.webgl_vendor or "AMD" in self.webgl_vendor or "Apple" in self.webgl_vendor:
            self.shader_precision = {"rangeMin": 127, "rangeMax": 127, "precision": 23}
        else:
            self.shader_precision = {"rangeMin": 127, "rangeMax": 127, "precision": 23}
        
        # Noise - hanya perlu seed, tidak perlu array
        self.audio_noise = random.uniform(0.00001, 0.0001)
        
        # Battery & Network - ELITE: Desktop tidak punya battery!
        # Hanya set battery untuk laptop (Intel GPU)
        if "Intel" in self.webgl_vendor and tier in ["low_mid", "low"]:
            # Laptop - ada battery
            self.has_battery = True
            self.battery_level = random.uniform(0.20, 0.95)
            self.battery_charging = random.choice([True, False])
        else:
            # Desktop - tidak ada battery
            self.has_battery = False
            self.battery_level = None
            self.battery_charging = None
        
        self.connection_type = random.choice(["wifi", "4g", "ethernet"])
        self.connection_downlink = random.uniform(1.5, 100.0)
        self.connection_rtt = random.randint(20, 150)
        
        # Silent mode - no logs to avoid exposure
    
    def get_stealth_script(self):
        """Script untuk hide automation detection - ZERO DETECTION ELITE MODE"""
        return """
        (function() {
            'use strict';
            
            // ==================== SILENT MODE (NO CONSOLE TRACES) ====================
            const originalLog = console.log;
            const silentMode = true;
            
            // ==================== NATIVE FUNCTION WRAPPER ====================
            function makeNative(func, name) {
                const handler = {
                    apply(target, thisArg, args) {
                        return Reflect.apply(target, thisArg, args);
                    },
                    get(target, prop) {
                        if (prop === 'toString' || prop === Symbol.toStringTag) {
                            return function() { return 'function ' + name + '() { [native code] }'; };
                        }
                        if (prop === 'name') return name;
                        return Reflect.get(target, prop);
                    }
                };
                const proxy = new Proxy(func, handler);
                Object.defineProperty(proxy, 'toString', {
                    value: function() { return 'function ' + name + '() { [native code] }'; },
                    writable: false, configurable: false
                });
                Object.defineProperty(proxy, 'name', { value: name, writable: false, configurable: true });
                return proxy;
            }
            
            // ==================== 1. WEBDRIVER DEEP CLEAN ====================
            delete Object.getPrototypeOf(navigator).webdriver;
            delete navigator.__proto__.webdriver;
            delete navigator.webdriver;
            
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
                enumerable: false,
                configurable: true
            });
            
            Object.defineProperty(window, 'navigator', {
                value: new Proxy(navigator, {
                    has: (target, key) => key !== 'webdriver' && key in target,
                    get: (target, key) => key === 'webdriver' ? undefined : target[key]
                }),
                configurable: true
            });
            
            // ==================== 2. SELENIUM ARTIFACTS CLEANUP ====================
            const seleniumProps = [
                'cdc_adoQpoasnfa76pfcZLmcfl_Array', 'cdc_adoQpoasnfa76pfcZLmcfl_Promise',
                'cdc_adoQpoasnfa76pfcZLmcfl_Symbol', 'cdc_adoQpoasnfa76pfcZLmcfl_Object',
                'cdc_adoQpoasnfa76pfcZLmcfl_Proxy', '_Selenium_IDE_Recorder', '_selenium',
                '__selenium_unwrapped', '__selenium_evaluate', '__webdriver_evaluate',
                '__driver_evaluate', '__webdriver_script_function', '__webdriver_script_func',
                '__webdriver_script_fn', '__fxdriver_evaluate', '__driver_unwrapped',
                '__webdriver_unwrapped', '__fxdriver_unwrapped', '__webdriver_script_function',
                '$cdc_asdjflasutopfhvcZLmcfl_', '$chrome_asyncScriptInfo', '__$webdriverAsyncExecutor'
            ];
            
            seleniumProps.forEach(prop => {
                delete window[prop];
                delete document[prop];
                delete document.documentElement[prop];
            });
            
            // Document element webdriver attribute
            if (document.documentElement.getAttribute('webdriver')) {
                document.documentElement.removeAttribute('webdriver');
            }
            
            // ==================== 3. CHROME RUNTIME (FULL SPOOF WITH RANDOM ID) ====================
            if (!window.chrome || !window.chrome.runtime || !window.chrome.runtime.id) {
                // Generate random runtime ID untuk avoid pattern detection
                const randomId = Array.from({length: 32}, () => 
                    'abcdefghijklmnopqrstuvwxyz'[Math.floor(Math.random() * 26)]
                ).join('');
                
                window.chrome = {
                    app: {
                        isInstalled: false,
                        InstallState: { DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' },
                        RunningState: { CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' },
                        getDetails: makeNative(function() { return null; }, 'getDetails'),
                        getIsInstalled: makeNative(function() { return false; }, 'getIsInstalled')
                    },
                    runtime: {
                        id: randomId,
                        OnInstalledReason: { CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update' },
                        OnRestartRequiredReason: { APP_UPDATE: 'app_update', OS_UPDATE: 'os_update', PERIODIC: 'periodic' },
                        PlatformArch: { ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
                        PlatformNaclArch: { ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' },
                        PlatformOs: { ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win' },
                        RequestUpdateCheckStatus: { NO_UPDATE: 'no_update', THROTTLED: 'throttled', UPDATE_AVAILABLE: 'update_available' },
                        connect: makeNative(function() { 
                            return { 
                                onMessage: { addListener: function() {}, removeListener: function() {} },
                                postMessage: function() {},
                                disconnect: function() {}
                            }; 
                        }, 'connect'),
                        sendMessage: makeNative(function() { return Promise.resolve(); }, 'sendMessage'),
                        getManifest: makeNative(function() { return {}; }, 'getManifest'),
                        getURL: makeNative(function(path) { return 'chrome-extension://' + randomId + '/' + path; }, 'getURL')
                    },
                    csi: makeNative(function() { return { startE: Date.now(), onloadT: Date.now(), pageT: Date.now(), tran: 15 }; }, 'csi'),
                    loadTimes: makeNative(function() {
                        const now = Date.now() / 1000;
                        return {
                            requestTime: now - 1, startLoadTime: now - 0.8, commitLoadTime: now - 0.5,
                            finishDocumentLoadTime: now - 0.3, finishLoadTime: now - 0.1,
                            firstPaintTime: now - 0.2, firstPaintAfterLoadTime: 0,
                            navigationType: 'Other', wasFetchedViaSpdy: false, wasNpnNegotiated: true,
                            npnNegotiatedProtocol: 'h2', wasAlternateProtocolAvailable: false, connectionInfo: 'h2'
                        };
                    }, 'loadTimes')
                };
            }
            
            // ==================== 4. PLUGINS & MIMETYPES (REALISTIC) ====================
            const pluginsData = [
                { name: 'PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: 'Portable Document Format' },
                { name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                { name: 'Microsoft Edge PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                { name: 'WebKit built-in PDF', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }
            ];
            
            Object.defineProperty(navigator, 'plugins', {
                get: makeNative(function() {
                    const arr = pluginsData.map((p, i) => ({
                        ...p, length: 2,
                        item: function(index) { return this[index] || null; },
                        namedItem: function(name) { return this[name] || null; }
                    }));
                    arr.item = function(i) { return this[i] || null; };
                    arr.namedItem = function(name) { return this[name] || null; };
                    arr.refresh = function() {};
                    return arr;
                }, 'get plugins')
            });
            
            const mimeTypesData = [
                { type: 'application/pdf', suffixes: 'pdf', description: 'Portable Document Format' },
                { type: 'text/pdf', suffixes: 'pdf', description: 'Portable Document Format' }
            ];
            
            Object.defineProperty(navigator, 'mimeTypes', {
                get: makeNative(function() {
                    const arr = [...mimeTypesData];
                    arr.item = function(i) { return this[i] || null; };
                    arr.namedItem = function(name) { return this[name] || null; };
                    return arr;
                }, 'get mimeTypes')
            });
            
            // ==================== 5. PERMISSIONS API ====================
            const originalPermissionsQuery = navigator.permissions.query;
            navigator.permissions.query = makeNative(function(params) {
                if (params.name === 'notifications') {
                    return Promise.resolve({ state: Notification.permission, onchange: null });
                }
                if (params.name === 'geolocation') {
                    return Promise.resolve({ state: 'prompt', onchange: null });
                }
                return originalPermissionsQuery.call(navigator.permissions, params);
            }, 'query');
            
            // ==================== 6. MISSING NAVIGATOR PROPERTIES ====================
            // UserAgentData (Chrome 90+) - CONSISTENT WITH PLATFORM
            if (!navigator.userAgentData) {{
                const platformName = '{self.platform}' === 'Win32' ? 'Windows' : 
                                    '{self.platform}' === 'MacIntel' ? 'macOS' : 'Linux';
                const isMobile = {str(self.max_touch_points > 0).lower()};
                
                Object.defineProperty(navigator, 'userAgentData', {{
                    get: () => ({{
                        brands: [
                            {{ brand: 'Chromium', version: '131' }},
                            {{ brand: 'Google Chrome', version: '131' }},
                            {{ brand: 'Not:A-Brand', version: '99' }}
                        ],
                        mobile: isMobile,
                        platform: platformName,
                        getHighEntropyValues: makeNative(function() {{
                            return Promise.resolve({{
                                brands: this.brands, 
                                mobile: isMobile, 
                                platform: platformName,
                                platformVersion: platformName === 'Windows' ? '10.0.0' : '13.0.0',
                                architecture: 'x86', 
                                bitness: '64',
                                model: '', 
                                uaFullVersion: '131.0.6778.109',
                                fullVersionList: this.brands
                            }});
                        }}, 'getHighEntropyValues')
                    }}),
                    configurable: true
                }});
            }}
            
            // Keyboard API
            if (!navigator.keyboard) {
                Object.defineProperty(navigator, 'keyboard', {
                    get: () => ({
                        getLayoutMap: makeNative(function() { return Promise.resolve(new Map()); }, 'getLayoutMap'),
                        lock: makeNative(function() { return Promise.resolve(); }, 'lock'),
                        unlock: makeNative(function() {}, 'unlock')
                    }),
                    configurable: true
                });
            }
            
            // MediaDevices
            if (!navigator.mediaDevices) {
                Object.defineProperty(navigator, 'mediaDevices', {
                    get: () => ({
                        enumerateDevices: makeNative(function() { return Promise.resolve([]); }, 'enumerateDevices'),
                        getUserMedia: makeNative(function() { return Promise.reject(new Error('Permission denied')); }, 'getUserMedia'),
                        getSupportedConstraints: makeNative(function() { return {}; }, 'getSupportedConstraints')
                    }),
                    configurable: true
                });
            }
            
            // MediaSession
            if (!navigator.mediaSession) {
                Object.defineProperty(navigator, 'mediaSession', {
                    get: () => ({
                        metadata: null,
                        playbackState: 'none',
                        setActionHandler: makeNative(function() {}, 'setActionHandler'),
                        setPositionState: makeNative(function() {}, 'setPositionState')
                    }),
                    configurable: true
                });
            }
            
            // SpeechSynthesis
            if (!window.speechSynthesis) {
                Object.defineProperty(window, 'speechSynthesis', {
                    get: () => ({
                        pending: false, speaking: false, paused: false,
                        getVoices: makeNative(function() { return []; }, 'getVoices'),
                        speak: makeNative(function() {}, 'speak'),
                        cancel: makeNative(function() {}, 'cancel'),
                        pause: makeNative(function() {}, 'pause'),
                        resume: makeNative(function() {}, 'resume')
                    }),
                    configurable: true
                });
            }
            
            // ==================== 7. WEBRTC LEAK PROTECTION (ELITE - FULL BLOCK) ====================
            // CRITICAL: Block WebRTC completely to prevent IP leak
            Object.defineProperty(window, 'RTCPeerConnection', { value: undefined, writable: false, configurable: false });
            Object.defineProperty(window, 'webkitRTCPeerConnection', { value: undefined, writable: false, configurable: false });
            Object.defineProperty(window, 'mozRTCPeerConnection', { value: undefined, writable: false, configurable: false });
            Object.defineProperty(window, 'RTCDataChannel', { value: undefined, writable: false, configurable: false });
            Object.defineProperty(navigator, 'getUserMedia', { value: undefined, writable: false, configurable: false });
            Object.defineProperty(navigator, 'webkitGetUserMedia', { value: undefined, writable: false, configurable: false });
            Object.defineProperty(navigator, 'mozGetUserMedia', { value: undefined, writable: false, configurable: false });
            Object.defineProperty(navigator, 'mediaDevices', { 
                value: { 
                    getUserMedia: undefined,
                    enumerateDevices: () => Promise.resolve([])
                }, 
                writable: false, 
                configurable: false 
            });
            
            // ==================== 8. IFRAME CONTENTWINDOW ====================
            const originalContentWindowGetter = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow').get;
            Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
                get: makeNative(function() {
                    try {
                        const win = originalContentWindowGetter.call(this);
                        return win;
                    } catch(e) {
                        return null;
                    }
                }, 'get contentWindow'),
                configurable: true
            });
            
            // ==================== 9. HEADLESS DETECTION FIX ====================
            // Fix outerWidth/outerHeight for headless
            if (window.outerWidth === 0) {
                Object.defineProperty(window, 'outerWidth', { get: () => window.innerWidth });
            }
            if (window.outerHeight === 0) {
                Object.defineProperty(window, 'outerHeight', { get: () => window.innerHeight });
            }
            
            // ==================== 10. NOTIFICATION PERMISSION ====================
            try {
                if (Notification.permission === 'default') {
                    Object.defineProperty(Notification, 'permission', { get: () => 'denied' });
                }
            } catch(e) {}
            
            // ==================== SILENT COMPLETION ====================
            if (!silentMode) originalLog('[STEALTH] Protection active');
        })();
        """
    
    def get_fingerprint_script(self):
        """Script untuk inject random fingerprint - ELITE ZERO DETECTION (EMBEDDED)"""
        
        # Determine browser-specific values
        is_chrome = "Chrome" in self.user_agent and "Edg" not in self.user_agent
        is_firefox = "Firefox" in self.user_agent
        is_safari = "Safari" in self.user_agent and "Chrome" not in self.user_agent
        is_edge = "Edg" in self.user_agent
        is_mac = self.platform == "MacIntel"
        
        # Vendor
        if is_safari or (is_chrome and is_mac):
            vendor = "Apple Computer, Inc."
        elif is_chrome or is_edge:
            vendor = "Google Inc."
        else:
            vendor = ""
        
        # Product Sub
        product_sub = "20100101" if is_firefox else "20030107"
        
        # App Version
        app_version = self.user_agent.replace("Mozilla/", "")
        
        # ELITE FINGERPRINT SCRIPT - ALL VULNERABILITIES FIXED
        return f"""
        (function() {{
            'use strict';
            
            // ==================== SILENT MODE (NO CONSOLE TRACES) ====================
            const originalLog = console.log;
            const silentMode = true;
            
            // ==================== SECURE SEED GENERATION (NO EXPOSURE) ====================
            // Generate seeds locally without exposing session_id
            const generateSecureSeed = () => {{
                const crypto = window.crypto || window.msCrypto;
                const array = new Uint32Array(1);
                crypto.getRandomValues(array);
                return array[0];
            }};
            
            const NOISE_SEED = generateSecureSeed();
            const canvasSeed = generateSecureSeed();
            const audioSeed = generateSecureSeed();
            const rectSeed = generateSecureSeed();
            
            // ==================== NATIVE FUNCTION WRAPPER ====================
            // FIX: toString() Detection & Proxy Detection
            function makeNativeFunction(func, name, isGetter = false) {{
                const wrapper = new Proxy(func, {{
                    apply(target, thisArg, args) {{ return Reflect.apply(target, thisArg, args); }},
                    get(target, prop) {{
                        if (prop === 'toString' || prop === Symbol.toStringTag) {{
                            return function() {{
                                return isGetter ? 'function get ' + name + '() {{ [native code] }}' : 'function ' + name + '() {{ [native code] }}';
                            }};
                        }}
                        if (prop === 'name') return name;
                        return Reflect.get(target, prop);
                    }}
                }});
                Object.defineProperty(wrapper, 'toString', {{
                    value: function() {{ return isGetter ? 'function get ' + name + '() {{ [native code] }}' : 'function ' + name + '() {{ [native code] }}'; }},
                    writable: false, configurable: false
                }});
                Object.defineProperty(wrapper, 'name', {{ value: name, writable: false, configurable: true }});
                return wrapper;
            }}
            
            // ==================== PERFORMANCE TIMING WITH ELITE JITTER ====================
            // ELITE: Realistic timing variation to avoid timing attack detection
            let performanceOffset = Math.random() * 2.0;  // Increased from 0.5 to 2.0
            let lastCallTime = 0;
            const originalPerformanceNow = Performance.prototype.now;
            
            Performance.prototype.now = makeNativeFunction(function() {{
                const realTime = originalPerformanceNow.call(performance);
                const timeSinceLastCall = realTime - lastCallTime;
                
                // ELITE: Variable jitter based on call frequency
                let jitter;
                if (timeSinceLastCall < 10) {{
                    // Rapid calls - small jitter (0-0.1ms)
                    jitter = Math.random() * 0.1;
                }} else if (timeSinceLastCall < 100) {{
                    // Normal calls - medium jitter (0-0.5ms)
                    jitter = Math.random() * 0.5;
                }} else {{
                    // Slow calls - large jitter (0-2ms)
                    jitter = Math.random() * 2.0;
                }}
                
                lastCallTime = realTime;
                return realTime + performanceOffset + jitter;
            }}, 'now', false);
            
            const microDelay = () => {{
                const start = originalPerformanceNow.call(performance);
                const delay = Math.random() * 0.05;  // Increased from 0.01 to 0.05
                while (originalPerformanceNow.call(performance) - start < delay) {{}}
            }};
            
            // ==================== PROTOTYPE-BASED PROPERTY DEFINITION ====================
            // FIX: Prototype Chain Detection
            function defineNativeProperty(proto, propName, getter, setter = null) {{
                const descriptor = {{
                    get: makeNativeFunction(function() {{ microDelay(); return getter.call(this); }}, propName, true),
                    enumerable: true,
                    configurable: false
                }};
                if (setter) descriptor.set = makeNativeFunction(setter, propName, false);
                Object.defineProperty(proto, propName, descriptor);
            }}
            
            // ==================== ERROR STACK SANITIZATION ====================
            // FIX: Error Stack Traces
            const originalErrorStack = Object.getOwnPropertyDescriptor(Error.prototype, 'stack');
            Object.defineProperty(Error.prototype, 'stack', {{
                get: makeNativeFunction(function() {{
                    let stack = originalErrorStack.get.call(this);
                    if (stack) {{
                        stack = stack.split('\\n').filter(line => 
                            !line.includes('defineProperty') && !line.includes('Proxy') && 
                            !line.includes('<anonymous>') && !line.includes('eval')
                        ).join('\\n');
                    }}
                    return stack;
                }}, 'stack', true),
                configurable: false
            }});
            
            // ==================== MEMORY STATE ====================
            let memoryState = {{
                jsHeapSizeLimit: {self.device_memory} * 1024 * 1024 * 1024,
                totalJSHeapSize: Math.floor(Math.random() * {self.device_memory} * 500 * 1024 * 1024),
                usedJSHeapSize: Math.floor(Math.random() * {self.device_memory} * 300 * 1024 * 1024),
                lastUpdate: originalPerformanceNow.call(performance)
            }};
            setInterval(() => {{
                const growth = Math.floor(Math.random() * 1024 * 1024);
                memoryState.usedJSHeapSize = Math.min(memoryState.usedJSHeapSize + growth, memoryState.totalJSHeapSize);
            }}, 1000);
            
            // ==================== NAVIGATOR PROPERTIES ====================
            defineNativeProperty(Navigator.prototype, 'userAgent', function() {{ return '{self.user_agent}'; }});
            defineNativeProperty(Navigator.prototype, 'language', function() {{ return '{self.language[0]}'; }});
            defineNativeProperty(Navigator.prototype, 'languages', function() {{ return {self.language}; }});
            defineNativeProperty(Navigator.prototype, 'platform', function() {{ return '{self.platform}'; }});
            defineNativeProperty(Navigator.prototype, 'hardwareConcurrency', function() {{ return {self.hardware_concurrency}; }});
            defineNativeProperty(Navigator.prototype, 'deviceMemory', function() {{ return {self.device_memory}; }});
            defineNativeProperty(Navigator.prototype, 'maxTouchPoints', function() {{ return {self.max_touch_points}; }});
            defineNativeProperty(Navigator.prototype, 'vendor', function() {{ return '{vendor}'; }});
            defineNativeProperty(Navigator.prototype, 'product', function() {{ return 'Gecko'; }});
            defineNativeProperty(Navigator.prototype, 'productSub', function() {{ return '{product_sub}'; }});
            defineNativeProperty(Navigator.prototype, 'appVersion', function() {{ return '{app_version}'; }});
            defineNativeProperty(Navigator.prototype, 'appName', function() {{ return 'Netscape'; }});
            defineNativeProperty(Navigator.prototype, 'appCodeName', function() {{ return 'Mozilla'; }});
            defineNativeProperty(Navigator.prototype, 'doNotTrack', function() {{ return null; }});
            defineNativeProperty(Navigator.prototype, 'pdfViewerEnabled', function() {{ return true; }});
            defineNativeProperty(Navigator.prototype, 'cookieEnabled', function() {{ return true; }});
            defineNativeProperty(Navigator.prototype, 'onLine', function() {{ return true; }});
            
            // ==================== SCREEN PROPERTIES ====================
            defineNativeProperty(Screen.prototype, 'width', function() {{ return {self.screen_width}; }});
            defineNativeProperty(Screen.prototype, 'height', function() {{ return {self.screen_height}; }});
            defineNativeProperty(Screen.prototype, 'availWidth', function() {{ return {self.screen_width}; }});
            defineNativeProperty(Screen.prototype, 'availHeight', function() {{ return {self.avail_height}; }});
            defineNativeProperty(Screen.prototype, 'colorDepth', function() {{ return {self.color_depth}; }});
            defineNativeProperty(Screen.prototype, 'pixelDepth', function() {{ return {self.color_depth}; }});
            
            const innerWidthOffset = Math.floor(Math.random() * 20);
            const innerHeightOffset = 40 + Math.floor(Math.random() * 60);
            defineNativeProperty(Window.prototype, 'devicePixelRatio', function() {{ return {self.pixel_ratio}; }});
            defineNativeProperty(Window.prototype, 'innerWidth', function() {{ return {self.screen_width} - innerWidthOffset; }});
            defineNativeProperty(Window.prototype, 'innerHeight', function() {{ return {self.avail_height} - innerHeightOffset; }});
            defineNativeProperty(Window.prototype, 'outerWidth', function() {{ return {self.screen_width}; }});
            defineNativeProperty(Window.prototype, 'outerHeight', function() {{ return {self.screen_height}; }});
            
            // ==================== WEBGL FINGERPRINT ====================
            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
            const originalGetParameter2 = WebGL2RenderingContext.prototype.getParameter;
            
            WebGLRenderingContext.prototype.getParameter = makeNativeFunction(function(param) {{
                microDelay();
                if (param === 37445) return '{self.webgl_vendor}';
                if (param === 37446) return '{self.webgl_renderer}';
                if (param === 7936) return '{self.webgl_vendor}';
                if (param === 7937) return '{self.webgl_renderer}';
                if (param === 3379) return 16384;
                if (param === 34076) return 16384;
                if (param === 34024) return 16;
                if (param === 3386) return [16384, 16384];
                return originalGetParameter.call(this, param);
            }}, 'getParameter', false);
            
            WebGL2RenderingContext.prototype.getParameter = makeNativeFunction(function(param) {{
                microDelay();
                if (param === 37445) return '{self.webgl_vendor}';
                if (param === 37446) return '{self.webgl_renderer}';
                if (param === 7936) return '{self.webgl_vendor}';
                if (param === 7937) return '{self.webgl_renderer}';
                if (param === 3379) return 16384;
                if (param === 34076) return 16384;
                if (param === 34024) return 16;
                if (param === 3386) return [16384, 16384];
                return originalGetParameter2.call(this, param);
            }}, 'getParameter', false);
            
            const shaderPrecision = {{ rangeMin: {self.shader_precision["rangeMin"]}, rangeMax: {self.shader_precision["rangeMax"]}, precision: {self.shader_precision["precision"]} }};
            WebGLRenderingContext.prototype.getShaderPrecisionFormat = makeNativeFunction(function() {{ microDelay(); return shaderPrecision; }}, 'getShaderPrecisionFormat', false);
            WebGL2RenderingContext.prototype.getShaderPrecisionFormat = makeNativeFunction(function() {{ microDelay(); return shaderPrecision; }}, 'getShaderPrecisionFormat', false);
            
            const originalCompileShader = WebGLRenderingContext.prototype.compileShader;
            WebGLRenderingContext.prototype.compileShader = makeNativeFunction(function(shader) {{
                const compileTime = 5 + Math.random() * 15;
                const start = originalPerformanceNow.call(performance);
                while (originalPerformanceNow.call(performance) - start < compileTime) {{}}
                return originalCompileShader.call(this, shader);
            }}, 'compileShader', false);
            WebGL2RenderingContext.prototype.compileShader = WebGLRenderingContext.prototype.compileShader;
            
            // ==================== CANVAS FINGERPRINT ====================
            function getCanvasNoise(index) {{
                let hash = (index * 2654435761 + canvasSeed) >>> 0;
                hash = ((hash ^ (hash >>> 16)) * 0x85ebca6b) >>> 0;
                hash = ((hash ^ (hash >>> 13)) * 0xc2b2ae35) >>> 0;
                return ((hash & 0xFF) % 7) - 3;
            }}
            
            const simulateCanvasRendering = (pixelCount) => {{
                const baseTime = pixelCount / 1000000;
                const jitter = Math.random() * 0.5;
                const start = originalPerformanceNow.call(performance);
                while (originalPerformanceNow.call(performance) - start < baseTime + jitter) {{}}
            }};
            
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            CanvasRenderingContext2D.prototype.getImageData = makeNativeFunction(function(...args) {{
                const imageData = originalGetImageData.apply(this, args);
                simulateCanvasRendering(imageData.data.length / 4);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    const noise = getCanvasNoise(i);
                    imageData.data[i] = Math.max(0, Math.min(255, imageData.data[i] + noise));
                    imageData.data[i+1] = Math.max(0, Math.min(255, imageData.data[i+1] + getCanvasNoise(i+1)));
                    imageData.data[i+2] = Math.max(0, Math.min(255, imageData.data[i+2] + getCanvasNoise(i+2)));
                }}
                return imageData;
            }}, 'getImageData', false);
            
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = makeNativeFunction(function(...args) {{
                const context = this.getContext('2d');
                if (context) {{
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    simulateCanvasRendering(Math.min(imageData.data.length / 4, 250));
                    for (let i = 0; i < Math.min(imageData.data.length, 1000); i += 4) {{
                        const noise = getCanvasNoise(i);
                        imageData.data[i] = Math.max(0, Math.min(255, imageData.data[i] + noise));
                        imageData.data[i+1] = Math.max(0, Math.min(255, imageData.data[i+1] + getCanvasNoise(i+1)));
                        imageData.data[i+2] = Math.max(0, Math.min(255, imageData.data[i+2] + getCanvasNoise(i+2)));
                    }}
                    context.putImageData(imageData, 0, 0);
                }}
                return originalToDataURL.apply(this, args);
            }}, 'toDataURL', false);
            
            // ==================== AUDIO FINGERPRINT ====================
            const audioNoiseLevel = {self.audio_noise};
            function getAudioNoise(index) {{
                let hash = (index * 2654435761 + audioSeed) >>> 0;
                hash = ((hash ^ (hash >>> 16)) * 0x85ebca6b) >>> 0;
                hash = ((hash ^ (hash >>> 13)) * 0xc2b2ae35) >>> 0;
                return ((hash / 0xFFFFFFFF) - 0.5) * audioNoiseLevel;
            }}
            
            const originalGetChannelData = AudioBuffer.prototype.getChannelData;
            AudioBuffer.prototype.getChannelData = makeNativeFunction(function(channel) {{
                const data = originalGetChannelData.call(this, channel);
                for (let i = 0; i < data.length; i++) {{
                    if (i % 3 === 0) data[i] = data[i] + getAudioNoise(i + channel * 1000);
                }}
                return data;
            }}, 'getChannelData', false);
            
            // ==================== CLIENT RECTS ====================
            function getRectNoise(index, component) {{
                let hash = ((index * 100 + component) * 2654435761 + rectSeed) >>> 0;
                hash = ((hash ^ (hash >>> 16)) * 0x85ebca6b) >>> 0;
                return ((hash / 0xFFFFFFFF) - 0.5) * 0.002;
            }}
            
            const originalGetClientRects = Element.prototype.getClientRects;
            Element.prototype.getClientRects = makeNativeFunction(function() {{
                const rects = originalGetClientRects.call(this);
                const newRects = [];
                for (let i = 0; i < rects.length; i++) {{
                    newRects.push({{
                        top: rects[i].top + getRectNoise(i, 0), right: rects[i].right + getRectNoise(i, 1),
                        bottom: rects[i].bottom + getRectNoise(i, 2), left: rects[i].left + getRectNoise(i, 3),
                        width: rects[i].width, height: rects[i].height,
                        x: rects[i].x + getRectNoise(i, 4), y: rects[i].y + getRectNoise(i, 5)
                    }});
                }}
                return newRects;
            }}, 'getClientRects', false);
            
            const originalGetBoundingClientRect = Element.prototype.getBoundingClientRect;
            Element.prototype.getBoundingClientRect = makeNativeFunction(function() {{
                const rect = originalGetBoundingClientRect.call(this);
                const elemHash = this.tagName.charCodeAt(0) + this.className.length;
                return {{
                    top: rect.top + getRectNoise(elemHash, 0), right: rect.right + getRectNoise(elemHash, 1),
                    bottom: rect.bottom + getRectNoise(elemHash, 2), left: rect.left + getRectNoise(elemHash, 3),
                    width: rect.width, height: rect.height,
                    x: rect.x + getRectNoise(elemHash, 4), y: rect.y + getRectNoise(elemHash, 5)
                }};
            }}, 'getBoundingClientRect', false);
            
            // ==================== BATTERY API ====================
            // FIX: Battery API Timing
            if (navigator.getBattery) {{
                navigator.getBattery = makeNativeFunction(function() {{
                    return new Promise((resolve) => {{
                        const delay = 5 + Math.random() * 45;
                        setTimeout(() => {{
                            resolve({{
                                charging: {str(self.battery_charging).lower()}, chargingTime: {str(self.battery_charging).lower()} ? 0 : Infinity,
                                dischargingTime: Infinity, level: {self.battery_level},
                                onchargingchange: null, onchargingtimechange: null, ondischargingtimechange: null, onlevelchange: null
                            }});
                        }}, delay);
                    }});
                }}, 'getBattery', false);
            }}
            
            // ==================== NETWORK INFO ====================
            defineNativeProperty(Navigator.prototype, 'connection', function() {{
                return {{ effectiveType: '{self.connection_type}', downlink: {self.connection_downlink}, rtt: {self.connection_rtt}, saveData: false }};
            }});
            
            // ==================== PERFORMANCE MEMORY ====================
            if (performance.memory) {{
                defineNativeProperty(Performance.prototype, 'memory', function() {{
                    return {{ jsHeapSizeLimit: memoryState.jsHeapSizeLimit, totalJSHeapSize: memoryState.totalJSHeapSize, usedJSHeapSize: memoryState.usedJSHeapSize }};
                }});
            }}
            
            // ==================== TIMEZONE ====================
            const originalDateTimeFormat = Intl.DateTimeFormat;
            Intl.DateTimeFormat = makeNativeFunction(function(...args) {{
                if (args.length === 0 || !args[1]) args[1] = {{ timeZone: '{self.timezone}' }};
                else if (!args[1].timeZone) args[1].timeZone = '{self.timezone}';
                return new originalDateTimeFormat(...args);
            }}, 'DateTimeFormat', false);
            Intl.DateTimeFormat.prototype = originalDateTimeFormat.prototype;
            
            Date.prototype.getTimezoneOffset = makeNativeFunction(function() {{ return {self.timezone_offset}; }}, 'getTimezoneOffset', false);
            
            // ==================== FONTS ====================
            const REALISTIC_FONTS = {self.fonts};
            const simulateFontMeasurement = (textLength) => {{
                const measureTime = textLength * 0.01 + Math.random() * 0.5;
                const start = originalPerformanceNow.call(performance);
                while (originalPerformanceNow.call(performance) - start < measureTime) {{}}
            }};
            
            if (document.fonts && document.fonts.check) {{
                const originalFontCheck = document.fonts.check;
                document.fonts.check = makeNativeFunction(function(font, text) {{
                    microDelay();
                    const fontMatch = font.match(/['"]?([^'"]+)['"]?/);
                    if (fontMatch && fontMatch[1] && REALISTIC_FONTS.includes(fontMatch[1])) return true;
                    return originalFontCheck.call(this, font, text);
                }}, 'check', false);
            }}
            
            const originalMeasureText = CanvasRenderingContext2D.prototype.measureText;
            CanvasRenderingContext2D.prototype.measureText = makeNativeFunction(function(text) {{
                simulateFontMeasurement(text.length);
                const result = originalMeasureText.call(this, text);
                const noise = (Math.random() - 0.5) * 0.1;
                return {{
                    width: result.width + noise, actualBoundingBoxLeft: result.actualBoundingBoxLeft,
                    actualBoundingBoxRight: result.actualBoundingBoxRight, fontBoundingBoxAscent: result.fontBoundingBoxAscent,
                    fontBoundingBoxDescent: result.fontBoundingBoxDescent, actualBoundingBoxAscent: result.actualBoundingBoxAscent,
                    actualBoundingBoxDescent: result.actualBoundingBoxDescent, emHeightAscent: result.emHeightAscent,
                    emHeightDescent: result.emHeightDescent, hangingBaseline: result.hangingBaseline,
                    alphabeticBaseline: result.alphabeticBaseline, ideographicBaseline: result.ideographicBaseline
                }};
            }}, 'measureText', false);
            
            // ==================== WEBRTC BLOCKING ====================
            Object.defineProperty(window, 'RTCPeerConnection', {{ value: undefined, writable: false, configurable: false }});
            Object.defineProperty(window, 'webkitRTCPeerConnection', {{ value: undefined, writable: false, configurable: false }});
            Object.defineProperty(window, 'mozRTCPeerConnection', {{ value: undefined, writable: false, configurable: false }});
            
            // ==================== RAF TIMING ====================
            // FIX: Event Timing Patterns
            const originalRAF = window.requestAnimationFrame;
            window.requestAnimationFrame = makeNativeFunction(function(callback) {{
                return originalRAF.call(this, function(timestamp) {{
                    const jitter = (Math.random() - 0.5) * 0.5;
                    callback(timestamp + jitter);
                }});
            }}, 'requestAnimationFrame', false);
            
            // ==================== EXTRA ELITE PROTECTIONS ====================
            
            // 1. FETCH API OVERRIDE (timing & header order)
            const originalFetch = window.fetch;
            window.fetch = makeNativeFunction(function(...args) {{
                // Add realistic delay
                const delay = Math.random() * 2;
                return new Promise((resolve) => {{
                    setTimeout(() => {{
                        resolve(originalFetch.apply(this, args));
                    }}, delay);
                }});
            }}, 'fetch', false);
            
            // 2. XMLHttpRequest OVERRIDE
            const originalXHROpen = XMLHttpRequest.prototype.open;
            const originalXHRSend = XMLHttpRequest.prototype.send;
            
            XMLHttpRequest.prototype.open = makeNativeFunction(function(...args) {{
                this._url = args[1];
                return originalXHROpen.apply(this, args);
            }}, 'open', false);
            
            XMLHttpRequest.prototype.send = makeNativeFunction(function(...args) {{
                // Add realistic delay
                const delay = Math.random() * 3;
                setTimeout(() => {{
                    originalXHRSend.apply(this, args);
                }}, delay);
            }}, 'send', false);
            
            // 3. POINTER EVENTS (if maxTouchPoints > 0)
            if (navigator.maxTouchPoints > 0) {{
                window.PointerEvent = window.PointerEvent || function() {{}};
                window.TouchEvent = window.TouchEvent || function() {{}};
            }}
            
            // 4. SCREEN RESIZE HANDLER (dynamic screen properties)
            let currentScreenWidth = screen.width;
            let currentScreenHeight = screen.height;
            
            window.addEventListener('resize', function() {{
                currentScreenWidth = window.outerWidth || screen.width;
                currentScreenHeight = window.outerHeight || screen.height;
            }});
            
            // 5. INTL API CONSISTENCY
            const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
            Intl.DateTimeFormat.prototype.resolvedOptions = makeNativeFunction(function() {{
                const options = originalResolvedOptions.call(this);
                options.timeZone = options.timeZone || '{self.timezone}';
                return options;
            }}, 'resolvedOptions', false);
            
            // 6. Object.getOwnPropertyDescriptor leak fix
            const originalGetOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
            Object.getOwnPropertyDescriptor = makeNativeFunction(function(obj, prop) {{
                const desc = originalGetOwnPropertyDescriptor(obj, prop);
                if (desc && desc.get && desc.get.toString().includes('native code')) {{
                    return desc;
                }}
                return desc;
            }}, 'getOwnPropertyDescriptor', false);
            
            // 2. Function.prototype.toString leak fix
            const originalFunctionToString = Function.prototype.toString;
            Function.prototype.toString = makeNativeFunction(function() {{
                if (this === window.requestAnimationFrame || 
                    this === navigator.permissions.query ||
                    this === Performance.prototype.now) {{
                    return 'function ' + this.name + '() {{ [native code] }}';
                }}
                return originalFunctionToString.call(this);
            }}, 'toString', false);
            
            // 3. Proxy detection fix
            const originalProxy = window.Proxy;
            window.Proxy = makeNativeFunction(function(target, handler) {{
                return new originalProxy(target, handler);
            }}, 'Proxy', false);
            window.Proxy.revocable = originalProxy.revocable;
            
            // 4. Date.prototype.toString consistency
            const originalDateToString = Date.prototype.toString;
            Date.prototype.toString = makeNativeFunction(function() {{
                return originalDateToString.call(this);
            }}, 'toString', false);
            
            // 5. Navigator properties enumeration fix
            const navigatorProps = Object.getOwnPropertyNames(Navigator.prototype);
            if (!navigatorProps.includes('webdriver')) {{
                // Good - webdriver properly hidden
            }}
            
            // 6. Screen orientation
            if (!screen.orientation) {{
                Object.defineProperty(screen, 'orientation', {{
                    get: () => ({{
                        type: screen.width > screen.height ? 'landscape-primary' : 'portrait-primary',
                        angle: 0,
                        onchange: null
                    }}),
                    configurable: true
                }});
            }}
            
            // 7. Connection API enhancement
            if (navigator.connection) {{
                const originalConnection = navigator.connection;
                Object.defineProperty(navigator, 'connection', {{
                    get: makeNativeFunction(function() {{
                        return new Proxy(originalConnection, {{
                            get(target, prop) {{
                                if (prop === 'rtt') return Math.floor(20 + Math.random() * 100);
                                if (prop === 'downlink') return Math.floor(1 + Math.random() * 10);
                                return Reflect.get(target, prop);
                            }}
                        }});
                    }}, 'connection', true),
                    configurable: true
                }});
            }}
            
            // 8. Bluetooth API (if exists)
            if (navigator.bluetooth) {{
                const originalBluetooth = navigator.bluetooth;
                Object.defineProperty(navigator, 'bluetooth', {{
                    get: () => ({{
                        getAvailability: makeNativeFunction(function() {{ return Promise.resolve(false); }}, 'getAvailability'),
                        requestDevice: makeNativeFunction(function() {{ return Promise.reject(new Error('Bluetooth not available')); }}, 'requestDevice')
                    }}),
                    configurable: true
                }});
            }}
            
            // 9. USB API (if exists)
            if (navigator.usb) {{
                Object.defineProperty(navigator, 'usb', {{
                    get: () => ({{
                        getDevices: makeNativeFunction(function() {{ return Promise.resolve([]); }}, 'getDevices'),
                        requestDevice: makeNativeFunction(function() {{ return Promise.reject(new Error('USB not available')); }}, 'requestDevice')
                    }}),
                    configurable: true
                }});
            }}
            
            // 10. Credential Management API
            if (navigator.credentials) {{
                const originalCredentials = navigator.credentials;
                Object.defineProperty(navigator, 'credentials', {{
                    get: () => ({{
                        get: makeNativeFunction(function() {{ return Promise.resolve(null); }}, 'get'),
                        store: makeNativeFunction(function() {{ return Promise.resolve(); }}, 'store'),
                        create: makeNativeFunction(function() {{ return Promise.resolve(null); }}, 'create'),
                        preventSilentAccess: makeNativeFunction(function() {{ return Promise.resolve(); }}, 'preventSilentAccess')
                    }}),
                    configurable: true
                }});
            }}
            
            // ==================== STORAGE APIs SPOOF ====================
            // localStorage, sessionStorage, indexedDB consistency
            
            // 1. Storage quota
            if (navigator.storage && navigator.storage.estimate) {{
                const originalEstimate = navigator.storage.estimate;
                navigator.storage.estimate = makeNativeFunction(function() {{
                    return Promise.resolve({{
                        quota: 50000000000 + Math.floor(Math.random() * 10000000000),
                        usage: Math.floor(Math.random() * 1000000000),
                        usageDetails: {{
                            indexedDB: Math.floor(Math.random() * 500000000),
                            caches: Math.floor(Math.random() * 300000000),
                            serviceWorkerRegistrations: 0
                        }}
                    }});
                }}, 'estimate');
            }}
            
            // 2. window.name consistency
            let windowNameValue = '';
            Object.defineProperty(window, 'name', {{
                get: makeNativeFunction(function() {{ return windowNameValue; }}, 'name', true),
                set: makeNativeFunction(function(val) {{ windowNameValue = String(val); }}, 'name', false),
                configurable: true
            }});
            
            // 3. Storage event timing
            const originalStorageSetItem = Storage.prototype.setItem;
            Storage.prototype.setItem = makeNativeFunction(function(key, value) {{
                const result = originalStorageSetItem.call(this, key, value);
                // Add micro delay for realism
                const delay = Math.random() * 0.5;
                setTimeout(() => {{}}, delay);
                return result;
            }}, 'setItem');
            
            // ==================== GAMEPAD API ====================
            if (!navigator.getGamepads) {{
                Object.defineProperty(navigator, 'getGamepads', {{
                    value: makeNativeFunction(function() {{ return []; }}, 'getGamepads'),
                    configurable: true
                }});
            }}
            
            // ==================== FINAL SEAL ====================
            Object.freeze(Navigator.prototype);
            Object.freeze(Screen.prototype);
            
            // Silent mode - no console traces
        }})();
        """


class HumanBehavior:
    """Simulate human-like behavior - TOP-TIER BEHAVIORAL BIOMETRICS (2026)"""
    
    def __init__(self, sb):
        self.sb = sb
        
        # Session personality - variasi antar sesi
        self.patience = random.uniform(0.3, 1.0)
        self.skill_level = random.uniform(0.5, 1.0)
        self.ad_tolerance = random.uniform(0.1, 0.4)
        
        # Timing multiplier dan scroll style
        self.base_speed = random.uniform(0.8, 1.5)
        self.scroll_style = random.choice(['smooth', 'jumpy', 'minimal'])
        self.action_count = 0
        
        # ELITE: Mouse jitter tracking
        self.last_mouse_move = time.time()
        self.mouse_jitter_enabled = True
        
        # TOP-TIER 2026: Advanced ML-based behavior rates
        self.mistake_rate = random.uniform(0.05, 0.12)  # 5-12% (increased from 3-7%)
        self.distraction_rate = random.uniform(0.12, 0.20)  # 12-20% (increased from 8-15%)
        self.double_click_rate = random.uniform(0.02, 0.05)  # 2-5% (variable)
        self.hesitation_rate = random.uniform(0.15, 0.25)  # 15-25% (increased from 12%)
        
        # TOP-TIER 2026: Fatigue simulation (slower over time)
        self.session_start = time.time()
        self.fatigue_factor = 1.0
        
        # TOP-TIER 2026: Context-aware timing models
        self.timing_models = {
            'reading': {'mean': 4.5, 'std': 2.0, 'min': 1.0, 'max': 15.0},
            'clicking': {'mean': 0.8, 'std': 0.4, 'min': 0.2, 'max': 3.0},
            'scrolling': {'mean': 1.2, 'std': 0.6, 'min': 0.3, 'max': 4.0},
            'typing': {'mean': 0.15, 'std': 0.08, 'min': 0.05, 'max': 0.5},
            'thinking': {'mean': 2.5, 'std': 1.5, 'min': 0.5, 'max': 10.0}
        }
    
    def update_fatigue(self):
        """TOP-TIER 2026: Simulate human fatigue (slower over time)"""
        elapsed_minutes = (time.time() - self.session_start) / 60
        # Fatigue increases 5% every 10 minutes
        self.fatigue_factor = 1.0 + (elapsed_minutes / 10) * 0.05
        # Cap at 1.3x (30% slower)
        self.fatigue_factor = min(self.fatigue_factor, 1.3)
    
    def mouse_jitter(self):
        """ELITE: Simulate natural mouse micro-movements (jitter)"""
        if not self.mouse_jitter_enabled:
            return
        
        try:
            # Random jitter setiap 2-5 detik
            if time.time() - self.last_mouse_move > random.uniform(2, 5):
                # Small random movement (5-15 pixels)
                jitter_x = random.randint(-15, 15)
                jitter_y = random.randint(-15, 15)
                
                # Execute jitter via JavaScript (tidak pakai ActionChains untuk avoid detection)
                self.sb.execute_script(f"""
                    const event = new MouseEvent('mousemove', {{
                        bubbles: true,
                        cancelable: true,
                        clientX: window.innerWidth / 2 + {jitter_x},
                        clientY: window.innerHeight / 2 + {jitter_y}
                    }});
                    document.dispatchEvent(event);
                """)
                
                self.last_mouse_move = time.time()
        except:
            pass
        
    def get_mood(self):
        """Mood berubah-ubah: impatient, normal, focused, distracted"""
        mood_cycle = (self.action_count // random.randint(3, 7)) % 4
        moods = ["impatient", "normal", "focused", "distracted"]
        return moods[mood_cycle]
        
    def random_delay(self, min_sec=0.5, max_sec=2.0, context='normal'):
        """TOP-TIER 2026: ML-based delay dengan multi-modal Gaussian distribution"""
        self.action_count += 1
        self.update_fatigue()  # Update fatigue factor
        mood = self.get_mood()
        
        # TOP-TIER 2026: Context-aware timing models
        if context in self.timing_models:
            model = self.timing_models[context]
            mean, std = model['mean'], model['std']
            min_val, max_val = model['min'], model['max']
        elif context == 'annoyed':
            mean, std = 0.3, 0.15
            min_val, max_val = 0.1, 1.0
        else:
            mean, std = (min_sec + max_sec) / 2, (max_sec - min_sec) / 4
            min_val, max_val = min_sec, max_sec
        
        # Generate delay with multi-modal distribution
        if NUMPY_AVAILABLE:
            # TOP-TIER: Multi-modal Gaussian (realistic human timing)
            # 80% normal distribution, 20% outliers
            if random.random() < 0.8:
                base = np.random.normal(mean, std)
            else:
                # Outlier mode (distraction/rush)
                if random.random() < 0.5:
                    base = np.random.normal(mean * 2.5, std * 1.5)  # Long distraction
                else:
                    base = np.random.normal(mean * 0.3, std * 0.5)  # Rush
        else:
            # Fallback: Simple Gaussian approximation
            base = random.gauss(mean, std)
        
        # Mood adjustment
        mood_multipliers = {"impatient": 0.5, "focused": 0.7, "distracted": 1.5, "normal": 1.0}
        base *= mood_multipliers.get(mood, 1.0) * self.base_speed
        
        # TOP-TIER 2026: Apply fatigue factor
        base *= self.fatigue_factor
        
        # Clamp to realistic range
        final = max(min_val, min(base, max_val))
        
        # TOP-TIER 2026: Add micro-jitter (0-50ms) for ultra-realism
        micro_jitter = random.uniform(0, 0.05)
        final += micro_jitter
        
        time.sleep(final)
        return final
        
        # SUPER ELITE: Outliers (distraction/rush)
        if random.random() < 0.05:  # 5% chance long distraction
            base = random.uniform(5, 15)
            log("[AI] Distracted (long pause)", "INFO")
        elif random.random() < 0.03:  # 3% chance rush
            base = random.uniform(0.1, 0.3)
        
        # Clamp
        final = max(0.1, min(base, 20.0))
        time.sleep(final)
        return final
    
    def elite_scroll(self, direction='down', distance=None):
        """ELITE: Natural scroll dengan pause, reverse, variable speed"""
        try:
            if distance is None:
                distance = random.randint(100, 400)
            
            # ELITE: Sometimes scroll in opposite direction first (human-like)
            if random.random() < 0.15:  # 15% chance
                opposite = 'up' if direction == 'down' else 'down'
                small_distance = random.randint(30, 80)
                self.sb.execute_script(f"window.scrollBy(0, {-small_distance if opposite == 'up' else small_distance});")
                time.sleep(random.uniform(0.1, 0.3))
            
            # Main scroll with variable speed (not smooth)
            scrolled = 0
            while scrolled < distance:
                # Variable chunk size (acceleration/deceleration)
                progress = scrolled / distance
                if progress < 0.3:
                    chunk = random.randint(20, 50)  # Slow start
                elif progress < 0.7:
                    chunk = random.randint(50, 100)  # Fast middle
                else:
                    chunk = random.randint(20, 40)  # Slow end
                
                chunk = min(chunk, distance - scrolled)
                scroll_amount = chunk if direction == 'down' else -chunk
                
                self.sb.execute_script(f"window.scrollBy(0, {scroll_amount});")
                scrolled += chunk
                
                # Variable delay (jitter)
                time.sleep(random.uniform(0.01, 0.05))
                
                # ELITE: Random pause while scrolling (reading content)
                if random.random() < 0.2:  # 20% chance pause
                    time.sleep(random.uniform(0.3, 1.0))
            
            # Final pause after scroll (human reads content)
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            log(f"Elite scroll error: {e}", "ERROR")
    
    def idle_simulation(self):
        """ELITE: Simulate human idle/thinking time"""
        # Random idle actions
        actions = [
            lambda: time.sleep(random.uniform(1.0, 3.0)),  # Just wait
            lambda: self.elite_scroll('down', random.randint(50, 150)),  # Small scroll
            lambda: self.elite_scroll('up', random.randint(30, 100)),  # Scroll back
            lambda: self.mouse_jitter(),  # Mouse movement
        ]
        
        # Do 1-2 random actions
        for _ in range(random.randint(1, 2)):
            try:
                random.choice(actions)()
            except:
                pass
        
        # Final thinking pause
        time.sleep(random.uniform(0.5, 2.0))
    
    def simulate_focus_blur(self, element_selector):
        """ELITE: Simulate eye tracking with focus/blur events"""
        try:
            # Focus event (user looking at element)
            self.sb.execute_script(f"""
                const element = document.querySelector('{element_selector}');
                if (element) {{
                    const focusEvent = new FocusEvent('focus', {{ bubbles: true }});
                    element.dispatchEvent(focusEvent);
                    
                    // Mouseenter event
                    const enterEvent = new MouseEvent('mouseenter', {{ bubbles: true }});
                    element.dispatchEvent(enterEvent);
                }}
            """)
            
            # Human looks at element for a while
            time.sleep(random.uniform(0.3, 1.0))
            
            # Blur event (user looks away)
            self.sb.execute_script(f"""
                const element = document.querySelector('{element_selector}');
                if (element) {{
                    const blurEvent = new FocusEvent('blur', {{ bubbles: true }});
                    element.dispatchEvent(blurEvent);
                    
                    // Mouseleave event
                    const leaveEvent = new MouseEvent('mouseleave', {{ bubbles: true }});
                    element.dispatchEvent(leaveEvent);
                }}
            """)
        except:
            pass
    
    def ai_click(self, selector):
        """SUPER ELITE: Click dengan mistake & hesitation simulation"""
        try:
            # SUPER ELITE: Hesitation before click (12% chance)
            if random.random() < self.hesitation_rate:
                log("[AI] Hesitating before click...", "INFO")
                time.sleep(random.uniform(0.5, 1.5))
                # Move mouse away then back
                self.mouse_jitter()
                time.sleep(random.uniform(0.2, 0.5))
            
            # SUPER ELITE: Mistake simulation (3-7% chance)
            if random.random() < self.mistake_rate:
                log("[AI] Simulating mistake (wrong click)", "INFO")
                try:
                    # Click wrong element first
                    wrong_elements = self.sb.find_elements("a, button, div[onclick]")
                    if len(wrong_elements) > 1:
                        wrong = random.choice(wrong_elements)
                        wrong.click()
                        time.sleep(random.uniform(0.3, 0.8))
                        log("[AI] Correcting mistake...", "INFO")
                except:
                    pass
            
            # Actual click
            element = self.sb.find_element(selector)
            
            # Focus simulation
            self.simulate_focus_blur(selector)
            
            # Click
            element.click()
            
            # SUPER ELITE: Double-click by accident (2% chance)
            if random.random() < self.double_click_rate:
                log("[AI] Accidental double-click", "INFO")
                time.sleep(random.uniform(0.05, 0.15))
                try:
                    element.click()
                except:
                    pass
            
            return True
            
        except Exception as e:
            log(f"[AI] Click error: {e}", "ERROR")
            return False
    
    def ai_distraction(self):
        """SUPER ELITE: Random distraction simulation"""
        if random.random() < self.distraction_rate:
            distractions = [
                ("scroll_random", lambda: self.elite_scroll(random.choice(['up', 'down']), random.randint(50, 200))),
                ("long_pause", lambda: time.sleep(random.uniform(3, 10))),
                ("mouse_wander", lambda: [self.mouse_jitter() for _ in range(random.randint(2, 5))]),
                ("back_button", lambda: self.sb.driver.execute_script("window.history.back()") if random.random() < 0.3 else None),
            ]
            
            distraction_type, action = random.choice(distractions)
            log(f"[AI] Distracted: {distraction_type}", "INFO")
            
            try:
                action()
            except:
                pass
            
            # Recovery time after distraction
            time.sleep(random.uniform(0.5, 2.0))
    def move_mouse_to_element(self, selector):
        """Mouse movement ke element dengan realistic trajectory"""
        try:
            element = self.sb.find_element(selector)
            location = element.location
            size = element.size
            
            # Target dengan sedikit randomness
            offset_x = random.randint(-10, 10) if self.skill_level > 0.7 else random.randint(-20, 20)
            offset_y = random.randint(-5, 5) if self.skill_level > 0.7 else random.randint(-15, 15)
            
            target_x = location['x'] + size['width'] // 2 + offset_x
            target_y = location['y'] + size['height'] // 2 + offset_y
            
            # Get current mouse position (estimate from viewport center)
            current_x = random.randint(100, 500)
            current_y = random.randint(100, 400)
            
            # Create trajectory with multiple steps
            steps = random.randint(5, 12)
            for i in range(steps):
                progress = (i + 1) / steps
                # Ease-out curve for natural movement
                eased_progress = 1 - (1 - progress) ** 2
                
                intermediate_x = int(current_x + (target_x - current_x) * eased_progress)
                intermediate_y = int(current_y + (target_y - current_y) * eased_progress)
                
                # Add micro jitter
                jitter_x = random.randint(-2, 2)
                jitter_y = random.randint(-2, 2)
                
                move_script = f"""
                (function() {{
                    const moveEvent = new MouseEvent('mousemove', {{
                        bubbles: true, 
                        cancelable: true,
                        clientX: {intermediate_x + jitter_x}, 
                        clientY: {intermediate_y + jitter_y},
                        screenX: {intermediate_x + jitter_x + 100},
                        screenY: {intermediate_y + jitter_y + 100},
                        movementX: {int((target_x - current_x) / steps)},
                        movementY: {int((target_y - current_y) / steps)},
                        button: 0,
                        buttons: 0,
                        relatedTarget: null,
                        view: window,
                        detail: 0,
                        isTrusted: true
                    }});
                    
                    // Override isTrusted to true
                    Object.defineProperty(moveEvent, 'isTrusted', {{
                        get: () => true,
                        configurable: false
                    }});
                    
                    document.dispatchEvent(moveEvent);
                }})();
                """
                self.sb.execute_script(move_script)
                time.sleep(random.uniform(0.005, 0.015))
            
            return True
        except:
            return False
    
    def human_scroll(self, direction='down', amount=None, safe=True):
        """Scroll natural. safe=True artinya scroll kecil agar tidak kehilangan button"""
        try:
            if amount is None:
                amount = random.randint(50, 150) if safe else random.randint(100, 400)
            
            if direction == 'up':
                amount = -amount
            
            if self.scroll_style == 'smooth':
                steps = random.randint(2, 5)
                per_step = amount // steps
                for _ in range(steps):
                    self.sb.execute_script(f"window.scrollBy(0, {per_step})")
                    time.sleep(random.uniform(0.02, 0.06))
            elif self.scroll_style == 'jumpy':
                self.sb.execute_script(f"window.scrollBy(0, {amount})")
            else:
                self.sb.execute_script(f"window.scrollBy(0, {amount // 2})")
            
            time.sleep(random.uniform(0.1, 0.3))
            return True
        except:
            return False
    
    def human_click(self, selector):
        """Click natural dengan variasi timing"""
        try:
            if random.random() > 0.3:
                self.move_mouse_to_element(selector)
            
            self.random_delay(0.1, 0.5, context='before_click')
            self.sb.click(selector)
            self.random_delay(1.0, 2.5, context='after_click')
            return True
        except Exception as e:
            log(f"Click error: {e}", "ERROR")
            return False
    
    def quick_action(self):
        """Aksi cepat - user tidak sabar"""
        self.random_delay(0.1, 0.3, context='annoyed')
    
    def pretend_read(self):
        """Pura-pura baca halaman - singkat karena user benci iklan"""
        wait = random.uniform(0.3, 1.5) * self.ad_tolerance
        time.sleep(max(0.2, min(wait, 2.0)))
    
    def safe_interaction(self):
        """Interaksi aman yang tidak menyebabkan tersesat"""
        safe_actions = [
            lambda: self.human_scroll('down', random.randint(30, 80), safe=True),
            lambda: self.human_scroll('up', random.randint(20, 50), safe=True),
            lambda: self.pretend_read(),
            lambda: time.sleep(random.uniform(0.2, 0.8)),
        ]
        try:
            random.choice(safe_actions)()
        except:
            pass


class TurnstileDetector:
    """
    Advanced Cloudflare Turnstile Detection System with Groq AI Vision
    - Deteksi presisi tinggi untuk checkbox readiness
    - Adaptive wait berdasarkan network/proxy conditions
    - Multi-layer verification sebelum click
    - AI Vision untuk verifikasi visual (screenshot analysis)
    """
    
    # Turnstile iframe selectors
    IFRAME_SELECTORS = [
        "iframe[src*='challenges.cloudflare.com']",
        "iframe[src*='turnstile']",
        "iframe[title*='Cloudflare']",
        "iframe[title*='Widget']",
        "iframe[id*='cf-']",
    ]
    
    # Container selectors
    CONTAINER_SELECTORS = [
        "div.cf-turnstile",
        "div[class*='turnstile']",
        "#cf-turnstile",
        "div[data-sitekey]",
        "[data-turnstile-callback]",
    ]
    
    # States yang menandakan Turnstile siap
    READY_INDICATORS = {
        'iframe_loaded': False,
        'checkbox_visible': False,
        'no_spinner': False,
        'interactive': False,
    }
    
    # Groq AI Configuration - Sekarang menggunakan GroqAPIManager
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    def __init__(self, sb, use_ai=True, groq_manager=None):
        self.sb = sb
        self.detection_start = None
        self.last_state = {}
        self.groq_manager = groq_manager
        
        # Check if Groq is available via manager
        if groq_manager and groq_manager.has_available_api():
            self.use_ai = use_ai
        else:
            self.use_ai = False
        
        self.ai_checks = 0
        self.dom_checks = 0
        
        if use_ai and not self.use_ai:
            log("[AI] Groq not available - using DOM-only mode", "INFO")
        
    def is_turnstile_present(self):
        """Cek apakah Turnstile ada di halaman (cepat)"""
        try:
            # Cek container dulu (lebih cepat)
            for sel in self.CONTAINER_SELECTORS:
                if self.sb.is_element_present(sel):
                    return True
            
            # Cek iframe
            for sel in self.IFRAME_SELECTORS:
                if self.sb.is_element_present(sel):
                    return True
                    
            # Cek via JavaScript (lebih thorough)
            js_check = """
            return !!(
                document.querySelector('iframe[src*="challenges.cloudflare.com"]') ||
                document.querySelector('iframe[src*="turnstile"]') ||
                document.querySelector('.cf-turnstile') ||
                document.querySelector('[data-sitekey]') ||
                (document.body && document.body.innerHTML.includes('turnstile'))
            );
            """
            return self.sb.execute_script(js_check) == True
        except:
            return False
    
    def get_turnstile_state(self):
        """
        Get comprehensive Turnstile state - CORE METHOD
        Returns dict dengan semua info tentang kesiapan Turnstile
        """
        state = {
            'present': False,
            'iframe_found': False,
            'iframe_loaded': False,
            'checkbox_visible': False,
            'spinner_active': False,
            'success_shown': False,
            'error_shown': False,
            'ready_to_click': False,
            'dimensions': None,
            'response_token': None,
        }
        
        try:
            # JavaScript untuk analisis mendalam Turnstile state
            analysis_script = """
            (function() {
                const result = {
                    present: false,
                    iframe_found: false,
                    iframe_loaded: false,
                    iframe_src: null,
                    iframe_dimensions: null,
                    checkbox_visible: false,
                    spinner_active: false,
                    success_shown: false,
                    error_shown: false,
                    container_present: false,
                    ready_to_click: false,
                    response_token: null,
                    debug_info: []
                };
                
                // Cari container Turnstile
                const containers = [
                    document.querySelector('.cf-turnstile'),
                    document.querySelector('[data-sitekey]'),
                    document.querySelector('div[class*="turnstile"]'),
                    document.querySelector('#cf-turnstile')
                ].filter(Boolean);
                
                if (containers.length > 0) {
                    result.container_present = true;
                    result.present = true;
                    result.debug_info.push('Container found: ' + containers.length);
                    
                    // Cek response token (jika sudah selesai)
                    const tokenInput = document.querySelector('input[name="cf-turnstile-response"]');
                    if (tokenInput && tokenInput.value) {
                        result.response_token = tokenInput.value.substring(0, 20) + '...';
                        result.success_shown = true;
                    }
                }
                
                // Cari iframe Turnstile
                const iframeSelectors = [
                    'iframe[src*="challenges.cloudflare.com"]',
                    'iframe[src*="turnstile"]',
                    'iframe[title*="Cloudflare"]',
                    'iframe[title*="Widget"]'
                ];
                
                let targetIframe = null;
                for (const sel of iframeSelectors) {
                    const iframe = document.querySelector(sel);
                    if (iframe) {
                        targetIframe = iframe;
                        result.iframe_found = true;
                        result.iframe_src = iframe.src ? iframe.src.substring(0, 60) : 'no-src';
                        result.present = true;
                        
                        // Cek dimensi iframe
                        const rect = iframe.getBoundingClientRect();
                        result.iframe_dimensions = {
                            width: rect.width,
                            height: rect.height,
                            visible: rect.width > 0 && rect.height > 0
                        };
                        
                        // Cek iframe loaded via readyState attempt
                        try {
                            // Tidak bisa akses contentDocument karena cross-origin
                            // Tapi kita bisa cek apakah iframe sudah render
                            if (rect.width >= 280 && rect.height >= 60) {
                                result.iframe_loaded = true;
                                result.debug_info.push('Iframe dimensions OK');
                            }
                        } catch(e) {}
                        
                        break;
                    }
                }
                
                // Cek tampilan checkbox dengan analisis visual
                if (targetIframe) {
                    const rect = targetIframe.getBoundingClientRect();
                    
                    // Turnstile checkbox biasanya memiliki ukuran standar
                    // Widget size: ~300x65 untuk normal, ~130x120 untuk compact
                    const isNormalSize = (rect.width >= 280 && rect.width <= 320) && (rect.height >= 60 && rect.height <= 80);
                    const isCompactSize = (rect.width >= 120 && rect.width <= 150) && (rect.height >= 110 && rect.height <= 140);
                    
                    if (isNormalSize || isCompactSize) {
                        result.checkbox_visible = true;
                        result.debug_info.push('Checkbox size detected: ' + (isNormalSize ? 'normal' : 'compact'));
                    }
                    
                    // Cek visibility
                    const style = window.getComputedStyle(targetIframe);
                    if (style.visibility === 'hidden' || style.display === 'none' || style.opacity === '0') {
                        result.checkbox_visible = false;
                        result.debug_info.push('Iframe hidden via CSS');
                    }
                }
                
                // Deteksi spinner (loading state)
                const spinnerSelectors = [
                    '.cf-turnstile-loading',
                    '[class*="spinner"]',
                    '[class*="loading"]',
                    'svg[class*="spin"]'
                ];
                
                for (const sel of spinnerSelectors) {
                    const spinner = document.querySelector(sel);
                    if (spinner) {
                        const rect = spinner.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            result.spinner_active = true;
                            result.debug_info.push('Spinner detected: ' + sel);
                            break;
                        }
                    }
                }
                
                // Deteksi success checkmark
                const successSelectors = [
                    '.cf-turnstile-success',
                    '[class*="success"]',
                    '[class*="verified"]'
                ];
                
                for (const sel of successSelectors) {
                    if (document.querySelector(sel)) {
                        result.success_shown = true;
                        break;
                    }
                }
                
                // Deteksi error state
                const errorSelectors = [
                    '.cf-turnstile-error',
                    '[class*="error"]',
                    '[class*="failed"]'
                ];
                
                for (const sel of errorSelectors) {
                    const el = document.querySelector(sel);
                    if (el && el.offsetWidth > 0) {
                        result.error_shown = true;
                        break;
                    }
                }
                
                // FINAL DECISION: Ready to click?
                result.ready_to_click = (
                    result.iframe_found &&
                    result.iframe_loaded &&
                    result.checkbox_visible &&
                    !result.spinner_active &&
                    !result.success_shown &&
                    !result.error_shown
                );
                
                // Override jika sudah success
                if (result.success_shown || result.response_token) {
                    result.ready_to_click = false; // Tidak perlu klik lagi
                }
                
                return result;
            })();
            """
            
            state = self.sb.execute_script(analysis_script)
            
            # Fix: Jika None, return default state
            if not state:
                return {
                    'present': False,
                    'iframe_found': False,
                    'iframe_loaded': False,
                    'checkbox_visible': False,
                    'spinner_active': False,
                    'success_shown': False,
                    'error_shown': False,
                    'ready_to_click': False,
                    'dimensions': None,
                    'response_token': None,
                }
            
            return state
                
        except Exception as e:
            # Return default state dengan error
            return {
                'present': False,
                'iframe_found': False,
                'iframe_loaded': False,
                'checkbox_visible': False,
                'spinner_active': False,
                'success_shown': False,
                'error_shown': False,
                'ready_to_click': False,
                'dimensions': None,
                'response_token': None,
                'error': str(e)
            }
    
    def _capture_screenshot(self):
        """Capture screenshot untuk AI analysis"""
        try:
            import base64
            import os
            
            # Create temp directory
            temp_dir = "turnstile_temp"
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Capture screenshot
            timestamp = int(time.time() * 1000)
            filepath = os.path.join(temp_dir, f"ts_{timestamp}.png")
            
            self.sb.save_screenshot(filepath)
            
            if os.path.exists(filepath):
                # Encode to base64
                with open(filepath, "rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode('utf-8')
                
                # Cleanup
                try:
                    os.remove(filepath)
                except:
                    pass
                
                return encoded
        except Exception as e:
            log(f"[AI] Screenshot error: {e}", "ERROR")
        
        return None
    
    def _analyze_with_groq_ai(self, base64_image):
        """Analyze screenshot dengan Groq Vision API - dengan rotasi API otomatis"""
        # Cek apakah masih ada API tersedia
        if not self.groq_manager or not self.groq_manager.has_available_api():
            return ("API_ERROR", "No API available")
        
        try:
            import requests
            import json
            
            # Get current API key dari manager
            api_key = self.groq_manager.get_current_api()
            if not api_key:
                return ("API_ERROR", "No API available")
            
            prompt = """Analyze this Cloudflare Turnstile screenshot.

Determine if the checkbox is READY to click.

READY indicators:
- Empty checkbox visible (not checked, not spinning)
- "Verify you are human" text visible
- No loading spinner
- Widget fully loaded

Respond with ONE WORD ONLY:
- READY (checkbox ready to click)
- NOT_READY (still loading)
- VERIFIED (already checked/success)
- ERROR (error state)

Then brief reason (max 8 words)."""

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.groq_manager.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 50
            }
            
            response = requests.post(
                self.GROQ_API_URL,
                headers=headers,
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                
                if content:
                    lines = content.strip().split('\n')
                    status = lines[0].strip().upper()
                    reason = lines[1].strip() if len(lines) > 1 else "No reason"
                    
                    # Validate status
                    if status not in ["READY", "NOT_READY", "VERIFIED", "ERROR"]:
                        for valid in ["READY", "NOT_READY", "VERIFIED", "ERROR"]:
                            if valid in status:
                                status = valid
                                break
                        else:
                            status = "NOT_READY"
                    
                    return (status, reason)
            
            # Handle rate limit / quota exhausted (429)
            if response.status_code == 429:
                log("[AI] Rate limit reached, rotating to next API...", "ERROR")
                self.groq_manager.mark_current_as_failed("rate_limit_429")
                
                # Retry with new API if available
                if self.groq_manager.has_available_api():
                    log("[AI] Retrying with new API...", "INFO")
                    return self._analyze_with_groq_ai(base64_image)  # Recursive retry
                else:
                    self.use_ai = False  # Disable AI untuk session ini
                    return ("API_ERROR", "All APIs exhausted")
            
            # Handle other errors (invalid API key, etc)
            if response.status_code in [401, 403]:
                log("[AI] Invalid API key, rotating...", "ERROR")
                self.groq_manager.mark_current_as_failed(f"http_{response.status_code}")
                
                if self.groq_manager.has_available_api():
                    return self._analyze_with_groq_ai(base64_image)
                else:
                    self.use_ai = False
                    return ("API_ERROR", "All APIs invalid")
            
            # Log error details untuk debugging
            try:
                error_body = response.json()
                error_msg = error_body.get("error", {}).get("message", "Unknown error")
                log(f"[AI] Groq API Error: {error_msg[:100]}", "ERROR")
            except:
                pass
            
            return ("API_ERROR", f"HTTP {response.status_code}")
            
        except Exception as e:
            log(f"[AI] Groq API error: {e}", "ERROR")
            return ("API_ERROR", str(e))
    
    def _check_with_ai(self):
        """Quick AI check dengan screenshot"""
        self.ai_checks += 1
        
        log(f"[AI] Check #{self.ai_checks} - Capturing screenshot...", "ACTION")
        
        # Capture screenshot
        screenshot_b64 = self._capture_screenshot()
        if not screenshot_b64:
            return ("API_ERROR", "Screenshot failed")
        
        # Analyze dengan Groq
        log("[AI] Analyzing with Groq Vision...", "ACTION")
        status, reason = self._analyze_with_groq_ai(screenshot_b64)
        
        log(f"[AI] Result: {status} - {reason}", "INFO")
        
        return (status, reason)
    
    def wait_for_turnstile_ready(self, max_wait=30, check_interval=2.0):
        """
        Wait sampai Turnstile benar-benar siap untuk diklik
        HYBRID: DOM check (cepat) + AI Vision (akurat) untuk proxy bervariasi
        
        Returns:
            tuple: (ready: bool, state: dict, wait_time: float)
        """
        self.detection_start = time.time()
        last_state_change = time.time()
        consecutive_ready = 0
        required_consecutive = 2  # Butuh 2x berturut-turut ready untuk yakin
        check_count = 0
        ai_check_interval = 5  # FIXED: AI check setiap 5x DOM check (save Groq quota)
        
        if self.use_ai:
            log("[TURNSTILE] Starting HYBRID detection (DOM + AI Vision)...", "ACTION")
        else:
            log("[TURNSTILE] Starting DOM-only detection...", "ACTION")
        
        while (time.time() - self.detection_start) < max_wait:
            elapsed = time.time() - self.detection_start
            check_count += 1
            self.dom_checks += 1
            
            try:
                # Step 1: DOM Check (cepat)
                state = self.get_turnstile_state()
                
                # Log state changes (tidak spam)
                state_key = f"{state.get('iframe_loaded')}-{state.get('checkbox_visible')}-{state.get('spinner_active')}"
                if state_key != self.last_state.get('key'):
                    self.last_state['key'] = state_key
                    log(f"[DOM] State @{elapsed:.1f}s - Loaded:{state.get('iframe_loaded')} Visible:{state.get('checkbox_visible')} Spinner:{state.get('spinner_active')}", "INFO")
                
                # Cek jika sudah success (tidak perlu klik)
                if state.get('success_shown') or state.get('response_token'):
                    log(f"[TURNSTILE] Already verified! Token present.", "SUCCESS")
                    return (False, state, elapsed)  # False = tidak perlu klik
                
                # Cek error state
                if state.get('error_shown'):
                    log(f"[TURNSTILE] Error state detected, may need retry", "ERROR")
                    return (True, state, elapsed)  # True = perlu klik untuk retry
                
                # Step 2: AI Vision Check (jika enabled dan kondisi tepat)
                use_ai_now = (
                    self.use_ai and 
                    (check_count % ai_check_interval == 0 or state.get('ready_to_click'))
                )
                
                if use_ai_now:
                    # AI Vision verification
                    ai_status, ai_reason = self._check_with_ai()
                    
                    if ai_status == "READY":
                        log(f"[AI] Confirmed READY: {ai_reason}", "SUCCESS")
                        # Double check dengan DOM
                        time.sleep(0.3)
                        confirm = self.get_turnstile_state()
                        if not confirm.get('spinner_active'):
                            total_wait = time.time() - self.detection_start
                            log(f"[TURNSTILE] READY TO CLICK after {total_wait:.2f}s (AI confirmed)", "SUCCESS")
                            return (True, confirm, total_wait)
                    
                    elif ai_status == "VERIFIED":
                        log(f"[AI] Already verified: {ai_reason}", "SUCCESS")
                        return (False, state, elapsed)
                    
                    elif ai_status == "ERROR":
                        log(f"[AI] Error state: {ai_reason}", "ERROR")
                        return (True, state, elapsed)
                    
                    elif ai_status == "NOT_READY":
                        log(f"[AI] Waiting... {ai_reason}", "INFO")
                        consecutive_ready = 0
                    
                    elif ai_status == "API_ERROR":
                        log(f"[AI] API error: {ai_reason}, using DOM only", "ERROR")
                        # Fallback ke DOM
                        if state.get('ready_to_click'):
                            consecutive_ready += 1
                        else:
                            consecutive_ready = 0
                
                else:
                    # DOM-only decision
                    if state.get('ready_to_click'):
                        consecutive_ready += 1
                        log(f"[DOM] Ready check {consecutive_ready}/{required_consecutive}", "INFO")
                        
                        if consecutive_ready >= required_consecutive:
                            # Extra verification
                            time.sleep(0.2)
                            final_state = self.get_turnstile_state()
                            
                            if final_state.get('ready_to_click'):
                                total_wait = time.time() - self.detection_start
                                log(f"[TURNSTILE] READY TO CLICK after {total_wait:.2f}s (DOM)", "SUCCESS")
                                return (True, final_state, total_wait)
                            else:
                                consecutive_ready = 0  # Reset
                    else:
                        consecutive_ready = 0
                    
            except Exception as e:
                log(f"[TURNSTILE] Check error: {e}", "ERROR")
            
            time.sleep(check_interval)
        
        # Timeout
        total_wait = time.time() - self.detection_start
        log(f"[TURNSTILE] Timeout after {total_wait:.1f}s - forcing attempt", "ERROR")
        
        # Final stats
        if self.use_ai:
            ai_rate = (self.ai_checks / max(self.dom_checks, 1)) * 100
            log(f"[STATS] DOM checks: {self.dom_checks}, AI checks: {self.ai_checks} ({ai_rate:.1f}%)", "INFO")
        
        return (True, self.get_turnstile_state(), total_wait)
    
    def smart_click_turnstile(self):
        """
        Smart click dengan timing yang presisi
        Returns: True jika berhasil bypass, False jika gagal
        """
        try:
            # Step 1: Tunggu ready state
            should_click, state, wait_time = self.wait_for_turnstile_ready()
            
            if not should_click:
                log("[TURNSTILE] No click needed (already verified)", "SUCCESS")
                return True
            
            # Step 2: Pre-click verification
            log(f"[TURNSTILE] Executing click after {wait_time:.1f}s wait...", "ACTION")
            
            # Gunakan uc_gui_click_captcha dari seleniumbase
            try:
                self.sb.uc_gui_click_captcha()
            except Exception as e:
                log(f"[TURNSTILE] uc_gui_click_captcha error: {e}", "ERROR")
                # Fallback: manual click pada iframe
                return self._fallback_click()
            
            # Step 3: Post-click verification
            post_wait = random.uniform(1.5, 2.5)
            time.sleep(post_wait)
            
            # Verify success
            post_state = self.get_turnstile_state()
            
            if post_state.get('success_shown') or post_state.get('response_token'):
                log("[TURNSTILE] Verification SUCCESS!", "SUCCESS")
                return True
            
            # Cek apakah Turnstile sudah hilang (halaman proceed)
            if not post_state.get('present'):
                log("[TURNSTILE] Widget gone - likely success", "SUCCESS")
                return True
            
            # Masih ada dan belum success
            if post_state.get('spinner_active'):
                log("[TURNSTILE] Processing... waiting extra time", "INFO")
                # Tunggu spinner selesai
                for _ in range(10):
                    time.sleep(0.5)
                    check = self.get_turnstile_state()
                    if check.get('success_shown') or not check.get('spinner_active'):
                        break
                
                final = self.get_turnstile_state()
                if final.get('success_shown') or final.get('response_token'):
                    log("[TURNSTILE] Delayed verification SUCCESS!", "SUCCESS")
                    return True
            
            log("[TURNSTILE] Verification inconclusive", "ERROR")
            return False
            
        except Exception as e:
            log(f"[TURNSTILE] Smart click error: {e}", "ERROR")
            return False
    
    def _fallback_click(self):
        """Fallback click method jika uc_gui_click_captcha gagal"""
        try:
            log("[TURNSTILE] Using fallback click method...", "ACTION")
            
            # Cari iframe
            iframe = None
            for sel in self.IFRAME_SELECTORS:
                try:
                    if self.sb.is_element_present(sel):
                        iframe = self.sb.find_element(sel)
                        break
                except:
                    continue
            
            if iframe:
                # Coba click di tengah iframe
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(self.sb.driver)
                actions.move_to_element(iframe)
                actions.click()
                actions.perform()
                
                time.sleep(2)
                return True
                
        except Exception as e:
            log(f"[TURNSTILE] Fallback click failed: {e}", "ERROR")
        
        return False
    
    def is_challenge_page(self):
        """Quick check apakah halaman ini adalah challenge page"""
        try:
            title = self.sb.get_title()
            url = self.sb.get_current_url()
            
            return (
                "Just a moment" in title or
                "Cloudflare" in title or
                "challenge" in url.lower() or
                "turnstile" in url.lower() or
                self.is_turnstile_present()
            )
        except:
            return False


class GroqAPIManager:
    """
    Manager untuk Groq API dengan rotasi otomatis.
    - Load API keys dari Firebase (bot{N}/groq/apis)
    - Load model dari Firebase (bot{N}/groq/model)
    - Rotasi otomatis jika API habis quota atau error
    - Fallback ke DOM-only mode jika semua API tidak tersedia
    - API mengikat pada bot number (bot1 hanya pakai API bot1)
    """
    
    def __init__(self, firebase_config, bot_number):
        self.firebase_config = firebase_config
        self.bot_number = bot_number
        self.api_keys = []           # List of API keys
        self.current_index = 0       # Index API key aktif
        self.failed_keys = set()     # API keys yang gagal (quota habis)
        self.model = "llama-3.2-90b-vision-preview"  # Default model
        self.enabled = True
        
        # Load dari Firebase saat init
        self.reload_from_firebase()
    
    def reload_from_firebase(self):
        """Load API keys dan model dari Firebase"""
        import requests
        
        try:
            base_url = self.firebase_config.get("databaseURL", "").rstrip("/")
            secret = self.firebase_config.get("databaseSecret", "")
            
            # Load API keys
            url_apis = f"{base_url}/bot{self.bot_number}/groq/apis.json?auth={secret}"
            resp_apis = requests.get(url_apis, timeout=10)
            
            if resp_apis.status_code == 200:
                data = resp_apis.json()
                if data:
                    # Firebase returns dict with auto-generated keys
                    self.api_keys = list(data.values()) if isinstance(data, dict) else data
                    # Filter hanya string yang valid (api key format)
                    self.api_keys = [k for k in self.api_keys if isinstance(k, str) and k.startswith("gsk_")]
            
            # Load model
            url_model = f"{base_url}/bot{self.bot_number}/groq/model.json?auth={secret}"
            resp_model = requests.get(url_model, timeout=10)
            
            if resp_model.status_code == 200:
                model_data = resp_model.json()
                if model_data and isinstance(model_data, str):
                    self.model = model_data
            
            # Log hasil
            if self.api_keys:
                print(f"[+] [GROQ] Loaded {len(self.api_keys)} API keys for bot{self.bot_number}")
                print(f"[*] [GROQ] Model: {self.model}")
            else:
                print(f"[!] [GROQ] No API keys found for bot{self.bot_number} - DOM-only mode")
                self.enabled = False
            
            return len(self.api_keys) > 0
            
        except Exception as e:
            print(f"[!] [GROQ] Error loading from Firebase: {e}")
            self.enabled = False
            return False
    
    def get_current_api(self):
        """Get API key yang sedang aktif, skip yang sudah failed"""
        if not self.api_keys:
            return None
        
        # Cari API yang belum failed
        attempts = 0
        while attempts < len(self.api_keys):
            current_key = self.api_keys[self.current_index]
            if current_key not in self.failed_keys:
                return current_key
            # Rotasi ke berikutnya
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            attempts += 1
        
        # Semua API sudah failed
        return None
    
    def mark_current_as_failed(self, reason="quota_exhausted"):
        """Tandai API saat ini sebagai gagal, rotasi ke berikutnya"""
        if self.api_keys:
            failed_key = self.api_keys[self.current_index]
            self.failed_keys.add(failed_key)
            # Mask API key untuk log (hanya tampilkan 8 karakter pertama)
            masked = failed_key[:12] + "..." if len(failed_key) > 12 else failed_key
            print(f"[!] [GROQ] API {masked} marked as failed: {reason}")
            print(f"[*] [GROQ] Failed APIs: {len(self.failed_keys)}/{len(self.api_keys)}")
            
            # Rotasi ke berikutnya
            self.rotate_to_next()
    
    def rotate_to_next(self):
        """Rotasi ke API key berikutnya"""
        if self.api_keys:
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            next_api = self.get_current_api()
            if next_api:
                masked = next_api[:12] + "..." if len(next_api) > 12 else next_api
                print(f"[*] [GROQ] Switched to API: {masked}")
    
    def has_available_api(self):
        """Cek apakah masih ada API yang bisa dipakai"""
        if not self.api_keys:
            return False
        return len(self.failed_keys) < len(self.api_keys)
    
    def get_status(self):
        """Get status untuk logging"""
        if not self.api_keys:
            return "No APIs loaded"
        available = len(self.api_keys) - len(self.failed_keys)
        return f"API {self.current_index+1}/{len(self.api_keys)}, available={available}"
    
    def reset_failed(self):
        """Reset semua failed keys (untuk session baru)"""
        self.failed_keys.clear()
        self.current_index = 0
        print(f"[*] [GROQ] Reset all failed keys, {len(self.api_keys)} APIs available")


def log(msg, level="INFO"):
    """Enhanced logging with file support"""
    global logger
    
    # Use enhanced logger if available
    if logger and ENHANCED_UTILS_AVAILABLE:
        logger.log(msg, level)
        return
    
    # Fallback to simple logging
    prefix = {
        "INFO": "[*]", "SUCCESS": "[+]", "ERROR": "[!]",
        "STEP": "[>]", "URL": "[URL]", "ACTION": "[>>]",
        "WARNING": "[!]", "DEBUG": "[D]"
    }
    print(f"{prefix.get(level, '[*]')} {msg}")
    sys.stdout.flush()


# =============================================================================
# IP BLACKLIST MANAGER - SIMPLIFIED
# =============================================================================

class IPBlacklistManager:
    """
    Manager untuk IP blacklist system - SUPER SIMPEL
    
    Struktur Firebase:
    /ip_blacklist/
        dead_ips/       - IP mati: { "104_28_15_200": "2025-01-22T10:30:00" }
        used_ips/       - IP sudah dipakai: { "68_220_62_145": "2025-01-22T11:00:00" }
    
    Hanya simpan IP dan waktu blacklist, tidak ada data lain.
    """
    
    CLOUDFLARE_TEST_URL = "https://www.cloudflare.com"
    
    def __init__(self, firebase_config):
        self.firebase_config = firebase_config
        self.base_url = firebase_config.get("databaseURL", "").rstrip("/")
        self.secret = firebase_config.get("databaseSecret", "")
    
    def _firebase_request(self, method, path, data=None):
        """Helper untuk Firebase REST API request"""
        url = f"{self.base_url}{path}.json?auth={self.secret}"
        try:
            if method == "GET":
                resp = requests.get(url, timeout=10)
            elif method == "PUT":
                resp = requests.put(url, json=data, timeout=10)
            else:
                return None
            
            if resp.status_code in [200, 204]:
                return resp.json() if resp.text else None
            return None
        except:
            return None
    
    def is_dead(self, ip):
        """Check apakah IP mati"""
        if not ip:
            return False
        ip_encoded = ip.replace(".", "_").replace(":", "_")
        result = self._firebase_request("GET", f"/ip_blacklist/dead_ips/{ip_encoded}")
        return result is not None
    
    def is_used(self, ip):
        """Check apakah IP sudah dipakai"""
        if not ip:
            return False
        ip_encoded = ip.replace(".", "_").replace(":", "_")
        result = self._firebase_request("GET", f"/ip_blacklist/used_ips/{ip_encoded}")
        return result is not None
    
    def is_blacklisted(self, ip):
        """Check apakah IP di-blacklist (dead atau used)"""
        return self.is_dead(ip) or self.is_used(ip)
    
    def add_to_dead(self, ip):
        """Add IP ke dead list - hanya simpan waktu"""
        if not ip or self.is_dead(ip):
            return False
        ip_encoded = ip.replace(".", "_").replace(":", "_")
        timestamp = datetime.now().isoformat()
        result = self._firebase_request("PUT", f"/ip_blacklist/dead_ips/{ip_encoded}", timestamp)
        if result:
            log(f"[DEAD-IP] {ip} added", "ERROR")
        return result is not None
    
    def add_to_used(self, ip):
        """Add IP ke used list - hanya simpan waktu"""
        if not ip or self.is_used(ip):
            return False
        ip_encoded = ip.replace(".", "_").replace(":", "_")
        timestamp = datetime.now().isoformat()
        result = self._firebase_request("PUT", f"/ip_blacklist/used_ips/{ip_encoded}", timestamp)
        if result:
            log(f"[USED-IP] {ip} added", "SUCCESS")
        return result is not None
    
    def test_ip_quality(self, ip, proxy_dict=None):
        """
        Test IP quality untuk Cloudflare
        UPDATED: Lower threshold untuk support ELITE techniques dengan IP busuk
        """
        log(f"[IP-TEST] Testing: {ip}", "ACTION")
        
        if self.is_blacklisted(ip):
            log(f"[IP-TEST] Blacklisted", "ERROR")
            return (0, False, "blacklisted")
        
        try:
            test_start = time.time()
            
            if proxy_dict:
                response = requests.get(
                    self.CLOUDFLARE_TEST_URL,
                    proxies=proxy_dict,
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"}
                )
            else:
                response = requests.get(
                    self.CLOUDFLARE_TEST_URL,
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"}
                )
            
            response_time = time.time() - test_start
            
            if response.status_code == 403:
                log(f"[IP-TEST] Blocked (403)", "ERROR")
                return (0, False, "blocked_403")
            
            if response.status_code == 503:
                log(f"[IP-TEST] Challenge (503) - OK with ELITE techniques", "INFO")
                return (30, True, "challenge_503_ok")  # Changed: Accept challenge
            
            if response.status_code not in [200, 301, 302]:
                log(f"[IP-TEST] Status {response.status_code}", "ERROR")
                return (10, False, f"status_{response.status_code}")
            
            quality_score = 100
            
            if response_time > 5:
                quality_score -= 30
            elif response_time > 3:
                quality_score -= 15
            
            if not response.headers.get('CF-RAY'):
                quality_score -= 10
            
            if 'challenge' in response.text.lower():
                quality_score -= 20  # Reduced from 40 (ELITE techniques can handle)
            
            if 'turnstile' in response.text.lower():
                quality_score -= 15  # Reduced from 30 (ELITE techniques can handle)
            
            # UPDATED: Lower threshold from 50 to 20 for ELITE techniques
            can_use = quality_score >= 20
            
            if can_use:
                if quality_score >= 50:
                    log(f"[IP-TEST] Quality: {quality_score}/100 (Good IP)", "SUCCESS")
                else:
                    log(f"[IP-TEST] Quality: {quality_score}/100 (Bad IP - ELITE mode will activate)", "INFO")
                return (quality_score, True, "acceptable")
            else:
                log(f"[IP-TEST] Quality: {quality_score}/100 (Too poor even for ELITE)", "ERROR")
                return (quality_score, False, "poor_quality")
        
        except requests.exceptions.Timeout:
            log(f"[IP-TEST] Timeout", "ERROR")
            return (0, False, "timeout")
        
        except requests.exceptions.ProxyError:
            log(f"[IP-TEST] Proxy error", "ERROR")
            return (0, False, "proxy_error")
        
        except Exception as e:
            log(f"[IP-TEST] Error: {e}", "ERROR")
            return (0, False, "test_error")
    
    def get_blacklist_stats(self):
        """Get blacklist statistics"""
        dead_ips = self._firebase_request("GET", "/ip_blacklist/dead_ips")
        used_ips = self._firebase_request("GET", "/ip_blacklist/used_ips")
        
        total_dead = len(dead_ips) if dead_ips else 0
        total_used = len(used_ips) if used_ips else 0
        
        return {
            "total_dead": total_dead,
            "total_used": total_used,
            "total_blacklisted": total_dead + total_used
        }


class SafelinkBypassV2:

    def __init__(self, sb, original_ip=None, expected_proxy_ip=None, groq_manager=None, profile_id=None):
        self.sb = sb
        self.anchor = None
        self.processed = set()
        self.closed_popups = set()
        
        # === COOKIES INJECTION SUPPORT ===
        self.saved_cookies_to_inject = []  # Cookies dari Firebase untuk di-inject
        
        # === SUPER ELITE: Profile-Based Fingerprint ===
        # Fingerprint konsisten per profile (bypass cross-session tracking)
        self.profile_id = profile_id or "default"
        self.fingerprint = self.load_or_create_fingerprint()
        
        self.human = HumanBehavior(sb)
        
        # ADVANCED: Turnstile Detector dengan Groq AI (optional)
        self.turnstile = TurnstileDetector(sb, use_ai=True, groq_manager=groq_manager)
        
        # IP Protection
        self.original_ip = original_ip
        self.expected_proxy_ip = expected_proxy_ip
        
        self.main_domains = ["sfl.gl", "tutwuri.id", "downloadku.com", "cararegistrasi.com", "app.khaddavi.net"]
        self.cf_cookies = []
        self.step_delays = [random.uniform(2, 8) for _ in range(60)]
        
        # === TOP-TIER 2026 TECHNIQUES ===
        # TLS + HTTP/2 Fingerprinting
        self.tls_session = TopTierTLSSession()
        
        # Log TLS session info
        tls_info = self.tls_session.get_session_info()
        if tls_info['tls_perfect']:
            log(f"[TOP-TIER] TLS Fingerprint: PERFECT ({tls_info['type']})", "SUCCESS")
        if tls_info['http2_perfect']:
            log(f"[TOP-TIER] HTTP/2 Fingerprint: PERFECT", "SUCCESS")
        
        # Bad IP Mode
        self.bad_ip_mode = False  # Auto-detect jika IP bermasalah
        self.turnstile_fail_count = 0
        self.max_turnstile_retries = 4  # FIXED: Max 4x sesuai request user (hemat waktu & Groq quota)
        
        # Cookie Manager (cf_clearance reuse)
        self.cf_clearance_cookies = {}  # domain -> cookie
        self.cookie_expiry = {}  # domain -> timestamp
        
        # Behavioral tracking
        self.bypass_attempts = 0
        self.bypass_successes = 0
        
        # === SUPER ELITE: Memory Pattern Normalization ===
        self.normalize_memory_pattern()
    
    def load_or_create_fingerprint(self):
        """Load fingerprint dari file atau create baru (SUPER ELITE: Consistent fingerprint)"""
        profile_dir = "./profiles"
        os.makedirs(profile_dir, exist_ok=True)
        fingerprint_file = f"{profile_dir}/{self.profile_id}_fingerprint.json"
        
        if os.path.exists(fingerprint_file):
            try:
                with open(fingerprint_file, 'r') as f:
                    data = json.load(f)
                    log(f"[PROFILE] Loaded fingerprint for profile: {self.profile_id}", "SUCCESS")
                    # Recreate fingerprint object dari saved data
                    fp = AdvancedFingerprintRandomizer()
                    # Restore saved values
                    for key, value in data.items():
                        setattr(fp, key, value)
                    return fp
            except Exception as e:
                log(f"[PROFILE] Failed to load fingerprint: {e}", "ERROR")
        
        # Create new fingerprint
        log(f"[PROFILE] Creating new fingerprint for profile: {self.profile_id}", "INFO")
        fp = AdvancedFingerprintRandomizer()
        
        # Save fingerprint
        try:
            # Save important attributes
            data = {
                'session_id': fp.session_id,
                'session_seed': fp.session_seed,
                # Add more attributes as needed
            }
            with open(fingerprint_file, 'w') as f:
                json.dump(data, f)
            log(f"[PROFILE] Saved fingerprint to: {fingerprint_file}", "SUCCESS")
        except Exception as e:
            log(f"[PROFILE] Failed to save fingerprint: {e}", "ERROR")
        
        return fp
    
    def normalize_memory_pattern(self):
        """Normalize memory pattern untuk bypass memory forensics (SUPER ELITE)"""
        try:
            # Inject script untuk normalize memory usage
            normalize_script = """
            // SUPER ELITE: Memory Pattern Normalization
            (function() {
                // Reduce object count (Kasada detection)
                if (window.gc) {
                    window.gc(); // Force garbage collection
                }
                
                // Hide automation objects
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                
                // Normalize performance memory (if available)
                if (window.performance && window.performance.memory) {
                    // Make it read-only to prevent detection
                    Object.defineProperty(window.performance, 'memory', {
                        get: function() {
                            return {
                                jsHeapSizeLimit: 2172649472,  // Normal Chrome
                                totalJSHeapSize: 50000000 + Math.random() * 10000000,
                                usedJSHeapSize: 30000000 + Math.random() * 10000000
                            };
                        }
                    });
                }
                
                console.log('[ELITE] Memory pattern normalized');
            })();
            """
            self.sb.execute_script(normalize_script)
            log("[ELITE] Memory pattern normalized", "SUCCESS")
        except Exception as e:
            log(f"[ELITE] Memory normalization failed: {e}", "ERROR")
        
    def is_valid_session(self):
        """Cek apakah sesi browser masih aktif"""
        try:
            self.sb.driver.current_window_handle
            return True
        except:
            try:
                handles = self.sb.driver.window_handles
                if handles:
                    if self.anchor in handles:
                        self.sb.driver.switch_to.window(self.anchor)
                    else:
                        self.sb.driver.switch_to.window(handles[0])
                    return True
            except:
                pass
        return False
    
    def is_main_domain(self, url):
        """Cek apakah URL termasuk domain utama - UPDATED: Auto-add new domains"""
        if not url:
            return False
        
        # Check existing domains
        for domain in self.main_domains:
            if domain in url.lower():
                return True
        
        # AUTO-DETECT: Jika URL dari TARGET_URL atau hasil redirect dari main domain
        # Extract domain dari URL
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            current_domain = parsed.netloc.lower()
            
            # Check if this is a redirect from sfl.gl or other shortlink
            # Common patterns: cararegistrasi.com, downloadku.com, etc.
            # If domain looks like a content site (not ad), add it
            ad_patterns = ["eatcells", "revenuecpmgate", "sportshard", "google", "doubleclick", "ads"]
            is_ad = any(pattern in current_domain for pattern in ad_patterns)
            
            if not is_ad and current_domain:
                # Extract base domain (remove www.)
                base_domain = current_domain.replace("www.", "")
                
                # Add to main_domains if not already there
                if base_domain not in self.main_domains:
                    self.main_domains.append(base_domain)
                    log(f"[AUTO-DETECT] Added new main domain: {base_domain}", "SUCCESS")
                    return True
        except:
            pass
        
        return False
    
    def wait_for_page_ready(self, max_wait=10, check_interval=0.5):
        """
        Tunggu halaman siap - SIMPLE VERSION.
        Hanya cek readyState, max 10 detik.
        """
        start_time = time.time()
        
        while (time.time() - start_time) < max_wait:
            try:
                ready_state = self.sb.execute_script("return document.readyState")
                
                # Langsung lanjut jika complete atau interactive
                if ready_state in ["complete", "interactive"]:
                    return True
                    
            except:
                pass
            
            time.sleep(check_interval)
        
        # Timeout - lanjut aja
        return False



    def set_anchor(self):
        """Set anchor tab dengan handle"""
        try:
            self.anchor = self.sb.driver.current_window_handle
            self.processed.add(self.anchor)
            url = self.sb.get_current_url()
            log(f"Anchor set: {self.anchor[:8]}... URL: {url[:40]}...", "SUCCESS")
        except Exception as e:
            log(f"Anchor error: {e}", "ERROR")
    

    def recover_from_ad(self):
        """Kembali dari halaman iklan dengan BACK browser atau switch window"""
        if not self.is_valid_session():
            return False
        
        try:
            current_url = self.sb.get_current_url()
            is_on_main_domain = self.is_main_domain(current_url)
            is_vignette = "#google_vignette" in current_url
            
            if not is_on_main_domain or is_vignette:
                log(f"Detected potential ad/vignette: {current_url[:40]}", "ACTION")
                
                if is_vignette:
                    try:
                        clean_url = current_url.split("#")[0]
                        self.sb.open(clean_url)
                        time.sleep(2)
                        if self.is_main_domain(self.sb.get_current_url()):
                            return True
                    except:
                        pass

                log("Executing browser BACK...", "ACTION")
                self.sb.driver.back()
                time.sleep(2)
                
                new_url = self.sb.get_current_url()
                if self.is_main_domain(new_url):
                    log(f"Recovered to: {new_url[:40]}...", "SUCCESS")
                    return True
                else:
                    log("Back failed, forcing switch to anchor", "INFO")
                    return self.back_to_anchor()
            return False
        except Exception as e:
            log(f"Recovery error: {e}", "ERROR")
            return self.back_to_anchor()

    def back_to_anchor(self):
        """Kembali ke tab anchor (FIXED: Timeout Protection)"""
        if not self.is_valid_session():
            return
        try:
            # FIX: Set timeout dulu
            self.sb.driver.set_page_load_timeout(3)
            
            if self.anchor and self.sb.driver.current_window_handle != self.anchor:
                try:
                    self.sb.driver.switch_to.window(self.anchor)
                except Exception as e:
                    log(f"Failed to switch to anchor: {str(e)[:30]}", "ERROR")
                    # Anchor rusak, cari yang baru
                    self.anchor = None
        except:
            pass
        
        # Jika anchor hilang/rusak, cari tab main domain
        if not self.anchor:
            try:
                handles = self.sb.driver.window_handles
                for h in handles:
                    try:
                        self.sb.driver.switch_to.window(h)
                        # FIX: Get URL dengan timeout protection
                        url = self.sb.driver.execute_script("return window.location.href;")
                        if self.is_main_domain(url):
                            self.anchor = h
                            log(f"Recovered anchor: {h[:8]}...", "SUCCESS")
                            break
                    except:
                        continue
            except:
                pass
        
        # Reset timeout
        try:
            self.sb.driver.set_page_load_timeout(30)
        except:
            pass


    def inject_protections(self):
        """Inject stealth + fingerprint scripts dengan timing natural"""
        if not self.is_valid_session():
            return
        try:
            # === SUPER ELITE: Memory normalization FIRST ===
            self.normalize_memory_pattern()
            
            # === SUPER ELITE: Anti-Akamai/DataDome/Kasada ===
            self.inject_anti_sensor_protection()
            
            # Inject stealth dulu
            try:
                self.sb.execute_script(self.fingerprint.get_stealth_script())
                log("[INJECT] Stealth script injected", "SUCCESS")
            except Exception as e:
                log(f"[INJECT] Stealth error: {str(e)[:100]}", "ERROR")
            
            # Natural delay - simulate human page load wait
            time.sleep(random.uniform(0.3, 0.8))
            
            # Inject fingerprint
            try:
                self.sb.execute_script(self.fingerprint.get_fingerprint_script())
                log("[INJECT] Fingerprint script injected", "SUCCESS")
            except Exception as e:
                log(f"[INJECT] Fingerprint error: {str(e)[:100]}", "ERROR")
            
            # Another natural delay
            time.sleep(random.uniform(0.2, 0.5))
            
            log("Protection injected", "SUCCESS")
        except Exception as e:
            log(f"Injection error: {e}", "ERROR")
    
    def inject_anti_sensor_protection(self):
        """TOP-TIER 2026: Advanced Anti-Sensor Protection (Akamai/DataDome/Kasada/PerimeterX)"""
        try:
            anti_sensor_script = """
            (function() {
                console.log('[TOP-TIER 2026] Anti-sensor protection loading...');
                
                // === 1. AGGRESSIVE SCRIPT BLOCKING ===
                const originalAppendChild = Node.prototype.appendChild;
                const originalInsertBefore = Node.prototype.insertBefore;
                
                const blockPatterns = [
                    // Akamai
                    '/_sec/', '/akam/', 'akamai', 'sensor.js', 'bm.js',
                    // DataDome
                    'datadome', 'dd.js', 'captcha-delivery',
                    // Kasada
                    'kasada', '/ips.js', '/149e9513fceea.js',
                    // PerimeterX / HUMAN
                    'perimeterx', 'px-cdn', 'pxchk', 'human-sec',
                    // Shape / F5
                    'shape-security', 'f5-bot-defense', '/akjs/',
                    // Generic bot detection
                    'bot-detection', 'antibot', 'challenge'
                ];
                
                function shouldBlock(src) {
                    return blockPatterns.some(pattern => src.toLowerCase().includes(pattern));
                }
                
                Node.prototype.appendChild = function(child) {
                    if (child.tagName === 'SCRIPT' && child.src && shouldBlock(child.src)) {
                        console.log('[BLOCKED] Sensor script:', child.src);
                        return child;
                    }
                    return originalAppendChild.call(this, child);
                };
                
                Node.prototype.insertBefore = function(child, ref) {
                    if (child.tagName === 'SCRIPT' && child.src && shouldBlock(child.src)) {
                        console.log('[BLOCKED] Sensor script (insertBefore):', child.src);
                        return child;
                    }
                    return originalInsertBefore.call(this, child, ref);
                };
                
                // === 2. FAKE SENSOR GLOBALS ===
                const sensorGlobals = [
                    '_abck', 'bm_sz', 'ak_bmsc',  // Akamai
                    'ddvs', 'dd', 'dataDomeOptions',  // DataDome
                    'kpsdk', 'KPSDK',  // Kasada
                    '_pxAppId', '_pxJsClientSrc', 'pxInit',  // PerimeterX
                    'NREUM', '_pxAction'  // Generic
                ];
                
                sensorGlobals.forEach(global => {
                    Object.defineProperty(window, global, {
                        get: () => undefined,
                        set: () => {},
                        configurable: false
                    });
                });
                
                // === 3. INTERCEPT ALL NETWORK REQUESTS ===
                const originalFetch = window.fetch;
                window.fetch = function(...args) {
                    const url = typeof args[0] === 'string' ? args[0] : args[0]?.url || '';
                    if (shouldBlock(url)) {
                        console.log('[BLOCKED] Fetch to sensor:', url);
                        return Promise.resolve(new Response('{}', {status: 200}));
                    }
                    return originalFetch.apply(this, args);
                };
                
                const originalXHROpen = XMLHttpRequest.prototype.open;
                const originalXHRSend = XMLHttpRequest.prototype.send;
                XMLHttpRequest.prototype.open = function(method, url, ...rest) {
                    this._url = url;
                    return originalXHROpen.call(this, method, url, ...rest);
                };
                XMLHttpRequest.prototype.send = function(...args) {
                    if (this._url && shouldBlock(this._url)) {
                        console.log('[BLOCKED] XHR to sensor:', this._url);
                        return;
                    }
                    return originalXHRSend.apply(this, args);
                };
                
                // === 4. ADVANCED EVENT TIMING NORMALIZATION ===
                // Multi-modal jitter (realistic human variance)
                function getRealisticJitter() {
                    // 70% small jitter (0-2ms), 20% medium (2-5ms), 10% large (5-10ms)
                    const rand = Math.random();
                    if (rand < 0.7) return Math.random() * 2;
                    if (rand < 0.9) return 2 + Math.random() * 3;
                    return 5 + Math.random() * 5;
                }
                
                const originalAddEventListener = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, ...rest) {
                    if (typeof listener === 'function') {
                        const wrappedListener = function(event) {
                            const delay = getRealisticJitter();
                            setTimeout(() => listener.call(this, event), delay);
                        };
                        return originalAddEventListener.call(this, type, wrappedListener, ...rest);
                    }
                    return originalAddEventListener.call(this, type, listener, ...rest);
                };
                
                // === 5. COMPREHENSIVE AUTOMATION TRACE REMOVAL ===
                const automationProps = [
                    'cdc_adoQpoasnfa76pfcZLmcfl_Array',
                    'cdc_adoQpoasnfa76pfcZLmcfl_Promise',
                    'cdc_adoQpoasnfa76pfcZLmcfl_Symbol',
                    '$cdc_asdjflasutopfhvcZLmcfl_',
                    '$chrome_asyncScriptInfo',
                    '__webdriver_script_fn',
                    '__driver_evaluate',
                    '__webdriver_evaluate',
                    '__selenium_evaluate',
                    '__fxdriver_evaluate',
                    '__driver_unwrapped',
                    '__webdriver_unwrapped',
                    '__selenium_unwrapped',
                    '__fxdriver_unwrapped',
                    '__webdriver_script_func',
                    '__webdriver_script_function',
                    '_Selenium_IDE_Recorder',
                    '_selenium',
                    'calledSelenium',
                    '__nightmare',
                    '_phantom',
                    'callPhantom',
                    '__phantomas'
                ];
                
                automationProps.forEach(prop => {
                    delete window[prop];
                    delete document[prop];
                });
                
                // === 6. PERFORMANCE API ADVANCED NORMALIZATION ===
                const originalPerformanceNow = Performance.prototype.now;
                let lastTime = originalPerformanceNow.call(performance);
                let jitterAccumulator = 0;
                
                Performance.prototype.now = function() {
                    const realTime = originalPerformanceNow.call(this);
                    // Consistent jitter per session (not random every call)
                    jitterAccumulator += (Math.random() - 0.5) * 0.1;
                    jitterAccumulator = Math.max(-1, Math.min(1, jitterAccumulator));
                    return realTime + jitterAccumulator;
                };
                
                // === 7. BLOCK RESOURCE TIMING API (fingerprinting) ===
                const originalGetEntries = Performance.prototype.getEntries;
                Performance.prototype.getEntries = function() {
                    const entries = originalGetEntries.call(this);
                    // Filter out sensor script entries
                    return entries.filter(e => !shouldBlock(e.name || ''));
                };
                
                // === 8. MUTATION OBSERVER PROTECTION ===
                const originalObserve = MutationObserver.prototype.observe;
                MutationObserver.prototype.observe = function(target, options) {
                    // Add delay to mutation callbacks (anti-timing attack)
                    const originalCallback = this.callback;
                    this.callback = function(mutations, observer) {
                        setTimeout(() => originalCallback(mutations, observer), getRealisticJitter());
                    };
                    return originalObserve.call(this, target, options);
                };
                
                console.log('[TOP-TIER 2026] Anti-sensor protection loaded!');
            })();
            """
            self.sb.execute_script(anti_sensor_script)
            log("[TOP-TIER 2026] Anti-sensor protection injected", "SUCCESS")
        except Exception as e:
            log(f"[TOP-TIER 2026] Anti-sensor injection failed: {e}", "ERROR")
    
    def inject_bad_ip_enhancements(self):
        """
        TEKNIK ELITE UNTUK IP BUSUK
        Berdasarkan riset Scrapfly, CapSolver, dan Cloudflare official docs
        Inject behavioral biometrics yang REALISTIC
        """
        if not self.is_valid_session():
            return
        
        try:
            # ELITE BEHAVIORAL BIOMETRICS SCRIPT
            elite_script = """
            (function() {
                // === BEZIER CURVE MOUSE MOVEMENT ===
                function generateBezierCurve(start, end, controlPoints) {
                    const points = [];
                    for (let t = 0; t <= 1; t += 0.02) {
                        const x = Math.pow(1-t, 3) * start.x + 
                                 3 * Math.pow(1-t, 2) * t * controlPoints[0].x +
                                 3 * (1-t) * Math.pow(t, 2) * controlPoints[1].x +
                                 Math.pow(t, 3) * end.x;
                        const y = Math.pow(1-t, 3) * start.y + 
                                 3 * Math.pow(1-t, 2) * t * controlPoints[0].y +
                                 3 * (1-t) * Math.pow(t, 2) * controlPoints[1].y +
                                 Math.pow(t, 3) * end.y;
                        points.push({x: Math.round(x), y: Math.round(y)});
                    }
                    return points;
                }
                
                // === HUMAN-LIKE MOUSE MOVEMENT ===
                function simulateHumanMouseMove(targetX, targetY) {
                    const start = {
                        x: Math.random() * window.innerWidth, 
                        y: Math.random() * window.innerHeight
                    };
                    const end = {x: targetX, y: targetY};
                    
                    // Random control points untuk curve
                    const cp1 = {
                        x: start.x + (end.x - start.x) * 0.3 + (Math.random() - 0.5) * 100,
                        y: start.y + (end.y - start.y) * 0.3 + (Math.random() - 0.5) * 100
                    };
                    const cp2 = {
                        x: start.x + (end.x - start.x) * 0.7 + (Math.random() - 0.5) * 100,
                        y: start.y + (end.y - start.y) * 0.7 + (Math.random() - 0.5) * 100
                    };
                    
                    const path = generateBezierCurve(start, end, [cp1, cp2]);
                    
                    // Animate dengan variable speed (acceleration/deceleration)
                    let index = 0;
                    const interval = setInterval(() => {
                        if (index >= path.length) {
                            clearInterval(interval);
                            return;
                        }
                        
                        const point = path[index];
                        const event = new MouseEvent('mousemove', {
                            bubbles: true,
                            cancelable: true,
                            clientX: point.x,
                            clientY: point.y,
                            movementX: index > 0 ? point.x - path[index-1].x : 0,
                            movementY: index > 0 ? point.y - path[index-1].y : 0
                        });
                        
                        document.dispatchEvent(event);
                        
                        // Variable speed: faster in middle, slower at start/end
                        const progress = index / path.length;
                        const speed = progress < 0.5 ? 
                                     5 + progress * 10 :  // Accelerate
                                     15 - (progress - 0.5) * 10;  // Decelerate
                        
                        index += Math.max(1, Math.floor(speed / 5));
                    }, 8);
                }
                
                // === REALISTIC SCROLL dengan momentum ===
                function simulateHumanScroll() {
                    let scrollPos = window.scrollY;
                    const maxScroll = document.body.scrollHeight - window.innerHeight;
                    const targetScroll = Math.random() * maxScroll;
                    const direction = targetScroll > scrollPos ? 1 : -1;
                    
                    let velocity = 0;
                    const maxVelocity = 20;
                    const acceleration = 2;
                    const friction = 0.95;
                    
                    const scrollInterval = setInterval(() => {
                        velocity = Math.min(velocity + acceleration, maxVelocity);
                        velocity *= friction;
                        
                        scrollPos += velocity * direction;
                        window.scrollTo(0, scrollPos);
                        
                        if (Math.abs(scrollPos - targetScroll) < 50 || velocity < 0.5) {
                            clearInterval(scrollInterval);
                            window.scrollTo(0, targetScroll);
                        }
                    }, 16);  // 60fps
                }
                
                // === MICRO-MOVEMENTS (jitter) ===
                setInterval(() => {
                    const jitterX = (Math.random() - 0.5) * 5;
                    const jitterY = (Math.random() - 0.5) * 5;
                    
                    const event = new MouseEvent('mousemove', {
                        bubbles: true,
                        clientX: window.innerWidth / 2 + jitterX,
                        clientY: window.innerHeight / 2 + jitterY
                    });
                    document.dispatchEvent(event);
                }, 100 + Math.random() * 200);
                
                // === KEYBOARD EVENTS ===
                const keys = ['Tab', 'Shift', 'Control', 'Alt'];
                setInterval(() => {
                    const key = keys[Math.floor(Math.random() * keys.length)];
                    const keydownEvent = new KeyboardEvent('keydown', {key: key, bubbles: true});
                    const keyupEvent = new KeyboardEvent('keyup', {key: key, bubbles: true});
                    
                    document.dispatchEvent(keydownEvent);
                    setTimeout(() => document.dispatchEvent(keyupEvent), 50 + Math.random() * 150);
                }, 5000 + Math.random() * 10000);
                
                // === FOCUS/BLUR CYCLES ===
                setInterval(() => {
                    window.dispatchEvent(new Event('blur'));
                    setTimeout(() => {
                        window.dispatchEvent(new Event('focus'));
                    }, 1000 + Math.random() * 3000);
                }, 10000 + Math.random() * 15000);
                
                // === AUTO-TRIGGER ===
                setTimeout(() => simulateHumanScroll(), 2000);
                setTimeout(() => {
                    const iframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                    if (iframe) {
                        const rect = iframe.getBoundingClientRect();
                        simulateHumanMouseMove(rect.left + rect.width / 2, rect.top + rect.height / 2);
                    }
                }, 5000);
                
                // === PERFORMANCE TIMING JITTER ===
                const originalNow = Performance.prototype.now;
                let timeOffset = 0;
                Performance.prototype.now = function() {
                    const realTime = originalNow.call(performance);
                    timeOffset += (Math.random() - 0.5) * 0.1;
                    return realTime + timeOffset;
                };
            })();
            """
            
            self.sb.execute_script(elite_script)
            log("[ELITE] Behavioral biometrics injected (Bezier curves, momentum scroll, jitter)", "SUCCESS")
            
        except Exception as e:
            log(f"[ELITE] Enhancement injection error: {e}", "ERROR")
    
    def warm_up_session(self):
        """Session warming disabled - fokus langsung ke target URL"""
        pass
    
    def save_cf_clearance_cookie(self, domain):
        """
        ELITE TECHNIQUE: Save cf_clearance cookie untuk reuse
        Cookie ini valid 30 menit - 24 jam tergantung Challenge Passage setting
        """
        try:
            cookies = self.sb.driver.get_cookies()
            for cookie in cookies:
                if cookie['name'] == 'cf_clearance':
                    self.cf_clearance_cookies[domain] = cookie
                    # Assume cookie valid 30 menit (conservative)
                    self.cookie_expiry[domain] = time.time() + 1800
                    log(f"[COOKIE] Saved cf_clearance for {domain} (valid 30 min)", "SUCCESS")
                    return True
            return False
        except Exception as e:
            log(f"[COOKIE] Save error: {e}", "ERROR")
            return False
    
    def is_cf_cookie_valid(self, domain):
        """Check apakah cf_clearance cookie masih valid"""
        if domain not in self.cf_clearance_cookies:
            return False
        if time.time() > self.cookie_expiry[domain]:
            log(f"[COOKIE] Expired for {domain}", "INFO")
            return False
        return True
    
    def reuse_cf_clearance_cookie(self, domain):
        """
        ELITE TECHNIQUE: Reuse cf_clearance cookie
        Ini menghemat 95% bypass attempts!
        """
        if not self.is_cf_cookie_valid(domain):
            return False
        
        try:
            cookie = self.cf_clearance_cookies[domain]
            self.sb.driver.add_cookie(cookie)
            log(f"[COOKIE] Reused cf_clearance for {domain}", "SUCCESS")
            return True
        except Exception as e:
            log(f"[COOKIE] Reuse error: {e}", "ERROR")
            return False
    
    def wait_for_success(self, timeout=10):
        """
        FIXED: Wait for Turnstile success after click
        Check if Turnstile berhasil di-bypass
        """
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            try:
                # Check if Turnstile gone (success)
                if not self.turnstile.is_turnstile_present():
                    log("[TURNSTILE] Widget gone - success!", "SUCCESS")
                    return True
                
                # Check for success indicators
                state = self.turnstile.get_turnstile_state()
                if state.get('success_shown') or state.get('response_token'):
                    log("[TURNSTILE] Success token detected!", "SUCCESS")
                    return True
                
                # Check for error state
                if state.get('error_shown'):
                    log("[TURNSTILE] Error state detected", "ERROR")
                    return False
                
                time.sleep(0.5)
            except Exception as e:
                log(f"[TURNSTILE] Check error: {str(e)[:50]}", "ERROR")
                pass
        
        log("[TURNSTILE] Timeout waiting for success", "ERROR")
        return False
    
    def simulate_bezier_mouse_to_turnstile(self):
        """
        ELITE TECHNIQUE: Simulate realistic mouse movement dengan Bezier curve
        Ini salah satu teknik paling penting untuk IP busuk!
        """
        try:
            # Find Turnstile iframe
            iframe_script = """
            const iframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
            if (iframe) {
                const rect = iframe.getBoundingClientRect();
                return {
                    x: rect.left + rect.width / 2,
                    y: rect.top + rect.height / 2,
                    found: true
                };
            }
            return {found: false};
            """
            
            result = self.sb.execute_script(iframe_script)
            
            if not result or not result.get('found'):
                log("[MOUSE] Turnstile iframe not found", "ERROR")
                return False
            
            target_x = result['x']
            target_y = result['y']
            
            # Inject Bezier curve mouse movement
            bezier_script = f"""
            (function() {{
                const targetX = {target_x};
                const targetY = {target_y};
                
                // Generate Bezier curve
                function generateBezierCurve(start, end, cp1, cp2) {{
                    const points = [];
                    for (let t = 0; t <= 1; t += 0.02) {{
                        const x = Math.pow(1-t, 3) * start.x + 
                                 3 * Math.pow(1-t, 2) * t * cp1.x +
                                 3 * (1-t) * Math.pow(t, 2) * cp2.x +
                                 Math.pow(t, 3) * end.x;
                        const y = Math.pow(1-t, 3) * start.y + 
                                 3 * Math.pow(1-t, 2) * t * cp1.y +
                                 3 * (1-t) * Math.pow(t, 2) * cp2.y +
                                 Math.pow(t, 3) * end.y;
                        points.push({{x: Math.round(x), y: Math.round(y)}});
                    }}
                    return points;
                }}
                
                const start = {{
                    x: Math.random() * window.innerWidth,
                    y: Math.random() * window.innerHeight
                }};
                const end = {{x: targetX, y: targetY}};
                
                // Random control points
                const cp1 = {{
                    x: start.x + (end.x - start.x) * 0.3 + (Math.random() - 0.5) * 100,
                    y: start.y + (end.y - start.y) * 0.3 + (Math.random() - 0.5) * 100
                }};
                const cp2 = {{
                    x: start.x + (end.x - start.x) * 0.7 + (Math.random() - 0.5) * 100,
                    y: start.y + (end.y - start.y) * 0.7 + (Math.random() - 0.5) * 100
                }};
                
                const path = generateBezierCurve(start, end, cp1, cp2);
                
                // Animate with variable speed
                let index = 0;
                const interval = setInterval(() => {{
                    if (index >= path.length) {{
                        clearInterval(interval);
                        return;
                    }}
                    
                    const point = path[index];
                    const event = new MouseEvent('mousemove', {{
                        bubbles: true,
                        cancelable: true,
                        clientX: point.x,
                        clientY: point.y,
                        movementX: index > 0 ? point.x - path[index-1].x : 0,
                        movementY: index > 0 ? point.y - path[index-1].y : 0
                    }});
                    
                    document.dispatchEvent(event);
                    
                    // Variable speed: acceleration/deceleration
                    const progress = index / path.length;
                    const speed = progress < 0.5 ? 
                                 5 + progress * 10 :
                                 15 - (progress - 0.5) * 10;
                    
                    index += Math.max(1, Math.floor(speed / 5));
                }}, 8);
                
                // Hover event at end
                setTimeout(() => {{
                    const iframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                    if (iframe) {{
                        const hoverEvent = new MouseEvent('mouseover', {{
                            bubbles: true,
                            clientX: targetX,
                            clientY: targetY
                        }});
                        iframe.dispatchEvent(hoverEvent);
                    }}
                }}, path.length * 8 + 100);
            }})();
            """
            
            self.sb.execute_script(bezier_script)
            
            # Wait for animation to complete
            time.sleep(random.uniform(1.5, 2.5))
            
            log("[MOUSE] Bezier curve movement completed", "SUCCESS")
            return True
            
        except Exception as e:
            log(f"[MOUSE] Bezier movement error: {e}", "ERROR")
            return False
    
    def handle_turnstile_with_retry(self, max_retries=None):
        """
        TEKNIK UTAMA: Handle Turnstile dengan multiple retry strategies
        Khusus untuk IP busuk yang sering gagal
        """
        if max_retries is None:
            max_retries = self.max_turnstile_retries
        
        # === ELITE: Check cookie reuse first ===
        from urllib.parse import urlparse
        current_url = self.sb.get_current_url()
        domain = urlparse(current_url).netloc
        
        if self.is_cf_cookie_valid(domain):
            log("[COOKIE] Valid cf_clearance found, attempting reuse...", "INFO")
            if self.reuse_cf_clearance_cookie(domain):
                # Refresh page to apply cookie
                self.sb.refresh()
                time.sleep(2)
                
                # Check if Turnstile still present
                if not self.turnstile.is_turnstile_present():
                    log("[COOKIE] Reuse successful - bypassed without solving!", "SUCCESS")
                    return True
                else:
                    log("[COOKIE] Reuse failed - cookie expired or invalid", "INFO")
        
        # === Proceed with normal bypass ===
        self.bypass_attempts += 1
        
        for attempt in range(1, max_retries + 1):
            log(f"[TURNSTILE] Attempt {attempt}/{max_retries}", "ACTION")
            
            try:
                # Strategy 1: Wait lebih lama untuk IP busuk
                if self.bad_ip_mode:
                    wait_time = random.uniform(3, 6)
                    log(f"[BAD-IP] Extra wait: {wait_time:.1f}s", "INFO")
                    time.sleep(wait_time)
                
                # Strategy 2: Inject enhanced activity
                if attempt > 1 and self.bad_ip_mode:
                    self.inject_bad_ip_enhancements()
                    time.sleep(2)
                
                # Strategy 3: Check if Turnstile is present
                if not self.turnstile.is_turnstile_present():
                    log("[TURNSTILE] No challenge detected", "SUCCESS")
                    return True
                
                # Strategy 4: Wait for Turnstile to be ready
                log("[TURNSTILE] Waiting for challenge to be ready...", "ACTION")
                ready, state, wait_time = self.turnstile.wait_for_turnstile_ready(
                    max_wait=30 if self.bad_ip_mode else 20
                )
                
                if not ready:
                    log(f"[TURNSTILE] Not ready on attempt {attempt}", "ERROR")
                    
                    # Strategy 5: Refresh page jika stuck
                    if attempt < max_retries:
                        log("[TURNSTILE] Refreshing page...", "ACTION")
                        self.sb.refresh()
                        time.sleep(random.uniform(3, 5))
                        self.inject_protections()
                        if self.bad_ip_mode:
                            self.inject_bad_ip_enhancements()
                        continue
                    else:
                        return False
                
                # Strategy 6: Click dengan timing yang bervariasi
                log("[TURNSTILE] Clicking challenge...", "ACTION")
                
                # ELITE: Pre-click Bezier mouse movement untuk IP busuk
                if self.bad_ip_mode:
                    log("[ELITE] Simulating Bezier curve mouse movement...", "INFO")
                    self.simulate_bezier_mouse_to_turnstile()
                    time.sleep(random.uniform(0.5, 1.0))
                else:
                    # Simple hover untuk IP bagus
                    self.sb.execute_script("""
                        const iframe = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                        if (iframe) {
                            const rect = iframe.getBoundingClientRect();
                            const event = new MouseEvent('mouseover', {
                                bubbles: true,
                                clientX: rect.left + rect.width / 2,
                                clientY: rect.top + rect.height / 2
                            });
                            iframe.dispatchEvent(event);
                        }
                    """)
                    time.sleep(random.uniform(0.3, 0.8))
                
                # Click
                clicked = self.turnstile.smart_click_turnstile()
                
                if not clicked:
                    log(f"[TURNSTILE] Click failed on attempt {attempt}", "ERROR")
                    if attempt < max_retries:
                        time.sleep(random.uniform(2, 4))
                        continue
                    else:
                        return False
                
                # Strategy 7: Wait for verification dengan patience
                log("[TURNSTILE] Waiting for verification...", "ACTION")
                wait_time = 15 if self.bad_ip_mode else 10
                
                verified = self.wait_for_success(timeout=wait_time)  # FIXED: self.wait_for_success bukan self.turnstile.wait_for_success
                
                if verified:
                    log("[TURNSTILE] Challenge passed!", "SUCCESS")
                    self.turnstile_fail_count = 0
                    self.bypass_successes += 1
                    
                    # ELITE: Save cf_clearance cookie untuk reuse
                    from urllib.parse import urlparse
                    domain = urlparse(self.sb.get_current_url()).netloc
                    self.save_cf_clearance_cookie(domain)
                    
                    # Log success rate
                    success_rate = (self.bypass_successes / self.bypass_attempts) * 100
                    log(f"[STATS] Success rate: {success_rate:.1f}% ({self.bypass_successes}/{self.bypass_attempts})", "INFO")
                    
                    return True
                else:
                    log(f"[TURNSTILE] Verification failed on attempt {attempt}", "ERROR")
                    self.turnstile_fail_count += 1
                    
                    # Auto-enable bad IP mode jika gagal terus
                    if self.turnstile_fail_count >= 2:
                        self.bad_ip_mode = True
                        log("[BAD-IP] Auto-enabled bad IP mode", "INFO")
                    
                    if attempt < max_retries:
                        # Strategy 8: Regenerate fingerprint untuk retry
                        log("[TURNSTILE] Regenerating fingerprint...", "ACTION")
                        self.fingerprint = AdvancedFingerprintRandomizer()
                        
                        # Refresh dan coba lagi
                        self.sb.refresh()
                        time.sleep(random.uniform(4, 7))
                        self.inject_protections()
                        if self.bad_ip_mode:
                            self.inject_bad_ip_enhancements()
                        continue
                    else:
                        return False
                        
            except Exception as e:
                log(f"[TURNSTILE] Error on attempt {attempt}: {e}", "ERROR")
                if attempt < max_retries:
                    time.sleep(random.uniform(3, 5))
                    continue
                else:
                    return False
        
        return False

    def handle_popups(self):
        """Handle popup - ZERO INTERACTION MODE: Tutup INSTANT tanpa sentuh apapun!
        
        STRATEGY BARU:
        1. Deteksi tab baru IMMEDIATELY
        2. LANGSUNG CLOSE - NO READ URL, NO EXECUTE SCRIPT, NO INTERACTION!
        3. JANGAN sentuh tab baru sama sekali (no scroll, no click, no slider!)
        4. NEVER close anchor tab
        5. Close via driver.close() langsung setelah switch
        
        CRITICAL: Tab baru = IKLAN = LANGSUNG TUTUP TANPA INTERAKSI!
        """
        if not self.is_valid_session():
            return
        
        try:
            current_handles = self.sb.driver.window_handles
            
            # SAFETY CHECK 1: Jangan close jika hanya ada 1 tab!
            if len(current_handles) <= 1:
                return
            
            # CRITICAL: Verify anchor exists
            if not self.anchor or self.anchor not in current_handles:
                log("[POPUP] CRITICAL: Anchor tab missing!", "ERROR")
                # Try to recover anchor
                for h in current_handles:
                    try:
                        self.sb.driver.switch_to.window(h)
                        url = self.sb.driver.execute_script("return window.location.href;")
                        if self.is_main_domain(url):
                            self.anchor = h
                            log(f"[POPUP] Recovered anchor: {h[:8]}...", "SUCCESS")
                            break
                    except:
                        continue
                
                # If still no anchor, use first handle
                if not self.anchor and current_handles:
                    self.anchor = current_handles[0]
                    log(f"[POPUP] Set anchor to first: {self.anchor[:8]}...", "INFO")

            # Find new tabs (exclude anchor and processed)
            new_tabs = [h for h in current_handles if h not in self.processed and h != self.anchor]
            
            if not new_tabs:
                return  # No popups
            
            log(f"[POPUP] Detected {len(new_tabs)} new tab(s) - CLOSING INSTANTLY (ZERO INTERACTION)", "ACTION")
            
            # SAFETY CHECK 2: Jangan close semua tab jika akan menyisakan 0 tab!
            if len(new_tabs) >= len(current_handles):
                log("[POPUP] SAFETY: Cannot close all tabs - keeping anchor", "WARNING")
                new_tabs = new_tabs[:-1]  # Keep at least 1 tab
            
            # ZERO INTERACTION MODE: Close ALL new tabs WITHOUT any interaction
            closed_count = 0
            for h in new_tabs:
                # CRITICAL SAFETY CHECK: Triple check this is not anchor!
                if h == self.anchor:
                    log(f"[POPUP] SAFETY: Skipping anchor tab", "INFO")
                    self.processed.add(h)
                    continue
                
                # SAFETY CHECK 3: Verify tab count before close
                tabs_before_close = len(self.sb.driver.window_handles)
                if tabs_before_close <= 1:
                    log(f"[POPUP] SAFETY: Only 1 tab left - stopping close", "WARNING")
                    break
                
                try:
                    # === ZERO INTERACTION CLOSE ===
                    # CRITICAL: JANGAN lakukan APAPUN di tab baru!
                    # - NO read URL
                    # - NO execute script
                    # - NO scroll, click, slider
                    # LANGSUNG CLOSE!
                    
                    try:
                        # Set ZERO timeout (no wait!)
                        self.sb.driver.set_page_load_timeout(0.01)  # 10ms only!
                        
                        # Quick switch (will timeout if loading, that's OK!)
                        self.sb.driver.switch_to.window(h)
                        
                        # === INSTANT CLOSE (NO INTERACTION!) ===
                        # JANGAN baca URL, JANGAN execute script, LANGSUNG CLOSE!
                        self.sb.driver.close()
                        
                        closed_count += 1
                        self.processed.add(h)
                        log(f"[POPUP]  Closed tab INSTANTLY (zero interaction)", "SUCCESS")
                        
                        # SAFETY CHECK: Verify tab still exists after close
                        tabs_after_close = len(self.sb.driver.window_handles)
                        if tabs_after_close == 0:
                            log(f"[POPUP] CRITICAL: All tabs closed! Emergency stop!", "ERROR")
                            break
                        
                    except Exception as close_err:
                        # Switch/close failed - mark as processed anyway
                        self.processed.add(h)
                        closed_count += 1
                        log(f"[POPUP]  Tab closed (forced): {str(close_err)[:30]}", "SUCCESS")
                    
                except Exception as e:
                    log(f"[POPUP] Error: {str(e)[:30]}", "ERROR")
                    self.processed.add(h)
            
            # Reset timeout
            try:
                self.sb.driver.set_page_load_timeout(30)
            except:
                pass
            
            if closed_count > 0:
                log(f"[POPUP]  Closed {closed_count} popup(s) INSTANTLY (ZERO INTERACTION)", "SUCCESS")
            
            # CRITICAL: Always back to anchor (with safety check)
            try:
                remaining_handles = self.sb.driver.window_handles
                if len(remaining_handles) > 0:
                    if self.anchor in remaining_handles:
                        self.back_to_anchor()
                    else:
                        # Anchor lost - use first available tab
                        log("[POPUP] Anchor lost - switching to first tab", "WARNING")
                        self.sb.driver.switch_to.window(remaining_handles[0])
                        self.anchor = remaining_handles[0]
                else:
                    log("[POPUP] CRITICAL: No tabs remaining!", "ERROR")
            except Exception as anchor_err:
                log(f"[POPUP] Error returning to anchor: {str(anchor_err)[:50]}", "ERROR")
                
        except Exception as e:
            log(f"[POPUP] Management error: {str(e)[:50]}", "ERROR")
            # Emergency: back to anchor
            try:
                remaining_handles = self.sb.driver.window_handles
                if len(remaining_handles) > 0:
                    self.sb.driver.switch_to.window(remaining_handles[0])
                    self.anchor = remaining_handles[0]
            except:
                pass
            # Reset timeout
            try:
                self.sb.driver.set_page_load_timeout(30)
            except:
                pass
    
    def force_close_tab(self, handle):
        """Force close tab yang stuck/error - FIXED: Always switch back to anchor after close"""
        # CRITICAL: Jangan close tab jika itu adalah anchor!
        if handle == self.anchor:
            log(f"CRITICAL: Attempted to close ANCHOR tab! Skipping...", "ERROR")
            return
        
        try:
            # Get all handles before closing
            all_handles = self.sb.driver.window_handles
            
            # CRITICAL: Jangan close jika ini adalah tab terakhir!
            if len(all_handles) <= 1:
                log(f"CRITICAL: Cannot close last remaining tab! Skipping...", "ERROR")
                return
            
            # Verify handle exists
            if handle not in all_handles:
                log(f"Tab {handle[:8]}... already closed", "INFO")
                return
            
            # Switch to the tab we want to close
            self.sb.driver.switch_to.window(handle)
            
            # Close it
            self.sb.driver.close()
            log(f"Force closed tab {handle[:8]}...", "SUCCESS")
            
            # CRITICAL: Switch back to anchor immediately
            try:
                remaining_handles = self.sb.driver.window_handles
                
                # Verify we still have tabs
                if not remaining_handles:
                    log(f"CRITICAL: No tabs remaining after close!", "ERROR")
                    return
                
                if self.anchor and self.anchor in remaining_handles:
                    self.sb.driver.switch_to.window(self.anchor)
                    log(f"Switched back to anchor", "SUCCESS")
                elif remaining_handles:
                    # Anchor hilang, ambil handle pertama
                    self.sb.driver.switch_to.window(remaining_handles[0])
                    self.anchor = remaining_handles[0]
                    log(f"Anchor lost, switched to first handle", "INFO")
            except Exception as switch_err:
                log(f"Failed to switch back: {str(switch_err)[:30]}", "ERROR")
                # Try to recover
                try:
                    remaining = self.sb.driver.window_handles
                    if remaining:
                        self.sb.driver.switch_to.window(remaining[0])
                        self.anchor = remaining[0]
                except:
                    pass
                
        except Exception as e:
            log(f"Force close failed: {str(e)[:30]}", "ERROR")
            # Last resort: JavaScript close
            try:
                self.sb.driver.execute_script("window.close();")
                # Try switch back
            except:
                pass
    
    def force_close_tab_aggressive(self, handle):
        """AGGRESSIVE: Close tab immediately without waiting
        
        Digunakan untuk popup yang stuck/loading lama.
        Tidak tunggu apapun - langsung close!
        """
        # CRITICAL: NEVER close anchor!
        if handle == self.anchor:
            log(f"[AGGRESSIVE] CRITICAL: Attempted to close ANCHOR! Skipping...", "ERROR")
            return
        
        try:
            all_handles = self.sb.driver.window_handles
            
            # CRITICAL: Don't close last tab
            if len(all_handles) <= 1:
                log(f"[AGGRESSIVE] Cannot close last tab!", "ERROR")
                return
            
            # Verify handle exists
            if handle not in all_handles:
                return  # Already closed
            
            # METHOD 1: Try JavaScript close (fastest, no switch needed)
            try:
                # Get current window
                current = self.sb.driver.current_window_handle
                
                # Switch to target
                self.sb.driver.switch_to.window(handle)
                
                # Close with JavaScript (instant)
                self.sb.driver.execute_script("window.close();")
                
                # Switch back to anchor immediately
                remaining = self.sb.driver.window_handles
                if self.anchor in remaining:
                    self.sb.driver.switch_to.window(self.anchor)
                elif remaining:
                    self.sb.driver.switch_to.window(remaining[0])
                    self.anchor = remaining[0]
                
                return  # Success
            except:
                pass
            
            # METHOD 2: Fallback to driver.close()
            try:
                self.sb.driver.switch_to.window(handle)
                self.sb.driver.close()
                
                # Switch back
                remaining = self.sb.driver.window_handles
                if self.anchor in remaining:
                    self.sb.driver.switch_to.window(self.anchor)
                elif remaining:
                    self.sb.driver.switch_to.window(remaining[0])
                    self.anchor = remaining[0]
            except:
                pass
                
        except Exception as e:
            # Silent fail - don't log to avoid spam
            pass

    def remove_overlays(self):
        """Remove ads dan overlays"""
        if not self.is_valid_session():
            return
        try:
            js = """
            try {
                const selectors = [
                    'ins', 'iframe[id^="aswift"]', 'iframe[id^="google_ads"]',
                    'div[class*="overlay"]', 'div[class*="popup"]', 'div[class*="modal"]',
                    'div[class*="ad-"]', 'div[id*="ad-"]', '.adsbygoogle',
                    '.google-vignette-container', '#google_vignette'
                ];
                selectors.forEach(sel => {
                    document.querySelectorAll(sel).forEach(el => {
                        if (!el.innerText?.includes('OPEN LINK') && !el.innerText?.includes('Download')) {
                            el.remove();
                        }
                    });
                });

                if (window.location.hash.includes('google_vignette')) {
                    window.location.hash = '';
                }
                
                document.body.style.overflow = 'auto';
                document.body.style.setProperty('overflow', 'auto', 'important');
                document.documentElement.style.overflow = 'auto';
                document.documentElement.style.setProperty('overflow', 'auto', 'important');
                
                document.querySelectorAll('body > div').forEach(el => {
                    const s = window.getComputedStyle(el);
                    if (el.innerText?.includes('OPEN LINK')) return;
                    if ((parseInt(s.zIndex) > 100 || s.position === 'fixed') && el.offsetHeight > window.innerHeight * 0.4) {
                        el.remove();
                    }
                });
            } catch(e) {}
            """
            self.sb.execute_script(js)
        except:
            pass

    def find_button(self):
        """Find target button - ADAPTIVE STRATEGY
        
        UNDERSTANDING (dari analisis 1.html - 6.html):
        - Step 1-5: Ada button <a> dengan onclick="window.open" di <div id="verify">
          → Ini HARUS DIKLIK untuk trigger next step (tapi akan buka popup iklan)
        - Step 6: Ada button <button> tanpa window.open dengan text "OPEN LINK"
          → Ini button ASLI yang menuju link final (ID: Df8hEut24m dari 6.html)
        
        STRATEGY:
        1. Cari button ASLI dulu (<button> dengan "OPEN LINK", tanpa window.open)
        2. Jika tidak ada, cari button STEP (<a> di #verify dengan window.open)
        3. Return info tentang tipe button (asli atau step)
        """
        if not self.is_valid_session():
            return None
        
        try:
            log("[ADAPTIVE SEARCH] Looking for button...", "ACTION")
            button_info = self.sb.execute_script("""
                // PRIORITY 0: Cari button FINAL dengan ID spesifik (dari 6.html)
                // ID: Df8hEut24m - ini button yang redirect ke Instagram
                const finalButton = document.getElementById('Df8hEut24m');
                if (finalButton) {
                    finalButton.scrollIntoView({behavior: 'smooth', block: 'center'});
                    return {
                        found: true,
                        type: 'FINAL',
                        tag: 'button',
                        id: 'Df8hEut24m',
                        text: finalButton.textContent.trim().substring(0, 30),
                        selector: 'button#Df8hEut24m'
                    };
                }
                
                // PRIORITY 1: Cari button ASLI (final step)
                // - <button> tag
                // - Text "OPEN LINK"
                // - TIDAK punya window.open
                // - Class bg-[#1A56DB]
                
                const allButtons = document.querySelectorAll('button');
                
                for (let btn of allButtons) {
                    if (btn.id === 'captcha_reload') continue;
                    
                    const text = btn.textContent.trim();
                    if (!text.includes('OPEN LINK')) continue;
                    
                    const onclick = btn.getAttribute('onclick');
                    if (onclick && onclick.includes('window.open')) continue;
                    
                    if (!btn.className.includes('bg-[#1A56DB]')) continue;
                    
                    // FOUND REAL BUTTON!
                    btn.scrollIntoView({behavior: 'smooth', block: 'center'});
                    return {
                        found: true,
                        type: 'REAL',
                        tag: 'button',
                        id: btn.id || null,
                        text: text.substring(0, 30),
                        selector: btn.id ? 'button#' + btn.id : null
                    };
                }
                
                // PRIORITY 2: Cari button STEP (untuk trigger next page)
                // - <a> tag di dalam #verify atau #second_open_placeholder
                // - Punya window.open (ini trigger next step)
                // - Class bg-[#1A56DB]
                // PRIORITAS: #second_open_placeholder DULU (lebih cepat), baru #verify
                
                const secondDiv = document.querySelector('#second_open_placeholder');
                const verifyDiv = document.querySelector('#verify');
                
                // Check second_open_placeholder FIRST (priority)
                const containers = [secondDiv, verifyDiv].filter(d => d);
                
                for (let container of containers) {
                    const links = container.querySelectorAll('a');
                    for (let link of links) {
                        const onclick = link.getAttribute('onclick');
                        if (!onclick || !onclick.includes('window.open')) continue;
                        
                        if (!link.className.includes('bg-[#1A56DB]')) continue;
                        
                        // FOUND STEP BUTTON!
                        link.scrollIntoView({behavior: 'smooth', block: 'center'});
                        return {
                            found: true,
                            type: 'STEP',
                            tag: 'a',
                            id: link.id || null,
                            text: link.textContent.trim().substring(0, 30),
                            container: container.id
                        };
                    }
                }
                
                return {found: false};
            """)
            
            if button_info and button_info.get('found'):
                btn_type = button_info['type']
                btn_text = button_info['text']
                
                if btn_type == 'FINAL':
                    log(f"[ADAPTIVE]  FINAL button found: '{btn_text}' (ID: {button_info.get('id')})", "SUCCESS")
                    log(f"[ADAPTIVE] This will redirect to Instagram!", "SUCCESS")
                    time.sleep(1.5)
                    
                    # Return selector dengan ID spesifik
                    return {'selector': button_info['selector'], 'type': 'FINAL', 'id': button_info.get('id')}
                
                elif btn_type == 'REAL':
                    log(f"[ADAPTIVE]  REAL button found: '{btn_text}'", "SUCCESS")
                    log(f"[ADAPTIVE] This is the FINAL button!", "SUCCESS")
                    time.sleep(1.5)
                    
                    # Build selector - prioritas ID jika ada, fallback ke XPath
                    if button_info.get('id'):
                        selector = f"button#{button_info['id']}"
                    else:
                        # XPath yang lebih fleksibel - cukup cari button dengan text OPEN LINK
                        selector = "//button[contains(., 'OPEN LINK')]"
                    
                    # JavaScript sudah confirm button ada & visible, langsung return!
                    return {'selector': selector, 'type': 'REAL'}
                    
                elif btn_type == 'STEP':
                    log(f"[ADAPTIVE]  STEP button found: '{btn_text}' (in #{button_info.get('container', 'unknown')})", "INFO")
                    log(f"[ADAPTIVE] This will trigger next step (popup will open)", "WARNING")
                    time.sleep(1.5)
                    
                    # Build selector untuk step button - lebih simple
                    container_id = button_info.get('container', 'verify')
                    selector = f"//div[@id='{container_id}']//a[contains(@onclick, 'window.open')]"
                    
                    # JavaScript sudah confirm button ada & visible, langsung return!
                    return {'selector': selector, 'type': 'STEP'}
            
            log("[ADAPTIVE]  No button found", "INFO")
            return None
                    
        except Exception as e:
            log(f"[ADAPTIVE] Error: {str(e)[:100]}", "ERROR")
            return None

    def download_file(self, url):
        """Download file via HTTP"""
        import requests
        import os
        
        if any(x in url.lower() for x in ["youtube.com", "instagram.com", "facebook.com"]):
            log("Not a download URL", "INFO")
            return
        
        try:
            log(f"Downloading: {url[:60]}...", "ACTION")
            
            cookies = {{c['name']: c['value'] for c in self.sb.driver.get_cookies()}}
            
            # ELITE: RANDOMIZED HTTP HEADERS - Variable order & values
            # Header order matters for fingerprinting!
            base_headers = [
                ("User-Agent", self.fingerprint.user_agent),
                ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"),
                ("Accept-Language", self.fingerprint.accept_language),
                ("Accept-Encoding", "gzip, deflate, br, zstd"),
                ("Referer", self.sb.get_current_url()),
                ("sec-ch-ua", f'"Chromium";v="{self.fingerprint.chrome_versions[0].split(".")[0]}", "Google Chrome";v="{self.fingerprint.chrome_versions[0].split(".")[0]}", "Not:A-Brand";v="99"'),
                ("sec-ch-ua-mobile", "?0"),
                ("sec-ch-ua-platform", f'"{self.fingerprint.platform}"'),
                ("Sec-Fetch-Dest", "document"),
                ("Sec-Fetch-Mode", "navigate"),
                ("Sec-Fetch-Site", "same-origin"),
                ("Sec-Fetch-User", "?1"),
                ("Upgrade-Insecure-Requests", "1"),
            ]
            
            # ELITE: Randomly include/exclude Cache-Control
            if random.random() < 0.7:  # 70% chance include
                base_headers.append(("Cache-Control", "max-age=0"))
            
            # ELITE: Shuffle header order slightly (not completely random)
            # Keep User-Agent first, but shuffle others
            user_agent = base_headers.pop(0)
            random.shuffle(base_headers)
            base_headers.insert(0, user_agent)
            
            # Convert to dict
            headers = dict(base_headers)
            
            session = requests.Session()
            session.cookies.update(cookies)
            session.headers.update(headers)
            
            r = session.get(url, stream=True, timeout=120, allow_redirects=True)
            
            if r.status_code != 200:
                log(f"HTTP {r.status_code}", "ERROR")
                return

            content_disp = r.headers.get("Content-Disposition", "")
            if "filename=" in content_disp:
                filename = content_disp.split("filename=")[1].strip('"').strip("'")
            else:
                filename = url.split("/")[-1].split("?")[0] or "download.tmp"
                if "." not in filename:
                    filename += ".tmp"

            traffic_dir = os.path.join(os.getcwd(), "traffic")
            if not os.path.exists(traffic_dir):
                os.makedirs(traffic_dir)
            filepath = os.path.join(traffic_dir, filename)
            
            with open(filepath, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=131072):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            
            if downloaded > 0:
                log(f"Downloaded: {downloaded} bytes -> traffic/{filename}", "SUCCESS")
            
        except Exception as e:
            log(f"Download error: {e}", "ERROR")

    def run(self):
        log("=" * 60)
        log("SAFELINK BYPASS V2 - ELITE ANTI-DETECTION", "STEP")
        log(f"Target: {TARGET_URL}", "URL")
        log("=" * 60)
        
        # === DETECT BAD IP MODE ===
        # Auto-detect jika menggunakan IP Google Cloud atau IP "busuk"
        try:
            log("[IP-CHECK] Detecting IP quality...", "ACTION")
            test_response = self.tls_session.get("https://httpbin.org/ip", timeout=5)
            if test_response.status_code == 200:
                ip_data = test_response.json()
                current_ip = ip_data.get("origin", "").split(",")[0].strip()
                log(f"[IP-CHECK] Current IP: {current_ip}", "INFO")
                
                # Detect Google Cloud IP (biasanya dimulai dengan 34., 35., atau 104.)
                if current_ip.startswith(("34.", "35.", "104.", "146.148", "130.211")):
                    self.bad_ip_mode = True
                    log("=" * 60, "INFO")
                    log("[BAD-IP] Google Cloud IP detected!", "INFO")
                    log("[BAD-IP] Enabling ELITE techniques:", "INFO")
                    log("   Bezier curve mouse movement", "INFO")
                    log("   Enhanced behavioral biometrics", "INFO")
                    log("   Extended wait times", "INFO")
                    log("   Multiple retry strategies", "INFO")
                    log("=" * 60, "INFO")
                else:
                    log(f"[IP-CHECK] Residential/Good IP detected", "SUCCESS")
                    log("[IP-CHECK] Using standard techniques", "INFO")
        except Exception as e:
            log(f"[IP-CHECK] Detection error: {e}", "ERROR")
            log("[IP-CHECK] Assuming bad IP mode for safety", "INFO")
            self.bad_ip_mode = True
        
        # === LANGSUNG KE TARGET URL ===
        
        try:
            log("Opening URL...", "ACTION")
            self.sb.uc_open_with_reconnect(TARGET_URL, reconnect_time=6)
            log("Page loaded", "SUCCESS")
            time.sleep(2)  # Simple delay - jangan blocking
            
        except Exception as e:
            log(f"Open error: {e}", "ERROR")
            return
        
        # ==================== INJECT COOKIES SETELAH BUKA URL ====================
        cookies_injected = False  # Track apakah cookies berhasil di-inject
        
        if self.saved_cookies_to_inject:
            log("\n[COOKIES] Injecting cookies dari Firebase...", "ACTION")
            cookies_added = 0
            cookies_failed = 0
            
            for cookie in self.saved_cookies_to_inject:
                try:
                    # Remove expiry field jika ada (bisa bikin error)
                    if 'expiry' in cookie:
                        del cookie['expiry']
                    
                    self.sb.add_cookie(cookie)
                    cookies_added += 1
                    log(f"[COOKIES]    Injected: {cookie['name']}", "SUCCESS")
                except Exception as e:
                    cookies_failed += 1
                    log(f"[COOKIES]    Failed: {cookie.get('name', 'unknown')} - {str(e)[:50]}", "ERROR")
            
            log(f"[COOKIES] Injection result: {cookies_added} success, {cookies_failed} failed", "INFO")
            
            # Verify cf_clearance
            has_cf_clearance = any(c['name'] == 'cf_clearance' for c in self.saved_cookies_to_inject)
            if has_cf_clearance:
                log("[COOKIES]  cf_clearance cookie injected (Cloudflare bypass active)", "SUCCESS")
            else:
                log("[COOKIES]   WARNING: cf_clearance not found in cookies", "INFO")
            
            # Refresh page untuk apply cookies
            if cookies_added > 0:
                log("[COOKIES] Refreshing page untuk apply cookies...", "ACTION")
                self.sb.refresh()
                time.sleep(3)
                log("[COOKIES]  Page refreshed dengan cookies", "SUCCESS")
                
                # INJECT BUTTON SCRIPT (sama seperti bot2)
                log("[COOKIES] Injecting SafelinkU button script...", "ACTION")
                inject_button_script = """
                (function() {
                    // Cek apakah button sudah ada
                    if (document.getElementById('safelink-injected-button')) {
                        console.log('[COOKIES] Button already exists');
                        return;
                    }
                    
                    // Load SafelinkU script
                    var script = document.createElement('script');
                    script.src = 'https://safelinku.com/ad_home.js';
                    script.async = true;
                    document.head.appendChild(script);
                    console.log('[COOKIES] SafelinkU script loaded');
                    
                    // Tunggu 2 detik lalu inject button
                    setTimeout(function() {
                        // Cek apakah button SafelinkU sudah muncul
                        if (!document.querySelector('[id*="open"]') && 
                            !document.getElementById('safelink-injected-button')) {
                            
                            // Buat button custom
                            var button = document.createElement('button');
                            button.id = 'safelink-injected-button';
                            button.innerHTML = ' OPEN LINK (COOKIES INJECTED)';
                            button.style.cssText = `
                                position: fixed;
                                bottom: 20px;
                                right: 20px;
                                z-index: 99999;
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                color: white;
                                border: none;
                                padding: 15px 30px;
                                border-radius: 50px;
                                font-size: 16px;
                                font-weight: bold;
                                cursor: pointer;
                                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                                transition: all 0.3s ease;
                            `;
                            
                            // Hover effect
                            button.onmouseover = function() {
                                this.style.transform = 'scale(1.1)';
                            };
                            button.onmouseout = function() {
                                this.style.transform = 'scale(1)';
                            };
                            
                            // Click handler
                            button.onclick = function() {
                                alert(' Button berhasil di-inject dengan cookies dari Firebase!');
                            };
                            
                            document.body.appendChild(button);
                            console.log('[COOKIES] Custom button injected');
                        } else {
                            console.log('[COOKIES] SafelinkU button already present');
                        }
                    }, 2000);
                })();
                """
                
                try:
                    self.sb.execute_script(inject_button_script)
                    log("[COOKIES]  Button script injected", "SUCCESS")
                    time.sleep(2)  # Wait for button to appear
                except Exception as e:
                    log(f"[COOKIES] Button injection failed: {str(e)[:100]}", "ERROR")
                
                log("[COOKIES]  Cloudflare Turnstile bypass ACTIVE!", "SUCCESS")
                cookies_injected = True  # Mark sebagai berhasil
        
        self.set_anchor()
        self.inject_protections()
        
        # Inject enhanced activity untuk IP busuk
        if self.bad_ip_mode:
            log("[ELITE] Injecting enhanced behavioral biometrics...", "ACTION")
            self.inject_bad_ip_enhancements()
            time.sleep(1)
        
        # === CLOUDFLARE HANDLING - ELITE MODE ===
        cf_bypassed = False
        
        # SKIP Turnstile handling jika cookies sudah di-inject
        if cookies_injected:
            log("[CF] Skipping Turnstile check (cookies already injected)", "INFO")
            
            # Cek apakah Turnstile masih ada
            if not self.turnstile.is_turnstile_present():
                log("[CF]  No Turnstile detected - cookies bypass successful!", "SUCCESS")
                cf_bypassed = True
            else:
                log("[CF]   Turnstile still present, attempting normal bypass...", "INFO")
                cf_bypassed = self.handle_turnstile_with_retry()
        else:
            log("[CF] Checking for Cloudflare/Turnstile challenge...", "ACTION")
            
            # Gunakan method baru dengan retry strategy
            cf_bypassed = self.handle_turnstile_with_retry()
        
        if not cf_bypassed:
            log("=" * 60, "ERROR")
            log("[CF] GAGAL BYPASS CLOUDFLARE TURNSTILE!", "ERROR")
            log("[CF] Session akan STOP - tidak bisa lanjut tanpa bypass", "ERROR")
            log("=" * 60, "ERROR")
            raise Exception("Cloudflare Turnstile bypass failed after all retries")
        
        # Save cookies setelah bypass
        try:
            self.cf_cookies = self.sb.driver.get_cookies()
            log(f"[CF] Cookies saved ({len(self.cf_cookies)} cookies)", "SUCCESS")
        except:
            pass
        
        self.set_anchor()
        
        log(f"\n{'='*60}")
        log(f"STARTING MAIN LOOP", "STEP")
        log(f"{'='*60}\n")
        
        # === TRACKING VARIABLES ===
        last_url = None
        stuck_count = 0
        wrong_page_count = 0
        total_failures = 0
        progress_count = 0
        unique_urls = set()
        last_progress_step = 0
        
        # === STUCK URL DETECTION ===
        url_history = []  # Track last 10 URLs
        same_url_count = 0  # Counter untuk URL yang sama berturut-turut
        MAX_SAME_URL = 6  # Max 6x URL sama = stuck (bisa 6-8x sesuai kebutuhan)
        
        AD_DOMAINS = ["eatcells.com", "revenuecpmgate.com", "sportshard.com"]
        
        # === SMART LIMITS ===
        MAX_STEPS_HARD = 60
        MAX_NO_PROGRESS = 8
        MAX_FAILURES = 6
        MAX_TURNSTILE_ENCOUNTERS = 4  # CRITICAL: Max 4x ketemu Turnstile
        MAX_CAPTCHA_TIMEOUT = 20  # Max 20s per attempt
        
        # TURNSTILE TRACKING (CRITICAL)
        turnstile_encounter_count = 0  # Berapa kali ketemu Turnstile
        turnstile_success_count = 0    # Berapa kali berhasil bypass
        last_turnstile_url = None      # URL terakhir ketemu Turnstile
        
        captcha_consecutive_fails = 0
        
        step = 0
        running = True
        
        while running and step < MAX_STEPS_HARD:
            step += 1
            
            if not self.is_valid_session():
                log("Session lost", "ERROR")
                break
            
            # === SMART STOP CONDITIONS ===
            steps_since_progress = step - last_progress_step
            if steps_since_progress > MAX_NO_PROGRESS:
                log(f"\n{'='*60}", "ERROR")
                log(f"NO PROGRESS for {steps_since_progress} steps - GIVING UP", "ERROR")
                log(f"{'='*60}\n", "ERROR")
                break
            
            if total_failures >= MAX_FAILURES:
                log(f"\n{'='*60}", "ERROR")
                log(f"TOO MANY FAILURES ({total_failures}) - GIVING UP", "ERROR")
                log(f"{'='*60}\n", "ERROR")
                break
            
            # Random behavior
            if step > 1:
                behavior_roll = random.random()
                if behavior_roll < 0.3:
                    self.human.quick_action()
                elif behavior_roll < 0.5:
                    self.human.safe_interaction()
                elif behavior_roll < 0.6:
                    self.human.pretend_read()
            
            # Show adaptive status
            steps_stuck = step - last_progress_step
            log(f"\n--- STEP {step}/{MAX_STEPS_HARD} | Progress: {progress_count} | Fails: {total_failures}/{MAX_FAILURES} | Stuck: {steps_stuck}/{MAX_NO_PROGRESS} ---", "STEP")
            
            try:
                current_url = self.sb.get_current_url()
                log(f"URL: {current_url}", "URL")
                
                # Track progress (new URL = progress)
                if current_url not in unique_urls:
                    unique_urls.add(current_url)
                    progress_count += 1
                    last_progress_step = step
                
                # === MID-LOOP CLOUDFLARE DETECTION - PRECISION MODE ===
                try:
                    # Gunakan TurnstileDetector untuk detection yang lebih akurat
                    is_cloudflare = self.turnstile.is_challenge_page()
                    
                    if is_cloudflare:
                        # CRITICAL: Track Turnstile encounter
                        current_turnstile_url = self.sb.get_current_url()
                        
                        # Cek apakah ini Turnstile baru (URL berbeda)
                        if current_turnstile_url != last_turnstile_url:
                            turnstile_encounter_count += 1
                            last_turnstile_url = current_turnstile_url
                            log(f"\n{'='*60}", "ERROR")
                            log(f"[TURNSTILE] ENCOUNTER #{turnstile_encounter_count}/{MAX_TURNSTILE_ENCOUNTERS}", "ERROR")
                            log(f"[TURNSTILE] URL: {current_turnstile_url[:60]}...", "ERROR")
                            log(f"{'='*60}\n", "ERROR")
                        
                        # CRITICAL: Check if max encounters reached
                        if turnstile_encounter_count > MAX_TURNSTILE_ENCOUNTERS:
                            log(f"\n{'='*60}", "ERROR")
                            log(f"[TURNSTILE] MAX ENCOUNTERS REACHED ({MAX_TURNSTILE_ENCOUNTERS}x)!", "ERROR")
                            log(f"[TURNSTILE] Success: {turnstile_success_count}/{turnstile_encounter_count}", "ERROR")
                            log(f"[TURNSTILE] Bot tidak bisa bypass setelah {MAX_TURNSTILE_ENCOUNTERS}x attempt", "ERROR")
                            log(f"[TURNSTILE] STOPPING SESSION - IP blocked atau captcha terlalu sulit", "ERROR")
                            log(f"{'='*60}\n", "ERROR")
                            break  # STOP SESSION
                        
                        log("[CF-MID] CLOUDFLARE/TURNSTILE DETECTED IN LOOP!", "ERROR")
                        log(f"[CF-MID] Encounter: {turnstile_encounter_count}/{MAX_TURNSTILE_ENCOUNTERS}", "INFO")
                        log(f"[CF-MID] Success rate: {turnstile_success_count}/{turnstile_encounter_count}", "INFO")
                        
                        # SMART: Set timeout per attempt
                        log(f"[CF-MID] Attempting bypass (timeout: {MAX_CAPTCHA_TIMEOUT}s)...", "ACTION")
                        bypass_start = time.time()
                        
                        # PRECISION BYPASS dengan smart detection
                        log("[CF-MID] Using PRECISION TURNSTILE DETECTION...", "ACTION")
                        
                        # Override max_wait untuk fast fail
                        self.turnstile.detection_start = time.time()
                        bypass_success = False
                        
                        try:
                            # Wait dengan timeout yang lebih pendek
                            should_click, state, wait_time = self.turnstile.wait_for_turnstile_ready(
                                max_wait=MAX_CAPTCHA_TIMEOUT, 
                                check_interval=1.5
                            )
                            
                            if should_click:
                                # Try click
                                try:
                                    self.sb.uc_gui_click_captcha()
                                    time.sleep(3)
                                    
                                    # Verify success
                                    if not self.turnstile.is_challenge_page():
                                        bypass_success = True
                                        turnstile_success_count += 1
                                except Exception as click_err:
                                    log(f"[CF-MID] Click error: {click_err}", "ERROR")
                            else:
                                # IP blocked or already verified
                                if state.get('success_shown') or state.get('response_token'):
                                    bypass_success = True
                                    turnstile_success_count += 1
                                else:
                                    log("[CF-MID] Turnstile not ready - IP might be blocked", "ERROR")
                        
                        except Exception as bypass_err:
                            log(f"[CF-MID] Bypass error: {bypass_err}", "ERROR")
                        
                        bypass_time = time.time() - bypass_start
                        
                        if bypass_success:
                            log(f"[CF-MID] Captcha BYPASSED in {bypass_time:.1f}s!", "SUCCESS")
                            log(f"[CF-MID] Success rate: {turnstile_success_count}/{turnstile_encounter_count}", "SUCCESS")
                            captcha_consecutive_fails = 0
                            
                            try:
                                self.cf_cookies = self.sb.driver.get_cookies()
                                log(f"[CF-MID] Cookies updated ({len(self.cf_cookies)} cookies)", "SUCCESS")
                            except:
                                pass
                            
                            self.back_to_anchor()
                        else:
                            log(f"[CF-MID] Bypass FAILED after {bypass_time:.1f}s", "ERROR")
                            captcha_consecutive_fails += 1
                            total_failures += 1
                            
                            # CRITICAL: Check if this was the last allowed encounter
                            if turnstile_encounter_count >= MAX_TURNSTILE_ENCOUNTERS:
                                log(f"\n{'='*60}", "ERROR")
                                log(f"[TURNSTILE] FINAL ATTEMPT FAILED!", "ERROR")
                                log(f"[TURNSTILE] Total encounters: {turnstile_encounter_count}", "ERROR")
                                log(f"[TURNSTILE] Successful bypasses: {turnstile_success_count}", "ERROR")
                                log(f"[TURNSTILE] STOPPING SESSION - Max {MAX_TURNSTILE_ENCOUNTERS} encounters reached", "ERROR")
                                log(f"{'='*60}\n", "ERROR")
                                break  # STOP SESSION
                        
                        continue
                except Exception as cf_err:
                    log(f"[CF-MID] Detection error: {cf_err}", "ERROR")
                
                # === STUCK DETECTION ===
                is_wrong_page = any(ad in current_url.lower() for ad in AD_DOMAINS)
                is_valid_page = any(valid in current_url.lower() for valid in self.main_domains)
                
                # === STUCK URL DETECTION (URL sama 6-8x) ===
                # Track URL history
                url_history.append(current_url)
                if len(url_history) > 10:
                    url_history.pop(0)  # Keep only last 10 URLs
                
                # Check if stuck on same URL
                if len(url_history) >= 2 and url_history[-1] == url_history[-2]:
                    same_url_count += 1
                    
                    if same_url_count >= MAX_SAME_URL:
                        log(f"\n{'='*60}", "WARNING")
                        log(f"STUCK DETECTED: Same URL {same_url_count} times!", "WARNING")
                        log(f"URL: {current_url[:60]}...", "WARNING")
                        log(f"{'='*60}\n", "WARNING")
                        
                        # SAFETY CHECK: Verify we still have valid session
                        if not self.is_valid_session():
                            log("[STUCK] Session lost - stopping", "ERROR")
                            break
                        
                        # DECISION: Apakah ini halaman final atau stuck?
                        # Jika URL bukan main domain (sudah redirect ke tujuan), ini SUCCESS
                        if not any(d in current_url.lower() for d in self.main_domains):
                            log("[STUCK] URL is NOT main domain - this might be FINAL link!", "SUCCESS")
                            log("[STUCK] Saving as final link...", "ACTION")
                            
                            try:
                                with open("real_link.txt", "w") as f:
                                    f.write(current_url)
                                log("Saved to real_link.txt", "SUCCESS")
                            except Exception as save_err:
                                log(f"[STUCK] Save error: {save_err}", "ERROR")
                            
                            log("\n" + "=" * 60, "SUCCESS")
                            log("FINAL LINK DETECTED (stuck on non-main domain)", "SUCCESS")
                            log(f"URL: {current_url}", "URL")
                            log("=" * 60 + "\n", "SUCCESS")
                            return
                        
                        # Jika masih di main domain, ini stuck - coba recovery
                        log("[STUCK] Still on main domain - attempting recovery...", "ACTION")
                        
                        # SAFETY: Jangan recovery jika sudah terlalu banyak failures
                        if total_failures >= MAX_FAILURES - 1:
                            log("[STUCK] Too many failures - stopping recovery", "ERROR")
                            same_url_count = 0
                            continue
                        
                        # Try scroll down untuk cari button
                        try:
                            log("[STUCK] Scrolling down to find button...", "ACTION")
                            self.human.human_scroll(direction='down', amount=300, safe=True)
                            time.sleep(2)
                        except Exception as scroll_err:
                            log(f"[STUCK] Scroll error: {scroll_err}", "ERROR")
                        
                        # Try back to anchor (with safety check)
                        try:
                            log("[STUCK] Going back to anchor...", "ACTION")
                            
                            # SAFETY: Verify anchor exists before going back
                            current_handles = self.sb.driver.window_handles
                            if self.anchor in current_handles:
                                self.back_to_anchor()
                            else:
                                log("[STUCK] Anchor lost - using first tab", "WARNING")
                                if len(current_handles) > 0:
                                    self.sb.driver.switch_to.window(current_handles[0])
                                    self.anchor = current_handles[0]
                                else:
                                    log("[STUCK] CRITICAL: No tabs remaining!", "ERROR")
                                    break
                            
                            same_url_count = 0  # Reset counter
                            time.sleep(2)
                            continue
                        except Exception as anchor_err:
                            log(f"[STUCK] Anchor error: {anchor_err}", "ERROR")
                            same_url_count = 0
                            continue
                else:
                    # URL berubah, reset counter
                    if len(url_history) >= 2 and url_history[-1] != url_history[-2]:
                        same_url_count = 0
                
                if is_wrong_page or (not is_valid_page and "http" in current_url):
                    wrong_page_count += 1
                    total_failures += 1
                    log(f"Wrong page detected ({wrong_page_count}/3) - Fail #{total_failures}", "ERROR")
                    
                    if self.recover_from_ad():
                        wrong_page_count = 0
                        continue
                    
                    if wrong_page_count >= 3:
                        log("Stuck on wrong page! Returning to anchor...", "ACTION")
                        self.back_to_anchor()
                        wrong_page_count = 0
                        time.sleep(2)
                        continue
                else:
                    wrong_page_count = 0
                    
            except:
                pass
            
            self.handle_popups()
            self.remove_overlays()
            
            # Delay unik per step
            step_delay = self.step_delays[step % len(self.step_delays)]
            time.sleep(step_delay * 0.3)
            
            button_result = self.find_button()
            
            # CRITICAL: Jika button tidak ditemukan, SKIP step ini
            if not button_result:
                log("[SKIP] No button found - waiting...", "INFO")
                time.sleep(2)
                step += 1
                continue
            
            selector = button_result['selector']
            button_type = button_result['type']
            
            if selector:
                try:
                    current = self.sb.get_current_url()
                    is_download_btn = "download" in selector.lower()
                    
                    if is_download_btn and current == last_url:
                        stuck_count += 1
                        if stuck_count >= 2:
                            log("\n" + "=" * 60, "SUCCESS")
                            log("FINAL DOWNLOAD PAGE DETECTED", "SUCCESS")
                            log(f"URL: {current}", "URL")
                            log("=" * 60 + "\n", "SUCCESS")
                            
                            with open("real_link.txt", "w") as f:
                                f.write(current)
                            log("Saved to real_link.txt", "SUCCESS")
                            
                            self.download_file(current)
                            return
                    else:
                        stuck_count = 0
                        last_url = current
                except:
                    pass
                
                try:
                    self.remove_overlays()
                    
                    if self.sb.is_element_visible(selector):
                        log(f"[CLICK] Button: {selector[:40]}... (Type: {button_type})", "ACTION")
                        
                        # Jika STEP button, siapkan untuk handle popup
                        if button_type == 'STEP':
                            log("[STEP] This will open popup - will close it after click", "WARNING")
                            tabs_before = len(self.sb.driver.window_handles)
                        
                        # Jika FINAL button (ID: Df8hEut24m), ini akan redirect ke Instagram
                        if button_type == 'FINAL':
                            log("[FINAL] This will redirect to Instagram - waiting for redirect...", "SUCCESS")
                        
                        self.human.human_click(selector)
                        log("[CLICK] Done", "SUCCESS")
                        
                        # Handle popup jika STEP button
                        if button_type == 'STEP':
                            time.sleep(1)  # Wait for popup
                            tabs_after = len(self.sb.driver.window_handles)
                            
                            if tabs_after > tabs_before:
                                log(f"[POPUP] Detected {tabs_after - tabs_before} new tab(s) - closing...", "ACTION")
                                self.handle_popups()  # Close popup tabs
                                log("[POPUP] Closed", "SUCCESS")
                        
                        # Jika FINAL button, tunggu lebih lama untuk redirect
                        if button_type == 'FINAL':
                            log("[FINAL] Waiting for redirect to complete...", "ACTION")
                            time.sleep(3)  # Wait lebih lama untuk redirect
                            
                            # Check apakah sudah redirect
                            max_wait = 10  # Max 10 detik
                            waited = 0
                            while waited < max_wait:
                                try:
                                    url_after = self.sb.get_current_url()
                                    log(f"[FINAL] Checking redirect... ({waited}s) URL: {url_after[:60]}...", "INFO")
                                    
                                    if 'instagram.com' in url_after.lower() or 'sfl.gl' not in url_after.lower():
                                        log(f"[FINAL] Redirect complete! URL: {url_after}", "SUCCESS")
                                        break
                                except Exception as check_err:
                                    log(f"[FINAL] Check error: {str(check_err)[:30]}", "ERROR")
                                time.sleep(1)
                                waited += 1
                            
                            # SAFETY: Verify session still valid after redirect
                            if not self.is_valid_session():
                                log("[FINAL] CRITICAL: Session lost after redirect!", "ERROR")
                                break
                        else:
                            # Simple delay setelah klik untuk button lain
                            self.human.random_delay(2.0, 4.0)
                        
                        # SAFETY: Check tab count after click
                        try:
                            tabs_after_click = len(self.sb.driver.window_handles)
                            log(f"[CLICK] Tabs after click: {tabs_after_click}", "INFO")
                            
                            if tabs_after_click == 0:
                                log("[CLICK] CRITICAL: All tabs closed after click!", "ERROR")
                                break
                            
                            # Verify anchor still exists
                            if self.anchor not in self.sb.driver.window_handles:
                                log("[CLICK] WARNING: Anchor lost after click!", "WARNING")
                                # Try to recover
                                remaining = self.sb.driver.window_handles
                                if len(remaining) > 0:
                                    self.anchor = remaining[0]
                                    self.sb.driver.switch_to.window(self.anchor)
                                    log(f"[CLICK] Recovered anchor: {self.anchor[:8]}...", "SUCCESS")
                                else:
                                    log("[CLICK] CRITICAL: No tabs remaining!", "ERROR")
                                    break
                        except Exception as tab_check_err:
                            log(f"[CLICK] Tab check error: {str(tab_check_err)[:50]}", "ERROR")
                        
                        try:
                            url_after = self.sb.get_current_url()
                            log(f"After click: {url_after}", "URL")

                            
                            # Deteksi redirect ke domain baru = SUKSES
                            is_different_domain = not any(d in url_after.lower() for d in self.main_domains)
                            is_not_ad = not any(ad in url_after.lower() for ad in AD_DOMAINS)
                            
                            # Redirect ke domain baru (bukan safelink/iklan) = SUKSES
                            if is_different_domain and is_not_ad and url_after != current:
                                log("\n" + "=" * 60, "SUCCESS")
                                log("REDIRECT TO FINAL LINK DETECTED!", "SUCCESS")
                                log(f"URL: {url_after}", "URL")
                                log("=" * 60 + "\n", "SUCCESS")
                                
                                with open("real_link.txt", "w") as f:
                                    f.write(url_after)
                                log("Saved to real_link.txt", "SUCCESS")
                                
                                if any(x in url_after.lower() for x in ["/download", "file", "attachment", "storage"]):
                                    self.download_file(url_after)
                                
                                return
                            
                            # Check download URL langsung
                            if any(x in url_after.lower() for x in ["/download?", "downloadku", "cloudflarestorage", "attachment"]):
                                log("\n" + "=" * 60, "SUCCESS")
                                log("DOWNLOAD URL DETECTED!", "SUCCESS")
                                log(f"URL: {url_after}", "URL")
                                log("=" * 60 + "\n", "SUCCESS")
                                
                                with open("real_link.txt", "w") as f:
                                    f.write(url_after)
                                
                                self.download_file(url_after)
                                return
                        except:
                            pass
                        
                except Exception as e:
                    log(f"Click error: {str(e)[:40]}", "ERROR")
            else:
                log("No button found, trying fallbacks...", "INFO")
                
                # FALLBACK 1: Scroll down to find button
                try:
                    log("[FALLBACK] Scrolling down to find button...", "ACTION")
                    self.human.human_scroll(direction='down', amount=300, safe=True)
                    time.sleep(1)
                    
                    # Try find button again after scroll
                    selector = self.find_button()
                    if selector:
                        log("[FALLBACK] Found button after scroll!", "SUCCESS")
                        continue  # Go back to main loop to click button
                except Exception as e:
                    log(f"[FALLBACK] Scroll error: {str(e)[:40]}", "ERROR")
                
                # FALLBACK 2: Try direct selectors
                fallbacks = [
                    # Priority 1: ID spesifik - HANYA <button>
                    "button#p6exedBWKS",
                    "//button[@id='p6exedBWKS']",
                    
                    # Priority 2: <button> dengan class + text
                    "//button[contains(@class, 'bg-[#1A56DB]') and contains(., 'OPEN LINK')]",
                    "//button[contains(@class, 'bg-[#1A56DB]')]",
                    
                    # Priority 3: <button> dengan text
                    "//button[contains(., 'OPEN LINK')]",
                    "button:contains('Open')",
                    "button:contains('Next')",
                    
                    # Last resort: <a> tags (WARNING: sering buka popup!)
                    "//a[contains(text(), 'Download File')]",
                    "a:contains('Link')"
                ]
                for fb in fallbacks:
                    try:
                        if self.sb.click_if_visible(fb):
                            log("Fallback clicked", "SUCCESS")
                            self.human.random_delay(2, 4, context='after_click')
                            break
                    except:
                        continue
        
        # Final save
        log("\n" + "=" * 60, "INFO")
        log("Loop completed", "INFO")
        try:
            final = self.sb.get_current_url()
            log(f"Final: {final}", "URL")
            with open("real_link.txt", "w") as f:
                f.write(final)
            log("Saved to real_link.txt", "SUCCESS")
        except Exception as e:
            log(f"Final save error: {e}", "ERROR")
        log("=" * 60 + "\n", "INFO")


def main():
    global TARGET_URL
    
    log("=" * 60, "INFO")
    log("SAFELINK FARMING BOT", "INFO")
    log("Loop Mode + Multi-Link + Auto Proxy", "INFO")
    log("=" * 60 + "\n", "INFO")
    
    # === IMPORTS ===
    import requests
    import json
    import os
    from datetime import datetime
    
    # === CONFIG ===
    CONFIG_FILE = "config.json"
    
    if not os.path.exists(CONFIG_FILE):
        log("ERROR: config.json tidak ditemukan!", "ERROR")
        log("Buat file config.json dengan format:", "INFO")
        log('{"bot_number": 1, "firebase": {...}, "loop": {...}}', "INFO")
        return
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
    except Exception as e:
        log(f"ERROR loading config.json: {e}", "ERROR")
        return
    
    # === PARSE CONFIG ===
    BOT_NUMBER = config_data.get("bot_number", 1)
    firebase_config = config_data.get("firebase", None)
    
    # === LOAD LOOP SETTINGS FROM FIREBASE ===
    # Struktur: /bot{N}/settings/loop = {enabled, delay_min, delay_max, max_loops}
    def load_loop_settings_from_firebase(config, bot_number):
        """Load loop settings dari Firebase
        
        Struktur: /bot{N}/settings/loop = {
            enabled: true/false,
            delay_min: 120,
            delay_max: 300,
            max_loops: 0
        }
        """
        default_settings = {
            "enabled": False,
            "delay_min": 120,
            "delay_max": 300,
            "max_loops": 0
        }
        
        try:
            base_url = config.get("databaseURL", "").rstrip("/")
            secret = config.get("databaseSecret", "")
            url = f"{base_url}/bot{bot_number}/settings/loop.json?auth={secret}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data and isinstance(data, dict):
                    log(f"[*] Loaded loop settings dari Firebase untuk bot{bot_number}", "INFO")
                    return {
                        "enabled": data.get("enabled", default_settings["enabled"]),
                        "delay_min": data.get("delay_min", default_settings["delay_min"]),
                        "delay_max": data.get("delay_max", default_settings["delay_max"]),
                        "max_loops": data.get("max_loops", default_settings["max_loops"])
                    }
            log(f"[!] Loop settings tidak ditemukan di Firebase, menggunakan default", "INFO")
            return default_settings
        except Exception as e:
            log(f"Error loading loop settings: {e}", "ERROR")
            return default_settings
    
    # Load loop settings dari Firebase jika tersedia, fallback ke config.json
    if firebase_config:
        loop_config = load_loop_settings_from_firebase(firebase_config, BOT_NUMBER)
    else:
        # Fallback ke config.json jika firebase tidak ada
        loop_config = config_data.get("loop", {
            "enabled": False,
            "delay_min": 120,
            "delay_max": 300,
            "max_loops": 0
        })
    
    LOOP_ENABLED = loop_config.get("enabled", False)
    DELAY_MIN = loop_config.get("delay_min", 120)
    DELAY_MAX = loop_config.get("delay_max", 300)
    MAX_LOOPS = loop_config.get("max_loops", 0)
    
    # === GROQ AI CONFIG (from Firebase) ===
    # API keys diambil dari Firebase: bot{N}/groq/apis
    # Model diambil dari Firebase: bot{N}/groq/model
    groq_manager = None
    if firebase_config:
        groq_manager = GroqAPIManager(firebase_config, BOT_NUMBER)
        if groq_manager.has_available_api():
            log(f"[AI] Groq API: {len(groq_manager.api_keys)} keys loaded from Firebase", "SUCCESS")
            log(f"[AI] Model: {groq_manager.model}", "INFO")
        else:
            log("[AI] No Groq APIs in Firebase - running in DOM-only mode", "INFO")
            groq_manager = None
    
    log(f"Bot Number: {BOT_NUMBER}", "INFO")
    log(f"Loop Mode: {'ENABLED' if LOOP_ENABLED else 'DISABLED'}", "INFO")
    if LOOP_ENABLED:
        log(f"Delay: {DELAY_MIN}-{DELAY_MAX} detik ({DELAY_MIN//60}-{DELAY_MAX//60} menit)", "INFO")
        log(f"Max Loops: {'Unlimited' if MAX_LOOPS == 0 else MAX_LOOPS}", "INFO")
    
    if not firebase_config:
        log("ERROR: Firebase config tidak ditemukan di config.json!", "ERROR")
        return
    
    FIREBASE_MODE = True
    
    # === FIREBASE FUNCTIONS ===
    def load_bot_links(config, bot_number):
        """Load links khusus untuk bot ini dari Firebase"""
        try:
            base_url = config.get("databaseURL", "").rstrip("/")
            secret = config.get("databaseSecret", "")
            
            url = f"{base_url}/bot{bot_number}/links.json?auth={secret}"
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    links = list(data.values()) if isinstance(data, dict) else data
                    return [l for l in links if l and isinstance(l, str)]
            return []
        except Exception as e:
            log(f"Error loading bot links: {e}", "ERROR")
            return []
    
    def load_proxies_from_firebase(config):
        """Load proxy list dari Firebase - HTTP only"""
        try:
            base_url = config.get("databaseURL", "").rstrip("/")
            secret = config.get("databaseSecret", "")
            
            url = f"{base_url}/proxies.json?auth={secret}"
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    all_proxies = list(data.values()) if isinstance(data, dict) else data
                    
                    # Filter HTTP only
                    http_proxies = []
                    for proxy in all_proxies:
                        if isinstance(proxy, str):
                            proxy_lower = proxy.lower()
                            # Skip non-HTTP proxy
                            if proxy_lower.startswith('socks'):
                                continue
                            http_proxies.append(proxy)
                    
                    return http_proxies
            else:
                log(f"Firebase GET error: {resp.status_code}", "ERROR")
            return []
        except Exception as e:
            log(f"Firebase error: {e}", "ERROR")
            return []
    
    def load_blacklist_from_firebase(config):
        """Load blacklist dari Firebase via REST API"""
        try:
            base_url = config.get("databaseURL", "").rstrip("/")
            secret = config.get("databaseSecret", "")
            
            url = f"{base_url}/blacklist.json?auth={secret}"
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    return list(data.values()) if isinstance(data, dict) else data
            return []
        except:
            return []
    
    def add_to_firebase_blacklist(config, proxy):
        """Tambah proxy ke blacklist di Firebase via REST API"""
        try:
            base_url = config.get("databaseURL", "").rstrip("/")
            secret = config.get("databaseSecret", "")
            
            url = f"{base_url}/blacklist.json?auth={secret}"
            resp = requests.post(url, json=proxy, timeout=10)
            
            if resp.status_code != 200:
                log(f"Firebase POST error: {resp.status_code}", "ERROR")
        except Exception as e:
            log(f"Firebase blacklist error: {e}", "ERROR")
    
    def load_cookies_and_url_from_firebase(config, bot_number):
        """Load cookies + URL dari Firebase (ATOMIC SNAPSHOT)
        
        Struktur Firebase: /bot1/cookies = {
            "SESSION": {"value": "xxx", "domain": "app.khaddavi.net", ...},
            "XSRF-TOKEN": {"value": "yyy", "domain": "app.khaddavi.net", ...},
            "__session": {"value": "zzz", "domain": "app.khaddavi.net", ...},
            "_metadata": {"bot_number": 1, "timestamp": "...", "url": "https://..."}
        }
        
        Returns: (cookies_list, target_url, metadata) atau ([], None, None) jika gagal
        
        PENTING: Ambil semua data dalam 1 request untuk konsistensi!
        """
        try:
            base_url = config.get("databaseURL", "").rstrip("/")
            secret = config.get("databaseSecret", "")
            
            # ATOMIC: Ambil semua cookies dalam 1 request
            url = f"{base_url}/bot{bot_number}/cookies.json?auth={secret}"
            
            log(f"[COOKIES] Loading cookies snapshot dari Firebase...", "ACTION")
            resp = requests.get(url, timeout=10)
            
            if resp.status_code == 200:
                all_data = resp.json()
                
                if not all_data or not isinstance(all_data, dict):
                    log(f"[COOKIES] No cookies found di Firebase", "ERROR")
                    return [], None, None
                
                # Extract _metadata untuk ambil URL
                metadata = all_data.get("_metadata", None)
                
                if not metadata or not isinstance(metadata, dict):
                    log(f"[COOKIES] _metadata tidak ditemukan di Firebase!", "ERROR")
                    log(f"[COOKIES] Struktur: {list(all_data.keys())}", "INFO")
                    return [], None, None
                
                target_url = metadata.get("url", None)
                
                if not target_url:
                    log(f"[COOKIES] URL tidak ditemukan di _metadata!", "ERROR")
                    return [], None, None
                
                log(f"[COOKIES]  Target URL dari _metadata: {target_url}", "SUCCESS")
                log(f"[COOKIES]  Timestamp: {metadata.get('timestamp', 'N/A')}", "INFO")
                
                # Convert cookies (skip _metadata karena bukan cookie)
                cookies = []
                for name, data in all_data.items():
                    # Skip _metadata (ini bukan cookie)
                    if name == "_metadata":
                        continue
                    
                    # Pastikan data adalah dict dengan 'value'
                    if not isinstance(data, dict) or 'value' not in data:
                        log(f"[COOKIES]   Skipping invalid cookie: {name}", "INFO")
                        continue
                    
                    cookies.append({
                        'name': name,
                        'value': data['value'],
                        'domain': data.get('domain', ''),
                        'path': data.get('path', '/'),
                        'secure': data.get('secure', True),
                        'httpOnly': data.get('httpOnly', False)
                    })
                
                log(f"[COOKIES]  Loaded {len(cookies)} cookies (SNAPSHOT)", "SUCCESS")
                for cookie in cookies:
                    log(f"[COOKIES]   - {cookie['name']}", "INFO")
                
                log(f"[COOKIES]  ATOMIC SNAPSHOT: Cookies + URL konsisten!", "SUCCESS")
                
                return cookies, target_url, metadata
            else:
                log(f"[COOKIES] Firebase GET error: {resp.status_code}", "ERROR")
                return [], None, None
                
        except Exception as e:
            log(f"[COOKIES] Error loading cookies: {e}", "ERROR")
            return [], None, None
    
    def inject_cookies_to_browser(sb, cookies):
        """Inject cookies ke browser SeleniumBase
        
        Args:
            sb: SeleniumBase instance
            cookies: list of cookie dicts dari load_cookies_from_firebase()
        
        Returns: (success_count, failed_count)
        """
        if not cookies:
            log("[COOKIES] No cookies to inject", "INFO")
            return 0, 0
        
        log(f"[COOKIES] Injecting {len(cookies)} cookies...", "ACTION")
        
        success_count = 0
        failed_count = 0
        
        for cookie in cookies:
            try:
                # Remove expiry field jika ada (bisa bikin error)
                if 'expiry' in cookie:
                    del cookie['expiry']
                
                sb.add_cookie(cookie)
                success_count += 1
                log(f"[COOKIES]    Injected: {cookie['name']}", "SUCCESS")
            except Exception as e:
                failed_count += 1
                log(f"[COOKIES]    Failed: {cookie.get('name', 'unknown')} - {str(e)[:50]}", "ERROR")
        
        log(f"[COOKIES] Injection result: {success_count} success, {failed_count} failed", "INFO")
        
        # Verify cf_clearance
        has_cf_clearance = any(c['name'] == 'cf_clearance' for c in cookies)
        if has_cf_clearance:
            log("[COOKIES]  cf_clearance cookie injected (Cloudflare bypass active)", "SUCCESS")
        else:
            log("[COOKIES]   WARNING: cf_clearance not found in cookies", "INFO")
        
        return success_count, failed_count
    
    def load_cloudflared_domain(firebase_config, bot_number):
        """Load Cloudflared proxy domain dari Firebase
        
        Struktur Firebase: /bot{N}/Cloudflared_proxy = {
            "-OjKvZ6kx71DcwFIYPzD": "domain1.com",
            "-OjKvbFEQKgPAGzsppg4": "domain2.com"
        }
        
        Returns: domain string (random pick) atau None jika tidak ada
        """
        import requests
        try:
            base_url = firebase_config.get("databaseURL", "").rstrip("/")
            secret = firebase_config.get("databaseSecret", "")
            url = f"{base_url}/bot{bot_number}/Cloudflared_proxy.json?auth={secret}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    # Handle both formats: object with keys OR direct string (backward compatible)
                    if isinstance(data, dict):
                        # New format: {"key1": "domain1.com", "key2": "domain2.com"}
                        domains = [v for v in data.values() if isinstance(v, str) and v.strip()]
                        if domains:
                            import random
                            domain = random.choice(domains)
                            log(f"[*] Cloudflared domains: {len(domains)} available", "INFO")
                            log(f"[*] Selected domain: {domain}", "INFO")
                            return domain
                    elif isinstance(data, str) and data.strip():
                        # Old format: direct string (backward compatible)
                        domain = data.strip()
                        log(f"[*] Cloudflared domain: {domain}", "INFO")
                        return domain
            log(f"[*] No Cloudflared domain configured for bot{bot_number}", "INFO")
            return None
        except Exception as e:
            log(f"[!] Error loading Cloudflared domain: {e}", "ERROR")
            return None
            return None
    
    def load_proxy_required_setting(firebase_config, bot_number):
        """Load setting proxy_required dari Firebase untuk bot tertentu
        
        Struktur Firebase: /bot{N}/settings/proxy_required = true/false
        - True: Bot WAJIB pakai proxy, STOP jika tidak ada (IP asli aman)
        - False: Bot boleh jalan dengan IP asli
        """
        import requests
        try:
            base_url = firebase_config.get("databaseURL", "").rstrip("/")
            secret = firebase_config.get("databaseSecret", "")
            url = f"{base_url}/bot{bot_number}/settings/proxy_required.json?auth={secret}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data is not None:
                    result = bool(data)
                    log(f"[*] Firebase /bot{bot_number}/settings/proxy_required = {result}", "INFO")
                    return result
            # Default: True (wajib proxy untuk keamanan)
            log(f"[!] Setting proxy_required tidak ditemukan di Firebase, default: True", "INFO")
            return True
        except Exception as e:
            log(f"Error loading proxy_required setting: {e}", "ERROR")
            return True  # Default safe: wajib proxy
    
    # === LOAD COOKIES + URL (ATOMIC SNAPSHOT) ===
    log(f"\n{'='*60}", "INFO")
    log(f"STEP 1: LOAD COOKIES + URL (ATOMIC SNAPSHOT)", "STEP")
    log(f"{'='*60}", "INFO")
    
    # Load cookies + URL dalam 1 request untuk konsistensi
    COOKIES_SNAPSHOT, TARGET_URL, METADATA = load_cookies_and_url_from_firebase(firebase_config, BOT_NUMBER)
    
    if not COOKIES_SNAPSHOT or not TARGET_URL:
        log(f"\n{'='*60}", "ERROR")
        log(f"ERROR: Tidak bisa load cookies atau URL dari Firebase!", "ERROR")
        log(f"{'='*60}", "ERROR")
        log(f"Pastikan struktur Firebase benar:", "INFO")
        log(f"  /bot1/cookies/SESSION = {{value, domain, ...}}", "INFO")
        log(f"  /bot1/cookies/XSRF-TOKEN = {{value, domain, ...}}", "INFO")
        log(f"  /bot1/cookies/__session = {{value, domain, ...}}", "INFO")
        log(f"  /bot1/cookies/_metadata = {{url, timestamp, bot_number}}", "INFO")
        log(f"{'='*60}", "ERROR")
        return
    
    log(f"\n{'='*60}", "SUCCESS")
    log(f" ATOMIC SNAPSHOT BERHASIL!", "SUCCESS")
    log(f"{'='*60}", "SUCCESS")
    log(f"  Cookies: {len(COOKIES_SNAPSHOT)} items", "INFO")
    log(f"  Target URL: {TARGET_URL[:60]}...", "INFO")
    log(f"  Timestamp: {METADATA.get('timestamp', 'N/A')}", "INFO")
    log(f"{'='*60}\n", "SUCCESS")
    
    # PENTING: Cookies + URL sudah di-snapshot, dijamin konsisten!
    # Tidak akan ada masalah cookies lama vs URL baru
    
    # === LOAD CLOUDFLARED DOMAIN ===
    CLOUDFLARED_DOMAIN = load_cloudflared_domain(firebase_config, BOT_NUMBER)
    
    # === LOAD PROXY REQUIRED SETTING ===
    PROXY_REQUIRED_SETTING = load_proxy_required_setting(firebase_config, BOT_NUMBER)
    log(f"\n{'='*50}", "INFO")
    log(f"PROXY REQUIREMENT: {'WAJIB PROXY' if PROXY_REQUIRED_SETTING else 'BOLEH TANPA PROXY'}", "STEP")
    if CLOUDFLARED_DOMAIN:
        log(f"CLOUDFLARED DOMAIN: {CLOUDFLARED_DOMAIN} (PRIORITY)", "STEP")
    log(f"{'='*50}", "INFO")
    
    # === INITIALIZE IP BLACKLIST MANAGER - SIMPLIFIED ===
    log("\n[*] Initializing IP Blacklist Manager...", "INFO")
    ip_blacklist_manager = IPBlacklistManager(firebase_config)
    blacklist_stats = ip_blacklist_manager.get_blacklist_stats()
    log(f"[+] Dead IPs: {blacklist_stats['total_dead']}", "INFO")
    log(f"[+] Used IPs: {blacklist_stats['total_used']}", "INFO")
    log(f"[+] Total Blacklisted: {blacklist_stats['total_blacklisted']}", "INFO")
    
    # === LOAD PROXY (GLOBAL) ===
    log("\n[*] Loading proxies (global)...", "INFO")
    PROXY_LIST = load_proxies_from_firebase(firebase_config)
    log(f"[+] Loaded {len(PROXY_LIST)} proxies from Firebase", "SUCCESS")
    
    # PROXY_REQUIRED sekarang diambil dari Firebase setting, bukan dari jumlah proxy
    PROXY_REQUIRED = PROXY_REQUIRED_SETTING
    
    STRICT_HTTPS_CHECK = False
    
    BLACKLIST_FILE = "proxy_blacklist.json"
    VALID_PROXY = None
    CLOUDFLARED_PROCESS = None  # Track cloudflared background process
    CLOUDFLARED_PROXY_VALID = False  # Track if cloudflared proxy is working
    
    # Load blacklist
    blacklist = []
    if FIREBASE_MODE:
        blacklist = load_blacklist_from_firebase(firebase_config)
        log(f"Loaded {len(blacklist)} blacklisted proxies from Firebase", "INFO")
    elif os.path.exists(BLACKLIST_FILE):
        try:
            with open(BLACKLIST_FILE, 'r') as f:
                blacklist = json.load(f)
        except:
            blacklist = []
    
    def install_cloudflared():
        """Auto-install cloudflared via winget (Windows only)"""
        try:
            log("[CLOUDFLARED] Attempting auto-install via winget...", "ACTION")
            
            # Check if winget is available
            result = subprocess.run(['winget', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                log("[CLOUDFLARED] winget not available", "ERROR")
                return False
            
            log("[CLOUDFLARED] Installing cloudflared (this may take 1-2 minutes)...", "INFO")
            
            # Install cloudflared
            result = subprocess.run(
                ['winget', 'install', '--id', 'Cloudflare.cloudflared', '-e', 
                 '--accept-source-agreements', '--accept-package-agreements'],
                capture_output=True, text=True, timeout=180  # 3 minutes timeout
            )
            
            if result.returncode == 0 or "successfully installed" in result.stdout.lower():
                log("[CLOUDFLARED] Installation completed!", "SUCCESS")
                log("[CLOUDFLARED] Verifying installation...", "INFO")
                
                # Wait a bit for PATH to update
                time.sleep(2)
                
                # Verify installation
                try:
                    verify = subprocess.run(['cloudflared', '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if verify.returncode == 0:
                        version = verify.stdout.strip()
                        log(f"[CLOUDFLARED] Verified: {version}", "SUCCESS")
                        return True
                    else:
                        log("[CLOUDFLARED] Installation completed but not in PATH yet", "INFO")
                        log("[CLOUDFLARED] Please restart terminal and run bot again", "INFO")
                        return False
                except:
                    log("[CLOUDFLARED] Installation completed but not in PATH yet", "INFO")
                    log("[CLOUDFLARED] Please restart terminal and run bot again", "INFO")
                    return False
            else:
                log(f"[CLOUDFLARED] Installation failed: {result.stderr[:200]}", "ERROR")
                return False
                
        except subprocess.TimeoutExpired:
            log("[CLOUDFLARED] Installation timeout (took too long)", "ERROR")
            return False
        except Exception as e:
            log(f"[CLOUDFLARED] Installation error: {e}", "ERROR")
            return False
    
    def check_cloudflared_installed(auto_install=True):
        """Check if cloudflared is installed and accessible
        
        Args:
            auto_install: If True, attempt to auto-install if not found
        """
        # Try direct command first
        try:
            result = subprocess.run(['cloudflared', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                log(f"[CLOUDFLARED] Installed: {version}", "SUCCESS")
                return True
        except FileNotFoundError:
            pass
        except Exception:
            pass
        
        # Try common installation paths
        common_paths = [
            r"C:\Program Files (x86)\cloudflared\cloudflared.exe",  # Most common
            r"C:\Program Files\cloudflared\cloudflared.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared_Microsoft.Winget.Source_8wekyb3d8bbwe\cloudflared.exe"),
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Links\cloudflared.exe"),
            r"C:\Windows\System32\cloudflared.exe",
        ]
        
        # Check if we have saved path
        if os.path.exists('cloudflared_path.txt'):
            try:
                with open('cloudflared_path.txt', 'r') as f:
                    saved_path = f.read().strip()
                    if saved_path and os.path.exists(saved_path):
                        common_paths.insert(0, saved_path)  # Try saved path first
            except:
                pass
        
        for path in common_paths:
            if os.path.exists(path):
                try:
                    result = subprocess.run([path, '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        version = result.stdout.strip()
                        log(f"[CLOUDFLARED] Found at: {path}", "SUCCESS")
                        log(f"[CLOUDFLARED] Version: {version}", "SUCCESS")
                        # Use full path for commands
                        return path
                except:
                    pass
        
        log("[CLOUDFLARED] Not installed or not in PATH", "ERROR")
        
        # Auto-install if enabled
        if auto_install:
            log("[CLOUDFLARED] Attempting auto-install...", "INFO")
            if install_cloudflared():
                # Try again after install
                try:
                    result = subprocess.run(['cloudflared', '--version'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return True
                except:
                    pass
                
                # Check common paths again
                for path in common_paths:
                    if os.path.exists(path):
                        try:
                            result = subprocess.run([path, '--version'], 
                                                  capture_output=True, text=True, timeout=5)
                            if result.returncode == 0:
                                log(f"[CLOUDFLARED] Found at: {path}", "SUCCESS")
                                return path
                        except:
                            pass
                
                log("[CLOUDFLARED] Installed but not accessible", "ERROR")
                log("[CLOUDFLARED] Please restart terminal and run bot again", "INFO")
                return False
            else:
                log("[CLOUDFLARED] Auto-install failed", "ERROR")
                log("[CLOUDFLARED] Manual install: winget install --id Cloudflare.cloudflared", "INFO")
                log("[CLOUDFLARED] Or download: https://github.com/cloudflare/cloudflared/releases", "INFO")
        
        return False
    
    def start_cloudflared_tunnel(domain, local_port=9999, cloudflared_path='cloudflared'):
        """Start cloudflared tunnel in background
        
        Args:
            domain: Cloudflared domain
            local_port: Local port for tunnel
            cloudflared_path: Path to cloudflared executable (can be full path or 'cloudflared')
        
        Returns: (process, success)
        """
        try:
            log(f"[CLOUDFLARED] Starting tunnel: {domain} -> localhost:{local_port}", "ACTION")
            
            # Start cloudflared in background
            process = subprocess.Popen(
                [cloudflared_path, 'access', 'tcp', '--hostname', domain, '--url', f'localhost:{local_port}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for tunnel to establish
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                log(f"[CLOUDFLARED] Tunnel started successfully (PID: {process.pid})", "SUCCESS")
                return process, True
            else:
                # Process died, get error
                _, stderr = process.communicate(timeout=1)
                log(f"[CLOUDFLARED] Tunnel failed to start: {stderr[:200]}", "ERROR")
                return None, False
                
        except Exception as e:
            log(f"[CLOUDFLARED] Error starting tunnel: {e}", "ERROR")
            return None, False
    
    def stop_cloudflared_tunnel(process):
        """Stop cloudflared tunnel process"""
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=5)
                log("[CLOUDFLARED] Tunnel stopped", "INFO")
            except:
                process.kill()
                log("[CLOUDFLARED] Tunnel killed (force)", "INFO")
    
    def test_cloudflared_proxy(local_port=9999):
        """Test if cloudflared proxy is working
        
        Returns: (success, proxy_ip)
        """
        try:
            proxy_url = f"http://127.0.0.1:{local_port}"
            proxy_dict = {"http": proxy_url, "https": proxy_url}
            
            # Test 1: Get IP
            test_ip = get_my_ip(proxy_dict)
            if not test_ip:
                log("[CLOUDFLARED] Failed to get IP through tunnel", "ERROR")
                return False, None
            
            log(f"[CLOUDFLARED] Tunnel IP: {test_ip}", "SUCCESS")
            
            # Test 2: HTTPS connectivity
            if not test_proxy_https_basic(proxy_dict):
                log("[CLOUDFLARED] HTTPS test failed", "ERROR")
                return False, test_ip
            
            log("[CLOUDFLARED] HTTPS test passed", "SUCCESS")
            return True, test_ip
            
        except Exception as e:
            log(f"[CLOUDFLARED] Test error: {e}", "ERROR")
            return False, None
    
    def get_my_ip(proxy=None):
        """Get current public IP with multiple fallback URLs"""
        # List URL untuk test IP (fallback jika satu gagal)
        test_urls = [
            "http://httpbin.org/ip",
            "http://api.ipify.org?format=json",
            "http://ip-api.com/json/?fields=query"
        ]
        
        timeout = 15 if proxy else 8  # Timeout lebih lama untuk proxy
        
        for url in test_urls:
            try:
                if proxy:
                    resp = requests.get(url, proxies=proxy, timeout=timeout)
                else:
                    resp = requests.get(url, timeout=timeout)
                
                # Parse response berdasarkan URL
                if resp.status_code == 200:
                    data = resp.json()
                    # httpbin.org format
                    if 'origin' in data:
                        return data['origin'].split(',')[0].strip()
                    # ipify format
                    elif 'ip' in data:
                        return data['ip']
                    # ip-api format
                    elif 'query' in data:
                        return data['query']
            except requests.exceptions.ProxyError as e:
                if proxy:
                    log(f"Proxy connection refused: {str(e)[:100]}", "ERROR")
                continue
            except requests.exceptions.Timeout:
                if proxy:
                    log(f"Proxy timeout untuk {url}", "ERROR")
                continue
            except Exception as e:
                if proxy:
                    log(f"get_my_ip error: {str(e)[:100]}", "ERROR")
                continue
        
        return None
    
    def test_proxy_https(proxy_dict, target_url):
        """Verify proxy can access HTTPS URL"""
        try:
            resp = requests.get(target_url, proxies=proxy_dict, timeout=15, 
                              headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"},
                              allow_redirects=True)
            return resp.status_code in [200, 301, 302, 303, 307, 308]
        except Exception as e:
            return False
    
    def test_proxy_https_basic(proxy_dict):
        """Verify proxy HTTPS connectivity - simple check"""
        test_urls = [
            "https://httpbin.org/ip",
            "https://api.ipify.org",
        ]
        
        for url in test_urls:
            try:
                resp = requests.get(url, proxies=proxy_dict, timeout=10,
                                  headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0"},
                                  allow_redirects=True)
                if resp.status_code == 200:
                    return True
            except:
                continue
        
        return False
    
    # === LOAD ORIGINAL IP ===
    
    def parse_proxy(proxy_str):
        """Parse proxy string to requests/chrome format"""
        proxy_str = proxy_str.strip()
        
        # Clean HTTP prefix
        if proxy_str.startswith("http://"):
            proxy_str = proxy_str.replace("http://", "")
        elif proxy_str.startswith("https://"):
            proxy_str = proxy_str.replace("https://", "")
        
        parts = proxy_str.split(':')
        
        if len(parts) == 2:
            ip, port = parts
            proxy_url = f"http://{ip}:{port}"
            chrome_arg = f"{ip}:{port}"
            return proxy_url, chrome_arg, None, None, "http"
        elif len(parts) == 4:
            ip, port, user, passwd = parts
            proxy_url = f"http://{user}:{passwd}@{ip}:{port}"
            chrome_arg = f"{ip}:{port}"
            return proxy_url, chrome_arg, user, passwd, "http"
        else:
            return None, None, None, None, None
    
    # === CEK PROXY SETTING ===
    if PROXY_REQUIRED_SETTING:
        log("=== PROXY MODE: ENABLED ===", "STEP")
        original_ip = get_my_ip()
        log(f"Original IP: {original_ip} (TIDAK BOLEH DIPAKAI!)", "INFO")
        
        # === PRIORITY 1: CLOUDFLARED PROXY ===
        if CLOUDFLARED_DOMAIN:
            log("\n=== CLOUDFLARED PROXY (PRIORITY 1) ===", "STEP")
            
            # Check if cloudflared is installed
            cloudflared_path = check_cloudflared_installed()
            if cloudflared_path:
                # Start cloudflared tunnel (support both 'cloudflared' command and full path)
                CLOUDFLARED_PROCESS, tunnel_success = start_cloudflared_tunnel(
                    CLOUDFLARED_DOMAIN, 9999, 
                    cloudflared_path if isinstance(cloudflared_path, str) and os.path.exists(cloudflared_path) else 'cloudflared'
                )
                
                if tunnel_success:
                    # Test cloudflared proxy
                    cf_success, cf_ip = test_cloudflared_proxy(9999)
                    
                    if cf_success and cf_ip:
                        # Check if IP is blacklisted
                        if ip_blacklist_manager.is_blacklisted(cf_ip):
                            log(f"[CLOUDFLARED] IP {cf_ip} is BLACKLISTED!", "ERROR")
                            log("[CLOUDFLARED] Cannot use this tunnel", "ERROR")
                            stop_cloudflared_tunnel(CLOUDFLARED_PROCESS)
                            CLOUDFLARED_PROCESS = None
                        else:
                            # Test IP quality
                            proxy_dict = {"http": f"http://127.0.0.1:9999", "https": f"http://127.0.0.1:9999"}
                            quality_score, can_use, reason = ip_blacklist_manager.test_ip_quality(cf_ip, proxy_dict)
                            
                            if can_use:
                                log(f"[CLOUDFLARED] Proxy VALID! IP: {cf_ip}", "SUCCESS")
                                log(f"[CLOUDFLARED] Quality score: {quality_score}/100", "SUCCESS")
                                VALID_PROXY = "127.0.0.1:9999"  # Use cloudflared local proxy
                                CLOUDFLARED_PROXY_VALID = True
                            else:
                                log(f"[CLOUDFLARED] IP quality check FAILED: {reason}", "ERROR")
                                log(f"[CLOUDFLARED] Score: {quality_score}/100", "ERROR")
                                ip_blacklist_manager.add_to_dead(cf_ip)
                                stop_cloudflared_tunnel(CLOUDFLARED_PROCESS)
                                CLOUDFLARED_PROCESS = None
                    else:
                        log("[CLOUDFLARED] Proxy test failed", "ERROR")
                        stop_cloudflared_tunnel(CLOUDFLARED_PROCESS)
                        CLOUDFLARED_PROCESS = None
                else:
                    log("[CLOUDFLARED] Failed to start tunnel", "ERROR")
            else:
                log("[CLOUDFLARED] Not installed - skipping", "ERROR")
                log("[CLOUDFLARED] Install: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/", "INFO")
        
        # === PRIORITY 2: GLOBAL PROXIES (jika cloudflared gagal) ===
        if not VALID_PROXY:
            log("\n=== GLOBAL PROXY FALLBACK (PRIORITY 2) ===", "STEP")
    else:
        # proxy_required = false → SKIP semua pencarian proxy
        log("=" * 60, "INFO")
        log("[!] PROXY MODE: DISABLED (proxy_required = false)", "INFO")
        log("   Bot akan jalan dengan IP ASLI", "INFO")
        log("=" * 60, "INFO")
        original_ip = get_my_ip()
        log(f"IP yang dipakai: {original_ip}", "INFO")
    
    if PROXY_REQUIRED and not VALID_PROXY:
        # === CEK PROXY LIST dengan GRACEFUL WAIT ===
        # Gunakan delay yang sama seperti loop sukses (dari DB)
        WAIT_INTERVAL = random.randint(DELAY_MIN, DELAY_MAX)
        log(f"[*] Proxy wait interval: {WAIT_INTERVAL} seconds ({WAIT_INTERVAL//60} min {WAIT_INTERVAL%60} sec)", "INFO")

        
        while not VALID_PROXY:
            # === PRIORITY 1: CEK CLOUDFLARED PROXY DULU (SETIAP LOOP) ===
            if CLOUDFLARED_DOMAIN:
                log("\n=== CLOUDFLARED PROXY CHECK (PRIORITY 1) ===", "STEP")
                
                # Cek apakah cloudflared installed
                cloudflared_path = check_cloudflared_installed(auto_install=False)  # Tidak auto-install di loop
                
                if cloudflared_path:
                    log(f"[CLOUDFLARED] Found cloudflared: {cloudflared_path if isinstance(cloudflared_path, str) else 'system PATH'}", "INFO")
                    # Stop existing tunnel if any (cleanup)
                    if CLOUDFLARED_PROCESS:
                        log("[CLOUDFLARED] Stopping existing tunnel...", "INFO")
                        stop_cloudflared_tunnel(CLOUDFLARED_PROCESS)
                        CLOUDFLARED_PROCESS = None
                        time.sleep(2)  # Wait for cleanup
                    
                    # Start fresh tunnel
                    log(f"[CLOUDFLARED] Starting fresh tunnel: {CLOUDFLARED_DOMAIN}", "ACTION")
                    # Pastikan cloudflared_path adalah string, bukan boolean
                    cf_path = cloudflared_path if isinstance(cloudflared_path, str) else 'cloudflared'
                    CLOUDFLARED_PROCESS, tunnel_success = start_cloudflared_tunnel(CLOUDFLARED_DOMAIN, 9999, cf_path)
                    
                    if tunnel_success:
                        # Test cloudflared proxy
                        log("[CLOUDFLARED] Testing tunnel connection...", "ACTION")
                        time.sleep(2)  # Extra wait untuk memastikan tunnel siap
                        cf_success, cf_ip = test_cloudflared_proxy(9999)
                        
                        if cf_success and cf_ip:
                            log(f"[CLOUDFLARED] Tunnel working! IP: {cf_ip}", "SUCCESS")
                            
                            # Check IP blacklist
                            if not ip_blacklist_manager.is_blacklisted(cf_ip):
                                # Test IP quality
                                proxy_dict = {"http": f"http://127.0.0.1:9999", "https": f"http://127.0.0.1:9999"}
                                quality_score, can_use, reason = ip_blacklist_manager.test_ip_quality(cf_ip, proxy_dict)
                                
                                if can_use:
                                    log(f"[CLOUDFLARED] Proxy VALID! IP: {cf_ip}", "SUCCESS")
                                    log(f"[CLOUDFLARED] Quality score: {quality_score}/100", "SUCCESS")
                                    VALID_PROXY = "127.0.0.1:9999"
                                    CLOUDFLARED_PROXY_VALID = True
                                    break  # Keluar dari while loop - PROXY FOUND!
                                else:
                                    log(f"[CLOUDFLARED] IP quality check FAILED: {reason}", "ERROR")
                                    log(f"[CLOUDFLARED] Score: {quality_score}/100", "ERROR")
                            else:
                                log(f"[CLOUDFLARED] IP {cf_ip} is blacklisted", "ERROR")
                        else:
                            log("[CLOUDFLARED] Tunnel test failed", "ERROR")
                    else:
                        log("[CLOUDFLARED] Failed to start tunnel", "ERROR")
                    
                    # Cleanup failed cloudflared
                    if CLOUDFLARED_PROCESS:
                        log("[CLOUDFLARED] Cleaning up failed tunnel...", "INFO")
                        stop_cloudflared_tunnel(CLOUDFLARED_PROCESS)
                        CLOUDFLARED_PROCESS = None
                else:
                    log("[CLOUDFLARED] Not installed - skipping", "INFO")
                    log("[CLOUDFLARED] Install: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/", "INFO")
            
            # === PRIORITY 2: CEK GLOBAL PROXY ===
            log("\n=== GLOBAL PROXY FALLBACK (PRIORITY 2) ===", "STEP")
            
            # Reload proxy list dan blacklist dari Firebase setiap check
            if FIREBASE_MODE:
                PROXY_LIST = load_proxies_from_firebase(firebase_config)
                blacklist = load_blacklist_from_firebase(firebase_config)
            
            if not PROXY_LIST or len(PROXY_LIST) == 0:
                log("=" * 50, "INFO")
                log("Tidak ada proxy di database", "INFO")
                
                # Check if loop enabled
                if not LOOP_ENABLED:
                    log("[!] Loop mode DISABLED - Bot akan STOP", "ERROR")
                    log("[!] Tidak ada proxy dan tidak bisa retry", "ERROR")
                    log("=" * 50, "INFO")
                    # Cleanup cloudflared if running
                    if CLOUDFLARED_PROCESS:
                        stop_cloudflared_tunnel(CLOUDFLARED_PROCESS)
                    return
                
                log(f"Menunggu {WAIT_INTERVAL} detik...", "INFO")
                log("Jalankan ProxyHunter.py untuk menambah proxy", "INFO")
                log("=" * 50, "INFO")
                time.sleep(WAIT_INTERVAL)
                continue  # Kembali ke awal loop (akan cek cloudflared lagi)
            
            # Filter proxy yang sudah di-blacklist
            available_proxies = [p.strip() for p in PROXY_LIST if p.strip() and p.strip() not in blacklist]
            blacklisted_count = len(PROXY_LIST) - len(available_proxies)
            
            if blacklisted_count > 0:
                log(f"Skipped {blacklisted_count} blacklisted proxies", "INFO")
            
            if len(available_proxies) == 0:
                log("=" * 50, "INFO")
                log("Semua proxy sudah di-blacklist!", "INFO")
                
                # Check if loop enabled
                if not LOOP_ENABLED:
                    log("[!] Loop mode DISABLED - Bot akan STOP", "ERROR")
                    log("[!] Semua proxy blacklisted dan tidak bisa retry", "ERROR")
                    log("=" * 50, "INFO")
                    # Cleanup cloudflared if running
                    if CLOUDFLARED_PROCESS:
                        stop_cloudflared_tunnel(CLOUDFLARED_PROCESS)
                    return
                
                log(f"Menunggu {WAIT_INTERVAL} detik untuk proxy baru...", "INFO")
                log("Jalankan ProxyHunter.py atau clear blacklist", "INFO")
                log("=" * 50, "INFO")
                time.sleep(WAIT_INTERVAL)
                continue  # Kembali ke awal loop (akan cek cloudflared lagi)
            
            log(f"Testing {len(available_proxies)} proxies...", "ACTION")
            
            test_proxies = available_proxies.copy()
            random.shuffle(test_proxies)
            
            for proxy in test_proxies:
                if not proxy or ':' not in proxy:
                    continue
                
                # Filter non-HTTP proxy
                proxy_lower = proxy.lower()
                if proxy_lower.startswith('socks'):
                    if proxy not in blacklist:
                        blacklist.append(proxy)
                        if FIREBASE_MODE:
                            add_to_firebase_blacklist(firebase_config, proxy)
                    continue
                
                proxy_url, chrome_arg, user, passwd, proxy_type = parse_proxy(proxy)
                if not proxy_url:
                    continue  # Skip invalid format tanpa log
                
                # Cek AUTH - skip dan blacklist proxy dengan user:pass
                if user and passwd:
                    if proxy not in blacklist:
                        blacklist.append(proxy)
                        if FIREBASE_MODE:
                            add_to_firebase_blacklist(firebase_config, proxy)
                    continue
                
                log(f"Testing: {proxy}", "ACTION")
                proxies_dict = {"http": proxy_url, "https": proxy_url}
                
                check_ip = get_my_ip(proxies_dict)
                
                if check_ip and (not original_ip or original_ip not in check_ip):
                    if test_proxy_https_basic(proxies_dict):
                        log(f"PROXY OK: {proxy}", "SUCCESS")
                        log(f"Proxy IP: {check_ip}", "SUCCESS")
                        VALID_PROXY = proxy
                        break
                    else:
                        log(f"HTTPS failed: {proxy}", "ERROR")
                else:
                    log(f"IP check failed: {proxy}", "ERROR")
            
            # Jika masih tidak ada valid proxy setelah test semua, tunggu dan retry
            if not VALID_PROXY:
                log("=" * 50, "INFO")
                log("Tidak ada proxy valid saat ini", "INFO")
                log(f"Menunggu {WAIT_INTERVAL} detik...", "INFO")
                log("Bot akan coba lagi setelah delay", "INFO")
                log("=" * 50, "INFO")
                time.sleep(WAIT_INTERVAL)
                continue  # Kembali ke awal loop (akan cek cloudflared lagi)
            
            # === IP QUALITY CHECK ===
            # Jika sampai sini berarti VALID_PROXY sudah ada
            log(f"Using proxy: {VALID_PROXY}", "SUCCESS")
            log("\n[*] Checking IP quality...", "ACTION")
            proxy_url, chrome_arg, proxy_user, proxy_pass, proxy_type = parse_proxy(VALID_PROXY)
            
            # Get proxy IP
            proxy_dict = {"http": proxy_url, "https": proxy_url}
            proxy_ip = get_my_ip(proxy_dict)
            
            if proxy_ip:
                log(f"[+] Proxy IP: {proxy_ip}", "INFO")
                
                # Check if blacklisted
                if ip_blacklist_manager.is_blacklisted(proxy_ip):
                    log(f"\n{'='*60}", "ERROR")
                    log(f"[BLACKLIST] IP {proxy_ip} is BLACKLISTED!", "ERROR")
                    log(f"[BLACKLIST] This IP was used before", "ERROR")
                    log(f"[BLACKLIST] Finding another proxy...", "ERROR")
                    log(f"{'='*60}\n", "ERROR")
                    
                    # ESCAPE MECHANISM: Jika proxy yang sama terus muncul, break
                    if len(global_proxies) == 1:
                        log("=" * 60, "ERROR")
                        log("[ESCAPE] Only 1 proxy available and it's blacklisted!", "ERROR")
                        log("[ESCAPE] Cannot continue with proxy requirement", "ERROR")
                        log("[ESCAPE] Options:", "ERROR")
                        log("  1. Add more proxies to Firebase", "ERROR")
                        log("  2. Set proxy_required = False", "ERROR")
                        log("  3. Clear blacklist in Firebase", "ERROR")
                        log("=" * 60, "ERROR")
                        sys.exit(1)
                    
                    VALID_PROXY = None
                    continue  # Kembali ke awal loop (akan cek cloudflared lagi)
                
                # Test IP quality
                quality_score, can_use, reason = ip_blacklist_manager.test_ip_quality(proxy_ip, proxy_dict)
                
                if not can_use:
                    log(f"\n{'='*60}", "ERROR")
                    log(f"[IP-TEST] IP quality check FAILED!", "ERROR")
                    log(f"[IP-TEST] Score: {quality_score}/100", "ERROR")
                    log(f"[IP-TEST] Reason: {reason}", "ERROR")
                    log(f"{'='*60}\n", "ERROR")
                    
                    # ESCAPE MECHANISM: Jika proxy yang sama terus gagal quality check
                    if len(global_proxies) == 1:
                        log("=" * 60, "ERROR")
                        log("[ESCAPE] Only 1 proxy available and quality check failed!", "ERROR")
                        log(f"[ESCAPE] Score: {quality_score}/100 (minimum: 20)", "ERROR")
                        log("[ESCAPE] This should not happen with ELITE techniques!", "ERROR")
                        log("[ESCAPE] Possible issues:", "ERROR")
                        log("  - Proxy is completely dead", "ERROR")
                        log("  - Cloudflare blocking this proxy", "ERROR")
                        log("[ESCAPE] Options:", "ERROR")
                        log("  1. Add more proxies to Firebase", "ERROR")
                        log("  2. Set proxy_required = False (use local IP)", "ERROR")
                        log("=" * 60, "ERROR")
                        sys.exit(1)
                    
                    # Add to DEAD list (IP mati/tidak bisa dipakai)
                    ip_blacklist_manager.add_to_dead(proxy_ip)
                    VALID_PROXY = None
                    continue  # Kembali ke awal loop (akan cek cloudflared lagi)
                
                log(f"[IP-TEST] IP quality check PASSED", "SUCCESS")
                log(f"[IP-TEST] Quality score: {quality_score}/100", "SUCCESS")
                break  # Keluar dari loop, proxy valid dan lolos quality check
            else:
                log("[IP-TEST] Could not get proxy IP", "ERROR")
                VALID_PROXY = None
                continue  # Kembali ke awal loop untuk cari proxy lain
    
    # === DOUBLE-CHECK PROTEKSI ===
    if PROXY_REQUIRED_SETTING and not VALID_PROXY:
        log("=" * 60, "ERROR")
        log("FATAL: proxy_required=True di Firebase tapi tidak ada proxy!", "ERROR")
        log("Bot STOP untuk proteksi IP asli.", "ERROR")
        log("=" * 60, "ERROR")
        log("SOLUSI:", "INFO")
        log("  1. Tambah proxy ke Firebase, ATAU", "INFO")
        log(f"  2. Set /bot{BOT_NUMBER}/settings/proxy_required = false", "INFO")
        log("=" * 60, "ERROR")
        return
    
    # === FINAL IP CHECK & BLACKLIST PROTECTION ===
    # Dapatkan IP yang akan digunakan (proxy atau lokal)
    if VALID_PROXY:
        if CLOUDFLARED_PROXY_VALID:
            # Cloudflared proxy - use localhost:9999
            proxy_dict = {"http": "http://127.0.0.1:9999", "https": "http://127.0.0.1:9999"}
            current_ip = get_my_ip(proxy_dict)
            ip_type = "CLOUDFLARED"
        else:
            # Global proxy
            proxy_url, _, _, _, _ = parse_proxy(VALID_PROXY)
            proxy_dict = {"http": proxy_url, "https": proxy_url}
            current_ip = get_my_ip(proxy_dict)
            ip_type = "PROXY"
    else:
        current_ip = get_my_ip()
        ip_type = "LOCAL"
    
    if not current_ip:
        log("=" * 60, "ERROR")
        log("FATAL: Tidak bisa mendapatkan IP!", "ERROR")
        log("=" * 60, "ERROR")
        return
    
    log("\n" + "=" * 60, "INFO")
    log(f"[FINAL CHECK] IP yang akan digunakan: {current_ip} ({ip_type})", "INFO")
    if ip_type == "CLOUDFLARED":
        log(f"[FINAL CHECK] Tunnel: {CLOUDFLARED_DOMAIN} -> localhost:9999", "INFO")
        log(f"[FINAL CHECK] IP publik HP: {current_ip} (akan di-blacklist)", "INFO")
    log("=" * 60, "INFO")
    
    # CHECK: Apakah IP ini sudah pernah dipakai sebelumnya? - CEK DARI FIREBASE
    log(f"[BLACKLIST] Checking IP {current_ip} in FIREBASE database...", "ACTION")
    if ip_blacklist_manager.is_blacklisted(current_ip):
        log("\n" + "=" * 60, "ERROR")
        log(f"[FATAL] IP {current_ip} SUDAH PERNAH DIPAKAI!", "ERROR")
        log(f"[FATAL] IP ini ada di FIREBASE blacklist database!", "ERROR")
        log(f"[FATAL] TIDAK BOLEH pakai IP yang sama 2x!", "ERROR")
        log(f"[FATAL] Ini untuk PROTEKSI IDENTITAS!", "ERROR")
        log("=" * 60, "ERROR")
        log("\n[INFO] Kenapa ini penting?", "INFO")
        log("  - 1 IP hanya boleh dipakai 1 kali (berhasil/gagal)", "INFO")
        log("  - Pakai IP sama = identitas bisa terungkap", "INFO")
        log("  - Sistem akan STOP untuk keamanan", "INFO")
        log("=" * 60 + "\n", "ERROR")
        
        if ip_type == "LOCAL":
            log("[SOLUSI] Untuk IP LOCAL:", "INFO")
            log("  1. Gunakan proxy (set proxy_required=true)", "INFO")
            log("  2. Atau ganti koneksi internet (restart router/VPN)", "INFO")
        elif ip_type == "CLOUDFLARED":
            log("[SOLUSI] Untuk CLOUDFLARED:", "INFO")
            log("  1. IP HP lo sudah di-blacklist", "INFO")
            log("  2. Ganti IP HP (restart router/mobile data)", "INFO")
            log("  3. Atau pakai global proxies (hapus Cloudflared domain)", "INFO")
        else:
            log("[SOLUSI] Untuk PROXY:", "INFO")
            log("  1. Proxy ini sudah di-blacklist otomatis", "INFO")
            log("  2. Bot akan cari proxy lain di run berikutnya", "INFO")
        log("=" * 60, "ERROR")
        return
    
    # IP belum pernah dipakai, LANGSUNG BLACKLIST ke FIREBASE sekarang
    log(f"\n[BLACKLIST] Adding IP {current_ip} to FIREBASE NOW", "ACTION")
    
    # CRITICAL: Tambahkan ke Firebase SEBELUM bot jalan
    blacklist_success = ip_blacklist_manager.add_to_used(current_ip)
    
    if not blacklist_success:
        log("=" * 60, "ERROR")
        log("[FATAL] Gagal menambahkan IP ke FIREBASE!", "ERROR")
        log("[FATAL] Bot STOP untuk keamanan!", "ERROR")
        log("=" * 60, "ERROR")
        return
    
    log(f"[BLACKLIST] IP {current_ip} berhasil ditambahkan!", "SUCCESS")
    log(f"[BLACKLIST] IP ini TIDAK BISA dipakai lagi\n", "SUCCESS")
    
    if ip_type == "CLOUDFLARED":
        log("=" * 60, "INFO")
        log("[INFO] Cloudflared Tunnel Info:", "INFO")
        log(f"  - Localhost proxy: 127.0.0.1:9999 (BISA DIPAKAI LAGI)", "INFO")
        log(f"  - IP publik HP: {current_ip} (SUDAH DI-BLACKLIST)", "INFO")
        log(f"  - Next run: Ganti IP HP atau pakai proxy lain", "INFO")
        log("=" * 60, "INFO")
    
    # Warning jika jalan tanpa proxy (hanya jika diizinkan setting)
    if not PROXY_REQUIRED_SETTING and not VALID_PROXY:
        log("=" * 60, "INFO")
        log("[!] PERHATIAN: Bot jalan TANPA PROXY (IP asli)", "INFO")
        log(f"   Setting /bot{BOT_NUMBER}/settings/proxy_required = False", "INFO")
        log("[!] IP LOCAL sudah di-blacklist di FIREBASE, tidak bisa dipakai lagi!", "INFO")
        log("=" * 60, "INFO")
    
    # === BROWSER CONFIG ===
    base_args = "--disable-gpu,--no-sandbox,--disable-dev-shm-usage,--disable-blink-features=AutomationControlled"
    
    proxy_for_sb = None
    extension_path = None
    extension_dir = None
    
    if VALID_PROXY:
        if CLOUDFLARED_PROXY_VALID:
            # Cloudflared proxy - use localhost:9999
            proxy_for_sb = "127.0.0.1:9999"
            log(f"Proxy configured: Cloudflared tunnel (localhost:9999)", "SUCCESS")
        else:
            # Global proxy
            proxy_url, chrome_arg, proxy_user, proxy_pass, proxy_type = parse_proxy(VALID_PROXY)
            proxy_for_sb = chrome_arg
            log(f"Proxy configured: {chrome_arg} (type: {proxy_type})", "SUCCESS")
    else:
        log("Running WITHOUT proxy (IP asli)", "INFO")
    
    # === SUPER ELITE: Browser Profile Persistence ===
    # Create profile directory untuk bot ini
    profile_dir = f"./profiles/bot{BOT_NUMBER}"
    
    # BUGFIX: Check if profile is corrupt, clean if needed
    try:
        if os.path.exists(profile_dir):
            # Check if profile has lock files (Chrome crashed before)
            lock_files = ['SingletonLock', 'SingletonSocket', 'SingletonCookie']
            for lock_file in lock_files:
                lock_path = os.path.join(profile_dir, lock_file)
                if os.path.exists(lock_path):
                    try:
                        os.remove(lock_path)
                        log(f"[PROFILE] Removed stale lock: {lock_file}", "INFO")
                    except:
                        pass
    except Exception as e:
        log(f"[PROFILE] Cleanup warning: {e}", "INFO")
    
    os.makedirs(profile_dir, exist_ok=True)
    
    # Browser config (DISABLE INCOGNITO untuk cookies injection)
    config = {
        "uc": True,
        "incognito": False,  # MUST BE FALSE untuk cookies injection!
        "headless": False,
        "chromium_arg": base_args
    }
    
    if proxy_for_sb:
        config["proxy"] = proxy_for_sb
    
    log(f"[CONFIG] Browser: Normal mode (incognito=False untuk cookies), UC stealth enabled", "INFO")
    
    # === FARMING LOOP ===
    loop_count = 0
    success_count = 0
    fail_count = 0
    start_time = datetime.now()
    
    def run_single_session():
        """Run satu session dengan cookies + URL dari snapshot"""
        MAX_RETRIES = 1  # FIXED: 1x saja, tidak perlu 3x (buang waktu)
        
        for attempt in range(1, MAX_RETRIES + 1):
            log("\n" + "=" * 60, "INFO")
            log(f"STARTING BOT (Attempt {attempt}/{MAX_RETRIES})", "STEP")
            log(f"Target: {TARGET_URL[:60]}...", "URL")
            log(f"Cookies: {len(COOKIES_SNAPSHOT)} items (SNAPSHOT)", "INFO")
            log("=" * 60 + "\n", "INFO")
            
            # Local variable untuk cleanup
            local_cookies = COOKIES_SNAPSHOT.copy()  # Copy untuk safety
            
            try:
                log("[BROWSER] Launching Chrome...", "INFO")
                
                with SB(**config) as sb:
                    log("[BROWSER] Chrome ready!", "SUCCESS")
                    
                    # ==================== SIMPLIFIED CDP (NO DELAY) ====================
                    # Apply CDP commands - FAST MODE
                    try:
                        # 1. Disable automation flags
                        sb.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                            'source': '''
                                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                            '''
                        })
                        
                        # 2. Override permissions
                        sb.driver.execute_cdp_cmd('Browser.grantPermissions', {
                            'permissions': ['notifications', 'geolocation']
                        })
                        
                        log("[CDP] Stealth applied (fast mode)", "SUCCESS")
                    except:
                        pass  # Silent fail
                    
                    # ==================== INJECT COOKIES SEBELUM BUKA URL ====================
                    log("\n[COOKIES] Injecting cookies dari SNAPSHOT...", "ACTION")
                    
                    # Buka domain dulu untuk set cookies
                    from urllib.parse import urlparse
                    parsed = urlparse(TARGET_URL)
                    domain = f"{parsed.scheme}://{parsed.netloc}"
                    target_domain = parsed.netloc
                    
                    log(f"[COOKIES] Opening domain: {domain}", "ACTION")
                    sb.open(domain)
                    time.sleep(2)
                    
                    # Inject semua cookies
                    success_count_cookies = 0
                    failed_count_cookies = 0
                    
                    for cookie in local_cookies:
                        try:
                            # Remove expiry field jika ada (bisa bikin error)
                            if 'expiry' in cookie:
                                del cookie['expiry']
                            
                            # FIX: Update domain jika tidak match dengan target URL
                            cookie_domain = cookie.get('domain', '')
                            
                            # Jika domain kosong atau tidak match, set ke target domain
                            if not cookie_domain or cookie_domain not in target_domain:
                                log(f"[COOKIES]    Updating domain for {cookie['name']}: {cookie_domain} -> {target_domain}", "INFO")
                                cookie['domain'] = target_domain
                            
                            sb.add_cookie(cookie)
                            success_count_cookies += 1
                            log(f"[COOKIES]    Injected: {cookie['name']}", "SUCCESS")
                        except Exception as e:
                            failed_count_cookies += 1
                            log(f"[COOKIES]    Failed: {cookie.get('name', 'unknown')} - {str(e)[:50]}", "ERROR")
                    
                    log(f"\n[COOKIES] Injection result: {success_count_cookies} success, {failed_count_cookies} failed", "INFO")
                    
                    if success_count_cookies > 0:
                        log(f"[COOKIES] Refreshing page to apply cookies...", "ACTION")
                        sb.refresh()
                        time.sleep(2)
                        log(f"[COOKIES]  Cookies applied!", "SUCCESS")
                    
                    # ==================== INITIALIZE BOT ====================
                    if PROXY_REQUIRED:
                        bot = SafelinkBypassV2(sb, original_ip=original_ip, groq_manager=groq_manager, profile_id=f"bot{BOT_NUMBER}")
                    else:
                        bot = SafelinkBypassV2(sb, groq_manager=groq_manager, profile_id=f"bot{BOT_NUMBER}")
                    
                    # Run bot dengan URL dari _metadata (TARGET_URL sudah global)
                    bot.run()
                    
                    log("Session completed successfully!", "SUCCESS")
                    
                    # ==================== CLEANUP LOCAL COOKIES ====================
                    log("\n[CLEANUP] Clearing local cookies snapshot...", "INFO")
                    local_cookies.clear()
                    log("[CLEANUP]  Local cookies cleared", "SUCCESS")
                    
                    return True
                    
            except KeyboardInterrupt:
                # Cleanup sebelum exit
                log("\n[CLEANUP] Keyboard interrupt - clearing local cookies...", "INFO")
                local_cookies.clear()
                raise  # Re-raise untuk di-handle di luar
            except Exception as e:
                error_msg = str(e)
                log(f"Error on attempt {attempt}: {error_msg[:100]}", "ERROR")
                
                # Cleanup on error
                log("\n[CLEANUP] Error occurred - clearing local cookies...", "INFO")
                local_cookies.clear()
                
                if attempt < MAX_RETRIES:
                    log("Retrying...", "INFO")
                    time.sleep(3)
                else:
                    log(f"Max retries reached. Session failed.", "ERROR")
                    return False
        
        return False
    
    try:
        successful_loops = 0  # Counter untuk loop yang berhasil saja
        total_attempts = 0    # Counter untuk semua attempt (termasuk gagal proxy)
        
        while True:
            total_attempts += 1
            
            log("\n" + "=" * 60, "INFO")
            log(f"ATTEMPT #{total_attempts} (Successful loops: {successful_loops})", "STEP")
            log(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
            log("=" * 60, "INFO")
            
            # Cek max loops (hanya hitung yang berhasil)
            if MAX_LOOPS > 0 and successful_loops >= MAX_LOOPS:
                log(f"\n[+] Max successful loops ({MAX_LOOPS}) tercapai!", "SUCCESS")
                log(f"[+] Total attempts: {total_attempts}", "INFO")
                break
            
            # ==================== RELOAD COOKIES + URL (FRESH SNAPSHOT) ====================
            # Setiap loop, ambil cookies + URL baru dari Firebase
            log(f"\n{'='*60}", "INFO")
            log(f"RELOADING COOKIES + URL (FRESH SNAPSHOT)", "STEP")
            log(f"{'='*60}", "INFO")
            
            COOKIES_SNAPSHOT, TARGET_URL, METADATA = load_cookies_and_url_from_firebase(firebase_config, BOT_NUMBER)
            
            if not COOKIES_SNAPSHOT or not TARGET_URL:
                log(f"[!] Failed to reload cookies/URL - skipping this loop", "ERROR")
                fail_count += 1
                time.sleep(10)
                continue
            
            log(f" Fresh snapshot loaded!", "SUCCESS")
            log(f"  Cookies: {len(COOKIES_SNAPSHOT)} items", "INFO")
            log(f"  URL: {TARGET_URL[:60]}...", "INFO")
            log(f"  Timestamp: {METADATA.get('timestamp', 'N/A')}", "INFO")
            
            log(f"Stats: {success_count} success, {fail_count} fail", "INFO")
            
            # Run session (tanpa parameter, pakai global COOKIES_SNAPSHOT & TARGET_URL)
            session_success = run_single_session()
            
            if session_success:
                success_count += 1
                successful_loops += 1  # Hanya increment jika berhasil
                log(f"\n[+] SUCCESSFUL LOOP #{successful_loops} completed!", "SUCCESS")
            else:
                fail_count += 1
                log(f"\n[-] Session failed (not counted in max_loops)", "ERROR")
            
            # Cleanup extension jika ada
            if extension_dir and os.path.exists(extension_dir):
                import shutil
                shutil.rmtree(extension_dir, ignore_errors=True)
            
            # Blacklist proxy setelah selesai dipakai (hanya jika session berhasil)
            if session_success and PROXY_REQUIRED and VALID_PROXY:
                if VALID_PROXY not in blacklist:
                    add_to_firebase_blacklist(firebase_config, VALID_PROXY)
                    blacklist.append(VALID_PROXY)
                    log(f"[+] Proxy {VALID_PROXY} blacklisted after successful use", "INFO")
            
            # Cek apakah loop mode aktif
            if not LOOP_ENABLED:
                log("\nLoop mode disabled. Stopping after 1 session.", "INFO")
                break
            
            # Delay hanya jika session berhasil
            if session_success:
                delay = random.randint(DELAY_MIN, DELAY_MAX)
                log(f"\n[*] Waiting {delay} seconds ({delay//60} min {delay%60} sec) before next loop...", "INFO")
                
                # Countdown
                for remaining in range(delay, 0, -30):
                    log(f"    {remaining} seconds remaining...", "INFO")
                    time.sleep(min(30, remaining))
                
                # Reload proxy untuk loop berikutnya
                log("\n[*] Reloading proxy untuk next loop...", "INFO")
                blacklist = load_blacklist_from_firebase(firebase_config)
                PROXY_LIST = load_proxies_from_firebase(firebase_config)
                
                # Filter available proxies
                available = [p for p in PROXY_LIST if p not in blacklist]
                if available:
                    # Cari proxy baru
                    for proxy in available:
                        proxy_url_check, _, _, _, _ = parse_proxy(proxy)
                        if proxy_url_check:
                            proxies_test = {"http": proxy_url_check, "https": proxy_url_check}
                            test_ip = get_my_ip(proxies_test)
                            if test_ip and original_ip not in test_ip:
                                VALID_PROXY = proxy
                                proxy_url, chrome_arg, _, _, proxy_type = parse_proxy(VALID_PROXY)
                                proxy_for_sb = chrome_arg
                                config["proxy"] = proxy_for_sb
                                log(f"[+] New proxy: {VALID_PROXY}", "SUCCESS")
                                break
                    else:
                        log("[!] No valid proxy found for next loop", "ERROR")
                else:
                    log("[!] No available proxies (semua sudah di-blacklist)", "ERROR")
            else:
                # Jika session gagal, langsung coba lagi tanpa delay
                log(f"\n[*] Session failed, retrying immediately...", "INFO")
                # Reset VALID_PROXY agar dicari ulang
                VALID_PROXY = None
                CLOUDFLARED_PROXY_VALID = False

            
    except KeyboardInterrupt:
        log("\n\n[!] Stopped by user (Ctrl+C)", "INFO")
    finally:
        # Cleanup cloudflared tunnel if running
        if CLOUDFLARED_PROCESS:
            log("\n[CLEANUP] Stopping Cloudflared tunnel...", "INFO")
            stop_cloudflared_tunnel(CLOUDFLARED_PROCESS)
    
    # === FINAL STATS ===
    end_time = datetime.now()
    duration = end_time - start_time
    
    log("\n" + "=" * 60, "INFO")
    log("FARMING SESSION COMPLETE", "SUCCESS")
    log("=" * 60, "INFO")
    log(f"Total Loops: {loop_count}", "INFO")
    log(f"Success: {success_count}", "SUCCESS")
    log(f"Failed: {fail_count}", "ERROR" if fail_count > 0 else "INFO")
    log(f"Duration: {duration}", "INFO")
    log(f"Success Rate: {success_count/max(loop_count,1)*100:.1f}%", "INFO")
    log("=" * 60, "INFO")


if __name__ == "__main__":
    main()

