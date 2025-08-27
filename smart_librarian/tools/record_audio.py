# Tool pentru înregistrarea audio
import argparse
import queue
import sys
from pathlib import Path
import sounddevice as sd
import soundfile as sf
import numpy as np

def list_devices():
    print("\n=== Dispozitive audio disponibile ===")
    print(sd.query_devices())

def check_device_and_rate(device, samplerate, channels):
    """Verifică dacă device-ul suportă setările dorite."""
    try:
        sd.check_input_settings(device=device, samplerate=samplerate, channels=channels)
        return True, ""
    except Exception as e:
        return False, str(e)

def record_duration(out_path: str, device: int | None, samplerate: int, channels: int, seconds: int):
    """Înregistrează un număr fix de secunde și salvează în WAV."""
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    ok, err = check_device_and_rate(device, samplerate, channels)
    if not ok:
        raise RuntimeError(f"Setări incompatibile cu device-ul: {err}")

    print(f"\n[REC] Încep înregistrarea pentru {seconds}s ...")
    sd.default.device = (device, None) if device is not None else None
    data = sd.rec(int(seconds * samplerate), samplerate=samplerate, channels=channels, dtype='float32')
    sd.wait()  # așteaptă să termine
    # scriem ca PCM_16
    sf.write(out_file, data, samplerate, subtype='PCM_16')
    print(f"[REC] Gata. Fișier salvat la: {out_file.resolve()}")

def record_live(out_path: str, device: int | None, samplerate: int, channels: int):
    """Înregistrează până la Ctrl+C, folosind un stream + callback."""
    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    ok, err = check_device_and_rate(device, samplerate, channels)
    if not ok:
        raise RuntimeError(f"Setări incompatibile cu device-ul: {err}")

    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        q.put(indata.copy())

    print("\n[REC] Pornit. Vorbește în microfon. Apasă Ctrl+C pentru STOP...")
    sd.default.device = (device, None) if device is not None else None
    with sf.SoundFile(out_file, mode='w', samplerate=samplerate, channels=channels, subtype='PCM_16') as f:
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
            try:
                while True:
                    # SoundFile acceptă float32; convertim la int16 pentru consistență
                    chunk = q.get()
                    f.write(chunk.astype(np.float32))
            except KeyboardInterrupt:
                print(f"\n[REC] Oprit. Fișier salvat la: {out_file.resolve()}")

def main():
    parser = argparse.ArgumentParser(description="Înregistrează audio de la microfon într-un fișier WAV.")
    parser.add_argument("--out", type=str, default="outputs/voice/input.wav", help="Calea fișierului WAV de ieșire")
    parser.add_argument("--device", type=int, default=None, help="Indexul dispozitivului audio (vezi --list)")
    parser.add_argument("--sr", type=int, default=44100, help="Sample rate (Hz), ex. 44100 sau 48000")
    parser.add_argument("--channels", type=int, default=1, help="Număr canale (1=mono, 2=stereo)")
    parser.add_argument("--mode", choices=["duration", "live"], default="duration", help="Mod de înregistrare")
    parser.add_argument("--seconds", type=int, default=10, help="Durata în secunde (doar pentru mode=duration)")
    parser.add_argument("--list", action="store_true", help="Listează dispozitivele și iese")
    args = parser.parse_args()

    if args.list:
        list_devices()
        return

    # Recomandăm să potrivești sr cu ce raportează device-ul tău (vezi --list, câmpul default_samplerate)
    try:
        if args.mode == "duration":
            record_duration(args.out, args.device, args.sr, args.channels, args.seconds)
        else:
            record_live(args.out, args.device, args.sr, args.channels)
    except Exception as e:
        print(f"[Eroare] {e}")
        print("\nSugestii:")
        print(" - Rulează cu --list și alege un --device corect")
        print(" - Încearcă --sr 48000 sau 44100, și channels=1")
        print(" - Verifică permisiunea Microphone în Windows: Settings → Privacy → Microphone")
        print(" - Dezactivează 'Exclusive Mode' la microfon (Sound settings → Device Properties → Advanced)")

if __name__ == "__main__":
    main()
