# AI-Adaptive Onboarding Engine - Presentation Diagrams

This folder contains 3 comprehensive diagrams for the AI-Adaptive Onboarding Engine project, designed for presentations, documentation, and project visualization.

## 📊 Diagrams Included

### 1. **System Architecture** (`1_system_architecture.*`)
**Description:** 5-layer architectural design showing the complete system structure

- **Frontend Layer:** React/Vue/HTML UI components for user interaction
- **Backend Layer:** Flask REST API for handling client requests
- **Processing Layer:** NLP pipeline for text extraction and analysis
- **AI/ML Models Layer:** sentence-transformers + PyTorch for semantic understanding
- **Output Layer:** Results generation and skill recommendations

**Use Cases:**
- Technical presentations to stakeholders
- Architecture documentation
- Understanding system design
- Integration planning

**Available Formats:**
- 📄 `1_system_architecture.png` - High-quality PNG (22 KB) - Use in PowerPoint/Slides
- 📐 `1_system_architecture.svg` - Scalable vector - Embed in documents
- 🔤 `1_system_architecture.mmd` - Mermaid source - Edit and customize
- 🌐 `1_system_architecture.html` - Interactive web version - Open in browser

---

### 2. **Data Flow Pipeline** (`2_data_flow.*`)
**Description:** Complete data processing pipeline from input to output

**Flow Steps:**
1. **Input:** Resume PDF + Job Description files
2. **Dual-Mode Extraction:** 
   - Keyword-based extraction
   - LLM-based semantic extraction
3. **Semantic Matching:** Compare extracted skills with job requirements
4. **Risk Assessment:** Identify skill gaps and prioritize by importance
5. **Output Generation:** Generate skill gap report and learning recommendations

**Use Cases:**
- Product demos
- Algorithm explanation
- UI/UX flow documentation
- Workflow presentations

**Available Formats:**
- 📄 `2_data_flow.png` - High-quality PNG (24 KB) - Use in presentations
- 📐 `2_data_flow.svg` - Scalable vector - Embed in web pages
- 🔤 `2_data_flow.mmd` - Mermaid source - Modify flow steps
- 🌐 `2_data_flow.html` - Interactive web version - View in browser

---

### 3. **User Journey & UI/UX Logic** (`3_ui_ux_logic.*`)
**Description:** Complete user interaction flow from onboarding to export

**User Steps:**
1. 📤 **Upload** - User uploads resume and job description
2. 🎯 **Select** - Choose extraction method (keyword/LLM/both)
3. 🔍 **Analyze** - System processes files and extracts skills
4. ⚙️ **Process** - AI models semantically match and assess
5. 📋 **Generate** - Create skill gap report
6. 👁️ **View** - Display results in interactive dashboard
7. 💾 **Export** - Download report as PDF/CSV
8. 🔄 **Retry** - Upload new files or modify parameters

**Use Cases:**
- Wireframe and mockup presentations
- User testing documentation
- Onboarding guides
- Feature roadmap visualization

**Available Formats:**
- 📄 `3_ui_ux_logic.png` - High-quality PNG (20 KB) - Use in presentations
- 📐 `3_ui_ux_logic.svg` - Scalable vector - Embed in prototypes
- 🔤 `3_ui_ux_logic.mmd` - Mermaid source - Add/remove steps
- 🌐 `3_ui_ux_logic.html` - Interactive web version - View in browser

---

## 🎯 How to Use

### For PowerPoint/Google Slides Presentations:
1. Copy the `.png` files to your presentation
2. Click on the image → Select "Format Picture"
3. Right-click → "Insert → Image" from this folder

### For Web Documentation:
1. Use `.html` files directly in browsers or embed in HTML pages
2. Use `<embed>` tag for `.svg` files in HTML
3. Reference the `.mmd` files with Mermaid.js CDN

### For Editing Diagrams:
1. Visit [mermaid.live](https://mermaid.live)
2. Paste content from `.mmd` files
3. Make edits
4. Export as PNG/SVG/PDF

### For GitHub README:
```markdown
![System Architecture](diagrams/1_system_architecture.png)
![Data Flow](diagrams/2_data_flow.png)
![User Journey](diagrams/3_ui_ux_logic.png)
```

---

## 📦 File Size Reference

| Diagram | PNG | SVG | Mermaid |
|---------|-----|-----|---------|
| System Architecture | 22 KB | 2.2 KB | 1.9 KB |
| Data Flow Pipeline | 24 KB | 2.0 KB | 1.2 KB |
| User Journey | 20 KB | 2.2 KB | 1.9 KB |
| **Total** | **66 KB** | **6.4 KB** | **5.0 KB** |

---

## 🔄 Format Comparison

### PNG (Raster)
- ✅ Best for: Presentations, printed documents
- ✅ Wide compatibility
- ✅ Embedded easily in PowerPoint/Slides
- ❌ Not scalable (may pixelate when enlarged)
- File Size: 20-24 KB each

### SVG (Vector)
- ✅ Best for: Web embedding, scalable graphics
- ✅ Fully scalable without quality loss
- ✅ Can embed in HTML directly
- ✅ Can apply CSS styling
- ❌ Not supported in older PowerPoint versions
- File Size: 2-2.2 KB each

### Mermaid (Source)
- ✅ Best for: Version control, easy editing
- ✅ Smallest file size
- ✅ git-friendly
- ✅ Can render in GitHub READMEs with proper markdown
- ❌ Requires Mermaid.js to render
- File Size: 1.2-1.9 KB each

### HTML (Interactive)
- ✅ Best for: Web viewing, interactive exploration
- ✅ Renders with Mermaid.js CDN
- ✅ Open directly in any browser
- ✅ Responsive design
- ❌ Requires internet for CDN
- File Size: 1.5-2.3 KB each

---

## 🛠️ Customization Guide

### To edit a diagram:
1. **Using Mermaid Live Editor:**
   - Open [mermaid.live](https://mermaid.live)
   - Paste content from `.mmd` file
   - Edit the syntax
   - Export as new PNG/SVG

2. **Using HTML Files:**
   - Open `.html` file in any text editor
   - Find the `<div class="mermaid">` section
   - Modify the Mermaid syntax inside
   - Save and open in browser

3. **Using SVG Files:**
   - Open in Inkscape, Adobe Illustrator, or online editor
   - Edit shapes, colors, and text
   - Export as PNG if needed

---

## 📝 Diagram Source Code

Detailed Mermaid syntax for each diagram is stored in respective `.mmd` files:
- Full source code is version-controlled in git
- Can be easily modified and regenerated
- See [DIAGRAMS_GUIDE.md](../DIAGRAMS_GUIDE.md) for detailed code

---

## 🚀 Integration with Project

These diagrams are integrated into:
- **README.md** - Main project overview
- **DIAGRAMS_GUIDE.md** - Detailed conversion instructions
- **Presentations** - Hackathon submissions
- **Documentation** - Technical architecture docs

---

## 📞 Support

For questions about specific diagrams or to request modifications:
1. Check the Mermaid source files (`.mmd`)
2. Refer to [DIAGRAMS_GUIDE.md](../DIAGRAMS_GUIDE.md) for generation methods
3. Use Mermaid.live for interactive editing

---

**Last Updated:** March 21, 2024
**Source Repository:** [adaptive-onboarding-engine](https://github.com/vaishnavkoka/adaptive-onboarding-engine)
