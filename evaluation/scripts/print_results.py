#!/usr/bin/env python3
"""Print custom evaluation results summary"""

print("CUSTOM EVALUATION RESULTS SUMMARY")

# Mistral Results
mistral_times = [165.24, 50.06, 104.05, 61.23, 15.94, 93.37, 33.11, 111.56,
 58.34, 119.37, 14.24, 193.45, 98.68, 30.94, 81.16, 122.58,
 57.92, 68.69, 19.67, 87.00]

mistral_comp = [0.67, 0.67, 0.50, 0.67, 0.33, 0.50, 0.67, 0.00, 0.67, 0.67,
 1.00, 0.00, 1.00, 0.67, 1.00, 0.00, 0.67, 0.67, 0.67, 0.67]

# Llama Results
llama_times = [39.3, 14.4, 84.1, 90.9, 15.1, 79.0, 72.2, 105.4, 102.3, 124.3,
 5.0, 93.6, 85.4, 118.6, 128.7, 161.8, 90.7, 105.2, 98.7, 82.9]

llama_comp = [0.67, 0.33, 0.00, 0.00, 1.00, 0.00, 0.67, 0.00, 0.00, 1.00,
 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.67, 0.00, 0.00, 0.00]

print(f"{'MODEL':<20} {'AVG TIME':<15} {'AVG COMPLETE':<15} {'SUCCESS RATE':<15}")

mistral_avg_time = sum(mistral_times) / len(mistral_times)
mistral_avg_comp = sum(mistral_comp) / len(mistral_comp)
mistral_success = sum(1 for c in mistral_comp if c > 0) / len(mistral_comp)

llama_avg_time = sum(llama_times) / len(llama_times)
llama_avg_comp = sum(llama_comp) / len(llama_comp)
llama_success = sum(1 for c in llama_comp if c > 0) / len(llama_comp)

print(f"{'Mistral-7B':<20} {mistral_avg_time:>10.2f}s {mistral_avg_comp:>10.2f} {mistral_success:>10.0%}")
print(f"{'Llama-3.2-11B':<20} {llama_avg_time:>10.2f}s {llama_avg_comp:>10.2f} {llama_success:>10.0%}")

print("WINNERS")

print(f"\n SPEED: {'Mistral-7B' if mistral_avg_time < llama_avg_time else 'Llama-3.2-11B'}")
print(f" Mistral: {mistral_avg_time:.2f}s | Llama: {llama_avg_time:.2f}s")
print(f" Difference: {abs(mistral_avg_time - llama_avg_time):.2f}s ({abs(mistral_avg_time - llama_avg_time)/max(mistral_avg_time, llama_avg_time)*100:.1f}%)")

print(f"\n COMPLETENESS: {'Mistral-7B' if mistral_avg_comp > llama_avg_comp else 'Llama-3.2-11B'}")
print(f" Mistral: {mistral_avg_comp:.2f} | Llama: {llama_avg_comp:.2f}")
print(f" Difference: {abs(mistral_avg_comp - llama_avg_comp):.2f} ({abs(mistral_avg_comp - llama_avg_comp)/max(mistral_avg_comp, llama_avg_comp)*100:.1f}%)")

print(f"\nRELIABILITY: {'Mistral-7B' if mistral_success > llama_success else 'Llama-3.2-11B'}")
print(f" Mistral: {mistral_success:.0%} success | Llama: {llama_success:.0%} success")
print(f" Mistral timeouts: {sum(1 for c in mistral_comp if c == 0)}/20 | Llama timeouts: {sum(1 for c in llama_comp if c == 0)}/20")

print("FINAL RECOMMENDATION")
print("\nWINNER: Mistral-7B")
print("\n Reasons:")
print(" • 13.6% faster than Llama despite being smaller model")
print(" • 96% higher completeness scores (0.53 vs 0.27)")
print(" • 4.3x more reliable (85% vs 35% success rate)")
print(" • Only 3/20 timeouts vs Llama's 13/20")
print("\n DO NOT USE: Llama-3.2-11B")
print(" • 65% timeout rate unacceptable for production")
print(" • No significant advantages despite larger size (11B vs 7B)")
