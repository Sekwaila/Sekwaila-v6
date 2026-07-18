"""
SEKWAILA OMEGA X
System Test
"""

print("Starting SEKWAILA OMEGA X...\n")

modules = [
    "config",
    "data",
    "indicators",
    "smc",
    "signals",
    "risk",
    "ai",
    "telegram_bot",
    "dashboard",
    "backtest",
    "logger",
    "utils",
]

passed = 0

for module in modules:
    try:
        __import__(module)
        print(f"✅ {module}")
        passed += 1
    except Exception as e:
        print(f"❌ {module}")
        print(e)

print("\n---------------------")
print(f"Passed: {passed}/{len(modules)}")
print("---------------------")

if passed == len(modules):
    print("🚀 SEKWAILA OMEGA X is ready.")
else:
    print("⚠ Some modules need fixing.")
