import sys
import time
import statistics
import torch

sys.stdout.reconfigure(encoding="utf-8")
from src.models.translator.service import TranslatorService
from src.models.example_generator.service import ExampleGeneratorService


def format_stats(runs_ms):
    m = statistics.mean(runs_ms)
    s = statistics.stdev(runs_ms) if len(runs_ms) > 1 else 0.0
    return (
        f"mean={m:.2f} ms | min={min(runs_ms):.2f} ms | max={max(runs_ms):.2f} ms | "
        f"std={s:.2f} ms (runs={len(runs_ms)})"
    )


def main():
    print("=== BENCHMARK 1: MATMUL 4000x4000 ===")
    n1 = 4000
    # CPU (10 runs)
    x_cpu1 = torch.randn(n1, n1, device="cpu")
    torch.matmul(x_cpu1, x_cpu1)  # Warmup
    cpu_m4k = []
    for _ in range(10):
        t0 = time.perf_counter()
        torch.matmul(x_cpu1, x_cpu1)
        cpu_m4k.append((time.perf_counter() - t0) * 1000)
    print("CPU (4000x4000):", format_stats(cpu_m4k))

    # GPU (10 runs)
    x_gpu1 = torch.randn(n1, n1, device="cuda")
    torch.cuda.synchronize()
    torch.matmul(x_gpu1, x_gpu1)  # Warmup
    torch.cuda.synchronize()
    gpu_m4k = []
    for _ in range(10):
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        torch.matmul(x_gpu1, x_gpu1)
        torch.cuda.synchronize()
        gpu_m4k.append((time.perf_counter() - t0) * 1000)
    print("GPU (4000x4000):", format_stats(gpu_m4k))
    print(f"Speedup (Mean): {statistics.mean(cpu_m4k)/statistics.mean(gpu_m4k):.2f}x\n")

    print("=== BENCHMARK 2: MATMUL 8192x8192 ===")
    n2 = 8192
    # CPU (5 runs)
    x_cpu2 = torch.randn(n2, n2, device="cpu")
    torch.matmul(x_cpu2, x_cpu2)  # Warmup
    cpu_m8k = []
    for _ in range(5):
        t0 = time.perf_counter()
        torch.matmul(x_cpu2, x_cpu2)
        cpu_m8k.append((time.perf_counter() - t0) * 1000)
    print("CPU (8192x8192):", format_stats(cpu_m8k))

    # GPU (10 runs)
    x_gpu2 = torch.randn(n2, n2, device="cuda")
    torch.cuda.synchronize()
    torch.matmul(x_gpu2, x_gpu2)  # Warmup
    torch.cuda.synchronize()
    gpu_m8k = []
    for _ in range(10):
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        torch.matmul(x_gpu2, x_gpu2)
        torch.cuda.synchronize()
        gpu_m8k.append((time.perf_counter() - t0) * 1000)
    tflops = (2 * n2**3) / (statistics.mean(gpu_m8k) * 1e-3 * 1e12)
    print("GPU (8192x8192):", format_stats(gpu_m8k), f"| Throughput: {tflops:.2f} TFLOPS")
    print(f"Speedup (Mean): {statistics.mean(cpu_m8k)/statistics.mean(gpu_m8k):.2f}x\n")

    print("=== BENCHMARK 3: MODEL 1 TRANSLATOR (MarianMT Seq2Seq) ===")
    sample_sentence = "Công nghệ giúp con người giải quyết nhiều vấn đề phức tạp."
    trans_cpu = TranslatorService("src/models/translator/checkpoint-best", device="cpu")
    trans_cpu.translate(sample_sentence)  # Warmup
    cpu_trans = []
    for _ in range(10):
        t0 = time.perf_counter()
        trans_cpu.translate(sample_sentence)
        cpu_trans.append((time.perf_counter() - t0) * 1000)
    print("CPU Translator:", format_stats(cpu_trans))

    trans_gpu = TranslatorService("src/models/translator/checkpoint-best", device="cuda")
    trans_gpu.translate(sample_sentence)  # Warmup
    gpu_trans = []
    for _ in range(10):
        t0 = time.perf_counter()
        trans_gpu.translate(sample_sentence)
        gpu_trans.append((time.perf_counter() - t0) * 1000)
    print("GPU Translator:", format_stats(gpu_trans))
    print(f"Speedup (Mean): {statistics.mean(cpu_trans)/statistics.mean(gpu_trans):.2f}x\n")

    print("=== BENCHMARK 4: MODEL 3A EXAMPLE GENERATOR (FLAN-T5-small Seq2Seq) ===")
    gen_cpu = ExampleGeneratorService("src/models/example_generator/checkpoint-best", device="cpu")
    gen_cpu.generate("comprehend", "B2")  # Warmup
    cpu_gen = []
    for _ in range(5):
        t0 = time.perf_counter()
        gen_cpu.generate("comprehend", "B2")
        cpu_gen.append((time.perf_counter() - t0) * 1000)
    print("CPU Example Gen:", format_stats(cpu_gen))

    gen_gpu = ExampleGeneratorService(
        "src/models/example_generator/checkpoint-best", device="cuda"
    )
    gen_gpu.generate("comprehend", "B2")  # Warmup
    gpu_gen = []
    for _ in range(5):
        t0 = time.perf_counter()
        gen_gpu.generate("comprehend", "B2")
        gpu_gen.append((time.perf_counter() - t0) * 1000)
    print("GPU Example Gen:", format_stats(gpu_gen))
    print(f"Speedup (Mean): {statistics.mean(cpu_gen)/statistics.mean(gpu_gen):.2f}x\n")

    print("=== SPOT-CHECK: MODEL 1 TRANSLATION ON GPU ===")
    spot_input = "Trí tuệ nhân tạo đang thay đổi cách chúng ta tiếp cận tri thức."
    t0 = time.perf_counter()
    spot_output = trans_gpu.translate(spot_input)
    t_spot = (time.perf_counter() - t0) * 1000
    print(f'Input (VI): "{spot_input}"')
    print(f'Output (EN): "{spot_output}"')
    print(f"Device: {trans_gpu.device}")
    print(f"Latency: {t_spot:.2f} ms")


if __name__ == "__main__":
    main()
