#!/usr/bin/env python3
"""
Test script para verificar que las imágenes de Google Drive se normalizan correctamente
y que la aplicación carga sin errores.
"""
import sys
sys.path.insert(0, '/home/andres/Escritorio/webControl')

from backend.utils.template_engine import normalize_drive_image, TemplateEngine

print("=" * 70)
print("🧪 TEST: Google Drive Image Normalization")
print("=" * 70)

# Test 1: Drive URL extraction and normalization
print("\n✅ Test 1: Drive URL Normalization")
print("-" * 70)

test_cases = [
    {
        "name": "Drive link with /file/d/ format",
        "input": "https://drive.google.com/file/d/1maQ1FoXyzxfoS_sq6qN-oRLiPELKF_yV/view?usp=drive_link",
        "expected_contains": "https://drive.google.com/uc?export=view&id=1maQ1FoXyzxfoS_sq6qN-oRLiPELKF_yV"
    },
    {
        "name": "Drive link with open?id= format",
        "input": "https://drive.google.com/open?id=1maQ1FoXyzxfoS_sq6qN-oRLiPELKF_yV",
        "expected_contains": "https://drive.google.com/uc?export=view&id=1maQ1FoXyzxfoS_sq6qN-oRLiPELKF_yV"
    },
    {
        "name": "Regular image URL (should pass through)",
        "input": "https://images.unsplash.com/photo-1234.jpg",
        "expected_contains": "https://images.unsplash.com/photo-1234.jpg"
    },
    {
        "name": "Empty string (should return empty)",
        "input": "",
        "expected_contains": ""
    }
]

all_passed = True
for test in test_cases:
    result = normalize_drive_image(test["input"])
    passed = test["expected_contains"] in result if test["expected_contains"] else result == ""
    status = "✅ PASS" if passed else "❌ FAIL"
    
    print(f"\n{status}: {test['name']}")
    print(f"  Input:    {test['input'][:60]}...")
    print(f"  Output:   {result[:60]}...")
    print(f"  Expected: {test['expected_contains'][:60]}...")
    
    if not passed:
        all_passed = False
        print(f"  ERROR: Output does not match expected!")

# Test 2: Template Engine initialization
print("\n\n✅ Test 2: Template Engine Initialization")
print("-" * 70)

try:
    engine = TemplateEngine()
    print("✅ PASS: TemplateEngine initialized successfully")
    print(f"   Templates directory: {engine.templates_dir}")
except Exception as e:
    print(f"❌ FAIL: {e}")
    all_passed = False

# Test 3: Template helper registration
print("\n✅ Test 3: Template Helper Registration")
print("-" * 70)

try:
    from jinja2 import Template
    
    template = Template('{{ normalize_drive_image(url) }}')
    template.globals["normalize_drive_image"] = normalize_drive_image
    
    test_url = "https://drive.google.com/file/d/ABC123/view?usp=drive_link"
    result = template.render(url=test_url)
    
    if "uc?export=view&id=ABC123" in result:
        print("✅ PASS: normalize_drive_image works in Jinja2 templates")
        print(f"   Template output: {result}")
    else:
        print(f"❌ FAIL: Template rendering didn't work as expected")
        print(f"   Output: {result}")
        all_passed = False
except Exception as e:
    print(f"❌ FAIL: {e}")
    all_passed = False

# Final summary
print("\n" + "=" * 70)
if all_passed:
    print("✅ ALL TESTS PASSED!")
    print("Drive image normalization is working correctly.")
    sys.exit(0)
else:
    print("❌ SOME TESTS FAILED")
    print("Please fix the issues above.")
    sys.exit(1)
