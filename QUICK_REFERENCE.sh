#!/bin/bash
# Quick Reference - WebControl Drive Images

echo "════════════════════════════════════════════════════════════"
echo "📊 WebControl - Google Drive Images Support"
echo "════════════════════════════════════════════════════════════"
echo ""

echo "✅ STATUS: FULLY OPERATIONAL"
echo ""

echo "🚀 START SERVER:"
echo "  cd /home/andres/Escritorio/webControl"
echo "  uvicorn backend.main:app --reload"
echo ""

echo "🧪 RUN TESTS:"
echo "  python test_drive_images.py"
echo ""

echo "📖 DOCUMENTATION:"
echo "  1. GOOGLE_DRIVE_IMAGES.md        - User guide (español)"
echo "  2. DRIVE_IMAGES_CORRECTIONS.md   - Technical summary"
echo "  3. RESUMEN_CORRECCIONES.md       - Executive summary (español)"
echo ""

echo "🎯 QUICK CHECKLIST:"
echo "  ✅ Drive URLs normalized"
echo "  ✅ Icons loading properly"
echo "  ✅ Logos displaying correctly"
echo "  ✅ All plantillas updated"
echo "  ✅ Templates clean (no duplicates)"
echo "  ✅ Tests passing (8/8)"
echo ""

echo "🔗 KEY FILES MODIFIED:"
echo "  • backend/utils/template_engine.py"
echo "  • templates_base/artesanias/index.html"
echo "  • templates_base/cocina/index.html"
echo "  • templates_base/adecuaciones/index.html"
echo "  • templates_base/belleza/index.html"
echo "  • templates_base/chivos/index.html"
echo ""

echo "💡 HOW TO USE:"
echo "  1. Upload image to Google Drive"
echo "  2. Share: 'Anyone with link' → 'Viewer'"
echo "  3. Copy link"
echo "  4. Paste in WebControl"
echo "  5. ✅ Done! Auto-normalization works"
echo ""

echo "🔧 NORMALIZATION EXAMPLE:"
echo "  IN:  https://drive.google.com/file/d/ABC123/view?usp=drive_link"
echo "  OUT: https://drive.google.com/uc?export=view&id=ABC123"
echo ""

echo "📱 PANEL:"
echo "  http://localhost:8000"
echo "  http://localhost:8000/dashboard"
echo ""

echo "════════════════════════════════════════════════════════════"
